"""Phase 20 TDD: candidates are time-bounded pair evidence, NOT incidents."""
from datetime import datetime, timedelta, timezone

import pytest

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.insights.unverified_activity import list_unverified_activity

NOW = datetime(2026, 10, 30, 15, tzinfo=timezone.utc)
MESSAGE = "Авторизация платежный шлюз HTTP 403 токен сессии отклонен"


def ticket(name, hours_ago, *, text=MESSAGE, product="billing", source="synthetic"):
    return CanonicalTicketV1(
        source_system=source,
        source_ticket_id=name,
        provenance_id="synthetic-unit",
        body_redacted=text,
        product_id=product,
        created_at=None if hours_ago is None else NOW - timedelta(hours=hours_ago),
    )


def rows(*records):
    return tuple((ticket_key(t), t, owner) for t, owner in records)


def activity(*records, **kwargs):
    return list_unverified_activity(rows(*records), as_of=NOW, **kwargs)


def test_two_recent_matching_tickets_are_only_unverified_pair_evidence():
    a, b = ticket("a", 1), ticket("b", 2)
    out = activity((a, "p1"), (b, "p2"))
    assert len(out) == 1
    pair = out[0]
    assert pair.ticket_key_a == min(ticket_key(a), ticket_key(b))
    assert pair.ticket_key_b == max(ticket_key(a), ticket_key(b))
    assert pair.recent_pattern == "both_current"
    assert pair.current_member_count == 2 and pair.previous_member_count == 0
    assert pair.evidence_type == "lexical_candidate"
    assert pair.coverage_status == "unknown_coverage"
    assert pair.eligible_for_alert is False
    assert pair.as_of == NOW
    assert pair.window_hours == 24
    assert pair.rank >= 1 and "lexical_overlap" in pair.signals
    assert not hasattr(pair, "confidence")
    assert not hasattr(pair, "incident_id")
    assert pair.created_at_a == a.created_at
    assert pair.created_at_b == b.created_at


def test_recent_with_previous_window_ticket_is_not_a_verified_cluster():
    a, b = ticket("a", 1), ticket("b", 26)
    item, = activity((a, "p1"), (b, "p2"))
    assert item.recent_pattern == "current_with_previous"
    assert item.current_member_count == 1 and item.previous_member_count == 1


def test_two_previous_window_tickets_are_not_current_activity():
    assert activity((ticket("a", 25), "p1"), (ticket("b", 26), "p2")) == ()


def test_strict_half_open_boundaries_and_timezone_offsets():
    a = ticket("a", 24)  # inclusive in current
    b = ticket("b", 48)  # inclusive in previous
    b = b.model_copy(update={"created_at": b.created_at.astimezone(timezone(timedelta(hours=3)))})
    item, = activity((a, "p1"), (b, "p2"))
    assert item.recent_pattern == "current_with_previous"
    assert item.created_at_b.utcoffset() == timedelta(0)  # normalized output UTC


@pytest.mark.parametrize("not_eligible", [None, -1, 0, 48.0001, 100])
def test_missing_future_equal_asof_and_old_timestamps_never_sneak_in(not_eligible):
    assert activity(
        (ticket("recent", 1), "p1"),
        (ticket("bad", not_eligible), "p2"),
    ) == ()


def test_no_lexical_support_means_no_activity_even_if_product_same():
    a = ticket("a", 1, text="Квитанция исчезла")
    b = ticket("b", 2, text="Сертификат просрочен")
    assert activity((a, "p1"), (b, "p2")) == ()


def test_approved_pairs_and_existing_problem_membership_are_excluded():
    a, b = ticket("a", 1), ticket("b", 2)
    pair = tuple(sorted((ticket_key(a), ticket_key(b))))
    assert list_unverified_activity(
        rows((a, "p1"), (b, "p2")),
        approved_pairs={pair}, as_of=NOW,
    ) == ()
    assert activity((a, "same"), (b, "same")) == ()


def test_does_not_fabricate_transitive_problem_or_confidence_from_three_pairs():
    tickets = [ticket(str(i), i + 1) for i in range(3)]
    out = activity(*[(t, "p" + str(i)) for i, t in enumerate(tickets)])
    assert len(out) == 3
    assert len({(v.ticket_key_a, v.ticket_key_b) for v in out}) == 3
    assert all(v.evidence_type == "lexical_candidate" and v.eligible_for_alert is False for v in out)


def test_results_are_deterministic_under_input_ordering_and_limit():
    tickets = [ticket(str(i), i + 1) for i in range(4)]
    vals = rows(*[(t, "p" + str(i)) for i, t in enumerate(tickets)])
    a = list_unverified_activity(vals, as_of=NOW, limit=2)
    b = list_unverified_activity(tuple(reversed(vals)), as_of=NOW, limit=2)
    assert a == b
    assert len(a) == 2


def test_corpus_cap_applies_to_entire_scope_not_just_recent_ticket_subset():
    records = [(ticket(str(i), 200), "p" + str(i)) for i in range(4)]
    with pytest.raises(ValueError, match="capacity"):
        activity(*records, corpus_cap=3)


def test_identity_collisions_and_key_forgery_are_rejected():
    a = ticket("a", 1)
    with pytest.raises(ValueError, match="duplicate"):
        list_unverified_activity(
            ((ticket_key(a), a, "p1"), (ticket_key(a), a, "p2")), as_of=NOW
        )
    with pytest.raises(ValueError, match="identity"):
        list_unverified_activity((("fake-id", a, "p1"),), as_of=NOW)


def test_invalid_clock_policy_and_limit_are_rejected():
    valid = rows((ticket("a", 1), "p1"), (ticket("b", 2), "p2"))
    with pytest.raises(ValueError, match="timezone"):
        list_unverified_activity(valid, as_of=datetime(2026, 10, 30))
    for invalid_window in (0, -1, 169):
        with pytest.raises(ValueError, match="window"):
            list_unverified_activity(valid, as_of=NOW, window_hours=invalid_window)
    for invalid_limit in (0, 31):
        with pytest.raises(ValueError, match="limit"):
            list_unverified_activity(valid, as_of=NOW, limit=invalid_limit)


def test_missing_event_time_omitted_without_fabricating_observation_time():
    assert activity((ticket("a", 1), "p1"), (ticket("b", None), "p2")) == ()


def test_recent_pair_not_starved_by_100_prior_only_pairs_in_ranked_shortlist():
    # Prior-only pairs must be filtered BEFORE the candidate ranker top-K,
    # otherwise 153 high-ranking old/old pairs can hide new pair evidence.
    older = [
        (ticket("old-" + str(i), 30, text="Сбой поиска документа склад HTTP 500"), "old-owner-" + str(i))
        for i in range(18)
    ]
    recent = [
        (ticket("recent-" + str(i), i + 1, text="Авторизация платежный шлюз HTTP 403 токен сессии отклонен"), "new-owner-" + str(i))
        for i in range(2)
    ]
    keys = {ticket_key(t) for t, _ in recent}
    result = activity(*(older + recent))
    assert any({row.ticket_key_a, row.ticket_key_b} == keys for row in result)
