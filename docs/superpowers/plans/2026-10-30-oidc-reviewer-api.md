# OIDC Reviewer API — Superpowers Implementation Plan

**Date:** 2026-10-30. **Status:** Backend/domain IMPLEMENTED and CI verified on isolated branch; external SSO/Keycloak and browser review UI NOT IMPLEMENTED.
**Spec:** [Authenticated reviewer design](../specs/2026-10-30-oidc-reviewer-api.md).

## Task 1: Authenticated reviewer domain persistence (RED→GREEN)
Files: `src/productpulse/incident/registry.py`, `tests/incident/test_review_workflow.py`.
- [x] RED: same reviewer cannot label twice; two different reviewers yield ready_for_lead, disagree yields disputed, uncertain/related not approvable, no silent approval, snapshot restore retains reviews, idempotency retries; test revoked pre-split reviews cannot authorize re-approval.
- [x] Add immutable review state and `submit_review()`, `review_statuses()`, `approve_reviewed_pair()` methods. Reuse existing human PairAnnotation and approval, not a second confirmation implementation.
- [x] GREEN: full Python tests and migration-backed Postgres tests.

## Task 2: OIDC/JWT verifier with defensive claims (RED→GREEN)
Files: `src/productpulse/api/reviewer_auth.py`, `tests/api/test_reviewer_auth.py`, `pyproject.toml`.
- [x] RED: reject invalid issuer/audience/signature, expired, wrong role/tenant, HS256, missing sub or iat, untrusted JWKS URL.
- [x] Implement PyJWT[crypto] OIDC verifier: issuer, audience and JWKS from trusted env only; test uses locally generated RSA public key and signed synthetic tokens.
- [x] GREEN: targeted tests and full suite.

## Task 3: FastAPI review routes (RED→GREEN)
Files: `src/productpulse/api/app.py`, `tests/api/test_review_routes.py`.
- [x] RED tests on PostgreSQL: both service token and OIDC token required; body cannot impersonate reviewer_id; independent reviewers save in transaction, lead must be third identity, retry is idempotent, dispute cannot approve, no automatic merge.
- [x] Implement typed routes with fail-closed verifier optional injection and Pydantic strict schema. Tenant fixed in factory; no reviewer-originated tenant selection. No raw ticket bodies in API outputs.
- [x] GREEN on PostgreSQL16 Python 3.11/3.13.

## Task 4: Verification and review
- [x] Update workflow matrix to include `[review]` optional PyJWT[crypto] dependencies; capture fresh successful CI logs and run IDs.
- [x] Write local OIDC Keycloak setup boundary and explicit unimplemented UI sign-in warning.
- [x] Keep draft PR stacked on #15. Avoid real Jira or live review effects.

**Important:** A test signed by a local generated RSA key verifies JWT validation logic but does not prove full Keycloak federation or independent real-world reviewers.

## TDD / independent CI evidence (2026-10-30)

- **Task 1 RED:** [run 41055033075](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055033075): 12 new tests failed because `ProblemRegistry.submit_review` was absent; later [run 41055182177](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055182177) passed full Python domain tests.
- **Task 2 RED:** [run 41055326333](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055326333): `ModuleNotFoundError: productpulse.api.reviewer_auth`; GREEN [run 41055465242](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055465242) passed PostgreSQL/PyJWT matrix.
- **Task 3 RED:** [run 41055588922](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055588922): new reviewer endpoints 404, `create_app` had no verifier parameter; GREEN [run 41055707761](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41055707761): **230 tests passed** on PostgreSQL 16 Python 3.11 and 3.13.
- Additional tests for concurrent same-tenant review votes and revoked lead-approval replay added: [run 41056071725](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41056071725): **232 tests passed** on PostgreSQL 16, Python 3.11 and 3.13.
- Full Python matrix [run 41056081962](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41056081962) also passed on both versions, without PostgreSQL-only tests.

### Review limitations
- Live OIDC provider/Keycloak, browser sign-in, role mapper and account issuance NOT exercised by CI. Tests cryptographically sign local RS256 JWTs with generated keys and verify claims, signature, replay, missing roles and tenancy.
- `reviewer_id` and timestamps cannot be supplied via request bodies; subject comes from access token. Two reviewers plus distinct third lead, separate Problem merge.
- Current Next.js UI uses shared **demo Basic Auth** and is **NOT authorized** to submit human reviews; do not expose buttons until real OIDC session/Keycloak is in place.
- Existing registry JSONB snapshot still rewrites tenant state; audit not database WORM; product/customer data not uploaded.
- Future: signed-in browser reviewer evidence view (redacted tickets, provenance, review history), Auth.js OIDC, protected server actions with CSRF and role checks, actual Keycloak integration test, human annotation export for metrics.
