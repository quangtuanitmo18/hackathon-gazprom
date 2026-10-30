# Internal Incident API — Superpowers Implementation Plan

> REQUIRED: superpowers:executing-plans and test-driven-development. RED → GREEN → all tests, logs before claims.

**Goal:** minimal internal HTTP facade for PostgreSQL Problem Registry.
**Architecture:** FastAPI app factory injects persistent repository and server-owned scope. Shared internal token from environment; no user-auth, no public reviewer writes.
**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL16, httpx TestClient, pytest.
**Spec:** [design](../specs/2026-10-30-internal-incident-api.md).

## Task 1: HTTP security + ingestion/read
**Files:** tests/api/test_internal_api.py; src/productpulse/api/app.py; src/productpulse/api/__init__.py; pyproject.toml; .github/workflows/postgres-registry.yml.
- [ ] RED: TestClient requires secret for data endpoints, no client-scope override, one synthetic ticket POST persists, GET list/detail/audit, 404 unknown, 422 extra fields, idempotent repeated POST and no reviewer write routes.
- [ ] Verify RED on PostgreSQL CI.
- [ ] Add OSS FastAPI dependency and versioned typed routes, compare_digest token; validate scope/token in factory before starting.
- [ ] GREEN: full test suite and Postgres tests in Python 3.11, 3.13; no printed secret values.

## Task 2: Deployment instructions + review
- [ ] Add factory-based uvicorn command and minimal local DB / Alembic steps. Explain internal token is not a substitute for OIDC/RBAC and must be restricted by firewall.
- [ ] Capture run IDs in ledger and PR, draft only, stacked on PostgreSQL PR.
