# Problem Registry — Superpowers TDD Implementation Plan

**Status:** IMPLEMENTED AND VERIFIED 2026-10-30; team review/merge pending.
**Spec:** [Auditable registry spec](../specs/2026-10-30-auditable-problem-registry.md).
**Stack:** Python 3.11+, in-memory immutable Python dataclasses + existing Pydantic ticket and human annotation records, pytest.

## Task 1 — Identity, singleton lifecycle and approvals
**Files:** src/productpulse/incident/registry.py; tests/incident/test_registry.py.
- [x] Write failing tests for repeated ticket registration, identity conflict, cross-scope link, human-independent same_incident approvals and all non-approved labels.
- [x] Run targeted test RED, inspect module-not-found failure.
- [x] Implement minimal register_ticket, get_problem, problem_for_ticket and approve_pair; audit append-only immutable events and operation-key replay detection.
- [x] Run targeted GREEN and full Python CI matrix. Preserve existing 131 tests.

## Task 2 — Explicit complete-link merge
**Files:** same registry and tests.
- [x] Write failing tests for merging two approved singleton Problems, tombstone lineage, stale revisions, idempotency replay, scope mismatch and unauthorized transitive A-B-B-C merge.
- [x] Run targeted RED; add merge implementation; GREEN full suite. Do not convert missing links into approved edges.
- [x] Record audit event and require caller-supplied human reviewer actor and reason (authentication is out-of-scope).

## Task 3 — Reversible split, approval invalidation and audits
**Files:** same registry and tests.
- [x] Write failing tests for exact full partition, empty/overlapping/missing partitions, stale versions and safe split behavior.
- [x] Implement split with immutable snapshots, tombstone lineage, revocation of crossing active approvals and history-preserving audit event.
- [x] Run targeted RED→GREEN + complete suite on both Python versions.
- [x] Document limitations and test evidence in README/PR; leave all external side effects disabled.

## Safety contract
No real customer data; no automatic cluster merging; no unverified same-incident claim; no persistent storage or business KPI; no merge to main without reviewer acceptance. Tests are software guarantees on small fixtures, not empirical precision.


## Execution ledger / verified evidence

- Task 1 RED: [GitHub Actions 41043829508](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41043829508) failed with ModuleNotFoundError: productpulse.incident.registry. GREEN: [41043970519](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41043970519), 3.11 and 3.13 jobs succeeded.
- Task 2 RED: [41044077236](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41044077236) before merge method; GREEN: [41044168935](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41044168935).
- Task 3 RED: [41044284649](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41044284649) before split method; GREEN: [41044381930](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41044381930): 165 tests passed on Python 3.11, Python 3.13 CI job also succeeded.
- **Tested:** source ID namespace collision, duplicate retry, content conflict, cross-scope rejection, two-person adjudicated positives, rejection of disputed/related-topic labels, idempotent keys, complete-link merge with explicit human actor, optimistic revision conflict, old ID tombstone, audited split and revocation of cross-partition approvals, safe re-approval and re-merge.
- **Ruling:** complete-link evidence for every cross-member pair, not connected components or similarity union. Trade-off: O(m*n) required approvals and high review burden; this is conservative MVP policy, measure review effort before scaling.
- **Ruling:** an in-process registry with immutable snapshots and append-only in-memory audit is valid for isolated domain tests; **not durable or concurrency safe across replicas**. Real database transactions, unique constraints, auth/RBAC, tenant isolation and event replay still pending.
- **Ruling:** split revokes active approvals across partitions and logs revocation; leaves original approval events untouched. Original merged-away IDs remain tombstones; split may create new IDs rather than restoring pre-merge ID exactly.
- **No claim:** no production persistence, Jira integration, model F1, company effectiveness, or measured cost savings. Still draft; no merge to main.
