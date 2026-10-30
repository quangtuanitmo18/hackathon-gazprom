"""Review-only bridge between retrieval IDs and incident evidence screening.

Retrieval may produce semantic neighbors, not verified duplicates.
No database updates, cluster merges, notifications or issue-tracker writes here.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.verify import PairScreening, screen_pair


@dataclass(frozen=True)
class CandidateReview:
    query_key: str
    candidate_key: str
    rank: int
    screening: PairScreening


def screen_retrieved_candidates(
    query: CanonicalTicketV1,
    candidate_keys: Sequence[str],
    tickets_by_key: Mapping[str, CanonicalTicketV1],
    symptom_keys: Mapping[str, str | None],
    *,
    max_candidates: int = 20,
) -> tuple[CandidateReview, ...]:
    """Deduplicate retrieved source-scoped IDs and record review-only outcomes.

    Missing candidate records / corrupted index metadata fail closed. Missing
    symptom enrichment is allowed only as an explicit abstention.
    """
    if max_candidates < 1:
        raise ValueError("candidate limit must be positive")
    q_key = ticket_key(query)
    ordered: list[str] = []
    seen = {q_key}
    for c_key in candidate_keys:
        if c_key in seen:
            continue
        seen.add(c_key)
        ordered.append(c_key)
    if len(ordered) > max_candidates:
        raise ValueError("candidate limit exceeded; refusing silent truncation")

    results = []
    for rank, key in enumerate(ordered, start=1):
        ticket = tickets_by_key.get(key)
        if ticket is None:
            raise ValueError(f"missing candidate in ticket index: {key}")
        if ticket_key(ticket) != key:
            raise ValueError(f"ticket index key mismatch: {key}")
        screening = screen_pair(
            query, ticket,
            symptom_keys.get(q_key), symptom_keys.get(key),
        )
        results.append(
            CandidateReview(
                query_key=q_key, candidate_key=key, rank=rank,
                screening=screening,
            )
        )
    return tuple(results)
