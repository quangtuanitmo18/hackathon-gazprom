# Phase 22 — Superpowers TDD plan

**Design:** [Evidence-grounded Insight Proposal](../specs/2026-10-30-evidence-grounded-insight-proposal-design.md).

1. RED unit `tests/agent/test_insight_proposals.py`: only active grouped Problems, exact evidence allowlist, no unknown product/owner/root cause; strict model adapter accepts only allowed action enum with matching keys, ignores injection/hallucination, fallback on invalid JSON; idempotent proposal identity/digest.
2. GREEN `src/productpulse/agent/proposals.py`: pure `build_proposal`, optional `model_output` validated by Pydantic, audit-safe output. Add read-only registry `insight_inputs()`.
3. RED integration/domain `tests/agent/test_proposal_approval.py` + `tests/api/test_insight_routes.py`: unauthenticated/wrong-tenant/role refusal, approved pair without merge cannot generate, merge approved 2 tickets emits draft, approval audit transaction, separate mock publish, replay idempotency, conflict reused operation key, revision/split invalidation and restart persistence.
4. GREEN domain state: `ProposalApproval`, `MockIssue` stored/reloaded via Registry versioned JSONB snapshot, operations audit and state validation; API new GET/POST endpoints bound to trusted scope and Keycloak reviewer/lead roles.
5. Actual GitHub Actions Python 3.11/3.13 + PostgreSQL 16 CI RED→GREEN. No synthetic outcome claims. Inspect PR patch and perform self-review COMMENT; keep draft stacked on #21, no merge.

**Evidence contract:** only stable source-scoped evidence IDs. `ModelOutput` can choose action enum, not title/body/root cause/owner; actual LLM HTTP provider not wired in this slice.
