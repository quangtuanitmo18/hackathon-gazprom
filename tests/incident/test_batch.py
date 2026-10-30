"""Retrieval returns candidates; screened candidates are review proposals, not gold."""
import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.batch import screen_retrieved_candidates


def item(id_, *, product="erp"):
    return CanonicalTicketV1(
        source_system="demo", source_ticket_id=id_, provenance_id="fixture",
        body_redacted="HTTP 403 в ERP", product_id=product,
        component_id="auth", reported_version="2.8.1", error_codes=("HTTP 403",)
    )


def setup():
    a, b, c = item("a"), item("b"), item("c", product="logistics")
    by_key = {ticket_key(t): t for t in (a,b,c)}
    symptoms = {ticket_key(t): "auth_denied" for t in (a,b,c)}
    return a,b,c,by_key,symptoms


def test_respects_retrieval_order_and_reviews_each_distinct_candidate():
    a,b,c,by_key,symptoms = setup()
    out = screen_retrieved_candidates(
        a, [ticket_key(c), ticket_key(b)], by_key, symptoms
    )
    assert [v.candidate_key for v in out] == [ticket_key(c),ticket_key(b)]
    assert [v.rank for v in out] == [1,2]
    assert out[0].screening.status == "insufficient_or_conflicting_evidence"
    assert out[1].screening.status == "candidate_for_human_review"
    assert all(v.screening.requires_human_review for v in out)


def test_self_and_duplicate_candidate_not_reviewed_twice():
    a,b,c,by_key,symptoms = setup()
    out = screen_retrieved_candidates(
        a, [ticket_key(a), ticket_key(b), ticket_key(b)], by_key, symptoms
    )
    assert len(out) == 1
    assert out[0].candidate_key == ticket_key(b)
    assert out[0].rank == 1


def test_unknown_candidate_fails_closed():
    a,b,c,by_key,symptoms = setup()
    with pytest.raises(ValueError, match="missing candidate"):
        screen_retrieved_candidates(a, ["missing"], by_key, symptoms)


def test_inconsistent_lookup_key_fails_closed():
    a,b,c,by_key,symptoms = setup()
    corrupt = {ticket_key(b): c}
    with pytest.raises(ValueError, match="index key"):
        screen_retrieved_candidates(a, [ticket_key(b)], corrupt, symptoms)


def test_missing_extracted_symptom_cannot_automerge():
    a,b,c,by_key,symptoms = setup()
    symptoms.pop(ticket_key(b))
    out = screen_retrieved_candidates(a, [ticket_key(b)], by_key, symptoms)
    assert "missing_symptom" in out[0].screening.blockers


def test_empty_candidates_is_safe():
    a,b,c,by_key,symptoms = setup()
    assert screen_retrieved_candidates(a, [], by_key, symptoms) == ()


def test_candidate_burst_rejected_not_silently_truncated():
    a,b,c,by_key,symptoms = setup()
    with pytest.raises(ValueError, match="candidate limit"):
        screen_retrieved_candidates(a, [ticket_key(b), ticket_key(c)], by_key, symptoms, max_candidates=1)


def test_source_scoped_key_collision_not_conflated():
    a,b,c,by_key,symptoms = setup()
    same_short_id = b.model_copy(update={"source_system": "another"})
    by_key[ticket_key(same_short_id)] = same_short_id
    symptoms[ticket_key(same_short_id)] = "auth_denied"
    out = screen_retrieved_candidates(a, [ticket_key(b), ticket_key(same_short_id)], by_key, symptoms)
    assert len(out) == 2
    assert out[0].candidate_key != out[1].candidate_key
