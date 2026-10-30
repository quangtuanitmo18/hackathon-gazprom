# Phase 20 — plan реализации unverified candidate activity

**Design:** [spec](../specs/2026-10-30-unverified-candidate-activity-design.md)

1. Новый standalone `tests/insights/test_unverified_activity.py`. TDD RED: повторное использование BM25, объяснимые признаки, отказ от кластеров, строгий event-time, `eligible_for_alert=false`, проверка лимитов.
2. Новый чистый `src/productpulse/insights/unverified_activity.py`: `list_unverified_activity(rows, approved_pairs, as_of, window_hours=24, limit=20, corpus_cap=500)`. Без I/O, без данных о reviewer, только подтверждённый server-scoped snapshot.
3. `GET /internal/v1/unverified-activity` в `src/productpulse/api/app.py`: существующий `require_internal` + `need_reviewer`, `CandidateQuery`-подобный строгий query model, `store.read(scope_id, ...)`, approved pair filter; strict Pydantic response. Never persist or notify.
4. Реальный `tests/api/test_review_routes.py` — missing OIDC/role/scope/service token, synthetic Russian ticket within window, approved pair excluded, returned evidence no raw body, no audit mutation.
5. Docs `docs/development/unverified-candidate-activity.md`: различие с verified Problem trends, источники времени, риск top-K truncation; Superpowers execution ledger.
6. Только после CI всех актуальных head jobs: проверить diff/чувствительные поля/negative tests, оставить COMMENT review. Keep Draft stacked on PR19, no merge/deploy.

**Требование:** никаких «подтверждённых инцидентов», измеренной доли false positive, автоматической отправки аналитики в tracker или TTAI на synthetic dataset.


## Verified execution ledger — 2026-10-30

- **TDD RED:** [Python run 41076692240](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41076692240), `ModuleNotFoundError: productpulse.insights.unverified_activity` after the new tests were committed before implementation.
- **Unit + API implementation:** `list_unverified_activity` reads Canonical source timestamps from a trusted scoped registry, uses existing Russian-aware `BM25Index` through `rank_review_candidates`; new `GET /internal/v1/unverified-activity` requires both internal token and tenant-matched reviewer OIDC.
- **Review finding:** the initial 18-old-ticket fixture did not reproduce top-100 starvation and passed without the fix. Replaced with **130 historical + 2 recent** ticket synthetic fixture which explicitly asserts that unfiltered top-100 **does not** contain the new/new pair, then asserts that pre-top-K `required_any_ticket_keys` **does** preserve the pair. Do not mislabel the original 18-ticket fixture as a RED result.
- **Actual GREEN, source code + docs head `5b96f7a7fe57d380123949c147a4cd9377d2eac3`:**
  - [Python 41077508203](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41077508203): **252 passed**, 44 DB tests skipped, both Python 3.11 and 3.13.
  - [PostgreSQL16 41077508262](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41077508262): **296 passed**, both Python 3.11 and 3.13.
- **Scope and safety:** `eligible_for_alert=false`, `coverage_status=unknown_coverage`, no transitive clustering, no incident/owner/LLM probability, no external write. Signed JWT negative tests + real migrated PostgreSQL included.
- **Remaining review gate:** no independent approval; Draft PR #20 stacked on unmerged Draft #19, no merge or deploy. Full CI must be checked again after this documentation commit, not inferred from earlier head.
- **Next separate work:** typed frontend BFF/dashboard view for this unverified shortlist, with pagination that can resolve both ticket keys; add actual observed_at/ingested_at for time-to-insight if the organizer data permits; then evidence-backed InsightProposal Agent with human approval.
