# Evaluation and Business Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Obtain defensible technical/operational evidence and a financial model that separates measured inputs from scenarios.

**Architecture:** Deterministic benchmark runner with logged provenance, temporal replay and human-timing CSV; finance calculations consume measurement records and explicit costs. No ungrounded claims.

**Tech Stack:** Python 3.11+, pytest, scikit-learn metrics, pandas (optional), CSV/JSON outputs.

**Spec:** [ProductPulse design](../specs/2026-10-30-productpulse-system-design.md) — pending approval.

## Global Constraints
- Dataset provenance and permissions required; never commit corporate data or PII.
- Holdout fixed before tuning; no use of future outcome fields in replay.
- Unknown baseline means no comparative TTAI claim.
- Financial estimates labeled MEASURED, ESTIMATED, SCENARIO.
- Use TDD and verify before all completion claims.

## Review Focus
- Singleton clusters should not produce divide-by-zero or dishonest recall (Task 1).
- Timestamp ties should give deterministic replay order (Task 2).
- Future resolution metadata must not leak into arrival-time features (Task 2).
- Human correction time must be counted in assisted work (Task 3).
- Negative net value must return no finite payback (Task 3).

---

### Task 1: Benchmark runner and errors

**Files:** Create `eval/metrics.py`, `eval/run.py`, `tests/eval/test_metrics.py`.

**Interfaces:** `calculate_classification_metrics(y_true, y_pred) -> dict`, `calculate_pairwise_metrics(true_pairs, predicted_pairs) -> dict`, `write_run_manifest(output_dir, metadata) -> str`.

- [ ] Step 1: Write tests for positive/negative pairs, singleton/empty cases, and metadata/run ID manifest.
- [ ] Step 2: Run `pytest tests/eval/test_metrics.py -v`; Expected: FAIL.
- [ ] Step 3: Implement deterministic metrics and manifest.
- [ ] Step 4: Run tests; Expected: PASS.
- [ ] Step 5: Commit `test: add reproducible evaluation metrics`.

### Task 2: Chronological incident replay

**Files:** Create `eval/replay.py`, `tests/eval/test_replay.py`.

**Interfaces:** `replay_tickets(events: list[TicketEvent], detector: Detector) -> list[DetectionEvent]`, `summarize_detection(events, labels) -> dict`.

- [ ] Step 1: Write tests for event ordering ties, future-data isolation, missed incidents, missing human baseline timestamp.
- [ ] Step 2: Run `pytest tests/eval/test_replay.py -v`; Expected: FAIL.
- [ ] Step 3: Implement sequential event replay and detection report.
- [ ] Step 4: Run tests; Expected: PASS.
- [ ] Step 5: Commit `feat: measure incident detection on chronological replay`.

### Task 3: Timed triage and scenario finance

**Files:** Create `eval/triage.py`, `src/productpulse/business/finance.py`, `tests/business/test_finance.py`.

**Interfaces:** `summarize_triage(trials: list[TimedTrial]) -> dict`, `calculate_financial_case(inputs: FinancialInputs) -> FinancialOutput`.

- [ ] Step 1: Write tests for review time inclusion, N=0, negative savings, no finite payback, separate capacity vs cash interpretation.
- [ ] Step 2: Run `pytest tests/business/test_finance.py -v`; Expected: FAIL.
- [ ] Step 3: Implement financial formulas described in `docs/business/financial-model.md`, require source classification per input.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: PASS.
- [ ] Step 5: Commit `feat: connect timed experiments to transparent cost model`.

## Acceptance
Every chart/table points to an immutable run manifest; unknown manual baseline must be reported as unknown rather than invented. No ROI statement beyond scope of measured evidence.
