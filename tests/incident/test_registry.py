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


def do_merge(r, p, q, *, key="merge-1", rv_p=1, rv_q=1, reason="Expert confirmed shared incident"):
    return r.merge(
        p.problem_id, q.problem_id, actor="product-owner",
        reason=reason, operation_key=key,
        expected_primary_revision=rv_p,
        expected_secondary_revision=rv_q,
    )


def test_merge_requires_source_confirmed_pair_and_preserves_tombstone():
    r,(a,b),(pa,pb)=registered("1","2")
    approve(r,a,b)
    merged=do_merge(r,pa,pb)
    assert merged.problem_id == pa.problem_id
    assert merged.status == "active"
    assert merged.revision == 2
    assert set(merged.ticket_keys) == {ticket_key(a),ticket_key(b)}
    assert r.problem_for_ticket(b) == merged
    tomb=r.get_problem(pb.problem_id)
    assert tomb.status == "merged" and tomb.merged_into == pa.problem_id
    assert tomb.ticket_keys == ()
    assert r.audit_events()[-1].kind == "problems_merged"


def test_no_human_pair_approval_means_merge_rejected_atomically():
    r,(a,b),(pa,pb)=registered("1","2")
    before=r.audit_events()
    with pytest.raises(ValueError, match="approved"):
        do_merge(r,pa,pb)
    assert r.audit_events()==before
    assert r.get_problem(pa.problem_id)==pa
    assert r.get_problem(pb.problem_id)==pb


def test_two_positive_edges_do_not_allow_unsafe_transitive_merge():
    r,(a,b,c),(pa,pb,pc)=registered("1","2","3")
    approve(r,a,b)
    approve(r,b,c)
    ab=do_merge(r,pa,pb)
    with pytest.raises(ValueError,match="approved cross-pair"):
        do_merge(r,ab,pc,key="merge-2",rv_p=ab.revision)
    assert r.problem_for_ticket(c)==pc
    assert r.get_problem(pa.problem_id)==ab


def test_complete_link_evidence_allows_merging_group_and_singleton():
    r,(a,b,c),(pa,pb,pc)=registered("1","2","3")
    approve(r,a,b)
    approve(r,b,c)
    approve(r,a,c)
    ab=do_merge(r,pa,pb)
    abc=do_merge(r,ab,pc,key="merge-2",rv_p=ab.revision)
    assert len(abc.ticket_keys)==3
    assert abc.revision==3


def test_stale_revision_rejected_without_side_effect():
    r,(a,b),(pa,pb)=registered("1","2")
    approve(r,a,b)
    before=r.audit_events()
    with pytest.raises(ValueError,match="stale revision"):
        do_merge(r,pa,pb,rv_p=99)
    assert r.audit_events()==before


def test_merge_operation_replay_is_idempotent_even_after_tombstone():
    r,(a,b),(pa,pb)=registered("1","2")
    approve(r,a,b)
    first=do_merge(r,pa,pb)
    count=len(r.audit_events())
    assert do_merge(r,pa,pb)==first
    assert len(r.audit_events())==count
    with pytest.raises(ValueError,match="idempotency"):
        do_merge(r,pa,pb,key="merge-1",reason="changed reason")


def test_cross_scope_merge_rejected_even_if_approval_cannot_exist():
    r=ProblemRegistry()
    a,b=ticket("1"),ticket("2")
    pa=r.register_ticket(a,"tenant-a")
    pb=r.register_ticket(b,"tenant-b")
    with pytest.raises(ValueError,match="scope"):
        do_merge(r,pa,pb)


def test_merge_self_or_blank_reason_disallowed():
    r,(a,b),(pa,pb)=registered("1","2")
    approve(r,a,b)
    with pytest.raises(ValueError,match="distinct"):
        do_merge(r,pa,pa)
    with pytest.raises(ValueError,match="reason"):
        do_merge(r,pa,pb,reason=" ")


def three_member_problem():
    r,(a,b,c),(pa,pb,pc)=registered("1","2","3")
    for x,y in ((a,b),(a,c),(b,c)):
        approve(r,x,y)
    ab=do_merge(r,pa,pb)
    abc=do_merge(r,ab,pc,key="merge-2",rv_p=ab.revision)
    return r,(a,b,c),abc


def split_two(r,abc,a,b,c,*,key="split-1",rv=None,reason="Reviewer corrects mixed incident grouping"):
    return r.split(
        abc.problem_id,
        partitions=((ticket_key(a),ticket_key(b)),(ticket_key(c),)),
        actor="reviewer-lead", reason=reason,
        operation_key=key, expected_revision=abc.revision if rv is None else rv,
    )


def test_explicit_split_changes_ownership_and_preserves_parent_lineage():
    r,(a,b,c),abc=three_member_problem()
    first,second=split_two(r,abc,a,b,c)
    assert first.problem_id == abc.problem_id
    assert first.revision == abc.revision+1
    assert set(first.ticket_keys)=={ticket_key(a),ticket_key(b)}
    assert second.parent_id==abc.problem_id
    assert second.status=="active"
    assert second.ticket_keys==(ticket_key(c),)
    assert r.problem_for_ticket(c)==second
    assert r.problem_for_ticket(a)==first
    assert r.audit_events()[-1].kind=="problem_split"


def test_split_revokes_only_approvals_crossing_partitions_preserving_audit():
    r,(a,b,c),abc=three_member_problem()
    original_approval_count=len(r.active_approvals())
    assert original_approval_count==3
    before=len([x for x in r.audit_events() if x.kind=="pair_approved"])
    first,second=split_two(r,abc,a,b,c)
    assert {ap.pair_id for ap in r.active_approvals()}=={pair_identity(a,b)}
    assert len(r.audit_events()[-1].revoked_pair_ids)==2
    assert len([x for x in r.audit_events() if x.kind=="pair_approved"])==before
    with pytest.raises(ValueError,match="approved cross-pair"):
        do_merge(r,first,second,key="merge-after-split",rv_p=first.revision,rv_q=second.revision)


def test_split_requires_fresh_human_reviews_not_just_new_operation_keys():
    r,(a,b,c),abc=three_member_problem()
    first,second=split_two(r,abc,a,b,c)
    with pytest.raises(ValueError,match="fresh post-split"):
        approve(r,a,c,key="re-review-a-c")
    with pytest.raises(ValueError,match="approved cross-pair"):
        do_merge(r,first,second,key="merge-corrected",rv_p=first.revision,rv_q=second.revision)
    # Both independent reviewers must supply a new post-split decision.
    for x,y,key in ((a,c,"new-review-a-c"),(b,c,"new-review-b-c")):
        old_one,old_two=reviews(x,y)
        fresh=datetime.now(timezone.utc)
        new_one=old_one.model_copy(update={"reviewed_at":fresh})
        new_two=old_two.model_copy(update={"reviewed_at":fresh})
        r.approve_pair(x,y,new_one,new_two,actor="lead",operation_key=key)
    merged=do_merge(r,first,second,key="merge-corrected",rv_p=first.revision,rv_q=second.revision)
    assert len(merged.ticket_keys)==3

def test_replaying_revoked_approval_key_must_not_claim_still_active():
    r,(a,b,c),abc=three_member_problem()
    split_two(r,abc,a,b,c)
    with pytest.raises(ValueError,match="revoked"):
        approve(r,a,c,key=f"approval:{ticket_key(a)}:{ticket_key(c)}")


@pytest.mark.parametrize("partitions",[
    (),
    (("dummy",),),
    (("dummy",),("another",)),
    (("bad","bad"),("anything",)),
])
def test_invalid_or_missing_split_partitions_fail_atomically(partitions):
    r,(a,b,c),abc=three_member_problem()
    before=r.audit_events()
    with pytest.raises(ValueError,match="partitions"):
        r.split(abc.problem_id,partitions=partitions,actor="lead",reason="correction",
                operation_key="split-bad",expected_revision=abc.revision)
    assert r.audit_events()==before
    assert r.get_problem(abc.problem_id)==abc


def test_overlap_and_missing_member_partitions_rejected_without_mutation():
    r,(a,b,c),abc=three_member_problem()
    before=r.audit_events()
    for parts in [
        ((ticket_key(a),ticket_key(b)),(ticket_key(b),ticket_key(c))),
        ((ticket_key(a),),(ticket_key(c),)),
        ((ticket_key(a),ticket_key(b)),()),
    ]:
        with pytest.raises(ValueError,match="partitions"):
            r.split(abc.problem_id,partitions=parts,actor="lead",reason="correction",
                    operation_key="split-bad",expected_revision=abc.revision)
        assert r.audit_events()==before


def test_stale_split_revision_is_rejected():
    r,(a,b,c),abc=three_member_problem()
    with pytest.raises(ValueError,match="stale revision"):
        split_two(r,abc,a,b,c,rv=1)
    assert r.get_problem(abc.problem_id)==abc


def test_split_retry_same_key_returns_same_snapshots_no_new_audit():
    r,(a,b,c),abc=three_member_problem()
    first=split_two(r,abc,a,b,c)
    n=len(r.audit_events())
    assert split_two(r,abc,a,b,c)==first
    assert len(r.audit_events())==n
    with pytest.raises(ValueError,match="idempotency"):
        split_two(r,abc,a,b,c,reason="modified correction note")


def test_split_requires_reason_and_leaves_no_side_effect_when_rejected():
    r,(a,b,c),abc=three_member_problem()
    n=len(r.audit_events())
    with pytest.raises(ValueError,match="reason"):
        split_two(r,abc,a,b,c,reason=" ")
    assert len(r.audit_events())==n


def test_screening_candidate_alone_never_grants_merge():
    from productpulse.incident.verify import screen_pair
    r,(a,b),(pa,pb)=registered("1","2")
    out=screen_pair(a,b,"auth_denied","auth_denied")
    assert out.status=="candidate_for_human_review"
    with pytest.raises(ValueError,match="approved"):
        do_merge(r,pa,pb)
