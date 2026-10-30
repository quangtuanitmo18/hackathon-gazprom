# Phase 21 — Superpowers execution plan

Design: [unverified console](../specs/2026-10-30-unverified-activity-console-design.md).

1. **RED** add `apps/web/tests/review-bff.test.ts` cases: new endpoint fetched with server-only auth, Zod rejects confidence/eligible_for_alert=true, missing evidence pair fails closed, pagination through 50 still resolves new pair, partial upstream failure visible. Record actual GitHub Actions.
2. **GREEN** update `apps/web/lib/review-bff.ts`: strict `UnverifiedActivity` schema; append `activity` to `ReviewData`; allowlist fixed API GET; BFF cross-check candidate ticket keys after all pages loaded.
3. **RED/GREEN UI+E2E** `apps/web/components/review-console.tsx`: separate unverified activity section, source timestamps and no-alert caveats; select pair and show existing two sanitized ticket evidence panels. Ensure empty-state differentiates from upstream failure. Update existing real Keycloak Chromium test and seed timestamps in `.github/workflows/keycloak-review-e2e.yml`.
4. **Verify** npm unit, TS typecheck, Next build, actual Keycloak+Postgres+Chromium workflow, dashboard smoke, Python if relevant. Pin current commit/run IDs; no claims of runtime success without actual GREEN.
5. **Review** inspect full PR patch for accidental credentials, unsafe HTML, extra fetches, source timing semantics, auth bypass, incidental changes; leave self-review COMMENT and independent-review gate. Do not merge/deploy. Note unmerged stacked PR dependency.

Non-goals: no HTTP mutations to Problem/issue tracker, no extra OSS, no calibrated incident probabilities and no production-ready alert claims.
