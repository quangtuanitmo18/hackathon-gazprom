# Superpowers execution plan — Phase23

1. **RED**: tests for `lib/insight-bff.ts` strict untrusted schema, token forwarding + allowlisted GET/POST, body forgery/scope/path traversal rejection, evidence missing fail-closed, pagination beyond #50, concurrency and idempotency payload isolation.
2. **GREEN**: add BFF contract + `app/api/insights/route.ts` using encrypted Auth.js JWT, same-origin check and exact input schema, response no-store.
3. UI: `app/insights/page.tsx` and `components/insight-console.tsx`, navbar and minimal existing CSS. Explicit independent buttons/reasons; read-only ticket panels; cannot skip lead.
4. **Actual browser E2E**: extend existing Keycloak workflow after pair approval to perform trusted explicit merge in fixture (private Python transaction, no public merge route), then run `tests/insights-oidc.browser.spec.ts` reviewer denial, lead approve + separate mock publish, audited persisted one mock. Do not claim real inference.
5. Run Python, PostgreSQL, Node/Next/Chromium actual CI to GREEN, inspect full diff + self-review comment. Independent approval still required. Keep Draft and do not merge.
