# Dataset catalog — 30.10.2026

**Статус:** SOURCE DISCOVERY (verified against public dataset cards, **not** downloaded, profiled, or benchmarked yet).

Пока «Газпром нефть» не предоставила датасет, берём **два независимых публичных реальных корпуса** для проверки разных частей решения, плюс небольшие вручную размеченные русскоязычные контрпримеры для тестов. Не выдаём их метрики за качество на данных компании.

## Recommended dataset A — IT support ticket classification

- **Name:** Classification of IT Support Tickets — Leonardo Santiago Benitez Pereira (2022; Zenodo v2).
- **Original:** https://zenodo.org/records/7648117
- **Processed HF mirror:** https://huggingface.co/datasets/tasksource/it-support-tickets
- **License:** CC BY 4.0 (attribution required).
- **Reported size:** 2,229 actual IT support tickets manually classified by three IT professionals into seven categories.
- **Columns:** text, label in the processed mirror; original X_train/X_test/y_train/y_test preserved.
- **Languages:** mostly English, German, Portuguese and Spanish; NOT a Russian benchmark.
- **Role:** baseline classification (TF-IDF + logistic regression, multilingual encoder comparison), evaluate Macro F1 on ORIGINAL holdout. Keep label mapping explicit; hardware/software/access categories do NOT equal our requested business taxonomy incident/how_to/feature.
- **Limitations:** no incident-link ground truth, no timestamps for replay, no reliable product-team routing labels.

## Recommended dataset B — software-company helpdesk operations

- **Name:** Help Desk Tickets — Mohammad Abdellatif, Mendeley Data version 3 (2026).
- **Original:** https://data.mendeley.com/datasets/btm76zndnt/3
- **Processed HF mirror:** https://huggingface.co/datasets/tasksource/help-desk-tickets
- **License:** CC BY 4.0 (attribution required).
- **Source:** anonymized real helpdesk records from an international software company.
- **Files (original):** issues.csv, issues_change_history.csv, issues_snapshot.csv, sample_utterances.csv, feature documentation.
- **Fields reported:** issue/project/category/priority, assignee, start/resolution timestamps and status/assignment histories.
- **Processed HF caveat:** reporter_messages view has **357 text-bearing issues**; its `issue_type` of Ticket/HD Service/Deployment is NOT seven-category classification ground truth.
- **Role:** ingestion mapping, time-based replay/process analytics, test team-assignment / operational metrics **when fields support them**.
- **Limitations:** this does not prove incident-duplicate links or whether first dev notification time is captured; inspect fields before choosing labels or TTAI comparison.

## Dataset C — controlled Russian hard-negative fixtures

- **Source:** human-authored examples by team; **synthetic** and labeled as such.
- **Role:** smoke/e2e tests for product/component, code/version preservation, similarity ≠ same incident, prompt-injection resistance, missing-data abstention.
- **Important:** never claim real-world model accuracy or business improvement from these examples. Keep fixtures small and artificial, no real company names/persons/secrets.

## Explicitly not the default

- **Tobi-Bueck/customer-support-tickets** (https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets): HF listing shows **CC BY-NC 4.0**, multilingual but not a Russian-first dataset. License requires non-commercial use; do not assume permission for commercial reuse. Other mirrors/copies may report different license metadata. Source license and provenance need independent validation before adoption.
- Synthetic 1M+ ticket datasets: useful for stress/performance smoke tests, inappropriate as independent evidence of production effectiveness.

## Separately: duplicate incident evaluation

Neither dataset A nor B is confirmed to contain a gold `same_incident` label. **Do not infer it from shared category, same product, issue_type or close timestamps.** Before reporting incident detection precision:
1. Define annotation guideline with same_incident / related_topic / different / uncertain.
2. Human-label candidate pairs with hard negatives and independently adjudicate some samples.
3. Evaluate pairwise P/R/F1 only on a separated labeled holdout.
4. If no defensible incident ground truth, report only candidate retrieval demo and limitations; never invent clustering F1.

## Data governance and reproducibility

- No raw downloads, real message bodies, names, email addresses or secrets in public GitHub.
- Explicit CC BY attribution in docs/results; check terms before use.
- Download to gitignored local `data/raw/` only after design approval; hash the source and record record/version.
- Canonical fields: source, original_id, created_at, product_id, subject, text_redacted, label, split, provenance.
- Preserve original labels and split; avoid mixing label semantics across sources.
- Inspect duplicates and group leakage before train/dev/test.
- Before claiming results: dataset checksum, row counts, missingness, language distribution, PII review, script version, train/test isolation and baseline metrics.

## Source links
- https://zenodo.org/records/7648117
- https://huggingface.co/datasets/tasksource/it-support-tickets
- https://data.mendeley.com/datasets/btm76zndnt/3
- https://huggingface.co/datasets/tasksource/help-desk-tickets
- https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
