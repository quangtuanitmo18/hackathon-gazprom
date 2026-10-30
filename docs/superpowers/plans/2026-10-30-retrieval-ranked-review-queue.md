# Ranking + Privacy Review Queue Implementation Plan

**Superpowers:** follow TDD RED→GREEN per task and annotate run IDs.

1. Implement `src/productpulse/incident/candidates.py` and `tests/incident/test_review_candidates.py`: deterministic BM25 from existing tested OSS-free baseline, nonzero lexical overlap, source/product hints, unique undirected pairs, exclude same active Problem and already-approved, avoid guessing duplicate labels, max 500 tickets fail closed.
2. Implement `src/productpulse/privacy/redaction.py`, tests, OSS `scrubadub` optional extras, and FastAPI ingress sanitizer. Verify source-scoped IDs cannot be mutated, preserve idempotency, block raw credentials and common PII from persistence. CI against real PostgreSQL.
3. Add `GET /internal/v1/review-candidates` OIDC reviewer service-token-gated endpoint; verify same/other scope, no JWT, bounded candidate size, stable output.
4. Integrate `apps/web/lib/review-bff.ts` typed data, reviewer console suggested-pair cards, and ensure actual Keycloak 3-user flow with Chromium still works. Add test to select suggested pair and render reason. No token leak or claim same incident.
5. Final quality pass + Superpowers ledger, updated PR description. Draft stacked on #17 and no main merge.
