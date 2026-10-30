# PostgreSQL Problem Registry Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Follow RED → GREEN, full regression and CI verification.

**Goal:** Preserve current incident domain invariants across process restarts and concurrent writes using proven OSS components.
**Architecture:** JSONB snapshot per scope plus append-only audit in PostgreSQL. SQLAlchemy transaction and row lock protect a reconstructed in-memory registry. The snapshot codec is explicit and versioned.
**Tech Stack:** SQLAlchemy 2, psycopg[binary] 3, Alembic, PostgreSQL 16, Pydantic 2, pytest.
**Spec:** [design](../specs/2026-10-30-postgres-registry-persistence.md).

## Global constraints

No external Jira/YouTrack writes; raw user data never committed. Keep `ProblemRegistry` existing behavior. No unauthenticated review mutations; no SQLAlchemy `create_all` in main app. Scope always trusted/authenticated at future API layer. Record limitations of JSONB snapshot O(N).

## Review focus

- Pair approvals after a split use *fresh* reviewer evidence, not a new key applied to stale reviews.
- Idempotency results round-trip typed Pydantic/dataclass values, not raw dicts.
- Concurrent first registration in same empty scope under PostgreSQL unique index does not lose data.
- Audit rows are committed in same transaction and sequential, no duplicates on retry.
- Invalid state version/corrupted snapshot fails closed; cross-tenant lookup cannot leak other scope.

### Task 1 — Versioned state codec for existing domain

**Files:** `src/productpulse/incident/registry.py`, `tests/incident/test_registry_snapshot.py`.

- [x] Write pytest tests for empty/complex roundtrip, approval idempotency after restore, post-split revocation survives reload, audit ordering, unknown version/corruption rejection.
- [x] Verify RED in CI (missing `to_state`/`from_state`), record run.
- [x] Add `registry.to_state() -> dict` and `ProblemRegistry.from_state(payload) -> ProblemRegistry` explicit typed encoding/decoding, no pickle.
- [x] Verify GREEN and entire suite, commit.

### Task 2 — PostgreSQL transaction adapter and migration

**Files:** `src/productpulse/storage/models.py`, `src/productpulse/storage/repository.py`, `src/productpulse/storage/__init__.py`, `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_registry.py`, `tests/storage/test_postgres_registry.py`, `pyproject.toml`, `.github/workflows/postgres-registry.yml`.

- [x] RED integration tests against PostgreSQL 16 for empty/multiple scopes, full lifecycle and restart, idempotency after restart, rollback snapshot+audit, two competing transactions same tenant, old-key replay.
- [x] Confirm RED because repository implementation absent.
- [x] Implement `PersistentProblemRegistry(engine).transact(scope_id, fn)`, `.read(scope_id, fn)`, `.audit(scope_id)`; SQLAlchemy transaction with `INSERT ON CONFLICT DO NOTHING`, row `FOR UPDATE`, mutation+audit in single commit.
- [x] Implement reviewed Alembic migration and workflow Postgres service. Require migration executed before tests, no create_all shortcut.
- [x] Confirm GREEN on PostgreSQL real service plus full suite and Python matrix.

### Task 3 — Documentation, scope and safety

- [x] Document production gaps, setup commands and exact run IDs.
- [x] Update this ledger with independently inspected CI evidence.
- [x] Request PR review, remain draft and stacked on #11.

## Important out-of-scope

Full enterprise persistence normalization, JWT, RBAC, frontend/UI, LangGraph and exact human accuracy evaluation deferred. Never present passing tests as proof of production security.

## Verified execution ledger (2026-10-30)

- Task 1 RED: [41050142023](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41050142023) (snapshot API absent). First GREEN exposed an incorrect test replay payload timestamp; corrected test to distinguish revoked approval from idempotency collision. GREEN: [41050421296](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41050421296).
- Task 2 first CI blocker was a GitHub service Docker health flag quoting error (`-U` parsed by Docker), not a PostgreSQL model bug; corrected to single-token `--health-cmd=pg_isready`.
- Task 2 RED: [41050855678](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41050855678), Alembic migration working but repository module absent. GREEN: [41050922318](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41050922318), **184 tests passed on Python 3.11 and 3.13 against PostgreSQL 16**, including concurrent scope writes and rollback.
- SQLite intentionally not used for locking proof. Alembic upgrade ran against a clean PostgreSQL service before the tests.
- Ruling: per-scope JSONB snapshot with `SELECT FOR UPDATE` is acceptable hackathon MVP and leverages tested domain invariants. It is O(tenant state) per write, so normalize members and audit/event partitions before high-volume production.
- Ruling: audit is application append-only, not database-tamperproof. Auth/RBAC/OIDC and human approval HTTP routes remain future work. No claim of security certification or company data accuracy.
- Review: draft PR #13, stacked on #11, **not merged into main**.
