# Keycloak Auth.js Review Console — Implementation Plan

1. **Evidence API (TDD):** tests/api/test_review_evidence.py RED; implement scoped `GET /internal/v1/review-tickets` and optional ticket-key detail guarded by service + OIDC; no tenant-switching. Real PostgreSQL CI GREEN.
2. **Auth.js OIDC BFF (TDD):** add `next-auth@beta` Keycloak provider and `apps/web/auth.ts`; crypto-protected httpOnly JWT cookie stores access token (never session). Tests for request authorization origin, expired token, sensitive field non-disclosure and backend URL safety; implement `apps/web/lib/review-bff.ts` and `apps/web/app/api/review/route.ts`. Keep Basic mode read-only.
3. **Reviewer Console UI:** add `/review` with ticket evidence, pair selection, 4-class labels, independent review, third-lead approval. Reuse existing React, Lucide and TypeScript. No links to unimplemented merge.
4. **Keycloak Integration:** local import realm and accounts for CI with no secrets, test SSO OAuth state/PKCE + claims. Strict backend issuer HTTPS requirement, do not silently turn off security. Separate real-IdP runtime status from build status. Verify unchanged existing PostgreSQL/Next/Chromium.
5. **Finalize:** log RED/GREEN run IDs, exact limits, draft stacked PR only. No merge without explicit user approval.
