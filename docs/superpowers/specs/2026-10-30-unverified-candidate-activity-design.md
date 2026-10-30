# Phase 20 — Ранняя активность неподтверждённых кандидатов (design)

**Статус:** proposed, approval pending; Draft stacked PR. В рамках hackathon MVP, НЕ подтверждённый детектор одинаковых инцидентов.

## Цель
До завершения ручной верификации показывать оператору **пары** потенциально связанных обращений в последних 24–48 часах. В отличие от Phase 19A, здесь **нет** `Problem` из двух тикетов до явного merge. Эта очередь не даёт права создавать инцидент, уведомлять продуктовую команду или автоматически записывать issue в корпоративный tracker.

## Брейнсторминг / альтернативы
1. Считать connected components по BM25-pairs: ОТКЛОНЕНО — транзитивность ложно объявляет разнородные тикеты одним событием.
2. Отдельный LLM/embedding pipeline: ОТЛОЖЕНО — не существует gold same-incident пар, по которым можно доказать преимущество; увеличивает latency/privacy surface.
3. **Выбрано:** повторно использовать `rank_review_candidates` и `ProblemRegistry.candidate_inputs`; ограничить вход текущими двумя последовательными event-time окнами; вернуть независимые, явно неподтверждённые пары с прозрачными evidence flags. Никаких новых зависимостей.

## Контракт
`GET /internal/v1/unverified-activity?window_hours=24&limit=20`.
- Оба заголовка обязательны: приватный `X-Internal-Token` и подписанный OIDC `Bearer` пользователя `productpulse_reviewer` того же server-configured tenant.
- Все входные тикеты поступают из одного проверенного scope; клиент не задаёт scope, as_of, список pair, reviewer_id или timestamps. `as_of` берётся из текущего backend UTC.
- Для консервативной парной проекции оба события имеют валидный `created_at` внутри `[as_of-2W,as_of)`, хотя бы один — в `[as_of-W,as_of)`. Время отсутствует, равно as_of, в будущем или слишком старое → тикет **не** участвует. Это исключает event-time future leakage в snapshot, но **не доказывает** честный исторический replay или полноту загрузки.
- Инпут передавать в уже существующий Russian-aware BM25; общие слова и одинаковые product/component без общих содержательных токенов не образуют pair. Нет NER/LLM verdict. Исключать same active Problem и уже `approved` links.
- Вывод: 1 строка на **неориентированную пару**, `ticket_key_a/b`, их source timestamps, `as_of`, `rank` и `signals` из BM25, `recent_pattern = both_current|current_with_previous`, `current_member_count` = 1..2; `previous_member_count` = 0..1. `evidence_type=lexical_candidate`, `coverage_status=unknown_coverage`, `eligible_for_alert=false`. **Не считать couple count количеством инцидентов**.
- Не создавать агрегатные transitive clusters, не указывать confidence/probability, guessed root cause или owner. Для review использовать исходный `review-candidates` и полноценный 2 reviewer + lead процесс.
- Поддерживаем не более 500 *всех* тикетов в одном tenant snapshot и 1..30 результатов. BM25 фильтрует пары, не содержащие свежий тикет, **до** top-100 output limit, чтобы старые пары не заглушали новые; внутренний top-30 BM25 соседей на запрос всё ещё ограничивает recall. Это **shortlist**, не исчерпывающая детекция. Превышение cap → HTTP 503, не скрытая выборка. Предыдущий JSONB snapshot и ranking — O(N²) MVP.

## Не входит в задачи
Полнота event-time интервала, import watermark, review SLA, historical `ingested_at`/observed-time log, обученная классификация same incident, продуктовые Insights, Jira и автоматическая эскалация. Для TTAI потребуются timestamps загрузки/назначения/первых человеческих действий. Нынешний `as_of` — момент чтения snapshot, не момент прибытия тикета.

## Безопасность/допущения
- Предполагаем существующий ingress DLP `scrubadub` (ограниченная поддержка PII русского языка) и OIDC/API находятся за внутренним gateway; полная защита PII ещё не доказана.
- `source coverage` всегда неизвестна, а `eligible_for_alert` всегда false, даже если две записи относятся к одному продукту.
- Не показывать никакие реальные закрытые тикеты в public GitHub и CI.

## Verification
RED → GREEN на Python 3.11/3.13; real PostgreSQL16 + RSA signed OIDC:
- same issue-like narrative 2 recent -> unverified pair (never confirmed);
- current+previous -> bucket, future/missing/as_of/exact bound/excess old omitted;
- metadata-only overlap cannot count, approved pairs and merged groups suppressed;
- scope/role/internal token denials; unknown query props / caps, output includes no raw body;
- no audit mutation; deterministic order; no retroactive as-of evaluation claims.
- PR self-review + independent approval before merge.
