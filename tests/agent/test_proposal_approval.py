"""RED: human approval gate, persisted mock publication and replay safety."""
import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.registry import ProblemRegistry


def confirmed():
    r=ProblemRegistry()
    a=CanonicalTicketV1(source_system="synthetic",source_ticket_id="a",provenance_id="unit",body_redacted="Ошибка входа")
    b=CanonicalTicketV1(source_system="synthetic",source_ticket_id="b",provenance_id="unit",body_redacted="Сбой логина")
    p1=r.register_ticket(a,"t")
    p2=r.register_ticket(b,"t")
    keys=(ticket_key(a),ticket_key(b))
    for who in ("alice","bob"):
        r.submit_review(*keys,reviewer_id=who,label="same_incident",
                        rationale="Independently verified",operation_key="vote-"+who)
    r.approve_reviewed_pair(*keys,actor="lead",reason="Verified link",operation_key="lead-pair")
    r.merge(p1.problem_id,p2.problem_id,actor="lead",reason="Full approved evidence",
            operation_key="group",expected_primary_revision=1,expected_secondary_revision=1)
    return r,p1.problem_id,keys


def test_singletons_and_approved_unmerged_pair_do_not_generate_proposal():
    r=ProblemRegistry()
    a=CanonicalTicketV1(source_system="synthetic",source_ticket_id="a",provenance_id="test",body_redacted="ошибка входа")
    b=CanonicalTicketV1(source_system="synthetic",source_ticket_id="b",provenance_id="test",body_redacted="ошибка входа")
    r.register_ticket(a,"t");r.register_ticket(b,"t")
    k=(ticket_key(a),ticket_key(b))
    for i in (1,2):
        r.submit_review(*k,reviewer_id=str(i),label="same_incident",rationale="Reviewed",operation_key=f"vote-{i}")
    r.approve_reviewed_pair(*k,actor="third",reason="Reviewed",operation_key="lead")
    assert r.insight_proposals("t")==()
    with pytest.raises(ValueError,match="verified|active|merged"):
        r.approve_insight("PRB-000001",expected_revision=1,evidence_digest="fake",
                          actor="lead",reason="x",operation_key="unmerged")


def test_approve_then_mock_publish_are_separate_audited_idempotent_transactions():
    r,pid,keys=confirmed()
    draft,=r.insight_proposals("t")
    assert draft.approval_status=="pending"
    with pytest.raises(ValueError,match="approval"):
        r.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                               actor="lead",reason="Publish",operation_key="publish-early")
    baseline=len(r.audit_events())
    approval=r.approve_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                               actor="lead",reason="Manual evidence review",operation_key="approve")
    assert approval.proposal_id==draft.proposal_id
    assert len(r.audit_events())==baseline+1
    assert r.approve_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                             actor="lead",reason="Manual evidence review",operation_key="approve")==approval
    assert len(r.audit_events())==baseline+1
    draft2,=r.insight_proposals("t")
    assert draft2.approval_status=="approved" and draft2.mock_issue_id is None
    issue=r.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                                 actor="lead",reason="Mock tracker only",operation_key="publish")
    assert issue.mock_issue_id.startswith("MOCK-")
    assert issue.scope_id=="t" and issue.proposal_id==draft.proposal_id
    assert len(r.audit_events())==baseline+2
    same=r.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                                actor="lead",reason="Mock tracker only",operation_key="publish")
    assert same==issue and len(r.audit_events())==baseline+2
    assert r.insight_proposals("t")[0].mock_issue_id==issue.mock_issue_id
    with pytest.raises(ValueError,match="idempotency"):
        r.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                               actor="lead",reason="different",operation_key="publish")
    state=r.to_state()
    restarted=ProblemRegistry.from_state(state)
    assert restarted.insight_proposals("t")==r.insight_proposals("t")
    assert len(restarted.audit_events())==len(r.audit_events())
    assert restarted.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                                          actor="lead",reason="Mock tracker only",operation_key="publish")==issue


def test_stale_revision_digest_and_split_invalidate_prior_approval_and_publish():
    r,pid,keys=confirmed()
    draft,=r.insight_proposals("t")
    with pytest.raises(ValueError,match="revision"):
        r.approve_insight(pid,expected_revision=9,evidence_digest=draft.evidence_digest,
                          actor="lead",reason="no",operation_key="wrong-revision")
    with pytest.raises(ValueError,match="evidence"):
        r.approve_insight(pid,expected_revision=2,evidence_digest="forged",
                          actor="lead",reason="no",operation_key="forged")
    r.approve_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                      actor="lead",reason="yes",operation_key="approved")
    r.split(pid,partitions=tuple((k,) for k in keys),actor="lead",
            reason="Corrected merge",operation_key="split",expected_revision=2)
    assert r.insight_proposals("t")==()
    with pytest.raises(ValueError,match="verified|active|merged"):
        r.publish_mock_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                               actor="lead",reason="Stale",operation_key="stale")
    assert all(e.kind!="insight_mock_published" for e in r.audit_events())


def test_approval_state_roundtrip_enforces_tenant_no_raw_ticket_text():
    r,pid,_=confirmed()
    draft,=r.insight_proposals("t")
    assert draft.scope_id=="t"
    with pytest.raises(ValueError,match="scope"):
        r.insight_proposals("other")
    r.approve_insight(pid,expected_revision=2,evidence_digest=draft.evidence_digest,
                      actor="lead",reason="Evidence checked",operation_key="a")
    state=r.to_state()
    assert "Ошибка входа" in str(state["tickets"])  # existing sanitized fixture, not proposal
    assert "Ошибка входа" not in str(state["proposal_approvals"])
    restored=ProblemRegistry.from_state(state)
    assert restored.insight_proposals("t")[0].approval_status=="approved"
