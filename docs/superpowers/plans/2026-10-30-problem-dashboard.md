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
- [x] RED tests in `apps/web/tests/auth.test.ts` and `apps/web/tests/api.test.ts`: malformed/absent/wrong credentials, upstream 503, fixed URL paths, token forwarding only to FastAPI.
- [x] GREEN `apps/web/lib/auth.ts`, `apps/web/lib/api.ts`, `apps/web/proxy.ts` and `apps/web/package.json`; run npm unit tests.
- [x] CI compile/build, no browser tokens.

## Task 2: Real dashboard pages
- [x] Add `apps/web/app/page.tsx`, `apps/web/app/problems/[id]/page.tsx`, `apps/web/app/audit/page.tsx`, `apps/web/components/problem-table.tsx`, CSS and layout. Use TanStack Table, Lucide and Russian copy.
- [x] Run typecheck + Next build.
- [x] Ensure non-fictional empty/error states and no render of raw ticket text.

## Task 3: End-to-end smoke
- [x] Add workflow `.github/workflows/dashboard-smoke.yml` with Postgres 16 service, Python installation/Alembic migration, Uvicorn startup, Node npm install + test + build and Next startup, seed synthetic ticket via localhost API, curl login protection and real HTML assertions.
- [x] GREEN in Actions and document exact run IDs (not just "should work").
- [x] Log limitations: demo Basic Auth, no OIDC, no reviewer UI, no real Russian data, no browser interaction unless Playwright is exercised.

## Reviewer focus
- Exposing service-to-service token in hydrated HTML or Next client bundles.
- Unauthenticated access to pages, route handlers and static secret-bearing data.
- Treating backend down as zero Problem count.
- Unsafely using arbitrary Problem ID to make external HTTP requests.
- Confusing “registered ticket” singleton with verified same-incident.

## Execution ledger (verified 2026-10-30)

- **RED:** [GitHub Actions 41052730675](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41052730675) failed Node tests with missing `lib/auth` and `lib/api` modules; new tests preceded implementation.
- **GREEN Stage 1:** [41053227352](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41053227352) passed 11 Node unit tests, TypeScript, Next.js production build and real Postgres16 → FastAPI → Next.js HTTP smoke: 401 no/wrong Basic, HTML seeded Problem, detail and audit, token non-disclosure.
- **Browser Stage:** [41053577358](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41053577358) passed 3 full Chromium Playwright tests: search/filter + detail navigation, audit and no token leakage.
- **Reproducibility:** generated `apps/web/package-lock.json` with GitHub Actions [41053695961](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41053695961) using `npm install --package-lock-only --ignore-scripts`; changed build to `npm ci`.
- **FINAL fresh verification:** [41053805097](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41053805097) succeeded from clean checkout: **11 Node tests, Next.js production build, real PostgreSQL/FastAPI HTTP smoke, 3 Playwright Chromium tests**. No service token/password in rendered HTML. Test environment uses synthetic ticket only. Every external program was executed on isolated GitHub-hosted runner, not a production system.
- **Limitations and architectural ruling:** Read-only UI; no human reviewer identity, pair adjudication UI, real customer evidence, persistent session OIDC/RBAC or Jira. Basic Auth is a TLS-only local-demo gate and must NOT be represented as production authentication. Backend token lives server side; client cannot change tenant scope.
- **Merge:** PR #15 is a draft stacked on #14. Do not merge until upstream PR chain is reviewed and rebased in order.

### UX honesty
- No invented trend or root-cause metrics. Only counts and source-scoped Problem metadata from actual API.
- When backend is unavailable, show a failure panel instead of false zero.
- Inaccessible/missing problem detail gets 404 or explicit failed-upstream state.
