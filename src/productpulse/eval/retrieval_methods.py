"""Offline, deterministic retrieval baselines with no heavyweight model dependency.

BM25 is a corpus indexing baseline, cosine_rank accepts externally-produced
embeddings, and RRF fuses ranks only (never incomparable raw scores).
"""
from __future__ import annotations

from collections import Counter
import math
import re
from collections.abc import Mapping, Sequence

_TOKEN = re.compile(r"(?u)\b[\w]+(?:[.-][\w]+)*\b")


def tokenize(text: str) -> list[str]:
    """Retain Russian words, underscores in error codes and dotted versions."""
    return _TOKEN.findall(text.lower())


class BM25Index:
    """Small-corpus BM25Okapi-style scores using always-positive smoothed IDF."""

    def __init__(self, ids: Sequence[str], documents: Sequence[str], k1: float = 1.5, b: float = 0.75):
        if len(ids) != len(documents):
            raise ValueError("corpus id/document length mismatch")
        if len(set(ids)) != len(ids):
            raise ValueError("corpus IDs must be unique")
        if not (k1 > 0 and 0 <= b <= 1):
            raise ValueError("invalid BM25 configuration")
        self.ids = list(ids)
        self.term_freq = [Counter(tokenize(s)) for s in documents]
        self.lengths = [sum(c.values()) for c in self.term_freq]
        self.avg_length = sum(self.lengths) / len(self.lengths) if self.lengths else 1.0
        doc_freq = Counter(token for tf in self.term_freq for token in tf)
        self.idf = {
            term: math.log(1.0 + (len(self.ids) - df + 0.5) / (df + 0.5))
            for term, df in doc_freq.items()
        }
        self.k1, self.b = k1, b

    def rank(self, query: str, *, exclude_id: str | None = None, k: int = 10) -> list[str]:
        if k < 1:
            raise ValueError("k must be positive")
        terms = set(tokenize(query))
        scores: list[float] = []
        for tf, dl in zip(self.term_freq, self.lengths):
            normalizer = self.k1 * (1.0 - self.b + self.b * dl / self.avg_length)
            score = sum(
                self.idf.get(t, 0.0) * tf.get(t, 0) * (self.k1 + 1) /
                (tf.get(t, 0) + normalizer)
                for t in terms if tf.get(t, 0)
            )
            scores.append(score)
        # Stable tie-break by original corpus order, not hash iteration order.
        order = sorted(range(len(self.ids)), key=lambda i: (-scores[i], i))
        return [self.ids[i] for i in order if self.ids[i] != exclude_id][:k]


def cosine_rank(
    query_id: str,
    ids: Sequence[str],
    vectors: Sequence[Sequence[float]],
    *,
    k: int = 10,
) -> list[str]:
    """Cosine ranking over external embeddings, free from model/network code."""
    if k < 1 or len(ids) != len(vectors):
        raise ValueError("invalid k or mismatched vector/ID lengths")
    if len(set(ids)) != len(ids):
        raise ValueError("embedding IDs must be unique")
    if query_id not in ids:
        raise ValueError("unknown query ID")
    if not vectors:
        return []
    size = len(vectors[0])
    if not size or any(len(v) != size for v in vectors):
        raise ValueError("invalid embedding dimensions")
    norms: list[float] = []
    for v in vectors:
        if not all(math.isfinite(float(x)) for x in v):
            raise ValueError("non-finite embedding component")
        norm = math.sqrt(sum(float(x) ** 2 for x in v))
        if norm <= 0:
            raise ValueError("zero norm embedding")
        norms.append(norm)
    qi = ids.index(query_id)
    q = vectors[qi]
    scores = [
        sum(float(x) * float(y) for x, y in zip(q, v)) / (norms[qi] * norm)
        for v, norm in zip(vectors, norms)
    ]
    order = sorted(range(len(ids)), key=lambda i: (-scores[i], i))
    return [ids[i] for i in order if ids[i] != query_id][:k]


def reciprocal_rank_fusion(
    ranked_by_method: Mapping[str, Sequence[str]],
    *,
    k: int = 10,
    rrf_k: int = 60,
    exclude_id: str | None = None,
) -> list[str]:
    """RRF(d) = sum_i 1/(rrf_k + rank_i(d)), rank starts at one."""
    if not ranked_by_method or k < 1 or rrf_k < 1:
        raise ValueError("nonempty methods and positive k/rrf_k required")
    scores: dict[str, float] = {}
    for method_name in sorted(ranked_by_method):
        unique: set[str] = set()
        rank = 0
        for doc in ranked_by_method[method_name]:
            if doc == exclude_id or doc in unique:
                continue
            rank += 1
            unique.add(doc)
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (rrf_k + rank)
    return sorted(scores, key=lambda doc: (-scores[doc], doc))[:k]
