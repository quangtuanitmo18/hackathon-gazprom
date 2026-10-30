"""Phase 19 RED tests: temporal, review-safe Problem volume signals."""
from datetime import datetime, timedelta, timezone

import pytest

from productpulse.insights.trends import ProblemTimeline, SourceCoverage, analyze_problem_trends


NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def make_problem(*ages, scope="tenant-a", problem_id="PRB-1", revision=2):
    """Age in hours; None is missing source event-time."""
    return ProblemTimeline(
        problem_id=problem_id, scope_id=scope, revision=revision,
        ticket_times=tuple(
            (f"{problem_id}:source:{i}", None if h is None else NOW - timedelta(hours=h))
            for i, h in enumerate(ages)
        ),
    )


def inspect(*problems, **kwargs):
    return analyze_problem_trends(
        problems, trusted_scope="tenant-a", as_of=NOW, **kwargs
    )


def test_confirmed_three_member_problem_new_activity_not_statistically_proven_spike():
    trend, = inspect(make_problem(1, 2, 3))
    assert trend.status == "unknown_coverage"
    assert trend.observed_pattern == "new_activity"
    assert trend.coverage_status == "unknown_coverage"
    assert trend.eligible_for_alert is False
    assert (trend.current_count, trend.previous_count, trend.delta) == (3, 0, 3)
    assert trend.problem_id == "PRB-1"
    assert trend.revision == 2
    assert trend.current_ticket_keys == ("PRB-1:source:0", "PRB-1:source:1", "PRB-1:source:2")
    assert trend.previous_ticket_keys == ()
    assert trend.as_of == NOW
    assert trend.window_hours == 24


def test_volume_increase_has_nonzero_observed_baseline_and_absolute_threshold():
    trend, = inspect(make_problem(1, 2, 3, 4, 25))
    assert (trend.status, trend.observed_pattern, trend.current_count, trend.previous_count) == (
        "unknown_coverage", "volume_increase", 4, 1
    )
    assert trend.delta == 3
    assert trend.previous_ticket_keys == ("PRB-1:source:4",)


def test_stable_declining_or_low_counts_do_not_emit_alerts():
    a, b, c = inspect(
        make_problem(1, 2, problem_id="a"),
        make_problem(2, 25, 26, problem_id="b"),
        make_problem(3, 27, 28, problem_id="c"),
    )
    assert (a.status, b.status, c.status) == ("monitor", "monitor", "monitor")
    assert (a.delta, b.delta, c.delta) == (2, -1, -1)


def test_exact_half_open_time_boundaries_and_timezone_normalization():
    problem = ProblemTimeline(
        problem_id="boundary", scope_id="tenant-a", revision=1,
        ticket_times=(
            ("a", NOW - timedelta(hours=48, seconds=1)),  # outside both windows
            ("b", NOW - timedelta(hours=24)),  # current
            ("c", NOW - timedelta(hours=48) + timedelta(seconds=1)),  # previous
            ("d", NOW),  # not yet within strictly historical window
        ),
    )
    trend, = inspect(problem)
    assert (trend.current_count, trend.previous_count) == (1, 1)
    assert trend.current_ticket_keys == ("b",)
    assert trend.previous_ticket_keys == ("c",)


def test_missing_or_future_event_time_never_silently_counts_as_zero_baseline():
    missing, future = inspect(
        make_problem(1, 2, None, problem_id="missing"),
        make_problem(1, 2, -1, problem_id="future"),
    )
    assert missing.status == "insufficient_timestamps"
    assert future.status == "insufficient_timestamps"


def test_singletons_are_not_confirmed_problem_trends_even_if_lexically_similar():
    assert inspect(make_problem(1)) == ()


def test_scopes_and_duplicate_ticket_keys_fail_closed():
    with pytest.raises(ValueError, match="scope"):
        inspect(make_problem(1, 2, scope="other-tenant"))
    broken = ProblemTimeline(
        problem_id="x", scope_id="tenant-a", revision=1,
        ticket_times=(("one", NOW), ("one", NOW)),
    )
    with pytest.raises(ValueError, match="duplicate"):
        inspect(broken)


@pytest.mark.parametrize("cap", [0, -1])
def test_invalid_capacity_is_rejected(cap):
    with pytest.raises(ValueError):
        inspect(make_problem(1, 2), corpus_cap=cap)


def test_no_silent_truncation_when_corpus_exceeds_cap():
    with pytest.raises(ValueError, match="capacity"):
        inspect(make_problem(1, 2, 3), corpus_cap=2)


def test_invalid_clock_and_policy_are_rejected():
    with pytest.raises(ValueError, match="timezone"):
        analyze_problem_trends([], trusted_scope="tenant-a",
                               as_of=datetime(2026, 10, 30))
    with pytest.raises(ValueError, match="window"):
        inspect(window_hours=0)
    with pytest.raises(ValueError, match="min_current"):
        inspect(min_current=0)
    with pytest.raises(ValueError, match="min_delta"):
        inspect(min_delta=0)


def test_deterministic_status_priority_and_problem_id_ordering():
    result = inspect(
        make_problem(25, 26, problem_id="z-monitor"),
        make_problem(1, 2, 3, problem_id="b-new"),
        make_problem(1, 2, 3, 25, problem_id="a-growth"),
    )
    assert [(r.problem_id, r.status) for r in result] == [
        ("a-growth", "unknown_coverage"),
        ("b-new", "unknown_coverage"),
        ("z-monitor", "monitor"),
    ]

def test_boundary_exact_48h_is_in_previous_window_and_offset_equivalence():
    utc_exact = NOW - timedelta(hours=48)
    shifted = utc_exact.astimezone(timezone(timedelta(hours=3)))
    p = ProblemTimeline(
        problem_id="boundary48", scope_id="tenant-a", revision=1,
        ticket_times=(("a", utc_exact), ("b", shifted), ("c", NOW - timedelta(hours=1))),
    )
    row, = inspect(p)
    assert row.previous_count == 2
    assert row.previous_ticket_keys == ("a", "b")
    assert row.current_count == 1


def test_verified_source_coverage_allows_descriptive_growth_not_auto_publication():
    cover = SourceCoverage(
        source_system="synthetic",
        complete_from=NOW - timedelta(hours=72),
        complete_through=NOW,
        evidence_ref="signed-adapter-import-001",
    )
    row, = inspect(ProblemTimeline(
        problem_id="verified", scope_id="tenant-a", revision=2,
        source_systems=("synthetic",),
        coverage=(cover,),
        ticket_times=(
            ("a", NOW - timedelta(hours=1)),
            ("b", NOW - timedelta(hours=2)),
            ("c", NOW - timedelta(hours=3)),
        ),
    ))
    assert row.coverage_status == "complete"
    assert row.status == "new_activity"
    assert row.observed_pattern == "new_activity"
    assert row.eligible_for_alert is False  # human review remains mandatory


def test_partial_source_watermark_and_multisource_coverage_are_unknown():
    cover = SourceCoverage(
        source_system="a", complete_from=NOW - timedelta(hours=48),
        complete_through=NOW - timedelta(hours=1),
        evidence_ref="import-a",
    )
    row, = inspect(ProblemTimeline(
        problem_id="mixed", scope_id="tenant-a", revision=2,
        source_systems=("a", "b"),
        coverage=(cover,),
        ticket_times=tuple((str(i), NOW - timedelta(hours=i)) for i in (1, 2, 3)),
    ))
    assert row.status == "unknown_coverage"
    assert row.coverage_status == "unknown_coverage"


def test_backfilled_old_event_can_change_observed_baseline_not_fake_spike():
    initial, = inspect(make_problem(1, 2, 3))
    backfilled, = inspect(make_problem(1, 2, 3, 25))
    assert initial.previous_count == 0
    assert backfilled.previous_count == 1
    assert initial.observed_pattern == "new_activity"
    assert backfilled.observed_pattern == "volume_increase"
    assert both_are_unverified(initial, backfilled)


def both_are_unverified(*rows):
    return all(row.status == "unknown_coverage" and not row.eligible_for_alert for row in rows)


def test_empty_provenance_and_duplicate_source_coverage_fail_closed():
    with pytest.raises(ValueError, match="coverage"):
        inspect(ProblemTimeline(
            problem_id="invalid", scope_id="tenant-a", revision=1,
            source_systems=("a",),
            coverage=(SourceCoverage("a", NOW - timedelta(hours=48), NOW, ""),),
            ticket_times=(("a", NOW - timedelta(hours=1)), ("b", NOW - timedelta(hours=2))),
        ))
    coverage = SourceCoverage("a", NOW - timedelta(hours=48), NOW, "import-a")
    with pytest.raises(ValueError, match="duplicate"):
        inspect(ProblemTimeline(
            problem_id="invalid", scope_id="tenant-a", revision=1,
            source_systems=("a",), coverage=(coverage, coverage),
            ticket_times=(("a", NOW - timedelta(hours=1)), ("b", NOW - timedelta(hours=2))),
        ))
