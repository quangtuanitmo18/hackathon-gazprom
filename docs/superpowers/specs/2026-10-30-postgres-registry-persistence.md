# PostgreSQL-Backed ProductPulse Registry — MVP Design

**Date:** 2026-10-30. **Status:** Owner-directed implementation scope; production hardening awaits review.
**Base:** tested in-memory ProblemRegistry on feat/auditable-problem-registry.
**Motivation:** make confirmed problem/approval/merge/split outcomes survive process restarts and avoid lost updates across replicas.

## Alternatives / chosen approach

1. Normalize every ticket/problem/link/operation into separate tables. Best scalable long term, but duplicates many complicated incident invariants already implemented and tested.
2. **Chosen now: transactional tenant-scoped snapshot + append-only audit table.** Serialize existing ProblemRegistry to a JSONB state row per scope; on each mutation, PostgreSQL SELECT ... FOR UPDATE locks exactly one scoped row, hydrate domain, execute existing invariant logic, commit new state + delta audit events in one SQLAlchemy Session transaction. Reliable for hackathon/demo and per-scope serialized writes; O(size of scope) JSONB re-write on every mutation, not final production architecture.
3. Event-sourcing + projection rebuild. Scalable audit but more code and replay logic than this deadline warrants.

## OSS decisions

Use **SQLAlchemy 2 ORM** / **psycopg 3** / **Alembic** instead of custom SQL clients or migration framework. FastAPI later for authenticated internal endpoints; do not build our own JWT/auth.

## Contract

- Tables: \`registry_states(scope_id PRIMARY KEY, revision INT, state JSONB, updated_at)\`; \`registry_events(id BIGSERIAL PRIMARY KEY, scope_id, seq INT, kind, actor, operation_key, occurred_at TZ, payload JSONB, UNIQUE(scope_id,seq))\`.
- \`PersistentProblemRegistry(engine).transact(scope_id, lambda registry: ...)\`: transaction begins, INSERT scoped empty row ON CONFLICT DO NOTHING, SELECT FOR UPDATE, strictly decode snapshot, execute callback synchronously, persist new state + only newly added audit records; return callback result. On exception, rollback all.
- \`read(scope_id, callback)\`: read immutable snapshot in a database transaction; no mutation persists and callback must be side-effect free. External actions forbidden inside callback.
- Per-scope API must trust scope from authenticated backend, not from untrusted ticket text. DB state must not contain raw company tickets without prior redaction. **Demo uses synthetic only.**
- All human approvals still require two independent signed-in reviewers; persistence is not proof of reviewer authentication. Do NOT expose approval/merge/split over public unauthenticated HTTP.
- Replay idempotency key, scoped IDs, post-split approval revocation timestamp, audit chronology and tombstones must survive reload. Reject corrupt or unsupported state schema. Preserve source-scoped IDs and binary-safe serialization.
- State mutation can only occur inside transaction; a PostgreSQL \`FOR UPDATE\` row lock serializes concurrent operations in same scope. Different scopes independent; use actual Postgres for locking tests.
- Immutable database audit: app role only has INSERT/SELECT, or DB privileges/triggers later; prototype ORM does not itself prevent SQL UPDATE/DELETE by a privileged user. Logs are application append-only, not tamper-proof/WORM.

## Acceptance

- Snapshot round trip after register → independently approved pair → merge → split → restart: identical active Problem snapshots, audit and revoked approvals. Old idempotency key never restores revoked approval, new post-split reviewer data required.
- Transaction abort rolls back snapshot and audit together.
- Concurrent operations under same scope do not lose tickets, tested with two connections against real PostgreSQL service in GitHub Actions.
- Distinct scopes remain isolated in read/write.
- Alembic migration is applied from an empty DB; no \`Base.metadata.create_all\` in production path.
- Existing full test suite on Python 3.11 and 3.13 remains green.
- Does not claim a production API, UI, distributed outbox, or measured Gazprom Neft metrics at this point.

## Next phase

Add a narrowly scoped FastAPI read/internal ingestion facade with real auth; frontend Next.js + shadcn/ui/TanStack Query/Recharts; distinct Human Review UI with authenticated identities and evidence, then LangGraph agent. Any enterprise deployment requires row-level scope policies, encryption/backups, rights audit, tenant quota, data retention and normalized tables if scale demands.
