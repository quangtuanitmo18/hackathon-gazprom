# Keycloak + Auth.js Review Console — Design

**Date:** 2026-10-30, scoped continuation of approved reviewer workflow in #16.
**Mode:** New `PRODUCTPULSE_AUTH_MODE=oidc` opt-in; legacy Basic demo remains read-only. **Never** infer human identity from legacy Basic Auth.

## Minimum viable user journey
- Keycloak OIDC login via Auth.js (Next.js 16 App Router); use the Authorization Code flow and OIDC Discovery.
- Server-only Auth.js encrypted JWT retains Keycloak **access token**; browser session exposes only name/email and no token, refresh token or backend service secret.
- All browser reviewer writes use same-origin Next.js `/api/review` server route (BFF), requiring a valid Auth.js session, OAuth access token, Origin/Host checks, nonce/idempotency key. BFF forwards `X-Internal-Token` from server configuration and `Authorization: Bearer <Keycloak access token>` to FastAPI.
- FastAPI validates **both** BFF's internal token and Keycloak access token cryptographically, role and tenant. Existing third-party lead approval independent of two reviewers. Don't expose `merge` from UI.
- A read-only review candidate/evidence endpoint in FastAPI returns bounded synthetic or properly redacted ticket bodies and scope-bound source identities; it doesn't create gold labels and never treats same product or same topic as confirmed same-incident. Manual pair selection can start with any two registered tickets of same scope.
- Review UI shows two tickets side-by-side, redacted title/body, product/component/version/error codes, two distinct reviewers' status (no peer's vote prior to submission to avoid anchoring), decision/rationale, independent lead approval. No automated same-incident claim.
- UI fails closed when Auth.js or Keycloak missing; Basic mode must never enable review writes.

## Security decisions
1. NextAuth v5 `next-auth@beta` provider Keycloak. Auth.js proxy for page access only OIDC mode, route handlers also authenticate close to data.
2. JWT stored in Auth.js `jwt` callback but **not copied** to `session` callback. `next-auth/jwt.getToken()` on server route obtains access token from encrypted HttpOnly cookie. If expired, reject with login_required; refresh token rotation deferred to future release. Identity proof remains in FastAPI validator.
3. Same-origin POST via browsers; Next.js BFF denies cross-Origin request and requires Content-Type JSON. HTTP Basic auth cannot access BFF.
4. Original `PRODUCTPULSE_INTERNAL_TOKEN` stays server-side; no CORS wildcard, no arbitrary URLs or tenant IDs in client payload.
5. No production claims without an actual Keycloak server, at least two independent accounts and an end-to-end browser test. If local Docker/HTTP Keycloak clashes with strict HTTPS backend security, use a TLS reverse proxy or explicitly mark the IdP integration unverified; never weaken production issuer HTTPS acceptance.

## OSS chosen
Keycloak, Auth.js, FastAPI, PyJWT, PostgreSQL, Zod, TanStack Table, Playwright. No bespoke login system or home-grown JWT issuer.

## Verification gates
- RED/GREEN backend source-scoped redacted evidence API: require both tokens, correct scopes; no raw admin/personal data; bounded list and no arbitrary fields.
- RED/GREEN BFF tests: unauthenticated/expired/CSRF/Basic-only deny, private token only upstream, validated data, no arbitrary redirect/SSRF.
- `npm ci`/TypeScript/Next production build + existing Basic demo Chromium tests remain green.
- Real Keycloak CI and three-browser-account reviewer e2e attempted in separated workflow; only claim a pass if observed. Do not weaken HTTPS verification to pass local tests.

## Trade-off
This is a hackathon review console increment. OIDC backend contract is secure-by-default, while full production needs network TLS, token rotation, CSRF hardening, session-revocation, approved user management and evidence privacy review.
