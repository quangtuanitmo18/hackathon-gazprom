"""Positive-only duplicate retrieval metrics: absence of a link != a negative."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence


def build_query_positives(pairs: Iterable[tuple[str, str]]) -> dict[str, frozenset[str]]:
    """Convert undirected positive source edges to query -> observed positives."""
    results: dict[str, set[str]] = defaultdict(set)
    for a, b in pairs:
        if a == b:
            raise ValueError("self-positive source link is invalid")
        results[a].add(b)
        results[b].add(a)
    return {k: frozenset(v) for k, v in sorted(results.items())}


def evaluate_positive_retrieval(
    ranked_by_query: Mapping[str, Sequence[str]],
    positive_by_query: Mapping[str, set[str] | frozenset[str]],
    *,
    known_ids: set[str] | None = None,
    ks: tuple[int, ...] = (1, 5, 10),
) -> dict[str, int | float | None]:
    """Score observed positives without inventing reviewed negative labels.

    Each eligible query has >=1 known positive, appears in ranking, and has all
    known targets present in corpus (when corpus index supplied). Self and
    duplicate ranked IDs are excluded. Metrics are macro means over queries.
    """
    if not ks or any(not isinstance(k, int) or k <= 0 for k in ks):
        raise ValueError("ks must contain strictly positive integers")
    unique_ks = tuple(sorted(set(ks)))
    stats: dict[int, dict[str, list[float]]] = {
        k: {"hit": [], "recall": [], "mrr": []} for k in unique_ks
    }
    no_positive = missing_rank = unavailable = evaluated = 0
    for query, positive_values in positive_by_query.items():
        gold = set(positive_values) - {query}
        if not gold:
            no_positive += 1
            continue
        if known_ids is not None and (
            query not in known_ids or not gold.issubset(known_ids)
        ):
            unavailable += 1
            continue
        if query not in ranked_by_query:
            missing_rank += 1
            continue
        rank: list[str] = []
        seen = {query}
        for doc in ranked_by_query[query]:
            if doc not in seen:
                rank.append(doc)
                seen.add(doc)
        evaluated += 1
        for k in unique_ks:
            top = rank[:k]
            matches = gold.intersection(top)
            stats[k]["hit"].append(float(bool(matches)))
            stats[k]["recall"].append(len(matches) / len(gold))
            first_rank = next((i for i, doc in enumerate(top, start=1) if doc in gold), None)
            stats[k]["mrr"].append(1.0 / first_rank if first_rank is not None else 0.0)
    report: dict[str, int | float | None] = {
        "queries_total": len(positive_by_query),
        "queries_evaluated": evaluated,
        "queries_without_positive": no_positive,
        "queries_without_ranking": missing_rank,
        "queries_with_unavailable_positive": unavailable,
    }
    for k in unique_ks:
        for name in ("hit", "recall", "mrr"):
            numbers = stats[k][name]
            report[f"{name}_at_{k}"] = sum(numbers) / len(numbers) if numbers else None
    return report
