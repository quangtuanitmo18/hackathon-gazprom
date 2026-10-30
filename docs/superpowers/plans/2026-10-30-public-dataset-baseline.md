# Public Dataset Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** TASK 1 APPROVED AND LOCALLY VERIFIED (2026-10-30); Tasks 2 and 3 remain pending.
**Goal:** Build reproducible, legally sourced local ticket dataset adapters and a measured classification baseline before organizer data is available.

**Architecture:** Two independent adapters for Zenodo v2 classification and Mendeley v3 process records, with source provenance and leakage-safe transforms. A minimal sklearn baseline plus a separate benchmark runner produces auditable results; Russian synthetic cases only test behavior.

**Tech Stack:** Python 3.11+, pytest, pydantic, pandas (optional), scikit-learn, hashlib, standard CSV/JSON libraries.

**Spec:** [Public dataset validation design](../specs/2026-10-30-public-dataset-validation-design.md)

## Global Constraints
- No real personal or company data in public GitHub.
- Dataset A/B license CC BY 4.0 and attribution required; verify exact source release.
- Preserve Zenodo original train/test partitions; never use final holdout for tuning.
- No fake incident-pair labels from category/product/time.
- No data after arrival available to an online predictor.
- No production code before the expected failing test is executed.

## Review Focus
- Dataset file schema changes => explicit exception and failure count, not silent shifted columns (Task 1).
- Blank/duplicate ID => rejected/quarantined before splitting (Task 1).
- Same source text in train and test => leak warning and documented handling (Task 2).
- Null timestamps => no chronological metric, no invented values (Task 3).
- Synthetic Russian fixtures => excluded from reported real-world evaluation metrics (Task 3).

---

### Task 1: Provenance manifest and safe local ingestion

**Verification:** 21 unit tests passed locally. See [Task 1 evidence](../../evaluation/task1-verification.md). Original public CSVs have not been profiled and GitHub CI is pending.

**Files:**
- Create: `.gitignore`
- Create: `src/productpulse/data/schema.py`
- Create: `src/productpulse/data/manifest.py`
- Create: `src/productpulse/data/adapters.py`
- Create: `tests/data/test_adapters.py`
- Create: `tests/data/test_manifest.py`

**Interfaces:**
- `CanonicalTicket(source: str, source_id: str, text_redacted: str, created_at: datetime | None, source_label: str | None, product_id: str | None)`.
- `parse_zenodo_split(x_rows: list[dict], y_rows: list[dict], split: str) -> list[CanonicalTicket]` (join text and category by original source ID; fail on unmatched IDs).
- `parse_mendeley_rows(rows: list[dict]) -> list[CanonicalTicket]`.
- `build_provenance_manifest(source_url: str, license_id: str, file_path: Path) -> dict`.

- [x] Step 1: Write tests that verify exact field mapping, X/y ID joins (misaligned order and missing IDs must fail), unknown label preservation, invalid blank IDs, timezone null handling, and sha256 of a known fixture.
- [x] Step 2: Run `pytest tests/data/test_adapters.py tests/data/test_manifest.py -v`; Expected: FAIL due missing implementation.
- [x] Step 3: Implement minimal models/adapters/manifest and ignore `data/raw/`, `data/processed/`, `*.env`, exported experiment outputs with personal content.
- [x] Step 4: Run same pytest command; Expected: PASS. Run `git check-ignore data/raw/placeholder.csv`; Expected: ignored.
- [x] Step 5: Commit `feat(data): validate ticket provenance and dataset adapters`.

### Task 2: Zenodo classification baseline with immutable splits

**Files:**
- Create: `src/productpulse/eval/classification_baseline.py`
- Create: `tests/eval/test_classification_baseline.py`
- Create: `scripts/run_zenodo_baseline.py`

**Interfaces:**
- `prepare_author_split(train_rows: list[CanonicalTicket], test_rows: list[CanonicalTicket]) -> tuple[DatasetSplit, DatasetSplit]`.
- `run_majority_baseline(train: DatasetSplit, test: DatasetSplit) -> dict`.
- `run_tfidf_baseline(train: DatasetSplit, test: DatasetSplit, seed: int = 42) -> dict`.

- [ ] Step 1: Write tests enforcing original split, no source ID overlap, train-only vectorizer fit, macro F1 class balance and deterministic result.
- [ ] Step 2: Run `pytest tests/eval/test_classification_baseline.py -v`; Expected: FAIL before implementation.
- [ ] Step 3: Implement majority predictor and TF-IDF + logistic regression, save report/manifest with source checksum, holdout counts, confusion matrix and training/runtime measurements.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: PASS. Run script on locally downloaded **approved** Zenodo CSVs; Expected: nonempty measured results with run ID (do not fabricate expected score).
- [ ] Step 5: Commit `feat(eval): establish held-out real-ticket classification baseline` (no data files).

### Task 3: Mendeley process profiling and Russian hard-negative fixture

**Files:**
- Create: `scripts/profile_mendeley.py`
- Create: `tests/data/test_process_profile.py`
- Create: `tests/fixtures/russian_hard_negatives.jsonl`
- Create: `docs/evaluation/dataset-audit-template.md`

**Interfaces:**
- `profile_process_rows(issues: list[dict], history: list[dict]) -> dict`.
- `validate_hard_negative_fixture(rows: list[dict]) -> dict`.

- [ ] Step 1: Write tests for missing timestamps, wrong join keys, duplicate state changes, future-resolution leakage and synthetics excluded from benchmark aggregates.
- [ ] Step 2: Run `pytest tests/data/test_process_profile.py -v`; Expected: FAIL.
- [ ] Step 3: Implement conservative process profiler and create 12–20 team-authored Russian test cases including HTTP 403 vs forgot-password, same module/different version, and injected commands inside ticket text.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: PASS. Run profiler on permissioned local source and write actual coverage stats; if not downloadable, label BLOCKED.
- [ ] Step 5: Commit `test(data): add replay-safe profiling and Russian adversarial cases`.

## Execution notes and gates
Tasks are ordered 1 → 2 → 3. Prefer one isolated feature branch and individual RED/GREEN commits. For GitHub-only execution without access to local worktree/tests, **do not claim task complete**; pass the plan to an executor that can run commands and read output.

Only after measured baselines and validated labels, consider incident clustering/evaluation. Mendeley workflow statistics and Zenodo category F1 are from **different populations**; do not combine them into a single claim or ROI measurement.
