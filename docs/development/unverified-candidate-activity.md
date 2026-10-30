# Ранняя активность неподтверждённых ticket-пар (Phase 20)

**Назначение:** дать reviewer возможность увидеть две похожие технические заявки до завершения human review. Это **не** предсказание подтверждённого инцидента, не автоматический merge, не доказательство одинаковой первопричины и не production alerting.

## Два принципиально разных потока

| Эндпоинт | Когда доступен | Доверие | Действие |
|---|---|---|---|
| `GET /internal/v1/unverified-activity` | До проверки, из BM25 candidate ranker | **Не подтверждено** | Только обзор evidence, перейти в 2 reviewer + независимый lead workflow |
| `GET /internal/v1/trends` | Только когда Problem явно объединён после проверки | Подтверждено **членство** в Problem, но **не** полнота истории | Анализ количества и покрытий; до source manifest — `unknown_coverage` |

**Одна связанная с другой BM25-пара не даёт транзитивной группы**. Нельзя подсчитать `len(pairs)` как число инцидентов.

## API

`GET /internal/v1/unverified-activity?window_hours=24&limit=20`

Обязательны приватный `X-Internal-Token` + валидный Keycloak OIDC Bearer токен с ролью `productpulse_reviewer` и совпадающим `tenant_scope`. Tenant, `as_of`, source timestamps и identity не принимаются из query. Ограничения: `window_hours = 1..168`, `limit = 1..30`.

- Система извлекает **весь scoped corpus** из `ProblemRegistry`, максимум 500 тикетов, иначе HTTP 503. Никогда не берёт «первые 500» в качестве полного датасета.
- Используется `CanonicalTicketV1.created_at`. Временной горизонт: `[as_of-2W, as_of)`; хотя бы один тикет в `[as_of-W, as_of)`. Требуются event timestamps обоих тикетов; отсутствующие, будущие, равные `as_of`, слишком старые пропускаются.
- Candidate ranker — тот же протестированный BM25 по обезличенному title/body + техническим данным, с **непустым narrative lexical overlap**. Совпадение только `product_id` или `component_id` не образует pair.
- Отдельные пары внутри одного active Problem и уже одобренные третьим reviewer связи исключаются.
- Результат включает `ticket_key_a/b`, `created_at_a/b`, `as_of`, `window_hours`, `recent_pattern` (`both_current` или `current_with_previous`), `current_member_count`, `previous_member_count`, `rank`, категориальные `signals`, и строгие `evidence_type=lexical_candidate`, `coverage_status=unknown_coverage`, `eligible_for_alert=false`. Не включаются тело тикета, AI confidence, incident ID, guessed owner/root cause.

**Важное ограничение recall:** `rank_review_candidates` выдаёт максимум 100 лучших lexical пар **до** проверки участия в текущем окне; shortlist может пропустить подходящую пару, если 100 предыдущих lexical пар занимают верх списка. Это сознательная граница MVP, не исчерпывающий поиск. По мере роста загрузки: indexed BM25 + фильтр времени в запросе/до top-K.

## Временная честность и безопасность

`as_of` в этом API — timestamp текущего запроса, не `ingested_at` в журнале данных. Фильтрация `created_at` не делает historical replay корректным: late backfills могли поступить позже предсказываемого момента. История полноты источника отсутствует; `coverage_status` остаётся `unknown_coverage`. Никаких TTAI и online recall/precision без входящего `observed_at` + независимых human adjudicated labels.

Проектный ingress `scrubadub` частично редактирует PII, но не подтверждает полноту защиты русских ФИО и корпоративных идентификаторов. Перед реальными данными нужен DLP/NER и политика локализации/retention.

**Нет** побочных эффектов при GET: нет записи в audit, нет auto-merge, нет уведомлений и Jira/Issue Tracker вызовов. Для бизнес-аналитики это *вход* в human review, не evidence confirmed incident.

## Что проверить
- Python unit: exact half-open boundaries и TZ, missing/future/old as_of, source identity, capacity, no zero lexical support, no transitive clustering, deterministic output.
- Real PostgreSQL+signed OIDC: unauthorized/tenant/role/service token, reviewed pair suppression, read-only result without raw body, no Problem mutation.
- CI logs являются единственным основанием для утверждения о GREEN; Final PR должен содержать ссылки на exact head jobs.

## Следующий этап
Генерировать `InsightProposal` **только** из ранее подтверждённых evidence, строгих цитат и source coverage; LLM/agent draft с abstention, политика approval и idempotent mock tracker. Отдельно вводить arrival-time `observed_at` и проверяемый source manifest для TTAI и replay.
