# Superpowers execution ledger: Phase 19A verified Problem trends

**Связанные артефакты:** [design](../specs/2026-10-30-verified-problem-trends-design.md), [runtime semantics](../../development/verified-problem-trends.md), [Draft PR #19](https://github.com/quangtuanitmo18/hackathon-gazprom/pull/19).

## Выполненные задачи
- [x] Определить non-goals/функциональные инварианты: confirmed Problem only, UTC event-time, read-only, tenant-bound.
- [x] Тест RED до модуля: [Python run 41066911180](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41066911180).
- [x] Реализовать `src/productpulse/insights/trends.py`, `registry.trend_inputs`, OIDC+service-token `GET /internal/v1/trends`.
- [x] Проверить Python и PostgreSQL исходного инкремента: [Python 41067617536](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41067617536), [PostgreSQL 41067617566](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41067617566).
- [x] Прочитать фактический diff, проверить GitHub reviews: до review `reviews=[]`; оставить self-review COMMENTS с рисками без APPROVE.
- [x] Исправить Critical/Important finding "неподтверждённая полнота": добавить структурированный `SourceCoverage`, `unknown_coverage`, `observed_pattern` и `eligible_for_alert=false`.
- [x] RED дополнительные tests: [Python 41072968845](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41072968845), включая новый schema contract, границы, late backfill, split, PostgreSQL.
- [x] Проверить отказ при изменении API response enum: [PostgreSQL run 41073246710](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41073246710), исправить `TrendOut.status` после реального `ResponseValidationError`.
- [ ] Приложить **итоговую** GREEN ссылку на head SHA после проверки всех Python/PostgreSQL jobs.
- [ ] Независимый reviewer одобрил PR; устранить его блокирующие замечания.
- [ ] Merge только после явного разрешения владельца.

## Open review concern — out of scope for verified stream
Текущая аналитика появляется после human merge и не решает раннюю маршрутизацию. Следующий отдельный PR должен реализовать **unverified candidate activity** с собственным названием и статусами; TTAI измеряется по реальному `ingested/observed_at`, а не задним числом по `created_at`. До этого не утверждать, что предиктор обнаруживает инциденты в момент поступления.

## Отдельные риски
`SourceCoverage` пока только контракт, без подключённого проверенного adapter; все production-like события роста помечены `unknown_coverage`. Текущие CI используют synthetic tickets, они не подтверждают accuracy на данных организатора. JSONB snapshot cap и отсутствие исторического журнала observed-time ограничивают масштабирование и воспроизводимый replay.
