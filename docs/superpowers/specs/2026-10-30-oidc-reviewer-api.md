# Authenticated Reviewer Workflow — Design (2026-10-30)

**Status:** Backend/API implementation increment selected under the approved Human Review roadmap. The UI sign-in integration is a separate gate: no button capable of producing a human review will be shipped behind shared Basic Auth.

## Why this boundary

The current PairAnnotation Pydantic model trusts `reviewer_id` supplied by callers, and current read-only dashboard has one shared Basic Auth password. **That password cannot prove that two distinct humans reviewed a pair.** Enabling reviewer action under shared login would make the same-incident gold invalid and open unauthorized merging.

## OSS / alternatives

- Selected: external OIDC provider (e.g. self-hosted **Keycloak**) and **PyJWT[crypto]** verifying issuer/audience/expiry/signature/JWKS and per-tenant claims. The backend uses *no* home-grown password store or JWT signing. Production JWKS URI must be explicit trusted HTTPS config. Test with locally signed RSA tokens to avoid using a live IdP in CI.
- Alternative Auth.js at Next.js first: convenient UI, but shared Basic Auth and unsigned downstream forwarded identity would be insufficient. Defer actual Auth.js SSO login until backend and token exchange are verified.
- Alternative raw reviewer_id from JSON: rejected as insecure.

## State and access model

Existing `ProblemRegistry` provides source-scoped canonical ticket identities, independently reviewed approval only, all-pairs merge, split and revoked approvals. Add **immutable** per-pair review records to versioned `to_state()` payload (same schema version with optional backwards-compatible field). One reviewer may submit once per pair; second distinct OIDC subject independently labels `same_incident | related_topic | different_incident | uncertain`. The backend issues review timestamps, never the caller. Same person cannot write both reviews, even using two tokens for same OIDC sub. After two reviews:

- both `same_incident`: `ready_for_lead` (still not merged and not an approved link).
- different labels: `disputed`.
- either uncertain: `uncertain`.
- both same non-positive label: `classified`, not an approval.
- incomplete: `awaiting_second_review`.

A `review_lead` token belonging to a **third distinct subject** may explicitly approve a `ready_for_lead` pair. It invokes the existing `approve_pair()` domain method and records immutable audit within a single PostgreSQL transaction. **No automatic Problem merge**; a later explicit actor-approved merge endpoint must separately check complete-link and revisions (outside this increment).

Split revocation means previous reviews and approvals can no longer authorize a future approval: require fresh reviews AFTER revocation, and block already-approved pair replay.

## API boundary

Under `/internal/v1/reviews`, require BOTH:
1. existing server-only internal service token;
2. `Authorization: Bearer <OIDC access token>` validated against issuer, audience, signature RS256, `exp`, `iat`, `nbf` where present, non-empty `sub`, `tenant_scope` matching app-configured scope and mandatory role.

Routes:
- `GET /internal/v1/reviews` returns scoped pair review statuses without raw ticket bodies.
- `POST /internal/v1/reviews` accepts only pair's ticket keys, label and rationale (no reviewer_id, timestamps or roles).
- `POST /internal/v1/reviews/approve` accepts ticket keys, reason and operation key; requires review_lead who is not either original reviewer; returns approval snapshot, no problem merge.
- Default `create_app` with no verifier returns unavailable for all reviewer endpoints, while existing read-only API remains.

## Test criteria / limits

TDD against actual PostgreSQL16: forged signature, HS256 downgrade, wrong issuer/audience, expired, wrong tenant, missing/invalid role, missing token all fail; same reviewer duplicate, two human reviews and dispute; third lead approves exactly once; after restart decisions persist; concurrent reviewers safe via FOR UPDATE; cross-scope rejected. **No model F1/accuracy claims.**

No live Keycloak sign-in or Next.js interactive reviewer form in this increment: do not claim full OIDC deployment or human independence guaranteed solely by JWT possession. Keycloak/user directory enrollment, browser session/OIDC PKCE, MFA, OAuth consent and role assignments require real IdP and security reviews.

## Production caveats

Trust only pre-configured IdP. Require an https issuer and JWKS URL, no dynamic issuer/JWKS from untrusted token claims. Do not log JWTs, PII or raw ticket bodies. Use JWKS caching and key rotation, enforce TLS and rate limits, and restrict service token to BFF. Review audit is app append-only and DB admin-modifiable, not WORM.
