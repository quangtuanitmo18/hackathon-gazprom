#!/usr/bin/env python3
"""Pinned GitBugs corpus: identical 129 positive queries for BM25, dense and RRF.

Static positive-only retrieval. Never infer negatives from absent duplicate links.
No raw ticket descriptions in GitHub reports/logs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from productpulse.data.gitbugs import normalize_positive_links
from productpulse.eval.duplicate_retrieval import (
    build_query_positives, evaluate_positive_retrieval,
)
from productpulse.eval.retrieval_methods import BM25Index, reciprocal_rank_fusion

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/gitbugs-hadoop"
OUT = ROOT / "docs/evaluation"
SOURCE_SHA = {
    "reports.csv": "a04ac6238c39afaf97b9ffb2a416c1318dd85672a31e9a6dd74f64e199b77358",
    "links.csv": "5d9978c8aaeb65fcaf2386fdd796a9023931dd4b66e3c5751f111db6624b6dc0",
}
MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
KS = (1, 5, 10)
RETRIEVE_DEPTH = 100


def read_csv(name: str) -> list[dict[str, str]]:
    path = RAW / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA[name]:
        raise ValueError(f"Source checksum mismatch for {name}: {digest}")
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as stream:
        return list(csv.DictReader(stream))


def prepare():
    rows = read_csv("reports.csv")
    links = read_csv("links.csv")
    ids = [r["Issue id"].strip() for r in rows]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("invalid source IDs")
    audit = normalize_positive_links(links, set(ids))
    if audit.orphan_count or audit.malformed_count or len(audit.positives) != 66:
        raise ValueError("positive link audit failed")
    gold = build_query_positives(audit.positives)
    if len(rows) != 2503 or len(gold) != 129:
        raise ValueError("source data unexpectedly changed")
    docs = [
        (str(r.get("Summary") or "") + " " + str(r.get("Description") or "")).strip()
        for r in rows
    ]
    if any(not text for text in docs):
        raise ValueError("empty report text")
    return ids, docs, gold


def common_report(ids, gold):
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": "GitBugs Hadoop original CSVs",
        "source_commit": "eadf2d6794990a1aaa26d0ae15391f29f8969301",
        "source_checksums": SOURCE_SHA,
        "total_reports": len(ids),
        "positive_pairs": 66,
        "source_labeled_query_ids": len(gold),
        "evaluation": "STATIC corpus-wide, leave-one-out, positive-link only",
        "k_values": KS,
        "python": platform.python_version(),
        "environment": "GitHub Actions Ubuntu runner, CPU",
        "limits": [
            "Queries selected for known positive duplicate links, not all support tickets.",
            "Unlinked pairs have unknown labels; no precision/F1 measured.",
            "No final issue resolution, status, duplicate label or future metadata used as retrieval features.",
            "Unsupervised static retrieval, not an online/chronological replay.",
            "No claim of company-specific performance, reduction in tickets or ROI.",
        ],
    }


def ranking_from_scores(ids, row_i, scores, depth=RETRIEVE_DEPTH):
    order = np.argsort(-np.asarray(scores), kind="stable")
    return [ids[j] for j in order if j != row_i][:depth]


def bm25_rank_all(ids, docs, gold):
    started = time.perf_counter()
    index = BM25Index(ids, docs)
    fit = time.perf_counter() - started
    keys = {id_: i for i, id_ in enumerate(ids)}
    started = time.perf_counter()
    ranked = {qid: index.rank(docs[keys[qid]], exclude_id=qid, k=RETRIEVE_DEPTH)
              for qid in sorted(gold)}
    retrieval = time.perf_counter() - started
    return ranked, {"index_seconds": round(fit, 5), "search_seconds": round(retrieval, 5)}


def lexical(ids, docs, gold):
    keys = {id_: i for i, id_ in enumerate(ids)}
    started = time.perf_counter()
    tfidf = TfidfVectorizer(
        lowercase=True, strip_accents="unicode",
        ngram_range=(1, 2), min_df=1, max_features=60000, dtype=np.float64,
    )
    mat = tfidf.fit_transform(docs)
    tfidf_build = time.perf_counter() - started
    started = time.perf_counter()
    trank = {
        q: ranking_from_scores(ids, keys[q], (mat[keys[q]] @ mat.T).toarray().reshape(-1))
        for q in sorted(gold)
    }
    tfidf_search = time.perf_counter() - started
    brank, btime = bm25_rank_all(ids, docs, gold)
    result = common_report(ids, gold)
    result["models"] = {
        "tfidf": {
            "model": "word unigrams+bigrams TF-IDF cosine, 60000 features",
            "metrics": evaluate_positive_retrieval(trank, gold, known_ids=set(ids), ks=KS),
            "index_seconds": round(tfidf_build, 5),
            "search_seconds": round(tfidf_search, 5),
        },
        "bm25": {
            "model": "BM25 k1=1.5,b=0.75, smoothed positive IDF, technical-aware tokenization",
            "metrics": evaluate_positive_retrieval(brank, gold, known_ids=set(ids), ks=KS),
            **btime,
        },
    }
    return result


def dense_hybrid(ids, docs, gold):
    # This function loads model weights ONLY in the benchmark process, never in tests.
    import torch
    from huggingface_hub import HfApi
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(2)
    model_revision = HfApi().model_info(MODEL_ID).sha
    if not model_revision:
        raise ValueError("cannot pin multilingual model revision")
    started = time.perf_counter()
    model = SentenceTransformer(
        MODEL_ID, revision=model_revision, device="cpu", trust_remote_code=False
    )
    model.eval()
    model_load = time.perf_counter() - started

    started = time.perf_counter()
    matrix = model.encode(
        docs, batch_size=24, show_progress_bar=False,
        convert_to_numpy=True, normalize_embeddings=True,
    )
    encode_seconds = time.perf_counter() - started
    if matrix.shape[0] != len(ids) or not np.isfinite(matrix).all():
        raise ValueError("invalid dense model output")
    keys = {id_: i for i, id_ in enumerate(ids)}
    started = time.perf_counter()
    dense_rank = {
        q: ranking_from_scores(ids, keys[q], matrix[keys[q]] @ matrix.T)
        for q in sorted(gold)
    }
    search_seconds = time.perf_counter() - started

    bm25_rank, bm25_time = bm25_rank_all(ids, docs, gold)
    fused_rank = {
        q: reciprocal_rank_fusion(
            {"bm25": bm25_rank[q], "dense": dense_rank[q]},
            k=RETRIEVE_DEPTH, rrf_k=60, exclude_id=q,
        )
        for q in sorted(gold)
    }
    result = common_report(ids, gold)
    result["models"] = {
        "dense": {
            "model_id": MODEL_ID,
            "revision": model_revision,
            "license": "Apache-2.0 (model card; verify before commercial deployment)",
            "embedding_dimensions": int(matrix.shape[1]),
            "model_max_seq_length_tokens": int(model.max_seq_length),
            "model_load_seconds": round(model_load, 5),
            "encode_all_seconds": round(encode_seconds, 5),
            "query_search_seconds": round(search_seconds, 5),
            "metrics": evaluate_positive_retrieval(dense_rank, gold, known_ids=set(ids), ks=KS),
        },
        "bm25": {
            "model": "BM25 k1=1.5,b=0.75",
            "metrics": evaluate_positive_retrieval(bm25_rank, gold, known_ids=set(ids), ks=KS),
            **bm25_time,
        },
        "hybrid_rrf": {
            "model": "BM25 + multilingual dense RRF, rank_constant=60, pool=100, not tuned",
            "metrics": evaluate_positive_retrieval(fused_rank, gold, known_ids=set(ids), ks=KS),
        },
    }
    result["limits"].append("Dense transformer truncates long report text at max_seq_length; lexical methods see full text.")
    result["limits"].append("Hugging Face model revision is recorded; dataset positive links not used to tune RRF.")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("lexical", "dense"), required=True)
    args = parser.parse_args()
    ids, docs, gold = prepare()
    result = lexical(ids, docs, gold) if args.mode == "lexical" else dense_hybrid(ids, docs, gold)
    path = OUT / f"gitbugs-retrieval-{args.mode}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": args.mode,
        "total_reports": len(ids),
        "query_ids": len(gold),
        "measurements": {k: v["metrics"] for k, v in result["models"].items()},
        "file": str(path)
    }, indent=2))


if __name__ == "__main__":
    main()
