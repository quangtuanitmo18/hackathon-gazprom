"""Real PostgreSQL integration (never in-memory SQLite for row locks)."""
from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("PG_REGISTRY_TEST_URL"),
    reason="requires PG_REGISTRY_TEST_URL and migrated PostgreSQL 16",
)


@pytest.fixture()
def store():
    from sqlalchemy import create_engine
    from productpulse.storage.repository import PersistentProblemRegistry
    engine = create_engine(os.environ["PG_REGISTRY_TEST_URL"], pool_pre_ping=True)
    registry = PersistentProblemRegistry(engine)
    yield registry
    engine.dispose()


def scope():
    return f"spike-{uuid4().hex}"


def ticket(id_):
    from productpulse.data.canonical import CanonicalTicketV1
    return CanonicalTicketV1(source_system="demo",source_ticket_id=id_,
        provenance_id="synthetic",body_redacted="Тест: HTTP 403",
        created_at=datetime(2026,10,30,tzinfo=timezone.utc),
        product_id="erp",component_id="auth",reported_version="1.0",
        error_codes=("HTTP 403",))


def review(a,b,when=None):
    from productpulse.incident.annotation import PairAnnotation,pair_identity
    pid=pair_identity(a,b)
    when=when or datetime.now(timezone.utc)
    return (
        PairAnnotation(pair_id=pid,label="same_incident",reviewer_id="user-1",
            rationale="checked root cause",reviewed_at=when),
        PairAnnotation(pair_id=pid,label="same_incident",reviewer_id="user-2",
            rationale="independent check",reviewed_at=when),
    )


def test_register_survives_new_repository_instance(store):
    from productpulse.storage.repository import PersistentProblemRegistry
    s=scope(); a=ticket("a")
    p=store.transact(s,lambda r:r.register_ticket(a,s))
    again=PersistentProblemRegistry(store.engine)
    assert again.read(s,lambda r:r.problem_for_ticket(a))==p
    assert len(again.audit(s))==1
    assert again.transact(s,lambda r:r.register_ticket(a,s))==p
    assert len(again.audit(s))==1


def test_two_scopes_have_separate_snapshot_and_audit(store):
    a,b=scope(),scope(); ta,tb=ticket("same"),ticket("same")
    store.transact(a,lambda r:r.register_ticket(ta,a))
    assert store.read(b,lambda r:r.audit_events())==()
    assert store.audit(b)==()
    store.transact(b,lambda r:r.register_ticket(tb,b))
    assert len(store.audit(a))==1 and len(store.audit(b))==1


def test_approved_merge_split_revoke_and_restart_persists(store):
    from productpulse.data.canonical import ticket_key
    from productpulse.incident.annotation import pair_identity
    from productpulse.storage.repository import PersistentProblemRegistry
    s=scope();a,b=ticket("a"),ticket("b")
    pa=store.transact(s,lambda r:r.register_ticket(a,s))
    pb=store.transact(s,lambda r:r.register_ticket(b,s))
    x,y=review(a,b)
    approved=store.transact(s,lambda r:r.approve_pair(a,b,x,y,actor="trusted",operation_key="ap1"))
    assert approved.pair_id==pair_identity(a,b)
    merged=store.transact(s,lambda r:r.merge(pa.problem_id,pb.problem_id,actor="trusted",reason="confirmed",
        operation_key="merge1",expected_primary_revision=1,expected_secondary_revision=1))
    split=store.transact(s,lambda r:r.split(merged.problem_id,
        partitions=((ticket_key(a),),(ticket_key(b),)),actor="trusted",reason="correction",
        operation_key="split1",expected_revision=merged.revision))
    again=PersistentProblemRegistry(store.engine)
    assert again.read(s,lambda r:r.problem_for_ticket(b))==split[1]
    assert len(again.audit(s))==5
    assert len(again.read(s,lambda r:r.active_approvals()))==0
    assert again.transact(s,lambda r:r.split(merged.problem_id,
        partitions=((ticket_key(a),),(ticket_key(b),)),actor="trusted",reason="correction",
        operation_key="split1",expected_revision=merged.revision))==split
    assert len(again.audit(s))==5
    with pytest.raises(ValueError,match="revoked"):
        again.transact(s,lambda r:r.approve_pair(a,b,x,y,actor="trusted",operation_key="ap1"))
    assert len(again.audit(s))==5


def test_transaction_rolls_back_state_and_audit_together(store):
    s=scope();a=ticket("a")
    def mutate_then_fail(reg):
        reg.register_ticket(a,s)
        raise RuntimeError("deliberate abort")
    with pytest.raises(RuntimeError,match="deliberate"):
        store.transact(s,mutate_then_fail)
    assert store.read(s,lambda r:r.audit_events())==()
    assert store.audit(s)==()
    assert store.transact(s,lambda r:r.register_ticket(a,s)).ticket_keys


def test_cross_scope_callback_cannot_persist_wrong_owner(store):
    s=scope()
    with pytest.raises(ValueError,match="scope"):
        store.transact(s,lambda r:r.register_ticket(ticket("a"),"wrong-tenant"))
    assert store.audit(s)==()


def test_read_callback_cannot_mutate_snapshot(store):
    s=scope()
    with pytest.raises(ValueError,match="read-only"):
        store.read(s,lambda r:r.register_ticket(ticket("a"),s))
    assert store.audit(s)==()


def test_concurrent_registrations_do_not_lose_updates(store):
    s=scope()
    def reg(i):
        def action(r):
            time.sleep(0.06)
            return r.register_ticket(ticket(str(i)),s)
        return store.transact(s,action)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(reg,i) for i in range(2)]
        a,b=(f.result(timeout=20) for f in futures)
    assert a.problem_id != b.problem_id
    assert len(store.audit(s))==2
    assert store.read(s,lambda r:(
        r.problem_for_ticket(ticket("0")).problem_id,
        r.problem_for_ticket(ticket("1")).problem_id
    )) == (a.problem_id,b.problem_id)


def test_no_audit_rows_when_retry_is_noop(store):
    s=scope();a=ticket("a")
    first=store.transact(s,lambda r:r.register_ticket(a,s))
    for _ in range(3): assert store.transact(s,lambda r:r.register_ticket(a,s))==first
    events=store.audit(s)
    assert len(events)==1 and events[0]["kind"]=="ticket_registered"
    assert events[0]["scope_id"]==s


def test_database_migrations_applied_not_create_all_shortcut(store):
    from sqlalchemy import inspect
    table_names=set(inspect(store.engine).get_table_names())
    assert {"registry_states","registry_events","alembic_version"}.issubset(table_names)
