# Ticket Intelligence Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reproducible ticket ingestion, classification baseline, candidate retrieval and governed incident grouping.

**Architecture:** Python modular pipeline from sanitized ticket input to candidate Problem records. First prove classical baselines, then add model-dependent adapters behind interfaces.

**Tech Stack:** Python 3.11+, FastAPI (later), Pydantic, pytest, scikit-learn, rank-bm25, sentence-transformers (optional), PostgreSQL/pgvector after in-memory baseline.

**Spec:** [ProductPulse design](../specs/2026-10-30-productpulse-system-design.md) — pending approval.

## Global Constraints
- No real personal/company data in public GitHub.
- No ungrounded same-incident claims based on cosine threshold alone.
- Arrival-time features only for chronological evaluation.
- No external issue write in this plan.
- Every test must be observed RED then GREEN; commits per task on isolated branch.

## Review Focus
- Duplicate (source,event_id) should be no-op and preserve counts (Task 1).
- Invalid/missing timezone timestamp should be quarantined rather than guessed (Task 1).
- A short login-password-reset ticket should not automatically merge with HTTP 403 incident (Task 3).
- Pairwise similarity non-transitivity should not merge A and C through B (Task 4).
- Unknown product or confidence should trigger abstention instead of owner invention (Task 2/4).

---

### Task 1: Ingestion and normalization

**Files:**
- Create: `src/productpulse/domain/tickets.py`
- Create: `src/productpulse/ingestion/normalize.py`
- Test: `tests/ingestion/test_normalize.py`

**Interfaces:** Produces `normalize_ticket(raw: dict) -> Ticket` and `EventDeduplicator.accept(source: str, event_id: str) -> bool`.

- [ ] Step 1: Write failing tests `test_requires_utc_timestamp`, `test_duplicate_event_noop`, `test_missing_identity_rejected`; assert contract from data-contracts.
- [ ] Step 2: Run `pytest tests/ingestion/test_normalize.py -v`; Expected: fail due missing module.
- [ ] Step 3: Implement minimal Pydantic ticket schema and deterministic normalizer; enforce UTC, source_event uniqueness, no content logging.
- [ ] Step 4: Run same command; Expected: all tests pass.
- [ ] Step 5: Commit `feat: normalize and deduplicate ticket events`.

### Task 2: Taxonomy and classification baseline

**Files:**
- Create: `src/productpulse/ml/classify.py`
- Test: `tests/ml/test_classify.py`
- Create: `eval/baselines/classification.py`

**Interfaces:** Consumes normalized Ticket; produces `ClassificationResult(intent, product_id, component, symptoms, error_codes, model_version, needs_review)`; `classify_ticket(ticket: Ticket) -> ClassificationResult`.

- [ ] Step 1: Write failing tests for incident HTTP 403, how-to password reset, and unknown product yielding needs_review.
- [ ] Step 2: Run `pytest tests/ml/test_classify.py -v`; Expected: FAIL missing classifier.
- [ ] Step 3: Implement deterministic baseline and separate TF-IDF trainer/evaluator; no LLM required.
- [ ] Step 4: Run test and `python -m eval.baselines.classification --help`; Expected: tests PASS, CLI help exits zero.
- [ ] Step 5: Commit `feat: add transparent classification baseline`.

### Task 3: Hybrid candidate search

**Files:**
- Create: `src/productpulse/ml/retrieve.py`
- Test: `tests/ml/test_retrieve.py`
- Create: `eval/baselines/retrieval.py`

**Interfaces:** Consumes Ticket and indexed history; produces `list[Candidate(ticket_id, keyword_score, dense_score, rank)]`; `retrieve_candidates(query: Ticket, history: list[Ticket], k: int) -> list[Candidate]`.

- [ ] Step 1: Write failing tests for exact error-code preservation, empty history, product filtering, deterministic ordering and password reset hard-negative handling.
- [ ] Step 2: Run `pytest tests/ml/test_retrieve.py -v`; Expected: FAIL.
- [ ] Step 3: Implement BM25 baseline; define pluggable embedding scorer, fusion, and metadata filters. Avoid network-dependent tests.
- [ ] Step 4: Run tests; Expected: PASS; report Recall@K only on annotated holdout.
- [ ] Step 5: Commit `feat: add pluggable hybrid retrieval`.

### Task 4: Pair verification and Problem Registry

**Files:**
- Create: `src/productpulse/domain/problems.py`
- Create: `src/productpulse/ml/match.py`
- Create: `src/productpulse/services/problem_registry.py`
- Test: `tests/services/test_problem_registry.py`

**Interfaces:** Consumes candidate pairs; produces `MatchDecision(relationship, evidence, needs_review)`; `ProblemRegistry.attach_ticket(problem_id, ticket_id, decision) -> Problem`.

- [ ] Step 1: Write failing tests for identical retry, false merge hard-negative, non-transitivity, unknown owner, reversible split and immutable audit.
- [ ] Step 2: Run `pytest tests/services/test_problem_registry.py -v`; Expected: FAIL missing implementation.
- [ ] Step 3: Implement evidence-aware decision policy and in-memory problem lifecycle; persist through storage adapter later.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: all PASS; no uncontrolled external effect.
- [ ] Step 5: Commit `feat: maintain auditable incident problem registry`.

## Acceptance
A command-line benchmark can ingest approved or public sanitized tickets, report reproducible baseline metrics, and demonstrate hard-negative cases. No claim of real-world Gazprom Neft performance without customer dataset.
