"""Conservative, deterministic volume signals for explicitly grouped Problems.

Not incident detection, statistical anomaly detection, LLM inference or a
root-cause verdict. An approved pair is not automatically a merged Problem.
Event-time is CanonicalTicketV1.created_at, never review/ingest timestamp.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Literal


TrendStatus = Literal[
    "volume_increase", "new_activity", "monitor",
    "insufficient_timestamps", "unknown_coverage"
]


@dataclass(frozen=True)
class SourceCoverage:
    """Trusted adapter's complete event-time interval for one source.

    The registry MUST NOT invent these records from the observed minimum or
    maximum ticket timestamp. `evidence_ref` is a trusted import reference.
    """
    source_system: str
    complete_from: datetime
    complete_through: datetime
    evidence_ref: str


@dataclass(frozen=True)
class ProblemTimeline:
    problem_id: str
    scope_id: str
    revision: int
    ticket_times: tuple[tuple[str, datetime | None], ...]
    source_systems: tuple[str, ...] = ()
    coverage: tuple[SourceCoverage, ...] = ()


@dataclass(frozen=True)
class ProblemTrend:
    problem_id: str
    scope_id: str
    revision: int
    status: TrendStatus
    as_of: datetime
    window_hours: int
    current_count: int
    previous_count: int
    delta: int
    current_ticket_keys: tuple[str, ...]
    previous_ticket_keys: tuple[str, ...]
    coverage_status: Literal["complete", "unknown_coverage"]
    observed_pattern: Literal["volume_increase", "new_activity", "monitor"]
    eligible_for_alert: bool


_PRIORITY = {
    "volume_increase": 0,
    "new_activity": 1,
    "insufficient_timestamps": 2,
    "unknown_coverage": 3,
    "monitor": 4,
}


def analyze_problem_trends(
    problems: Iterable[ProblemTimeline],
    *,
    trusted_scope: str,
    as_of: datetime,
    window_hours: int = 24,
    min_current: int = 3,
    min_delta: int = 2,
    corpus_cap: int = 5000,
) -> tuple[ProblemTrend, ...]:
    """Read-only adjacent-window counts for active, *explicitly merged* Problems.

    Windows are [as_of-2*window, as_of-window) and
    [as_of-window, as_of), in UTC. Values are raw counts, not statistically
    significant spikes, root cause or calibrated duplicate probabilities.
    Problems with unknown/future event-time do not emit a positive signal.
    Growth without source-verified interval coverage is `unknown_coverage`,
    never an alert, regardless of how impressive its raw observed count is.
    The caller MUST construct timelines from a tenant-scoped trusted registry,
    never from user-provided Problem membership.
    """
    if not isinstance(trusted_scope, str) or not trusted_scope.strip():
        raise ValueError("trusted scope is required")
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must have a timezone")
    if type(window_hours) is not int or not 1 <= window_hours <= 168:
        raise ValueError("window_hours must be in 1..168")
    if type(min_current) is not int or min_current < 1:
        raise ValueError("min_current must be positive")
    if type(min_delta) is not int or min_delta < 1:
        raise ValueError("min_delta must be positive")
    if type(corpus_cap) is not int or corpus_cap < 1:
        raise ValueError("corpus capacity must be positive")

    end = as_of.astimezone(timezone.utc)
    current_start = end - timedelta(hours=window_hours)
    previous_start = current_start - timedelta(hours=window_hours)
    result: list[ProblemTrend] = []
    seen_problems: set[str] = set()
    seen_ticket_keys: set[str] = set()
    total_tickets = 0
    total_problems = 0

    for problem in problems:
        total_problems += 1
        total_tickets += len(problem.ticket_times)
        if total_problems > corpus_cap or total_tickets > corpus_cap:
            raise ValueError("trend corpus capacity exceeded; use indexed analytics")
        if problem.scope_id != trusted_scope:
            raise ValueError("Problem scope mismatches trusted scope")
        if not problem.problem_id or problem.problem_id in seen_problems:
            raise ValueError("duplicate or blank Problem identity")
        seen_problems.add(problem.problem_id)
        if type(problem.revision) is not int or problem.revision < 1:
            raise ValueError("invalid Problem revision")
        if len(problem.ticket_times) < 2:
            # Singleton Problems can never establish repeated confirmed events.
            continue

        # Coverage cannot be inferred from the observed tickets. It must
        # come from an independently checked, source-scoped ingestion manifest.
        if len(set(problem.source_systems)) != len(problem.source_systems):
            raise ValueError("duplicate source systems in Problem coverage")
        if any(not isinstance(s, str) or not s.strip() for s in problem.source_systems):
            raise ValueError("invalid Problem source coverage")
        coverage_by_source: dict[str, SourceCoverage] = {}
        for record in problem.coverage:
            if not record.source_system or not record.evidence_ref.strip():
                raise ValueError("invalid source coverage evidence")
            if record.source_system in coverage_by_source:
                raise ValueError("duplicate source coverage")
            if (record.source_system not in problem.source_systems
                or not isinstance(record.complete_from, datetime)
                or not isinstance(record.complete_through, datetime)
                or record.complete_from.tzinfo is None
                or record.complete_from.utcoffset() is None
                or record.complete_through.tzinfo is None
                or record.complete_through.utcoffset() is None
                or record.complete_from >= record.complete_through):
                raise ValueError("invalid source coverage window")
            coverage_by_source[record.source_system] = record
        coverage_complete = bool(problem.source_systems) and all(
            (source in coverage_by_source
             and coverage_by_source[source].complete_from.astimezone(timezone.utc) <= previous_start
             and coverage_by_source[source].complete_through.astimezone(timezone.utc) >= end)
            for source in problem.source_systems
        )
        coverage_status = "complete" if coverage_complete else "unknown_coverage"

        current: list[str] = []
        previous: list[str] = []
        incomplete = False
        for key, event_time in problem.ticket_times:
            if not isinstance(key, str) or not key or key in seen_ticket_keys:
                raise ValueError("duplicate or blank ticket key")
            seen_ticket_keys.add(key)
            if event_time is None:
                incomplete = True
                continue
            if (not isinstance(event_time, datetime) or
                    event_time.tzinfo is None or event_time.utcoffset() is None):
                incomplete = True
                continue
            ts = event_time.astimezone(timezone.utc)
            if ts > end:
                incomplete = True
                continue
            if current_start <= ts < end:
                current.append(key)
            elif previous_start <= ts < current_start:
                previous.append(key)
        current.sort()
        previous.sort()
        n, baseline = len(current), len(previous)
        delta = n - baseline
        if n >= min_current and delta >= min_delta:
            pattern = "new_activity" if baseline == 0 else "volume_increase"
        else:
            pattern = "monitor"
        if incomplete:
            status: TrendStatus = "insufficient_timestamps"
        elif pattern != "monitor" and coverage_status != "complete":
            status = "unknown_coverage"
        else:
            status = pattern

        result.append(ProblemTrend(
            problem_id=problem.problem_id,
            scope_id=problem.scope_id,
            revision=problem.revision,
            status=status,
            as_of=end,
            window_hours=window_hours,
            current_count=n,
            previous_count=baseline,
            delta=delta,
            current_ticket_keys=tuple(current),
            previous_ticket_keys=tuple(previous),
            coverage_status=coverage_status,
            observed_pattern=pattern,
            eligible_for_alert=False,  # no automatic publication or escalation
        ))

    return tuple(sorted(
        result, key=lambda x: (
            _PRIORITY[x.status], -x.current_count, x.problem_id
        )
    ))
