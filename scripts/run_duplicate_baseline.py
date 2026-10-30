#!/usr/bin/env python3
"""Measure unsupervised TF-IDF duplicate retrieval on verified GitBugs Hadoop.

This is STATIC leave-one-out retrieval, not chronological/online incident
detection. Missing source duplicate links are NOT verified negative labels.
No raw text is printed or committed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

from productpulse.data.gitbugs import normalize_positive_links
from productpulse.eval.duplicate_retrieval import build_query_positives, evaluate_positive_retrieval

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "gitbugs-hadoop"
RESULT = ROOT / "docs" / "evaluation" / "gitbugs-hadoop-tfidf-baseline.json"
SOURCE_COMMIT = "eadf2d6794990a1aaa26d0ae15391f29f8969301"
TOP_K = (1, 5, 10)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as file:
        reader = csv.DictReader(file)
        return list(reader)


def main() -> int:
    report_path, link_path = RAW / "reports.csv", RAW / "links.csv"
    if not report_path.exists() or not link_path.exists():
        raise FileNotFoundError(
            "Run scripts/datasets/audit_gitbugs.py to download pinned source first"
        )
    reports = read_csv(report_path)
    mappings = read_csv(link_path)
    ids = [str(row.get("Issue id") or "").strip() for row in reports]
    if any(not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("original report IDs invalid or nonunique")
    keys = {key: i for i, key in enumerate(ids)}
    validated = normalize_positive_links(mappings, set(ids))
    if not validated.link_index_validated or validated.malformed_count or validated.orphan_count:
        raise ValueError("duplicate label link integrity check failed")
    positive_by_query = build_query_positives(validated.positives)
    if len(positive_by_query) < 2:
        raise ValueError("no query-to-positive links")

    # Arrival-time fields only: no Resolution, Duplicate-of or future outcomes.
    documents = [
        " ".join(
            str(row.get(column) or "").strip()
            for column in ("Summary", "Description")
        ).strip()
        for row in reports
    ]
    if not all(documents):
        raise ValueError("some bug report has no text; explicit policy required")
    started = time.perf_counter()
    model = TfidfVectorizer(
        lowercase=True, strip_accents="unicode", ngram_range=(1, 2),
        min_df=1, max_features=60000, dtype=np.float64
    )
    matrix = model.fit_transform(documents)
    fitted_seconds = time.perf_counter() - started

    started = time.perf_counter()
    ranked: dict[str, list[str]] = {}
    for query_id in sorted(positive_by_query):
        i = keys[query_id]
        scores = (matrix[i] @ matrix.T).toarray().reshape(-1)
        order = np.argsort(-scores, kind="stable")
        ranked[query_id] = [ids[j] for j in order if j != i][:max(TOP_K)]
    lookup_seconds = time.perf_counter() - started

    metrics = evaluate_positive_retrieval(
        ranked,
        positive_by_query,
        known_ids=set(ids),
        ks=TOP_K,
    )
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "task": "static_duplicate_link_retrieval",
        "scope": "GitBugs Hadoop, not Gazprom Neft, not an online time replay",
        "source_commit": SOURCE_COMMIT,
        "source_reports_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "source_duplicate_links_sha256": hashlib.sha256(link_path.read_bytes()).hexdigest(),
        "documents": len(reports),
        "source_labeled_undirected_positive_pairs": len(validated.positives),
        "query_ids_with_positive": len(positive_by_query),
        "model": "TF-IDF word uni/bi-gram cosine retrieval; no supervised pair training",
        "max_features": 60000,
        "vocabulary_size": int(matrix.shape[1]),
        "python": platform.python_version(),
        "scikit_learn": sklearn.__version__,
        "fit_seconds": round(fitted_seconds, 5),
        "search_seconds": round(lookup_seconds, 5),
        "top_k": list(TOP_K),
        "metrics": metrics,
        "claims_limitations": [
            "Unlinked reports are not proven negatives.",
            "Metric denominators include only queries with source-labeled positives.",
            "Source duplicate link is a proxy for same incident, not a root-cause label.",
            "Corpus-wide unsupervised TF-IDF fit is static/transductive; not online/chronological.",
            "No business workload reduction or Gazprom Neft effectiveness inferred."
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": result["documents"],
        "positive_pairs": result["source_labeled_undirected_positive_pairs"],
        "queries": result["query_ids_with_positive"],
        "metrics": metrics,
        "fit_seconds": result["fit_seconds"],
        "search_seconds": result["search_seconds"]
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
