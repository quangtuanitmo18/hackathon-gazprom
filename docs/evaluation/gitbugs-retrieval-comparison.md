# Real-data Retrieval Comparison — GitBugs Hadoop

**Date:** 2026-10-30  
**Status:** MEASURED on GitHub Actions; **NOT** a Gazprom Neft pilot result.  
**Reproduction:** [successful GitHub Actions workflow](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41041016292).  
**Machine-readable evidence:** [TF-IDF + BM25](gitbugs-retrieval-lexical.json) and [Dense + BM25 + Hybrid](gitbugs-retrieval-dense.json).  
**Source provenance:** [GitBugs Hadoop original-source audit](../data/gitbugs-audit.md).

## Dataset and scope

- 2,503 genuine issue reports in pinned GitBugs Hadoop original CSV.
- 126 original mapping rows → 66 unique undirected duplicate-positive pairs.
- 129 issue IDs with ≥1 known source-positive relationship; **all four methods tested on these same 129 queries**.
- Original CSV file SHA-256 verified; \`Summary + Description\` used for retrieval input.
- Candidate pool is all other reports, with self excluded; corpus-wide unsupervised fit means the experiment is **static/transductive**, not an online incident prediction.
- Source duplicate edge is a proxy for same-incident; unlinked issue pairs remain **unknown, not negative**. Therefore **no precision/F1 reported**.

## Models and deterministic parameters

| Method | Implementation | Notes |
|---|---|---|
| TF-IDF | scikit-learn word unigrams/bigrams, max 60k features, cosine | Earlier baseline reproduced |
| BM25 | Self-contained BM25, k1=1.5, b=0.75, always-positive smoothed IDF | Regex retains underscores, dotted version numbers, Russian letters |
| Dense multilingual | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | **Pinned model revision \`e8f8c211226b894fcb81acc59f3b34ba3efd5f42\`**, 384 dimensions, max seq length **128 tokens** |
| Hybrid | BM25 + dense **Reciprocal Rank Fusion** | RRF k=60, top-100 candidate lists; **no test-label tuning** |

**Important comparison limitation:** Dense truncates long reports to max 128 tokens, but lexical retrieval uses the full report. This is a meaningful difference in effective input context, so the result is not a controlled comparison of equal text lengths.

## Measured metrics

| Method | Hit@1 | Hit@5 | Hit@10 | Recall@10 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| TF-IDF | 41.86% | 62.02% | 69.77% | 68.99% | 0.5038 |
| BM25 | 37.98% | 65.89% | 71.32% | 70.54% | 0.4843 |
| Dense MiniLM | 40.31% | 65.12% | 68.99% | 68.99% | 0.5046 |
| **Hybrid RRF** | **41.86%** | **68.22%** | **72.87%** | **72.87%** | **0.5305** |

*Definitions:* Hit@K = share of source-labeled positive queries with at least one known linked report among the first K retrieved. Recall@K = macro-average fraction of **known linked reports** appearing in first K; not recall on all real incidents. MRR@K = macro-average reciprocal rank of first known positive within K.

**Difference:** Hybrid Hit@10 vs BM25 **+1.55 percentage points**, i.e. **2 additional Hit@10 queries of 129**. Without paired confidence intervals and a domain-matched holdout, this should NOT be described as a meaningful proven superiority. Hybrid Hit@1 equals TF-IDF (41.86%); no winner across every metric.

## Measured compute costs on one ephemeral GitHub Actions CPU runner

| Operation | Measured time | Caution |
|---|---:|---|
| TF-IDF index build | 0.613 s | One corpus-wide vectorizer fit |
| TF-IDF ranking, 129 queries | 0.174 s | Sparse matrix scores |
| BM25 index build | 0.114 s | Pure Python |
| BM25 ranking, 129 queries | 1.787 s | Pure Python, linear scan; optimize before production |
| Dense model load | 7.056 s | Excludes PyTorch install and first model download |
| Dense encode **all 2,503 reports** | **70.303 s** | CPU, batch 24, 2 torch threads, model context 128 tokens |
| Dense ranking, 129 queries | 0.053 s | Once embeddings have been precomputed |

Do not interpret the 70s batch index encoding as per-request latency or extrapolate worker throughput directly; inference and serving costs must be measured under a realistic online load including new-ticket encoding and ANN/database indexing.

## Decision for ProductPulse architecture

1. **BM25 as reliable lexical baseline and fallback**, especially for exact error codes, product names, versions and model-service failure.
2. **Async dense index**: embedding created in background when tickets arrive; no synchronous full-corpus re-encoding for each request.
3. **RRF hybrid as a candidate**, not yet mandatory. Evaluate extra relevance against CPU/GPU cost and Russian domain before production enablement.
4. **Pairwise same-incident verification remains separate**: similar reports can have different technical root causes. No automatic cluster merge based on retrieval score alone.
5. **Human-in-the-loop + tracking:** incident detection precision, high-impact recall and product routing need separately annotated evidence.

## Must-do next experiments before claiming business fit

- **Paired significance:** save per-query success/failure for each model and bootstrap difference in Hit@K; no assumption of independence between queries from one duplicate family.
- **Chronological replay**: use \`Created\` only if reliable; prevent future texts/labels from being known at event arrival, preserve unresolved cases.
- **Annotated hard negatives**: similar text, different incidents, including Russian technical tickets.
- **Russian ticket adaptation**: evaluate language, code and product taxonomy; do not assume English bug tracker transfer.
- **Unit economics**: capture average new-ticket encode latency, token counts/operational costs, human review minutes, alert acceptance before calculating ROI.

## Reproduce

\`\`\`bash
python -m pip install -e ".[dev,benchmark,dense]"
python -m pytest -q
python scripts/datasets/audit_gitbugs.py
python scripts/run_retrieval_comparison.py --mode lexical
python scripts/run_retrieval_comparison.py --mode dense
\`\`\`

The benchmark downloads publisher source files to gitignored \`data/raw/\`. Published JSON contains aggregate metrics and SHA-256, **not raw reports or private user data**. Do not publish actual ticket contents to public GitHub.

**Interpreting the case:** This is candidate retrieval performance, not demonstrated classification/incident clustering accuracy, routing accuracy, resolution improvement, TTAI or Gazprom Neft ROI.
