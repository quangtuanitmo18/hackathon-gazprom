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


def test_concurrent_distinct_reviews_are_serialized_by_postgresql(api):
    from concurrent.futures import ThreadPoolExecutor
    c,store,scope,keys,base,signed=api
    def submit_vote(who):
        def action(reg):
            return reg.submit_review(
                keys[0],keys[1],reviewer_id="https://idp.example.org/realms/test#"+who,
                label="same_incident",rationale="independent review",
                operation_key="concurrent-"+who,
            )
        return store.transact(scope,action)
    with ThreadPoolExecutor(max_workers=2) as pool:
        out=list(pool.map(submit_vote,("reviewer-C","reviewer-D")))
    statuses=store.read(scope,lambda r:r.review_statuses())
    assert len(out)==2
    assert len(statuses)==1 and statuses[0].status=="ready_for_lead"
    assert set(statuses[0].reviewer_ids)=={
        "https://idp.example.org/realms/test#reviewer-C",
        "https://idp.example.org/realms/test#reviewer-D",
    }
    assert not store.read(scope,lambda r:r.active_approvals())
    assert len([row for row in store.audit(scope) if row["kind"]=="pair_review_submitted"])==2


def test_lead_approval_does_not_replay_a_revoked_link_after_split(api):
    from productpulse.incident.registry import ProblemRegistry
    c,store,scope,keys,base,signed=api
    c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"),
           json=vote(keys,"same_incident","vote-A"))
    c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-B"),
           json=vote(keys,"same_incident","vote-B"))
    payload={"ticket_key_a":keys[0],"ticket_key_b":keys[1],
             "reason":"Verified", "operation_key":"lead-once"}
    approved=c.post("/internal/v1/reviews/approve",
           headers=h(base,signed,"lead","productpulse_review_lead"),json=payload)
    assert approved.status_code==201
    def merge_and_split(reg):
        p=reg.list_active()
        merged=reg.merge(p[0].problem_id,p[1].problem_id,actor="lead",
                         reason="same root cause",operation_key="merge",
                         expected_primary_revision=1,expected_secondary_revision=1)
        reg.split(merged.problem_id,partitions=((keys[0],),(keys[1],)),
                  actor="lead",reason="correction",operation_key="split",
                  expected_revision=merged.revision)
    store.transact(scope,merge_and_split)
    again=c.post("/internal/v1/reviews/approve",
           headers=h(base,signed,"lead","productpulse_review_lead"),json=payload)
    assert again.status_code==409
    assert not store.read(scope,lambda r:r.active_approvals())


def test_review_evidence_requires_service_and_reviewer_token_and_scope(api):
    c,store,scope,keys,base,signed=api
    assert c.get("/internal/v1/review-tickets").status_code==401
    assert c.get("/internal/v1/review-tickets",headers=base).status_code==401
    assert c.get("/internal/v1/review-tickets",
                 headers=h(base,signed,"bad",tenant="other-scope")).status_code in (401,403)
    resp=c.get("/internal/v1/review-tickets",headers=h(base,signed,"reviewer-A"))
    assert resp.status_code==200,resp.text
    rows=resp.json()
    assert len(rows)==2
    assert set(row["ticket_key"] for row in rows)==set(keys)
    assert all(row["body_redacted"]=="Сбой ERP HTTP 403" for row in rows)
    assert all("pseudonymous_user_id" not in row for row in rows)
    assert all(row["source_system"]=="synthetic" for row in rows)


def test_review_evidence_is_bounded_and_does_not_allow_client_scope_override(api):
    c,store,scope,keys,base,signed=api
    headers=h(base,signed,"reviewer-A")
    assert c.get("/internal/v1/review-tickets?limit=1",headers=headers).status_code==200
    assert len(c.get("/internal/v1/review-tickets?limit=1",headers=headers).json())==1
    assert c.get("/internal/v1/review-tickets?limit=501",headers=headers).status_code==422
    assert c.get("/internal/v1/review-tickets?scope_id=other",headers=headers).status_code==422


def test_ranked_candidate_endpoint_requires_both_tokens_and_is_not_a_verdict(api):
    c,store,scope,keys,base,signed=api
    # The two existing synthetic tickets have exactly the same lexical text.
    assert c.get("/internal/v1/review-candidates",headers=base).status_code==401
    assert c.get("/internal/v1/review-candidates").status_code==401
    bad=c.get("/internal/v1/review-candidates",
              headers=h(base,signed,"someone",tenant="cross-tenant"))
    assert bad.status_code in (401,403)
    found=c.get("/internal/v1/review-candidates",
                headers=h(base,signed,"reviewer-A"))
    assert found.status_code==200,found.text
    rows=found.json()
    assert len(rows)==1
    assert set((rows[0]["ticket_key_a"],rows[0]["ticket_key_b"]))==set(keys)
    assert rows[0]["rank"]>=1 and rows[0]["rank"]<=30
    assert "confidence" not in rows[0] and "is_duplicate" not in rows[0]
    assert "body_redacted" not in rows[0]
    assert c.get("/internal/v1/review-candidates?limit=101",
        headers=h(base,signed,"reviewer-A")).status_code==422
    assert c.get("/internal/v1/review-candidates?scope_id=other",
        headers=h(base,signed,"reviewer-A")).status_code==422


def test_confirmed_duplicate_pair_not_recommended_after_lead_approval(api):
    c,store,scope,keys,base,signed=api
    c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-A"),
        json=vote(keys,"same_incident","pair-1-a"))
    c.post("/internal/v1/reviews",headers=h(base,signed,"reviewer-B"),
        json=vote(keys,"same_incident","pair-1-b"))
    approved=c.post("/internal/v1/reviews/approve",
        headers=h(base,signed,"third-lead","productpulse_review_lead"),
        json={"ticket_key_a":keys[0],"ticket_key_b":keys[1],
              "reason":"Independent verified", "operation_key":"pair-1-approved"})
    assert approved.status_code==201
    ranked=c.get("/internal/v1/review-candidates",headers=h(base,signed,"reviewer-A"))
    assert ranked.status_code==200 and ranked.json()==[]


def test_ingestion_redacts_synthetic_email_and_secret_before_database(api):
    c,store,scope,keys,base,signed=api
    secret="Bearer abcDEF123456789.fake.synthetic.token"
    raw="Сбой HTTP 403: напишите test-reviewer@example.com "+secret
    packet={"source_system":"synthetic","source_ticket_id":"pii-probe",
            "provenance_id":"privacy-test","title":"Сбой у test-reviewer@example.com",
            "body_redacted":raw}
    response=c.post("/internal/v1/tickets",headers=base,json=packet)
    assert response.status_code==201,response.text
    persisted=store.read(scope,lambda r:r.to_state())
    body=str(persisted)
    assert "test-reviewer@example.com" not in body
    assert "abcDEF123456789" not in body
    exposed=c.get("/internal/v1/review-tickets",
        headers=h(base,signed,"reviewer-A"))
    assert exposed.status_code==200
    assert "test-reviewer@example.com" not in exposed.text
    assert "abcDEF123456789" not in exposed.text
    again=c.post("/internal/v1/tickets",headers=base,json=packet)
    assert again.status_code==201
    assert again.json()["problem_id"]==response.json()["problem_id"]


def test_ingestion_refuses_email_in_source_id_without_persistence(api):
    c,store,scope,keys,base,signed=api
    packet={"source_system":"synthetic","source_ticket_id":"user@corp.example",
            "provenance_id":"privacy-test","body_redacted":"Ошибка HTTP 403"}
    result=c.post("/internal/v1/tickets",headers=base,json=packet)
    assert result.status_code in (409,422)
    assert "user@corp.example" not in result.text
    assert len(store.read(scope,lambda r:r.list_active()))==2


def test_verified_trends_require_service_token_and_oidc_reviewer(api):
    c, store, scope, keys, base, signed = api
    url = "/internal/v1/trends"
    assert c.get(url).status_code == 401
    assert c.get(url, headers=base).status_code == 401
    assert c.get(url, headers={"Authorization": "Bearer " + signed("reviewer")}).status_code == 401
    assert c.get(url, headers=h(base, signed, "bad", tenant="wrong-scope")).status_code in (401, 403)
    assert c.get(url, headers=h(base, signed, "reviewer")).status_code == 200
    assert c.get(url + "?window_hours=0", headers=h(base, signed, "reviewer")).status_code == 422
    assert c.get(url + "?window_hours=169", headers=h(base, signed, "reviewer")).status_code == 422
    assert c.get(url + "?scope_id=other", headers=h(base, signed, "reviewer")).status_code == 422


def test_approved_pair_alone_must_not_create_trend_or_automatically_merge(api):
    c, store, scope, keys, base, signed = api
    for who, op in (("reviewer-1", "trend-review-1"), ("reviewer-2", "trend-review-2")):
        r = c.post("/internal/v1/reviews", headers=h(base, signed, who),
                   json=vote(keys, op=op))
        assert r.status_code == 201, r.text
    r = c.post(
        "/internal/v1/reviews/approve",
        headers=h(base, signed, "lead-3", "productpulse_review_lead"),
        json={"ticket_key_a": keys[0], "ticket_key_b": keys[1],
              "reason": "Confirmed link, no automatic merge",
              "operation_key": "trend-lead-3"},
    )
    assert r.status_code == 201, r.text
    before = store.audit(scope)
    response = c.get("/internal/v1/trends", headers=h(base, signed, "reviewer-1"))
    assert response.status_code == 200, response.text
    assert response.json() == []  # Approved link != explicit group membership.
    assert store.audit(scope) == before


def test_three_fully_approved_and_explicitly_merged_tickets_form_volume_signal(api):
    from productpulse.data.canonical import CanonicalTicketV1, ticket_key

    c, store, scope, keys, base, signed = api
    now = datetime.now(timezone.utc)
    member_keys, pids = [], []
    for name in ("trend-c", "trend-d", "trend-e"):
        packet = {
            "source_system": "synthetic",
            "source_ticket_id": name,
            "provenance_id": "test",
            "created_at": (now - timedelta(minutes=20)).isoformat(),
            "body_redacted": "Сбой авторизации HTTP 403 после обновления",
        }
        response = c.post("/internal/v1/tickets", headers=base, json=packet)
        assert response.status_code == 201, response.text
        pids.append(response.json()["problem_id"])
        member_keys.append(ticket_key(CanonicalTicketV1(**packet)))

    # Complete-link: each cross-member pair must have two independent votes
    # and a separate independent lead approval, before an explicit merge.
    pairs = [(0, 1), (0, 2), (1, 2)]
    for i, j in pairs:
        a, b = member_keys[i], member_keys[j]
        suffix = str(i) + "-" + str(j)
        for who in ("first-" + suffix, "second-" + suffix):
            r = c.post(
                "/internal/v1/reviews", headers=h(base, signed, who),
                json={"ticket_key_a": a, "ticket_key_b": b,
                      "label": "same_incident", "rationale": "Manual comparison",
                      "operation_key": "trend-vote-" + who},
            )
            assert r.status_code == 201, r.text
        r = c.post(
            "/internal/v1/reviews/approve",
            headers=h(base, signed, "lead-" + suffix, "productpulse_review_lead"),
            json={"ticket_key_a": a, "ticket_key_b": b,
                  "reason": "Manual approval",
                  "operation_key": "trend-lead-" + suffix},
        )
        assert r.status_code == 201, r.text

    def explicitly_merge(reg):
        first = reg.merge(
            pids[0], pids[1], actor="trusted-lead",
            reason="Full evidence", operation_key="trend-merge-1",
            expected_primary_revision=1, expected_secondary_revision=1,
        )
        reg.merge(
            pids[0], pids[2], actor="trusted-lead",
            reason="Full evidence", operation_key="trend-merge-2",
            expected_primary_revision=first.revision, expected_secondary_revision=1,
        )

    store.transact(scope, explicitly_merge)
    before = store.audit(scope)
    response = c.get("/internal/v1/trends", headers=h(base, signed, "reviewer-1"))
    assert response.status_code == 200, response.text
    trends = response.json()
    assert len(trends) == 1
    observed = trends[0]
    assert observed["problem_id"] == pids[0]
    assert observed["revision"] == 3
    assert observed["status"] == "new_activity"
    assert (observed["current_count"], observed["previous_count"]) == (3, 0)
    assert set(observed["current_ticket_keys"]) == set(member_keys)
    assert "root_cause" not in observed and "confidence" not in observed
    assert "body_redacted" not in observed
    assert store.audit(scope) == before
