# Problem Registry — Superpowers TDD Implementation Plan

**Status:** in implementation; team review/merge pending.
**Spec:** [Auditable registry spec](../specs/2026-10-30-auditable-problem-registry.md).
**Stack:** Python 3.11+, in-memory immutable Python dataclasses + existing Pydantic ticket and human annotation records, pytest.

## Task 1 — Identity, singleton lifecycle and approvals
**Files:** src/productpulse/incident/registry.py; tests/incident/test_registry.py.
- [ ] Write failing tests for repeated ticket registration, identity conflict, cross-scope link, human-independent same_incident approvals and all non-approved labels.
- [ ] Run targeted test RED, inspect module-not-found failure.
- [ ] Implement minimal register_ticket, get_problem, problem_for_ticket and approve_pair; audit append-only immutable events and operation-key replay detection.
- [ ] Run targeted GREEN and full Python CI matrix. Preserve existing 131 tests.

## Task 2 — Explicit complete-link merge
**Files:** same registry and tests.
- [ ] Write failing tests for merging two approved singleton Problems, tombstone lineage, stale revisions, idempotency replay, scope mismatch and unauthorized transitive A-B-B-C merge.
- [ ] Run targeted RED; add merge implementation; GREEN full suite. Do not convert missing links into approved edges.
- [ ] Record audit event and require caller-supplied human reviewer actor and reason (authentication is out-of-scope).

## Task 3 — Reversible split, approval invalidation and audits
**Files:** same registry and tests.
- [ ] Write failing tests for exact full partition, empty/overlapping/missing partitions, stale versions and safe split behavior.
- [ ] Implement split with immutable snapshots, tombstone lineage, revocation of crossing active approvals and history-preserving audit event.
- [ ] Run targeted RED→GREEN + complete suite on both Python versions.
- [ ] Document limitations and test evidence in README/PR; leave all external side effects disabled.

## Safety contract
No real customer data; no automatic cluster merging; no unverified same-incident claim; no persistent storage or business KPI; no merge to main without reviewer acceptance. Tests are software guarantees on small fixtures, not empirical precision.
