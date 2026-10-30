# ProductPulse Problem Dashboard — Design (2026-10-30)

**Status:** Owner has requested implementation and explicit real-world verification. The following is a bounded demo design, not a production security certification.

## Current contracts
Stacked on feat/internal-incident-api. Existing FastAPI exposes token-protected `GET /internal/v1/problems`, `GET /internal/v1/problems/{id}`, `GET /internal/v1/audit` and `POST /internal/v1/tickets`. PostgreSQL 16 persists Problem snapshots. The existing state is *human-approved only*, and the API exposes **no** pair approval/merge/split or Jira write.

## Options
- **Selected:** Next.js App Router server-rendered dashboard + Lucide icons + TanStack Table; reuse Next.js Server Components instead of custom frontend networking/state orchestration. Separate server-side BFF calls existing FastAPI. A local-demo HTTP Basic Auth boundary protects all routes, using env credentials; replace with OIDC for any actual deployment.
- Streamlit: fastest simple proof but harder to deliver polished, navigable review UI and proper BFF authentication architecture.
- Fork Rereflect: demo shell operates but its feedback schema loses incident provenance and approval details; would force deep upstream customization.

## Scope
1. Russian-first Problem Inbox: real count of active Problems and registered tickets (from source keys), searchable sortable table with ID, revision, ticket count and source scope, no invented KPIs.
2. Problem detail: scoped Problem from API; show associated **source-scoped ticket keys** but **do not claim real ticket body/evidence/impact**, since API does not provide them. Explain candidate vs confirmed distinction.
3. Audit view: real append-only events from API with names, timestamps and operation ids. No raw customer bodies.
4. Explicit unavailable/empty state when backend unreachable or no data. Never fabricate demo data in UI.
5. In demo-only auth, proxy enforces Basic username/password on navigation and route requests; backend internal token **never sent to browser**. Login credentials are server environment only, minimum length, protected by HTTPS for network deployment. This is NOT multi-user login/RBAC.

## Acceptance tests
- Unit: no credentials ⇒ unauthorized; valid & invalid Basic; malformed and Unicode-safe; method never forwards FastAPI secret to client; URL paths are fixed/encoded, no SSRF via arbitrary URL. API non-200 fails with controlled error; empty list remains empty.
- CI: npm unit tests + TypeScript + Next build; actual PostgreSQL 16 + Alembic + running FastAPI + running Next standalone; curl with and without credentials; seed one synthetic Russian ticket and verify it appears as Problem ID; check detail and audit pages; assert no service token in public HTML.
- No claim browser navigation or human OIDC until Playwright runs.
- Source data and privileges: exact tenant scope owned by server; no client tenant argument or public writes.

## OSS dependencies
Next.js 16 + React 19; @tanstack/react-table for UI sorting/search; lucide-react for icons; TypeScript. Use native CSS to minimize dependency coupling; do not write a custom table state library or router.

## Delivery
Code and reproducible CI in isolated PR stacked on #14. Keep draft, do not merge to main. Next step after demo: human-authenticated review UI and evidence API, then time-series trends and LangGraph.
