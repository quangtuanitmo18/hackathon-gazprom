# Phase 21 — Keycloak Reviewer Console для неподтверждённых пар

## Назначение и доверие

Страница `/review` получила **отдельную** секцию **«Ранняя активность — не подтверждено»**. Это список *попарных, лексически похожих* обращений по `created_at`, а не обнаруженные технические инциденты, не единый transitive cluster и не подтверждённая первопричина. Временной диапазон по умолчанию — текущие 24 часа и предыдущие 24 часа. Подробнее: [Phase 20 backend](unverified-candidate-activity.md).

Остальная панель `«Рекомендованные пары»` остаётся отдельным общим BM25-поиском без временной интерпретации. Считать пару инцидентом или суммировать две очереди для подсчёта инцидентов **запрещено**.

## Серверная архитектура

```text
Keycloak OIDC login -> encrypted Auth.js session
            |
            v
browser GET /api/review (cookie only, no OIDC tokens in JSON)
            |
            v
Next.js BFF node process, valid OIDC access token + server-only service secret
   |                   |                       |
   v                   v                       v
GET /reviews     GET /review-candidates    GET /unverified-activity
   |
   v
GET /review-tickets?limit=50&offset=N (up to the 500-ticket cap)
            |
            v
Strict Zod validation + cross-check both ticket keys exist
            |
            v
Browser sees sanitary evidence text, pairs + read-only scores/buckets
            |
            v
User clicks pair -> existing A/B evidence panels -> manual independent vote
```

- `fetchReviewerData` in `apps/web/lib/review-bff.ts` is the only upstream client; it fetches early activity with the private credentials stored on the **server**. Upstream URL is fixed/allowlisted and may not point at an attacker-controlled origin.
- Ответные поля проходят строгую проверку Zod, включая `evidence_type=lexical_candidate`, `coverage_status=unknown_coverage` и `eligible_for_alert=false`. Любые `confidence`, `incident_id` и другие лишние атрибуты отвергаются.
- Оба идентификатора `ticket_key_a/b` **обязательно** должны находиться в уже полученных страницах sanitized evidence. Если их нет, ошибка **502**, а не успешная пустая выдача или ссылка в неизвестную запись.
- Пустой список — это отсутствие *предложенных* пар для одного текущего запроса, **не** доказательство отсутствия инцидентов.
- Клик по паре только меняет выбор в существующей форме и очищает старое обоснование/лейбл, чтобы человеческая проверка осталась осознанной. Сам клик не вызывает POST, не объединяет Problem, не создаёт тикет Issue Tracker.
- Для любого изменения по-прежнему нужны **два независимых reviewer** и **независимый lead**. После успешного `approve` даже тогда нет автоматического `merge`.
- API response `Cache-Control: no-store`, Auth.js cookie содержит encrypted token на сервере, а browser получает только ticket keys/time buckets/ranks/category flags.

## E2E, безопасность и ограничение rollout

- Unit тесты `apps/web/tests/review-bff.test.ts`: whitelist, структура и доказательства, page 51+, backend failure, секреты не утекли; нарушение контракта fail-closed.
- Browser `apps/web/tests/review-oidc.browser.spec.ts` в реальном Keycloak 26.8.1, PostgreSQL16, FastAPI и Chromium: два синтетических русских тикета с UTC `created_at`, ранняя пара видима, клик открывает evidence, независимые голоса и third-lead approval, auth/CSRF/secrecy, отсутствие auto-merge проверяются.
- Тестовый fixture **не** является доказательством precision/recall и не позволяет оценить ROI/TTAI. `created_at` не заменяет `observed_at`, а ingest completeness/watermark неизвестен.
- Before production use, необходимо: независимый review и одобрение владельца, полноценный DLP/PII включая русские имена и бизнес-поля, index вместо JSONB/BM25 per-request 500 cap, authenticated provenance + `ingested_at` для time-safe replay, human-adjudicated evaluations, retention policies.

## Разделение задач
Следующий этап — evidence-grounded structured `InsightProposal` для уже проверенных Problem с отказом от галлюцинаций, human-approval и mock issue tracker. **Не** превращать неподтверждённые ранние пары в автоматически публикуемые продуктовые рекомендации.
