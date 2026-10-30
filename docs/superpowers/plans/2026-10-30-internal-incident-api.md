# Internal Incident API — Superpowers Implementation Plan

> REQUIRED: superpowers:executing-plans and test-driven-development. RED → GREEN → all tests, logs before claims.

**Goal:** minimal internal HTTP facade for PostgreSQL Problem Registry.
**Architecture:** FastAPI app factory injects persistent repository and server-owned scope. Shared internal token from environment; no user-auth, no public reviewer writes.
**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL16, httpx TestClient, pytest.
**Spec:** [design](../specs/2026-10-30-internal-incident-api.md).

## Task 1: HTTP security + ingestion/read
**Files:** tests/api/test_internal_api.py; src/productpulse/api/app.py; src/productpulse/api/__init__.py; pyproject.toml; .github/workflows/postgres-registry.yml.
- [x] RED: TestClient requires secret for data endpoints, no client-scope override, one synthetic ticket POST persists, GET list/detail/audit, 404 unknown, 422 extra fields, idempotent repeated POST and no reviewer write routes.
- [x] Verify RED on PostgreSQL CI.
- [x] Add OSS FastAPI dependency and versioned typed routes, compare_digest token; validate scope/token in factory before starting.
- [x] GREEN: full test suite and Postgres tests in Python 3.11, 3.13; no printed secret values.

## Task 2: Deployment instructions + review
- [x] Add factory-based uvicorn command and minimal local DB / Alembic steps. Explain internal token is not a substitute for OIDC/RBAC and must be restricted by firewall.
- [x] Capture run IDs in ledger and PR, draft only, stacked on PostgreSQL PR.

## Verified execution ledger (2026-10-30)

- RED: [PostgreSQL CI 41051285099](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41051285099): 184 existing tests passed, new API tests failed with `ModuleNotFoundError: productpulse.api` as designed.
- GREEN: [PostgreSQL CI 41051477066](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41051477066) / [41051480846](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41051480846): **196 tests passed** on Python 3.11 and 3.13; includes real database and FastAPI TestClient.
- Verified after local run-guide commit: [41051641221](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41051641221), 3.11 and 3.13 success.
- Ruling: server-side environment binds tenant scope; `X-Internal-Token` remains server-to-server credential. No JS/browser direct call with this token. Human review/merge/split endpoints intentionally unavailable until OIDC and RBAC.
- Ruling: use FastAPI+httpx+Uvicorn instead of custom HTTP framework or hand-written OpenAPI. Database via SQLAlchemy adapter and Alembic, no raw SQL framework.
- Next: choose dashboard OSS libraries (Streamlit for quickest internal proof; Next.js + shadcn/ui + TanStack Query if polished final), implement trusted BFF and user auth before opening on public internet.
- Review: draft PR #14, stacked on #13, **not merged into main**.
