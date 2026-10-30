"""Independent review: no synthetic fixture may become a human gold label."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from productpulse.data.canonical import CanonicalTicketV1
from productpulse.incident.annotation import (
    PairAnnotation, adjudicate_pair, pair_identity,
)


def ticket(i, source="synthetic"):
    return CanonicalTicketV1(
        source_system=source, source_ticket_id=i, provenance_id="fixture",
        body_redacted="Тестовая заявка",
    )


def annotation(label="same_incident", reviewer="reviewer-a", pair=None, **kwargs):
    data = dict(
        pair_id=pair or pair_identity(ticket("1"), ticket("2")),
        label=label, reviewer_id=reviewer,
        rationale="Verified common cause in evidence.",
        reviewed_at="2026-10-30T10:00:00+03:00",
    )
    data.update(kwargs)
    return PairAnnotation(**data)


def test_pair_identity_independent_of_input_order():
    assert pair_identity(ticket("1"), ticket("2")) == pair_identity(ticket("2"), ticket("1"))


def test_pair_id_namespaced_across_data_sources():
    assert pair_identity(ticket("42"), ticket("7")) != pair_identity(ticket("42", "organizer"), ticket("7", "organizer"))


def test_self_pair_is_rejected():
    with pytest.raises(ValueError, match="same ticket"):
        pair_identity(ticket("1"), ticket("1"))


def test_matching_independent_reviewers_confirm_genuine_positive():
    a = annotation()
    b = annotation(reviewer="reviewer-b")
    decision = adjudicate_pair(a, b)
    assert decision.status == "confirmed"
    assert decision.label == "same_incident"
    assert decision.reviewer_ids == ("reviewer-a", "reviewer-b")


def test_matching_negative_labels_are_valid_human_gold():
    out = adjudicate_pair(annotation(label="different_incident"), annotation(label="different_incident", reviewer="reviewer-b"))
    assert out.status == "confirmed"
    assert out.label == "different_incident"


def test_disagreement_stays_disputed_not_majority_guessed():
    a = annotation()
    b = annotation(label="related_topic", reviewer="reviewer-b")
    out = adjudicate_pair(a, b)
    assert out.status == "disputed"
    assert out.label is None


def test_both_uncertain_requires_more_evidence():
    out = adjudicate_pair(annotation(label="uncertain"), annotation(label="uncertain", reviewer="reviewer-b"))
    assert out.status == "uncertain"
    assert out.label is None


def test_same_person_cannot_reviewer_twice():
    with pytest.raises(ValueError, match="independent"):
        adjudicate_pair(annotation(reviewer="a"), annotation(reviewer="a"))


def test_distinct_pairs_cannot_be_adjudicated():
    with pytest.raises(ValueError, match="pair"):
        adjudicate_pair(annotation(), annotation(reviewer="b", pair=pair_identity(ticket("2"), ticket("3"))))


def test_reviewer_id_rationale_and_source_are_required():
    for change in (dict(reviewer_id=" "), dict(rationale=""), dict(label="made_up"),
                   dict(source_kind="synthetic")):
        with pytest.raises(ValidationError):
            annotation(**change)


def test_timestamps_require_timezone_and_are_utc_normalized():
    with pytest.raises(ValidationError, match="timezone"):
        annotation(reviewed_at="2026-10-30T10:00:00")
    assert annotation().reviewed_at == datetime(2026, 10, 30, 7, tzinfo=timezone.utc)


def test_review_record_is_immutable_and_not_a_model_prediction():
    a = annotation()
    assert a.source_kind == "human"
    with pytest.raises(Exception):
        a.label = "different_incident"
