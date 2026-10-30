# GitBugs Hadoop — Positive-Link Retrieval Benchmark

**Measured on:** 2026-10-30; [reproducible GitHub Actions run](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41039862317).  
**Evidence:** [aggregate JSON](gitbugs-hadoop-tfidf-baseline.json) and [source audit](../data/gitbugs-hadoop-audit.json).  
**Experiment type:** static unsupervised TF-IDF candidate retrieval. NOT chronological incident prediction or Gazprom Neft performance.

## Source and evaluation population

- Verified **2,503** reports (Hadoop; pinned GitBugs commit \`eadf2d6794990a1aaa26d0ae15391f29f8969301\`).
- Source duplicate mappings contain **66** distinct undirected positive pairs, spanning **129 distinct query issue IDs**.
- Each query ranks all OTHER reports in the full source corpus; self-match excluded. Queries have ≥1 source-labeled positive and all positives resolve in report index.
- \`Summary\` and \`Description\` are the **only features**. Status, Priority, Resolution, Resolved, Duplicate id/master are **not** input to the retrieval model. Text can contain information only visible after ticket creation, so this is **static**, not an arrival-time replay.
- Missing duplicate link means **unknown**, never a verified negative. No reported precision/F1. Source-labeled duplicate ≠ independently established common root cause.

## Method

\`\`\`text
documents = Summary + " " + Description
vectorizer = TfidfVectorizer(
    lowercase=True, strip_accents="unicode",
    ngram_range=(1,2), max_features=60000
)
matrix = vectorizer.fit_transform(documents)
query_candidates = sorted_by_cosine(query, all_other_documents)
metrics = evaluate_positive_retrieval(query_candidates, observed_source_links)
\`\`\`

The corpus-wide unsupervised TF-IDF fit is **transductive**; labels are never used in training. Temporal, product-based and family-disjoint evaluation are future tasks.

## Measured results

| Metric | Value | Definition |
|---|---:|---|
| Hit@1 | 0.4186 | At least one source-labeled linked report appears first |
| Hit@5 | 0.6202 | At least one linked report appears among first five |
| Hit@10 | 0.6977 | At least one linked report appears among first ten |
| Recall@1 | 0.4147 | Mean fraction of known linked reports retrieved at k=1 |
| Recall@5 | 0.6163 | Mean fraction retrieved at k=5 |
| Recall@10 | 0.6899 | Mean fraction retrieved at k=10 |
| MRR@10 | 0.5042 | Mean reciprocal rank of first known positive within 10 |
| Vocabulary | 60,000 | Bounded TF-IDF feature set |
| Fit time | 0.686s | Single GitHub Actions Python 3.11 runner; nonportable benchmark |
| Search time | 0.272s | Batch of 129 queries; runtime-specific |

**Measured, not estimated.** No high-impact recall or issue-clustering precision derived from these numbers. The positive-only selected query population is not the population of ALL incoming user tickets; do not report Hit@10 as "70% of all tickets correctly identified".

## Reproduction

\`\`\`bash
python -m pip install -e ".[dev,benchmark]"
python -m pytest -q
python scripts/datasets/audit_gitbugs.py
python scripts/run_duplicate_baseline.py
\`\`\`

Sources downloaded from pinned public commit into gitignored \`data/raw/gitbugs-hadoop\`; original bug report text not published because source audit detected potential email strings.

## Next validated experiments

1. BM25-only baseline on identical data/query population.
2. Dense multilingual encoder; measure model load/inference cost and sample hard negatives.
3. Hybrid score fusion (lexical + dense) calibrated only on a non-overlapping development subset; held-out evaluation by duplicate family.
4. Chronological replay using source \`Created\` timestamp after verifying timezone and event-time relevance; exclude future resolutions.
5. Label manually adjudicated negatives (similar topic, different incident) for meaningful precision/F1, then evaluate Russian test tickets separately.

No threshold or improvement target should be announced before measuring it.
