# Problem Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan, test-first and commit task by task.

**Goal:** Ship real read-only Russian-first dashboard fed by existing persisted internal FastAPI.
**Architecture:** Next.js Server Components fetch via private server-only BFF client, Basic Auth proxy for demo-only boundary. No browser access to backend token.
**Tech Stack:** Next.js16, React19, TanStack Table, Lucide, TypeScript, Node test runner, FastAPI, PostgreSQL16.
**Spec:** [design](../specs/2026-10-30-problem-dashboard.md).

## Global constraints
- No static/fake totals, no Jira or review mutation actions, no browser credential for ProductPulse backend.
- On API failure show outage/error not “0”.
- Credentials only from env; no default credentials for production; Basic Auth strictly demo, no RBAC claims.
- HTML must escape text through JSX; server side fetch no-store.

## Task 1: BFF security and API contracts (TDD)
- [ ] RED tests in `apps/web/tests/auth.test.ts` and `apps/web/tests/api.test.ts`: malformed/absent/wrong credentials, upstream 503, fixed URL paths, token forwarding only to FastAPI.
- [ ] GREEN `apps/web/lib/auth.ts`, `apps/web/lib/api.ts`, `apps/web/proxy.ts` and `apps/web/package.json`; run npm unit tests.
- [ ] CI compile/build, no browser tokens.

## Task 2: Real dashboard pages
- [ ] Add `apps/web/app/page.tsx`, `apps/web/app/problems/[id]/page.tsx`, `apps/web/app/audit/page.tsx`, `apps/web/components/problem-table.tsx`, CSS and layout. Use TanStack Table, Lucide and Russian copy.
- [ ] Run typecheck + Next build.
- [ ] Ensure non-fictional empty/error states and no render of raw ticket text.

## Task 3: End-to-end smoke
- [ ] Add workflow `.github/workflows/dashboard-smoke.yml` with Postgres 16 service, Python installation/Alembic migration, Uvicorn startup, Node npm install + test + build and Next startup, seed synthetic ticket via localhost API, curl login protection and real HTML assertions.
- [ ] GREEN in Actions and document exact run IDs (not just "should work").
- [ ] Log limitations: demo Basic Auth, no OIDC, no reviewer UI, no real Russian data, no browser interaction unless Playwright is exercised.

## Reviewer focus
- Exposing service-to-service token in hydrated HTML or Next client bundles.
- Unauthenticated access to pages, route handlers and static secret-bearing data.
- Treating backend down as zero Problem count.
- Unsafely using arbitrary Problem ID to make external HTTP requests.
- Confusing “registered ticket” singleton with verified same-incident.
