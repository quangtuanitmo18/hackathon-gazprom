# ProductPulse: Keycloak + Auth.js Reviewer Console (experimental)

This is an **opt-in OIDC review UI** stacked on PR #16. It never treats the legacy demo shared Basic Auth password as a human reviewer identity.

## Existing OSS reused

- **Keycloak** as external IdP and role/tenant issuer, with OIDC Authorization Code and TLS, no homemade password database.
- **Auth.js v5** for Next.js sessions/login, OAuth state/PKCE, encrypted HttpOnly session cookie, Keycloak provider.
- **PyJWT[crypto]** on FastAPI for independently verifying OIDC access token signature, issuer, audience, tenant and roles.
- Existing FastAPI/SQLAlchemy/PostgreSQL 16 registry with single-transaction pair reviews and independent lead approval.
- Playwright Chromium for real browser login, reviewer and lead flows.

## Configuration (OIDC mode only)

First, configure Keycloak's confidential web client with redirect URI
\`https://YOUR_FRONTEND/api/auth/callback/keycloak\` and OIDC access-token claims:

- \`aud\` must include \`productpulse-review-api\`;
- \`tenant_scope\` must match \`PRODUCTPULSE_SCOPE_ID\`;
- \`roles\` must be a string array, not a forged browser header, with \`productpulse_reviewer\` and/or \`productpulse_review_lead\`;
- two different reviewer accounts plus a third lead account must be registered independently.

On backend, configure \`PRODUCTPULSE_OIDC_ISSUER\`, \`PRODUCTPULSE_OIDC_AUDIENCE\`, \`PRODUCTPULSE_OIDC_JWKS_URL\`, \`DATABASE_URL\`, \`PRODUCTPULSE_INTERNAL_TOKEN\`, and \`PRODUCTPULSE_SCOPE_ID\`.

On Next.js server, configure:

\`\`\`sh
PRODUCTPULSE_AUTH_MODE=oidc
PRODUCTPULSE_BACKEND_URL=http://127.0.0.1:8000
PRODUCTPULSE_INTERNAL_TOKEN=<SAME_BACKEND_INTERNAL_SECRET>
AUTH_SECRET=<RANDOM_32PLUS_BYTES>
AUTH_KEYCLOAK_ISSUER=https://YOUR_KEYCLOAK/realms/productpulse
AUTH_KEYCLOAK_ID=productpulse-web
AUTH_KEYCLOAK_SECRET=<KEYCLOAK_CLIENT_SECRET>
PRODUCTPULSE_PUBLIC_ORIGIN=https://YOUR_FRONTEND
AUTH_URL=https://YOUR_FRONTEND
\`\`\`

All secrets must come from a secret manager or uncommitted \`.env.local\`; never use \`NEXT_PUBLIC_*\` names for them. All issuer and JWKS traffic must verify certificates, and the UI must run behind HTTPS. **Keycloak start-dev is for isolated local testing only**, not production.

## End-to-end review experience

1. Login using individual Keycloak credential on \`/login\`.
2. Open \`/review\`; only source-scoped evidence available to signed-in reviewer appears (max 50 tickets per page in current API).
3. Independently compare the ticket text labelled \`body_redacted\`, product/component/version and error codes. The application does **not** prove that the text has been scrubbed correctly; pipeline must enforce PII/secret redaction before actual customer data.
4. Select the pair and one of \`same_incident\`, \`related_topic\`, \`different_incident\`, \`uncertain\`; enter a rationale.
5. Two **distinct OIDC subjects** must agree on \`same_incident\` before \`ready_for_lead\`.
6. A third \`productpulse_review_lead\` can approve it. **Approval does not merge Problems, does not create Jira issue, and does not imply model accuracy.** Other labels cannot be approved as incident duplicates.
7. Any Basic Auth demo session is rejected by \`/api/review\` even if the user knows the shared demo password.

## Security boundaries

Auth.js stores the access token in an encrypted, HttpOnly JWT cookie but the public \`/api/auth/session\` callback returns only harmless session metadata. The Next.js \`/api/review\` route obtains the encrypted cookie server-side and forwards the OAuth token plus private internal service token only to the trusted upstream FastAPI. Backend verifies both.

POST writes require exact configured Origin; request body cannot choose reviewer identity, tenant or role. FastAPI verifies the JWT itself; a user-modified browser request is insufficient to impersonate another reviewer.

**Not production-ready:** OAuth refresh/revocation not implemented (expired access token requires re-login), Basic demo still available if explicitly selected, Keycloak authorization/role mapping must be provisioned and audited, rate limiting/CSP/CSRF/session rotation/PII pipeline and full security assessment outstanding. Current UI has manual pair selection, not a proven same-incident candidate ranking system.

## Reproducible CI

- Existing Python/PostgreSQL CI proves review invariants and JWT verification with synthetic RSA keys.
- \`.github/workflows/keycloak-review-e2e.yml\` provisions official pinned Keycloak image, **TLS with an ephemeral self-signed localhost CA**, a synthetic 3-account realm, PostgreSQL 16, FastAPI and Next.js; Playwright tests three separate browser sessions and verifies OIDC user/token isolation.
- \`npm ci\` uses committed lockfile. A live Keycloak CI PASS is necessary before claiming the OIDC experience works. Local self-signed test TLS is not an acceptable production TLS setup.

The reviewer endpoint currently lists a bounded page of registered redacted tickets for **manual** pair selection; it is **not** the retrieval/candidate-ranking engine and should not be used to report recall@k or precision without separate gold labels.
