"""Bounded, deterministic BM25 recommendations, NEVER same-incident verdicts.

Use the already-validated Russian-aware BM25Index instead of building an
additional retrieval engine. Per-scope inputs must come from trusted Registry.
"""
from __future__ import annotations

from collections.abc import Sequence
from productpulse.data.canonical import CanonicalTicketV1
from productpulse.eval.retrieval_methods import BM25Index, tokenize


def rank_review_candidates(
    inputs: Sequence[tuple[str, CanonicalTicketV1, str]],
    *, approved_pairs: set[tuple[str, str]] | frozenset[tuple[str, str]] = frozenset(),
    limit: int = 20,
    corpus_cap: int = 500,
) -> tuple[dict, ...]:
    """Return unique, lexically supported pairs; rank is NOT probability.

    Each input row is (source-scoped ticket_key, ticket, active problem ID),
    pre-filtered to ONE tenant by the caller. Zero term overlap is excluded.
    """
    if limit < 1 or corpus_cap < 1 or limit > 100:
        raise ValueError("invalid candidate limit or corpus capacity")
    if len(inputs) > corpus_cap:
        raise ValueError("candidate indexing capacity exceeded; use indexed backend")
    if len(inputs) < 2:
        return ()
    sorted_rows = sorted(inputs, key=lambda x: x[0])
    keys = [row[0] for row in sorted_rows]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate source-scoped candidate ticket ID")
    texts = [
        " ".join(filter(None,(
            t.title or "", t.body_redacted or "",
            t.product_id or "", t.component_id or "",
            " ".join(t.error_codes),
        ))) for _, t, _ in sorted_rows
    ]
    tokens = [set(tokenize(text)) - {"email","phone","url","secret","redacted"}
              for text in texts]
    # No account identifiers, human annotations, review labels or gold edges are
    # used as ranking features. All source text must already be PII scrubbed.
    bm25 = BM25Index(keys, texts)
    key_index = {key: i for i, key in enumerate(keys)}
    matches: dict[tuple[str, str], dict] = {}
    for i, (a_key, a_ticket, a_problem) in enumerate(sorted_rows):
        ranking = bm25.rank(texts[i],exclude_id=a_key,k=min(30,len(keys)-1))
        for position,b_key in enumerate(ranking,start=1):
            j = key_index[b_key]
            _, b_ticket, b_problem = sorted_rows[j]
            pair = tuple(sorted((a_key,b_key)))
            if a_problem == b_problem or pair in approved_pairs:
                continue
            overlap=tokens[i] & tokens[j]
            if not overlap:
                continue
            signals=["lexical_overlap"]
            if a_ticket.product_id and a_ticket.product_id == b_ticket.product_id:
                signals.append("same_product")
            if a_ticket.component_id and a_ticket.component_id == b_ticket.component_id:
                signals.append("same_component")
            if set(a_ticket.error_codes) & set(b_ticket.error_codes):
                signals.append("shared_error_code")
            candidate = {
                "ticket_key_a":pair[0],
                "ticket_key_b":pair[1],
                "rank":position,
                "signals":tuple(signals),
            }
            prior=matches.get(pair)
            if prior is None or (position, pair) < (prior["rank"],pair):
                matches[pair]=candidate
    # Reproducible ordering; rank describes within-query BM25 position,
    # not calibrated incident likelihood.
    return tuple(sorted(matches.values(),
                        key=lambda x:(x["rank"],x["ticket_key_a"],x["ticket_key_b"]))[:limit])
