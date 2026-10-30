# OIDC Reviewer API — Superpowers Implementation Plan

**Date:** 2026-10-30. **Status:** In progress on isolated feat/oidc-reviewer-workflow branch.
**Spec:** [Authenticated reviewer design](../specs/2026-10-30-oidc-reviewer-api.md).

## Task 1: Authenticated reviewer domain persistence (RED→GREEN)
Files: `src/productpulse/incident/registry.py`, `tests/incident/test_review_workflow.py`.
- [ ] RED: same reviewer cannot label twice; two different reviewers yield ready_for_lead, disagree yields disputed, uncertain/related not approvable, no silent approval, snapshot restore retains reviews, idempotency retries; test revoked pre-split reviews cannot authorize re-approval.
- [ ] Add immutable review state and `submit_review()`, `review_statuses()`, `approve_reviewed_pair()` methods. Reuse existing human PairAnnotation and approval, not a second confirmation implementation.
- [ ] GREEN: full Python tests and migration-backed Postgres tests.

## Task 2: OIDC/JWT verifier with defensive claims (RED→GREEN)
Files: `src/productpulse/api/reviewer_auth.py`, `tests/api/test_reviewer_auth.py`, `pyproject.toml`.
- [ ] RED: reject invalid issuer/audience/signature, expired, wrong role/tenant, HS256, missing sub or iat, untrusted JWKS URL.
- [ ] Implement PyJWT[crypto] OIDC verifier: issuer, audience and JWKS from trusted env only; test uses locally generated RSA public key and signed synthetic tokens.
- [ ] GREEN: targeted tests and full suite.

## Task 3: FastAPI review routes (RED→GREEN)
Files: `src/productpulse/api/app.py`, `tests/api/test_review_routes.py`.
- [ ] RED tests on PostgreSQL: both service token and OIDC token required; body cannot impersonate reviewer_id; independent reviewers save in transaction, lead must be third identity, retry is idempotent, dispute cannot approve, no automatic merge.
- [ ] Implement typed routes with fail-closed verifier optional injection and Pydantic strict schema. Tenant fixed in factory; no reviewer-originated tenant selection. No raw ticket bodies in API outputs.
- [ ] GREEN on PostgreSQL16 Python 3.11/3.13.

## Task 4: Verification and review
- [ ] Update workflow matrix to include `[review]` optional PyJWT[crypto] dependencies; capture fresh successful CI logs and run IDs.
- [ ] Write local OIDC Keycloak setup boundary and explicit unimplemented UI sign-in warning.
- [ ] Keep draft PR stacked on #15. Avoid real Jira or live review effects.

**Important:** A test signed by a local generated RSA key verifies JWT validation logic but does not prove full Keycloak federation or independent real-world reviewers.
