"""Internal-only FastAPI contract tested against real PostgreSQL 16."""
import os
from uuid import uuid4
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("PG_REGISTRY_TEST_URL"),
    reason="integration suite needs migrated PG_REGISTRY_TEST_URL and API extras",
)


@pytest.fixture()
def clients():
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from productpulse.storage.repository import PersistentProblemRegistry
    from productpulse.api.app import create_app
    engine=create_engine(os.environ["PG_REGISTRY_TEST_URL"],pool_pre_ping=True)
    store=PersistentProblemRegistry(engine)
    scope_a=f"api-a-{uuid4().hex}"
    scope_b=f"api-b-{uuid4().hex}"
    good="synthetic-internal-token-32-characters-only"
    with TestClient(create_app(store,scope_a,good)) as a, TestClient(create_app(store,scope_b,good)) as b:
        yield a,b,good
    engine.dispose()


def headers(token):
    return {"X-Internal-Token":token}


def valid_ticket(id_):
    return {"source_system":"synthetic","source_ticket_id":id_,
            "provenance_id":"synthetic-fixture",
            "body_redacted":"Синтетическая ошибка HTTP 403",
            "product_id":"erp", "component_id":"auth",
            "reported_version":"2.1", "error_codes":["HTTP 403"]}


def test_live_health_reports_only_process_status(clients):
    a,_,_=clients
    assert a.get("/health/live").json()=={"status":"alive"}


@pytest.mark.parametrize("path,method",[
    ("/internal/v1/problems","get"),
    ("/internal/v1/audit","get"),
    ("/internal/v1/tickets","post"),
])
def test_no_token_rejected(clients,path,method):
    a,_,_=clients
    response=(a.get(path) if method=="get" else a.post(path,json=valid_ticket("x")))
    assert response.status_code==401


def test_bad_token_rejected(clients):
    a,_,_=clients
    assert a.get("/internal/v1/problems",headers=headers("wrong")).status_code==401


def test_factory_refuses_blank_token_or_scope(clients):
    from productpulse.api.app import create_app
    from productpulse.storage.repository import PersistentProblemRegistry
    a,b,token=clients
    with pytest.raises(ValueError,match="token"):
        create_app(None,"scope","")
    with pytest.raises(ValueError,match="scope"):
        create_app(None," ",token)


def test_ingest_and_get_problem_and_audit_without_leaking_ticket_text(clients):
    a,b,token=clients
    h=headers(token)
    new=a.post("/internal/v1/tickets",headers=h,json=valid_ticket("x"))
    assert new.status_code==201,new.text
    problem=new.json()
    assert problem["scope_id"].startswith("api-a-")
    pid=problem["problem_id"]
    assert problem["ticket_keys"] == ["9:synthetic1:x"]
    assert "Синтетическая ошибка" not in new.text
    assert a.get(f"/internal/v1/problems/{pid}",headers=h).json()==problem
    listing=a.get("/internal/v1/problems",headers=h)
    assert listing.status_code==200
    assert len(listing.json())==1
    log=a.get("/internal/v1/audit",headers=h)
    assert log.status_code==200
    assert len(log.json())==1
    assert "Синтетическая ошибка" not in log.text
    # Same numeric/short Problem ID can exist in another tenant; no cross-scope
    # tenant information from the other instance must be returned.
    assert b.get("/internal/v1/problems",headers=h).json()==[]


def test_repeated_post_is_idempotent(clients):
    a,b,token=clients
    h=headers(token)
    first=a.post("/internal/v1/tickets",headers=h,json=valid_ticket("dedupe"))
    second=a.post("/internal/v1/tickets",headers=h,json=valid_ticket("dedupe"))
    assert first.status_code==201 and second.status_code==201
    assert first.json()["problem_id"]==second.json()["problem_id"]
    assert len(a.get("/internal/v1/audit",headers=h).json())==1


def test_client_supplied_scope_is_rejected_not_trusted(clients):
    a,b,token=clients
    data=valid_ticket("x")
    data["scope_id"]="another-tenant"
    assert a.post("/internal/v1/tickets",json=data,headers=headers(token)).status_code==422


def test_unknown_problem_returns_404_not_scope_information(clients):
    a,b,token=clients
    assert a.get("/internal/v1/problems/PRB-999999",headers=headers(token)).status_code==404


def test_no_untrusted_review_or_merge_http_surface(clients):
    a,b,token=clients
    for p in ("/internal/v1/merge","/internal/v1/approve","/internal/v1/split"):
        assert a.post(p,headers=headers(token),json={}).status_code==404


def test_empty_problem_list_and_audit_are_200(clients):
    a,b,token=clients
    assert a.get("/internal/v1/problems",headers=headers(token)).json()==[]
    assert a.get("/internal/v1/audit",headers=headers(token)).json()==[]
