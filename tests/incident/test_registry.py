"""In-memory Problem Registry contract. Human-approved evidence != text similarity."""
from datetime import datetime, timezone

import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.annotation import PairAnnotation, pair_identity
from productpulse.incident.registry import ProblemRegistry


def ticket(name: str, source="demo", text="HTTP 403 в ERP"):
    return CanonicalTicketV1(
        source_system=source, source_ticket_id=name, provenance_id="fixture",
        body_redacted=text, product_id="erp", component_id="auth",
        reported_version="2.8.1", error_codes=("HTTP 403",),
    )


def reviews(a, b, label="same_incident"):
    pair = pair_identity(a, b)
    return (
        PairAnnotation(pair_id=pair, label=label, reviewer_id="analyst-1",
                       rationale="Evidence verified", reviewed_at="2026-10-30T10:00:00Z"),
        PairAnnotation(pair_id=pair, label=label, reviewer_id="analyst-2",
                       rationale="Independently verified", reviewed_at="2026-10-30T10:01:00Z"),
    )


def approve(registry, a, b, key=None, label="same_incident"):
    first, second = reviews(a, b, label)
    return registry.approve_pair(
        a, b, first, second, actor="review-lead",
        operation_key=key or f"approval:{ticket_key(a)}:{ticket_key(b)}",
    )


def registered(*ids):
    r = ProblemRegistry()
    ts = [ticket(i) for i in ids]
    ps = [r.register_ticket(t, scope_id="demo-tenant") for t in ts]
    return r, ts, ps


def test_register_creates_separate_singletons_and_stable_keys():
    r, (a,b), (pa,pb) = registered("1","2")
    assert pa.problem_id != pb.problem_id
    assert pa.ticket_keys == (ticket_key(a),)
    assert pa.revision == 1 and pa.status == "active"
    assert r.problem_for_ticket(b).problem_id == pb.problem_id
    assert len(r.audit_events()) == 2


def test_register_retry_is_idempotent_and_creates_no_extra_audit():
    r, (a,), (pa,) = registered("1")
    assert r.register_ticket(a, scope_id="demo-tenant") == pa
    assert len(r.audit_events()) == 1


def test_reusing_same_scoped_id_with_different_content_is_rejected():
    r, (a,), _ = registered("1")
    with pytest.raises(ValueError, match="identity conflict"):
        r.register_ticket(ticket("1", text="new body"), scope_id="demo-tenant")
    assert len(r.audit_events()) == 1


def test_same_short_id_from_other_source_is_distinct_ticket():
    r, (a,), _ = registered("1")
    other = ticket("1", source="helpdesk")
    assert r.register_ticket(other, scope_id="demo-tenant").problem_id != r.problem_for_ticket(a).problem_id


def test_register_again_in_another_scope_is_rejected():
    r, (a,), _ = registered("1")
    with pytest.raises(ValueError, match="scope"):
        r.register_ticket(a, scope_id="other-tenant")


def test_approved_pair_is_human_confirmed_and_stored_without_merging():
    r, (a,b), (pa,pb) = registered("1","2")
    decision = approve(r,a,b)
    assert decision.pair_id == pair_identity(a,b)
    assert decision.reviewer_ids == ("analyst-1","analyst-2")
    assert r.problem_for_ticket(a).problem_id == pa.problem_id
    assert r.problem_for_ticket(b).problem_id == pb.problem_id
    assert len(r.active_approvals()) == 1
    assert r.audit_events()[-1].kind == "pair_approved"
    assert "HTTP 403" not in repr(r.audit_events())


@pytest.mark.parametrize("label",["related_topic","different_incident","uncertain"])
def test_non_same_incident_review_never_creates_approval(label):
    r, (a,b), _ = registered("1","2")
    with pytest.raises(ValueError, match="confirmed same_incident"):
        approve(r,a,b,label=label)
    assert len(r.active_approvals()) == 0


def test_disagreeing_reviewers_cannot_approve_pair():
    r,(a,b),_ = registered("1","2")
    first,second=reviews(a,b)
    second=second.model_copy(update={"label":"related_topic"})
    with pytest.raises(ValueError, match="confirmed same_incident"):
        r.approve_pair(a,b,first,second,actor="lead",operation_key="op")
    assert not r.active_approvals()


def test_wrong_pair_label_scope_is_rejected():
    r,(a,b,c),_=registered("1","2","3")
    first,second=reviews(a,c)
    with pytest.raises(ValueError,match="pair identity"):
        r.approve_pair(a,b,first,second,actor="lead",operation_key="op")


def test_approvals_cannot_cross_scopes():
    r=ProblemRegistry()
    a,b=ticket("1"),ticket("2")
    r.register_ticket(a,scope_id="tenant-a")
    r.register_ticket(b,scope_id="tenant-b")
    with pytest.raises(ValueError,match="scope"):
        approve(r,a,b)


def test_pair_approval_operation_idempotency_key_collision_rejected():
    r,(a,b,c),_=registered("1","2","3")
    x=approve(r,a,b,key="op-1")
    assert approve(r,a,b,key="op-1")==x
    assert len(r.active_approvals())==1
    with pytest.raises(ValueError,match="idempotency"):
        approve(r,a,c,key="op-1")
    assert len(r.active_approvals())==1


def test_no_mutable_audit_or_snapshot_leak():
    r,(a,), (pa,)=registered("1")
    ev=r.audit_events()[0]
    assert ev.at.tzinfo is not None and ev.at.utcoffset()==timezone.utc.utcoffset(None)
    with pytest.raises(Exception):
        ev.kind="injected"
    with pytest.raises(Exception):
        pa.status="tampered"
    assert isinstance(r.audit_events(),tuple)


def test_duplicate_approval_new_key_does_not_spam_audit():
    r,(a,b),_=registered("1","2")
    first=approve(r,a,b,key="key1")
    second=approve(r,a,b,key="key2")
    assert first.pair_id == second.pair_id
    assert len([x for x in r.audit_events() if x.kind=="pair_approved"])==1
