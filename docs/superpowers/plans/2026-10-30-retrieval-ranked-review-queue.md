# Ranking + Privacy Review Queue Implementation Plan

**Superpowers:** follow TDD RED→GREEN per task and annotate run IDs.

1. Implement `src/productpulse/incident/candidates.py` and `tests/incident/test_review_candidates.py`: deterministic BM25 from existing tested OSS-free baseline, nonzero lexical overlap, source/product hints, unique undirected pairs, exclude same active Problem and already-approved, avoid guessing duplicate labels, max 500 tickets fail closed.
2. Implement `src/productpulse/privacy/redaction.py`, tests, OSS `scrubadub` optional extras, and FastAPI ingress sanitizer. Verify source-scoped IDs cannot be mutated, preserve idempotency, block raw credentials and common PII from persistence. CI against real PostgreSQL.
3. Add `GET /internal/v1/review-candidates` OIDC reviewer service-token-gated endpoint; verify same/other scope, no JWT, bounded candidate size, stable output.
4. Integrate `apps/web/lib/review-bff.ts` typed data, reviewer console suggested-pair cards, and ensure actual Keycloak 3-user flow with Chromium still works. Add test to select suggested pair and render reason. No token leak or claim same incident.
5. Final quality pass + Superpowers ledger, updated PR description. Draft stacked on #17 and no main merge.

## Verified execution ledger — 2026-10-30

- **Ranker RED:** [Python CI 41062807229](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41062807229) failed for absent `productpulse.incident.candidates`; added deterministic Cyrillic-aware reuse of the existing `BM25Index` baseline.
- **Privacy RED:** [Python CI 41063038852](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41063038852) failed for absent `productpulse.privacy.redaction`. Added OSS scrubadub + narrow credential masking; installed `privacy` and `api` extras in CI. Sensitive identity fields fail closed instead of silently mutating referential IDs.
- **Real PostgreSQL API GREEN:** [41063442702](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41063442702) confirmed privacy-safe persistence, sanitization idempotency and OIDC-scoped candidate endpoint.
- **False positive RED:** [Python CI 41064059877](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064059877): same product/component alone produced a candidate even when incident narratives had zero overlap. Revised ranking gate to require substantive text-token intersection, so metadata are *support signals only*. **GREEN** [41064265728](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064265728): 216 passed Python 3.11/3.13 (37 integration tests skipped without DB); [PostgreSQL 41064265919](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064265919): **253 passed** each Python version.
- **Frontend pagination RED:** [Dashboard CI 41064411411](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064411411) reproduced that the UI cannot inspect a candidate after ticket 50 when first page is the only evidence fetched. BFF now fetches bounded pages up to 500, each constrained to allowlisted FastAPI URL/offset. **GREEN** [41064565344](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064565344): full dashboard build, Node suite, HTTP and 3 Chromium tests passed.
- **Real IdP integration GREEN:** [Keycloak CI 41064553688](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41064553688) — **24 Node tests passed**, 1 real Chromium three-account Keycloak scenario passed. Reviewer A clicked a suggested BM25 pair, B independently reviewed, third lead approved, PostgreSQL audit verified **two separate Problems and no automatic merge**.
- **Extra privacy coverage:** test for common phone-number masking added after previous successful CI; latest exact-head Python/PostgreSQL runs should be checked independently before claiming the new test passed.

### Explicit limitations and architectural rulings

- **Ruling: BM25 reuse rather than additional search service** — existing code and audit provide reproducible ranking quickly. Cost: O(N²) 500-ticket max and static/transductive features, not scalable or arrival-time-safe.
- **Ruling: reject source identity with PII rather than change IDs** — preserves referential integrity. Cost: some source datasets require a carefully designed pseudonymization adapter upstream.
- **Ruling: scrubadub is partial** — detected common PII and credentials covered; Russian full-name/address/company-specific identifiers require validated language-specific detectors and manual audit.
- **Ruling: no automatic incident verdict** — rank and categorical overlap signals are not probabilities or verified duplicates; two independent humans and third lead still required for approval.
- **Ruling: draft and stacked** — PR #18 depends on #17 and previous PRs; no merge/publish/deploy without user approval.
