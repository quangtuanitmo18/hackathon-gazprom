# Governed Agent and Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform an actionable Problem into a grounded insight proposal and a human-approved mock issue without unsafe side effects.

**Architecture:** Deterministic trigger and tool API, constrained LLM report generator, policy gate and auditable review workflow. Dependency on core Problem contract; mock tracker allows offline demo.

**Tech Stack:** Python 3.11+, Pydantic, pytest, FastAPI, LangGraph (after simple deterministic graph passes), mock tracker, Streamlit or minimal React.

**Spec:** [ProductPulse design](../specs/2026-10-30-productpulse-system-design.md) — pending approval.

## Global Constraints
- Ticket text is untrusted data; never execute its instructions.
- Never create real issues or send external notifications before authorized approval.
- Unknown team and unavailable tracker search force review.
- Idempotency key is `problem_id:event_type:revision`; no duplicate creates.
- Red/green TDD and per-task commits.

## Review Focus
- Injected tool instructions in ticket body must not change tool selection (Task 2).
- Existing issue must be updated, not newly created (Task 3).
- LLM output citing non-existent ticket IDs must be rejected (Task 2).
- Missing product owner must never be guessed (Task 1).
- Replaying approved event must not publish twice (Task 3).

---

### Task 1: Actionable trigger and read-only tools

**Files:** Create `src/productpulse/agent/tools.py`, `src/productpulse/agent/triggers.py`; Test `tests/agent/test_tools.py`.

**Interfaces:** Consumes Problem; produces `ActionableEvent` or no action; `get_problem_evidence(problem_id: str)`, `search_existing_issues(fingerprint: str)`, `get_product_owner(product_id: str)`, `get_trend_metrics(problem_id: str)`.

- [ ] Step 1: Write tests for no-trigger normal volume, urgent bypass, missing owner and read-only tool scope.
- [ ] Step 2: Run `pytest tests/agent/test_tools.py -v`; Expected: FAIL missing modules.
- [ ] Step 3: Implement deterministic rules and scoped mock tool adapters.
- [ ] Step 4: Run tests; Expected: PASS.
- [ ] Step 5: Commit `feat: add scoped agent read tools`.

### Task 2: Grounded report and validation

**Files:** Create `src/productpulse/agent/report.py`, `src/productpulse/agent/prompt_ru.txt`; Test `tests/agent/test_report.py`.

**Interfaces:** Produces `InsightProposal`; `generate_proposal(problem_id: str, context: EvidenceContext) -> InsightProposal`, `validate_proposal(proposal: InsightProposal, context: EvidenceContext) -> ValidationResult`.

- [ ] Step 1: Write tests for valid evidence, invalid cited ticket IDs, invalid JSON, unknown cause, prompt injection in ticket data and model timeout fallback.
- [ ] Step 2: Run `pytest tests/agent/test_report.py -v`; Expected: FAIL.
- [ ] Step 3: Implement strict schema + deterministic evidence validation; template fallback; optional LLM adapter behind interface.
- [ ] Step 4: Run tests; Expected: PASS.
- [ ] Step 5: Commit `feat: validate evidence-grounded agent proposals`.

### Task 3: Human review and mock integration

**Files:** Create `src/productpulse/agent/approval.py`, `src/productpulse/integrations/mock_tracker.py`; Test `tests/agent/test_approval.py`.

**Interfaces:** `submit_review(proposal_id: str) -> ReviewRequest`, `record_decision(review_id: str, decision: str, reviewer_id: str) -> ReviewDecision`, `publish_approved(proposal_id: str, idempotency_key: str) -> ExternalIssueLink`.

- [ ] Step 1: Write tests for unauthorized writes, reject path, repeated publish, existing issue reuse, missing owner and audit completeness.
- [ ] Step 2: Run `pytest tests/agent/test_approval.py -v`; Expected: FAIL.
- [ ] Step 3: Implement policy-controlled idempotent mock backend, no external network writes.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: PASS.
- [ ] Step 5: Commit `feat: add human-approved idempotent mock issue workflow`.

### Task 4: Demo UI and end-to-end contract

**Files:** Create `src/productpulse/api/main.py`, `demo/app.py`, `tests/e2e/test_demo.py`.

**Interfaces:** Expose POST /demo/import, GET /problems, GET /proposals/{id}, POST /reviews/{id}/decision in demo-only mock mode.

- [ ] Step 1: Write e2e tests for import → report → reject/approve → idempotent issue plus unauthorized access rejection.
- [ ] Step 2: Run `pytest tests/e2e/test_demo.py -v`; Expected: FAIL.
- [ ] Step 3: Implement minimal HTTP demo and presentation UI; use synthetic or permitted tickets.
- [ ] Step 4: Run `pytest tests/ -q`; Expected: PASS. Record offline backup demo.
- [ ] Step 5: Commit `feat: show reviewed support-to-product workflow`.

## Acceptance
A local mock demo demonstrates not only correct grouping and routing but refusal to merge similar unrelated incidents. It never claims to be connected to Gazprom Neft systems.
