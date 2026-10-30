"""Human reviewer identities are supplied by verified OIDC middleware, not form bodies."""
import json
from datetime import datetime, timezone

import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.registry import ProblemRegistry


def ticket(i, source="demo"):
    return CanonicalTicketV1(
        source_system=source, source_ticket_id=i, provenance_id="synthetic",
        body_redacted="Синтетическая ошибка авторизации HTTP 403",
        product_id="erp", component_id="auth", reported_version="2.1",
        error_codes=("HTTP 403",),
    )


def registry(*ids):
    r = ProblemRegistry()
    ts = [ticket(x) for x in ids]
    for t in ts:
        r.register_ticket(t, "org")
    return r, ts


def submit(r, a, b, reviewer, label="same_incident", key=None):
    return r.submit_review(ticket_key(a), ticket_key(b),
        reviewer_id=reviewer, label=label, rationale="Исследованы причины сбоя",
        operation_key=key or ("review:" + reviewer),
    )


def test_one_review_is_not_approval_and_waits_for_independent_reviewer():
    r, (a,b) = registry("a","b")
    result=submit(r,a,b,"issuer:user-a")
    assert result.status=="awaiting_second_review"
    assert result.reviewer_ids==("issuer:user-a",)
    assert len(r.active_approvals())==0
    assert len(r.review_statuses())==1


def test_distinct_reviewers_agree_ready_for_lead_but_no_merge_or_approval():
    r,(a,b)=registry("a","b")
    submit(r,a,b,"issuer:user-a")
    result=submit(r,a,b,"issuer:user-b",key="review-b")
    assert result.status=="ready_for_lead"
    assert result.reviewer_ids==("issuer:user-a","issuer:user-b")
    assert len(r.active_approvals())==0
    assert len(r.list_active())==2


@pytest.mark.parametrize("second,expected",[
    ("related_topic","disputed"),("different_incident","disputed"),
    ("uncertain","uncertain"),
])
def test_different_or_uncertain_review_does_not_grant_approval(second,expected):
    r,(a,b)=registry("a","b")
    submit(r,a,b,"issuer:user-a")
    result=submit(r,a,b,"issuer:user-b",label=second,key="review-b")
    assert result.status==expected
    with pytest.raises(ValueError,match="ready_for_lead"):
        r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
            actor="issuer:lead",reason="Confirmed",operation_key="approve1")


def test_same_reviewer_cannot_add_second_vote_with_new_key():
    r,(a,b)=registry("a","b")
    submit(r,a,b,"issuer:user-a")
    with pytest.raises(ValueError,match="already reviewed"):
        submit(r,a,b,"issuer:user-a",key="second-vote")
    assert len(r.audit_events())==3


def test_exact_retry_is_idempotent_and_does_not_add_audit():
    r,(a,b)=registry("a","b")
    first=submit(r,a,b,"issuer:user-a")
    count=len(r.audit_events())
    assert submit(r,a,b,"issuer:user-a")==first
    assert len(r.audit_events())==count


def test_approval_needs_distinct_third_person_and_cannot_auto_merge():
    r,(a,b)=registry("a","b")
    pa,pb=r.problem_for_ticket(a),r.problem_for_ticket(b)
    submit(r,a,b,"issuer:user-a")
    submit(r,a,b,"issuer:user-b",key="review-b")
    with pytest.raises(ValueError,match="third independent"):
        r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
            actor="issuer:user-a",reason="Confirmed",operation_key="lead")
    result=r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
        actor="issuer:lead",reason="Confirmed",operation_key="lead")
    assert result.reviewer_ids==("issuer:user-a","issuer:user-b")
    assert len(r.active_approvals())==1
    assert r.problem_for_ticket(a)==pa
    assert r.problem_for_ticket(b)==pb
    assert r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
        actor="issuer:lead",reason="Confirmed",operation_key="lead")==result


def test_only_explicit_merge_makes_one_problem():
    r,(a,b)=registry("a","b")
    pa,pb=r.problem_for_ticket(a),r.problem_for_ticket(b)
    submit(r,a,b,"issuer:user-a")
    submit(r,a,b,"issuer:user-b",key="review-b")
    r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
        actor="issuer:lead",reason="Confirmed",operation_key="lead")
    assert len(r.list_active())==2
    merged=r.merge(pa.problem_id,pb.problem_id,actor="issuer:lead",
        reason="approved pair", operation_key="merge",
        expected_primary_revision=1,expected_secondary_revision=1)
    assert len(merged.ticket_keys)==2


def test_snapshot_round_trip_retains_review_progress_and_audit():
    r,(a,b)=registry("a","b")
    submit(r,a,b,"issuer:user-a")
    restored=ProblemRegistry.from_state(json.loads(json.dumps(r.to_state())))
    assert restored.review_statuses()==r.review_statuses()
    assert restored.audit_events()==r.audit_events()
    assert submit(restored,a,b,"issuer:user-a")==r.review_statuses()[0]
    result=submit(restored,a,b,"issuer:user-b",key="review-b")
    assert result.status=="ready_for_lead"


def test_cross_source_ticket_and_wrong_identity_rejected():
    r,(a,b)=registry("a","b")
    with pytest.raises(ValueError,match="registered"):
        r.submit_review(ticket_key(a),ticket_key(ticket("other")),
            reviewer_id="issuer:user-a",label="same_incident",
            rationale="evidence",operation_key="missing")


def test_split_requires_new_reviews_not_previous_reviews():
    r,(a,b)=registry("a","b")
    pa,pb=r.problem_for_ticket(a),r.problem_for_ticket(b)
    submit(r,a,b,"issuer:user-a")
    submit(r,a,b,"issuer:user-b",key="review-b")
    r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
        actor="issuer:lead",reason="confirmed",operation_key="lead")
    merged=r.merge(pa.problem_id,pb.problem_id,actor="issuer:lead",reason="confirmed",
        operation_key="merge",expected_primary_revision=1,expected_secondary_revision=1)
    r.split(merged.problem_id,partitions=((ticket_key(a),),(ticket_key(b),)),
        actor="issuer:lead",reason="wrong",operation_key="split",expected_revision=2)
    with pytest.raises(ValueError,match="ready_for_lead"):
        r.approve_reviewed_pair(ticket_key(a),ticket_key(b),
            actor="issuer:other-lead",reason="old evidence",operation_key="lead-2")
    assert r.review_statuses()[0].status=="awaiting_first_review"
    assert not r.active_approvals()
