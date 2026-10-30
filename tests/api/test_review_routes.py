"""Real Postgres integration of JWT-derived independent reviewer identity."""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("PG_REGISTRY_TEST_URL"), reason="requires migrated PostgreSQL",
)

@pytest.fixture()
def api():
    import jwt
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from cryptography.hazmat.primitives.asymmetric import rsa
    from productpulse.api.app import create_app
    from productpulse.api.reviewer_auth import ReviewerJWTVerifier
    from productpulse.storage.repository import PersistentProblemRegistry
    from productpulse.data.canonical import ticket_key,CanonicalTicketV1

    engine=create_engine(os.environ["PG_REGISTRY_TEST_URL"],pool_pre_ping=True)
    store=PersistentProblemRegistry(engine)
    scope=f"human-{uuid4().hex}"
    private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    issuer="https://idp.example.org/realms/test"
    verifier=ReviewerJWTVerifier(
        issuer=issuer,audience="productpulse-review-api",
        signing_key_resolver=lambda token: private.public_key(),
    )
    def signed(who,role="productpulse_reviewer",tenant=None,private_key=None):
        now=datetime.now(timezone.utc)
        return jwt.encode({
            "iss":issuer,"aud":"productpulse-review-api","sub":who,
            "iat":now,"nbf":now,"exp":now+timedelta(minutes=15),
            "tenant_scope":tenant or scope,"roles":[role],
        },private_key or private,algorithm="RS256",headers={"kid":"test-key"})
    service_token="ci-strong-internal-service-token-256bits"
    headers={"X-Internal-Token":service_token}
    with TestClient(create_app(store,scope,service_token,reviewer_verifier=verifier)) as client:
        keys=[]
        for id_ in ("a","b"):
            ticket={"source_system":"synthetic","source_ticket_id":id_,
                    "provenance_id":"test", "body_redacted":"Сбой ERP HTTP 403"}
            r=client.post("/internal/v1/tickets",headers=headers,json=ticket)
            assert r.status_code==201,r.text
            keys.append(ticket_key(CanonicalTicketV1(**ticket)))
        yield client,store,scope,keys,headers,signed
    engine.dispose()


def vote(keys,label="same_incident",op="review-op"):
    return {
        "ticket_key_a":keys[0],"ticket_key_b":keys[1],
        "label":label,"rationale":"Сравнили воспроизведение ошибки и логи",
        "operation_key":op,
    }


def h(base,signed,who,role="productpulse_reviewer",tenant=None):
    return {**base,"Authorization":"Bearer "+signed(who,role,tenant)}


def test_without_oidc_verifier_routes_fail_closed():
    from fastapi.testclient import TestClient
    from productpulse.api.app import create_app
    with TestClient(create_app(None,"tenant","secure-internal-token-with-24-characters")) as c:
        r=c.get("/internal/v1/reviews",headers={"X-Internal-Token":"secure-internal-token-with-24-characters",
                                                "Authorization":"Bearer anything"})
        assert r.status_code==503


def test_no_service_token_cannot_submit_even_with_valid_oidc(api):
    c,store,scope,keys,base,signed=api
    r=c.post("/internal/v1/reviews",headers={"Authorization":"Bearer "+signed("a")},json=vote(keys))
    assert r.status_code==401


def test_no_oidc_bearer_or_forged_reviewer_id_is_denied(api):
    c,store,scope,keys,base,signed=api
    assert c.post("/internal/v1/reviews",headers=base,json=vote(keys)).status_code==401
    assert c.post("/internal/v1/reviews",headers={**base,"Authorization":"Bearer fake"},json=vote(keys)).status_code==401
    poisoned={**vote(keys),"reviewer_id":"forged-admin","reviewed_at":"2026-10-30T12:00:00Z"}
    assert c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"),json=poisoned).status_code==422


def test_wrong_role_and_scope_must_not_review(api):
    c,store,scope,keys,base,signed=api
    assert c.post("/internal/v1/reviews",headers=h(base,signed,"intruder","other"),json=vote(keys)).status_code in (401,403)
    assert c.post("/internal/v1/reviews",headers=h(base,signed,"intruder",tenant="another-scope"),json=vote(keys)).status_code in (401,403)


def test_two_independent_reviewers_and_third_lead_approve_without_merging(api):
    c,store,scope,keys,base,signed=api
    one=c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"),json=vote(keys,"same_incident","vote-a"))
    assert one.status_code==201,one.text
    assert one.json()["status"]=="awaiting_second_review"
    two=c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-B"),json=vote(keys,"same_incident","vote-b"))
    assert two.status_code==201,two.text
    assert two.json()["status"]=="ready_for_lead"
    same=c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"),json=vote(keys,"same_incident","second"))
    assert same.status_code==409
    as_reviewer=c.post("/internal/v1/reviews/approve",
        headers=h(base,signed,"reviewer-A","productpulse_review_lead"),
        json={**{"ticket_key_a":keys[0],"ticket_key_b":keys[1],"reason":"Согласен","operation_key":"lead-a"}})
    assert as_reviewer.status_code==409
    approved=c.post("/internal/v1/reviews/approve",
        headers=h(base,signed,"reviewer-lead","productpulse_review_lead"),
        json={"ticket_key_a":keys[0],"ticket_key_b":keys[1],"reason":"Согласен","operation_key":"lead-b"})
    assert approved.status_code==201,approved.text
    assert len(approved.json()["reviewer_ids"])==2
    assert len(c.get("/internal/v1/problems",headers=base).json())==2  # no implicit merge
    assert len(store.read(scope,lambda r:r.active_approvals()))==1
    statuses=c.get("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"))
    assert statuses.status_code==200 and len(statuses.json())==1
    # same key replay should not produce another lead approval
    replay=c.post("/internal/v1/reviews/approve",
        headers=h(base,signed,"reviewer-lead","productpulse_review_lead"),
        json={"ticket_key_a":keys[0],"ticket_key_b":keys[1],"reason":"Согласен","operation_key":"lead-b"})
    assert replay.status_code==201
    assert len(store.read(scope,lambda r:r.active_approvals()))==1


def test_disputed_pair_not_approvable(api):
    c,store,scope,keys,base,signed=api
    c.post("/internal/v1/reviews",headers=h(base,signed,"one"),json=vote(keys,op="first"))
    r=c.post("/internal/v1/reviews",headers=h(base,signed,"two"),
        json=vote(keys,label="related_topic",op="second"))
    assert r.status_code==201 and r.json()["status"]=="disputed"
    lead=c.post("/internal/v1/reviews/approve",
        headers=h(base,signed,"lead","productpulse_review_lead"),
        json={"ticket_key_a":keys[0],"ticket_key_b":keys[1],"reason":"bad","operation_key":"lead"})
    assert lead.status_code==409
    assert not store.read(scope,lambda r:r.active_approvals())


def test_reviews_survive_repository_restart(api):
    from productpulse.storage.repository import PersistentProblemRegistry
    c,store,scope,keys,base,signed=api
    r=c.post("/internal/v1/reviews",headers=h(base,signed,"person-1"),json=vote(keys))
    assert r.status_code==201
    new=PersistentProblemRegistry(store.engine)
    states=new.read(scope,lambda reg:reg.review_statuses())
    assert len(states)==1 and states[0].reviewer_ids[0].endswith("#person-1")
    assert len(new.audit(scope))==3


def test_client_cannot_override_tenant_scope(api):
    c,store,scope,keys,base,signed=api
    payload={**vote(keys),"scope_id":"attacker-scope"}
    assert c.post("/internal/v1/reviews",headers=h(base,signed,"person-1"),json=payload).status_code==422
