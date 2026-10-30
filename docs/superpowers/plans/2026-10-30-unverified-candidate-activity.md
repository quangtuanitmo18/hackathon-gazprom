# Phase 20 — plan реализации unverified candidate activity

**Design:** [spec](../specs/2026-10-30-unverified-candidate-activity-design.md)

1. Новый standalone `tests/insights/test_unverified_activity.py`. TDD RED: повторное использование BM25, объяснимые признаки, отказ от кластеров, строгий event-time, `eligible_for_alert=false`, проверка лимитов.
2. Новый чистый `src/productpulse/insights/unverified_activity.py`: `list_unverified_activity(rows, approved_pairs, as_of, window_hours=24, limit=20, corpus_cap=500)`. Без I/O, без данных о reviewer, только подтверждённый server-scoped snapshot.
3. `GET /internal/v1/unverified-activity` в `src/productpulse/api/app.py`: существующий `require_internal` + `need_reviewer`, `CandidateQuery`-подобный строгий query model, `store.read(scope_id, ...)`, approved pair filter; strict Pydantic response. Never persist or notify.
4. Реальный `tests/api/test_review_routes.py` — missing OIDC/role/scope/service token, synthetic Russian ticket within window, approved pair excluded, returned evidence no raw body, no audit mutation.
5. Docs `docs/development/unverified-candidate-activity.md`: различие с verified Problem trends, источники времени, риск top-K truncation; Superpowers execution ledger.
6. Только после CI всех актуальных head jobs: проверить diff/чувствительные поля/negative tests, оставить COMMENT review. Keep Draft stacked on PR19, no merge/deploy.

**Требование:** никаких «подтверждённых инцидентов», измеренной доли false positive, автоматической отправки аналитики в tracker или TTAI на synthetic dataset.
