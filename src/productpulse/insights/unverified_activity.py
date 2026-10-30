"""Pair-only early reviewer evidence, NEVER incident/group classification.

Uses the existing bounded, label-blind Cyrillic BM25 candidate ranker. Source
event-time is not ingestion time; this is a current snapshot recommendation
and must never be claimed as a time-safe historical online replay.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.candidates import rank_review_candidates


@dataclass(frozen=True)
class UnverifiedCandidateActivity:
    ticket_key_a: str
    ticket_key_b: str
    created_at_a: datetime
    created_at_b: datetime
    as_of: datetime
    window_hours: int
    recent_pattern: Literal["both_current", "current_with_previous"]
    current_member_count: int
    previous_member_count: int
    rank: int
    signals: tuple[str, ...]
    evidence_type: Literal["lexical_candidate"] = "lexical_candidate"
    coverage_status: Literal["unknown_coverage"] = "unknown_coverage"
    eligible_for_alert: Literal[False] = False


def list_unverified_activity(
    rows: Sequence[tuple[str, CanonicalTicketV1, str]],
    *,
    as_of: datetime,
    approved_pairs: set[tuple[str, str]] | frozenset[tuple[str, str]] = frozenset(),
    window_hours: int = 24,
    limit: int = 20,
    corpus_cap: int = 500,
) -> tuple[UnverifiedCandidateActivity, ...]:
    """Explain independent recent candidate pairs, not transitive clusters.

    The caller must provide the full, already-authenticated scoped snapshot.
    All tickets count against corpus_cap *before* filtering. The current
    runtime has no reliable ingest/observed_at or source coverage manifest.
    An eligible pair requires two event-time timestamps in [as_of-2W,as_of),
    at least one in the latest window [as_of-W,as_of). Missing/future
    timestamps are excluded, never replaced by the current clock.

    This is a ranker-bounded shortlist, not exhaustive pair recall.
    """
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must have a timezone")
    if type(window_hours) is not int or not 1 <= window_hours <= 168:
        raise ValueError("window_hours must be in 1..168")
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError("limit must be in 1..30")
    if type(corpus_cap) is not int or not 1 <= corpus_cap <= 500:
        raise ValueError("corpus capacity must be in 1..500")
    if len(rows) > corpus_cap:
        raise ValueError("candidate corpus capacity exceeded")
    seen: set[str] = set()
    end = as_of.astimezone(timezone.utc)
    current_start = end - timedelta(hours=window_hours)
    previous_start = current_start - timedelta(hours=window_hours)
    eligible: list[tuple[str, CanonicalTicketV1, str]] = []
    lookup: dict[str, datetime] = {}
    for key, ticket, owner in rows:
        if key in seen:
            raise ValueError("duplicate source-scoped ticket identity")
        seen.add(key)
        if not isinstance(ticket, CanonicalTicketV1) or key != ticket_key(ticket):
            raise ValueError("source-scoped ticket identity mismatch")
        if not isinstance(owner, str) or not owner:
            raise ValueError("invalid active Problem ownership")
        ts = ticket.created_at
        if ts is None:
            continue
        if ts.tzinfo is None or ts.utcoffset() is None:
            raise ValueError("event time must be timezone-aware")
        event_time = ts.astimezone(timezone.utc)
        if not previous_start <= event_time < end:
            continue
        lookup[key] = event_time
        eligible.append((key, ticket, owner))
    if len(eligible) < 2:
        return ()

    # Reuse the tested, non-authoritative BM25 candidate ranker, which
    # requires narrative token overlap and excludes approved/same-Problem.
    # Time constraints are applied before the top-100 pair shortlist, so
    # old-only pairs cannot starve current pairs. Retrieval still has a
    # top-30 neighbor bound for each query: NOT an exhaustive incident count.
    recent_keys = frozenset(
        key for key, ts in lookup.items() if current_start <= ts < end
    )
    if not recent_keys:
        return ()
    ranked = rank_review_candidates(
        eligible,
        approved_pairs=approved_pairs,
        required_any_ticket_keys=recent_keys,
        limit=100,
        corpus_cap=corpus_cap,
    )
    results: list[UnverifiedCandidateActivity] = []
    for candidate in ranked:
        a_key, b_key = candidate["ticket_key_a"], candidate["ticket_key_b"]
        a_time, b_time = lookup[a_key], lookup[b_key]
        current = int(current_start <= a_time) + int(current_start <= b_time)
        if current == 0:
            continue
        results.append(UnverifiedCandidateActivity(
            ticket_key_a=a_key,
            ticket_key_b=b_key,
            created_at_a=a_time,
            created_at_b=b_time,
            as_of=end,
            window_hours=window_hours,
            recent_pattern="both_current" if current == 2 else "current_with_previous",
            current_member_count=current,
            previous_member_count=2 - current,
            rank=candidate["rank"],
            signals=candidate["signals"],
        ))
        if len(results) >= limit:
            break
    return tuple(results)
