# BM25 → Dense → Hybrid Retrieval Benchmark (Superpowers)

> Execution mode: superpowers:executing-plans; test-first RED→GREEN per task, verify full suite on Python 3.11 and 3.13 before claims.

**Status:** In implementation on isolated branch.  
**Parent spec:** [Dataset-portable incident design](../specs/2026-10-30-dataset-portability-and-incident-benchmark-design.md)  
**Baseline:** [Measured static TF-IDF](../../evaluation/duplicate-benchmark-methodology.md)

## Goal

Compare TF-IDF, BM25, multilingual sentence embeddings, and untuned Reciprocal Rank Fusion (RRF) on **identical pinned GitBugs Hadoop corpus and identical 129 source-positive queries** with published SHA256 and transparent CPU runtime/cost. **No inferred negative pairs.** These are static retrieval metrics, not incident classification, production precision or Gazprom Neft quality.

## Design

- Reuse pinned GitBugs downloader and positive-link audit.
- Refactor all retrieval variants behind \`rank(query_id, k) -> list[str]\`.
- Lexical BM25 tokenizes words and exact identifiers, with explicit tokenizer and source ID self exclusion.
- Dense model \`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2\` with revision pinned once resolved; CPU inference, deterministic eval mode; full corpus encoded once. Model license/model commit recorded.
- RRF combines *rank positions* (not incomparable raw scores), with \`score(d)=sum(1/(60+rank_i(d)))\` and fixed k=60; uses lexical + dense.
- Scoring on exactly the positive query IDs, identical candidate corpus and exclusion. No supervised tuning or test-set threshold selection.
- Record hardware, dataset hashes, exact model revision, dependency versions and timing; do not commit raw text or model files.

## Task 1 — BM25 baseline (TDD)

**Files:** Create \`src/productpulse/eval/rank_fusion.py\` and \`tests/eval/test_rank_fusion.py\` (shared contract); \`scripts/run_retrieval_comparison.py\`; \`.github/workflows/compare-gitbugs-retrieval.yml\`.

- [ ] Add tests for BM25 tokenizer preserving HTTP/technical IDs, deterministic ranking, tie/self exclusions; observe RED.
- [ ] Implement BM25 using \`rank-bm25\` or pure Python with explicit IDF/tokenization; observe GREEN.
- [ ] Run static GitBugs comparison of existing TF-IDF vs BM25 on original 129 queries; publish aggregate metrics and source checksums.
- [ ] Verify complete test suite and data provenance.

## Task 2 — Dense multilingual model (TDD)

- [ ] Write tests for normalized embeddings, deterministic cosine ranking, no self rank, invalid/NaN vectors and correct query/candidate IDs; observe RED.
- [ ] Implement optional \`sentence-transformers\` adapter; avoid fetching models in unit tests.
- [ ] Run same corpus/query set on CPU with pinned model revision and log model loading, encoding and ranking times; if blocked, record explicit failure and do not fabricate dense results.

## Task 3 — RRF hybrid (TDD)

- [ ] Write failing tests proving rank-only RRF, duplicates/self excluded, deterministic tie-break, missing rank source, top_k behavior; observe RED.
- [ ] Implement simple fixed-parameter RRF, no optimization on benchmark holdout.
- [ ] Re-run comparison on same query/corpus; report improvement OR regression relative to TF-IDF and BM25.
- [ ] Publish measured table and limitations, clean review of code and CI.

## Guardrails

- Static evaluation: source ticket descriptions may have later edits and TF-IDF is fitted across corpus. **Never** call it "early incident detection".
- Source labels are sparse. Metric applies to 129 source-positive queries, NOT all 2,503 incoming tickets.
- If any model fails to load, keep BM25 output and label dense/hybrid pending.
- No model ID or fetched code automatically trusted: keep \`trust_remote_code=False\`; never pass ticket text as instructions.
- If model downloads require accepting third-party terms, check licensing before use in a corporate deployment.
- Merge only after PR review; no direct main writes.
