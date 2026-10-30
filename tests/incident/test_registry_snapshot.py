"""Domain state must survive PostgreSQL JSONB roundtrip without unsafe pickle."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.annotation import PairAnnotation, pair_identity
from productpulse.incident.registry import ProblemRegistry


def t(id_: str) -> CanonicalTicketV1:
    return CanonicalTicketV1(
        source_system="test", source_ticket_id=id_, provenance_id="synthetic",
        body_redacted="Тест: ошибка HTTP 403",
        created_at=datetime(2026,10,30,tzinfo=timezone.utc),
        product_id="erp", component_id="auth", reported_version="1.0",
        error_codes=("HTTP 403",),
    )


def approve(r, a, b, key="ap"):
    pid=pair_identity(a,b)
    when=datetime.now(timezone.utc)
    first=PairAnnotation(pair_id=pid,label="same_incident",reviewer_id="r1",
        rationale="independent check A",reviewed_at=when)
    second=PairAnnotation(pair_id=pid,label="same_incident",reviewer_id="r2",
        rationale="independent check B",reviewed_at=when)
    return r.approve_pair(a,b,first,second,actor="review-lead",operation_key=key)


def roundtrip(r):
    state=json.loads(json.dumps(r.to_state()))
    assert state["version"] == 1
    return ProblemRegistry.from_state(state)


def test_empty_registry_roundtrips_without_side_effects():
    loaded=roundtrip(ProblemRegistry())
    assert loaded.audit_events() == ()
    assert loaded.active_approvals() == ()


def test_ticket_identity_timestamps_and_problems_survive():
    registry=ProblemRegistry()
    a,b=t("a"),t("b")
    p1=registry.register_ticket(a,scope_id="org")
    p2=registry.register_ticket(b,scope_id="org")
    loaded=roundtrip(registry)
    assert loaded.problem_for_ticket(a)==p1
    assert loaded.problem_for_ticket(b)==p2
    assert loaded.audit_events()==registry.audit_events()
    assert loaded.register_ticket(a,scope_id="org")==p1
    assert len(loaded.audit_events())==2


def test_approved_merge_replay_survives_restart():
    r=ProblemRegistry();a,b=t("a"),t("b")
    p1=r.register_ticket(a,scope_id="org")
    p2=r.register_ticket(b,scope_id="org")
    ap=approve(r,a,b,key="approve-1")
    merged=r.merge(p1.problem_id,p2.problem_id,actor="owner",reason="confirmed",
       operation_key="merge-1",expected_primary_revision=1,expected_secondary_revision=1)
    restored=roundtrip(r)
    assert restored.active_approvals() == (ap,)
    assert restored.problem_for_ticket(b)==merged
    assert restored.merge(p1.problem_id,p2.problem_id,actor="owner",reason="confirmed",
       operation_key="merge-1",expected_primary_revision=1,expected_secondary_revision=1)==merged
    assert restored.audit_events()==r.audit_events()


def test_split_and_revoked_approval_survive_and_block_old_replay():
    r=ProblemRegistry();a,b=t("a"),t("b")
    pa=r.register_ticket(a,"org");pb=r.register_ticket(b,"org")
    approve(r,a,b,key="approved-before-split")
    merged=r.merge(pa.problem_id,pb.problem_id,actor="owner",reason="same",
       operation_key="merged",expected_primary_revision=1,expected_secondary_revision=1)
    split=r.split(merged.problem_id,partitions=((ticket_key(a),),(ticket_key(b),)),
       actor="owner",reason="wrong merge",operation_key="split",expected_revision=2)
    loaded=roundtrip(r)
    assert loaded.get_problem(split[0].problem_id)==split[0]
    assert loaded.get_problem(split[1].problem_id)==split[1]
    assert loaded.split(merged.problem_id,partitions=((ticket_key(a),),(ticket_key(b),)),
       actor="owner",reason="wrong merge",operation_key="split",expected_revision=2)==split
    with pytest.raises(ValueError,match="revoked|idempotency"):
        approve(loaded,a,b,key="approved-before-split")
    old_when=datetime.now(timezone.utc)-timedelta(days=1)
    pid=pair_identity(a,b)
    v1=PairAnnotation(pair_id=pid,label="same_incident",reviewer_id="r3",
                     rationale="not fresh",reviewed_at=old_when)
    v2=v1.model_copy(update={"reviewer_id":"r4"})
    with pytest.raises(ValueError,match="fresh"):
        loaded.approve_pair(a,b,v1,v2,actor="lead",operation_key="new-op")


@pytest.mark.parametrize("state",[
    {},
    {"version":999},
    {"version":1,"tickets":"not-dict"},
])
def test_unknown_or_corrupted_state_fails_closed(state):
    with pytest.raises((ValueError,KeyError,TypeError)):
        ProblemRegistry.from_state(state)


def test_snapshot_has_no_python_code_execution_or_pickle():
    r=ProblemRegistry()
    r.register_ticket(t("a"),"org")
    state=r.to_state()
    raw=json.dumps(state)
    assert "__reduce__" not in raw
    assert "_type" not in raw
    assert "Test: ..." not in raw
