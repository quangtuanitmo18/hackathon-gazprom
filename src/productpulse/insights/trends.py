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
    "volume_increase", "new_activity", "monitor", "insufficient_timestamps"
]


@dataclass(frozen=True)
class ProblemTimeline:
    problem_id: str
    scope_id: str
    revision: int
    ticket_times: tuple[tuple[str, datetime | None], ...]


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


_PRIORITY = {
    "volume_increase": 0,
    "new_activity": 1,
    "insufficient_timestamps": 2,
    "monitor": 3,
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
        if incomplete:
            status: TrendStatus = "insufficient_timestamps"
        elif n >= min_current and delta >= min_delta:
            status = "new_activity" if baseline == 0 else "volume_increase"
        else:
            status = "monitor"

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
        ))

    return tuple(sorted(
        result, key=lambda x: (
            _PRIORITY[x.status], -x.current_count, x.problem_id
        )
    ))
