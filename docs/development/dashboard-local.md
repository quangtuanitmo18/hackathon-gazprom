# ProductPulse Russian-first Problem Dashboard (local demo)

**Status:** Tested with real PostgreSQL 16 + FastAPI + Next.js 16 + Chromium. **NOT public production authorization.**

## Reuse instead of reinventing
- Next.js App Router / React Server Components: server-side rendering + routing / private BFF
- TanStack Table: query, table sorting, filtering
- Lucide: icons
- Zod: validation of backend responses
- Playwright: actual Chromium UI tests
- PostgreSQL + Alembic + SQLAlchemy + FastAPI backend from stacked PR #14

## Prerequisite
Follow [Backend/PostgreSQL setup](internal-api-local.md), start Postgres and Alembic, then Uvicorn on 127.0.0.1:8000. Set `PRODUCTPULSE_SCOPE_ID`, `PRODUCTPULSE_INTERNAL_TOKEN` (generated securely) in backend process.

## Run frontend

```bash
cd apps/web
npm ci
cp .env.example .env.local
# edit .env.local: PRODUCTPULSE_INTERNAL_TOKEN MUST equal the backend's secret
# set DASHBOARD_USERNAME and DASHBOARD_PASSWORD (at least 16 characters)
npm run test
npm run typecheck
npm run build
npm run dev
```

Visit http://127.0.0.1:3000 and enter your configured Basic Auth credentials. **Use localhost only** unless deployed behind mandatory HTTPS and an authenticated gateway. Do not place `PRODUCTPULSE_INTERNAL_TOKEN` in any `NEXT_PUBLIC_*` variable or expose it to JavaScript/browser storage.

## Reproduce proven integrated smoke

[GitHub Actions](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41053805097) starts PostgreSQL 16, migrates schema, launches FastAPI, ingests one **synthetic** Russian ticket and starts Next.js production server after `npm ci`, tests, typechecking and build. It then checks:

1. Unauthorized and incorrect Basic credentials yield 401.
2. Authenticated Dashboard shows the **actual** created Problem ID.
3. Detail page shows its source-scoped ticket key.
4. Audit page shows registration events persisted in PostgreSQL.
5. The backend internal token and dashboard password do not occur in rendered HTML.
6. Playwright runs 3 Chromium tests covering filtering, navigation, audit and token secrecy.

## Not production ready
- Basic Auth is **demo-only** and NOT per-user RBAC, 2FA, SSO/OIDC, session expiry or reviewer identity verification.
- Backend service token remains server-only, but reverse proxy/firewall, HTTPS/TLS, CSRF policy, security headers, rate limits and vulnerability scanning still need review.
- The UI is deliberately read-only; verified review evidence, incident severity, language-specific model quality, real issue tracker integration and trend data are not available in the existing API.
- Real company ticket texts MUST be sanitized and scoped before ingestion. Do not expose real customer data on public environments.
- Existing PostgreSQL JSONB-snapshot design is suitable for this prototype; normalize for scale and add hardened audit controls later.

## Open-source usage
Next.js, React, TanStack, Lucide, Zod and Playwright are used as libraries; no deep Rereflect/ITARS fork, no invented custom router/table framework.
