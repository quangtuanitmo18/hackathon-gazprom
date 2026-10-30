# Phase 22: Evidence-grounded Insight Proposal (review-gated mock tracker)

**Scope:** hackathon MVP, internal signed API, deterministic fallbacks. Это **не** автономная публикация предложений и **не** production LLM agent.

## Какие Problem могут стать Proposal

Только `ProblemRegistry.list_active()` с минимум двумя **явно merged** билетами после двух независимых reviewer и отдельного lead approval. `pair_approved`, две лексически похожие строки BM25 и ранние пары Phase 20 **не** дают право создавать продуктовую рекомендацию.

`GET /internal/v1/insight-proposals` требует `X-Internal-Token` и валидный OIDC reviewer Bearer с tenant match. Данные берутся из tenant-scoped PostgreSQL snapshot. `scope_id` нельзя передавать из HTTP. Неограниченное число предложений на SQL-запрос не поддерживается: текущий `corpus_cap=5000` и JSONB snapshot рассчитаны только на MVP.

## Grounding, ограничения LLM и fail-safe

Выход включает `proposal_id=problem_id:v<revision>`, `scope_id`, `revision`, **все** source-scoped `evidence_ticket_keys`, SHA-256 `evidence_digest`, `action_type` из фиксированного списка, детерминированный шаблон `title` и `recommended_action`.

**Никаких** догадок о root cause, owner, impact, F1, incident risk/odds или выгоде продукта. `root_cause_status=unknown`, `owner_team_id=null`, `requires_human_review=true` — обязательные значения. Конкретное `title` обращения, URL, raw body или credentials не передаются model adapter и не копируются в proposal.

`ModelSuggestion` принимает только **строгий JSON** вида:

```json
{"action_type":"improve_diagnostics","evidence_ticket_keys":["source-scoped-a","source-scoped-b"]}
```

Разрешённые действия: `investigate_regression`, `improve_diagnostics`, `review_documentation`. Для model suggestion разрешено **лишь** выбрать из списка и предъявить **точно тот же набор** evidence ticket keys, что и проверенный Problem. Дополнительные JSON поля (`root_cause`, `owner_team_id`, `confidence`, `title`, `issue_url`), неизвестная ссылка, невалидный JSON, prompt injection или отсутствующие evidence IDs приводят к deterministic fallback `investigate_regression` без раскрытия текста. **Ни один live LLM provider в данном PR не подключён** — boundary тестируется на злонамеренных строках и готов для отдельной адаптации после оценки privacy.

## Шлюз согласования и mock publish

1. `GET /internal/v1/insight-proposals` — **read-only draft**, `approval_status=pending`, `mock_issue_id=null`. Ни audit, ни tracker не меняются.
2. `POST /internal/v1/insight-proposals/{problem_id}/approve` — `productpulse_review_lead` из криптографически проверенного OIDC + service secret. Только JSON `{expected_revision, evidence_digest, reason, operation_key}`. Сверить **точный** номер revision и SHA-256 digest текущего состава. Пишет `insight_proposal_approved` в transactional tenant JSONB и audit.
3. `POST /internal/v1/insight-proposals/{problem_id}/mock-publish` — отдельное явно подтверждённое действие lead, только при наличии approval точно того же proposal revision+digest. Пишет **внутреннюю симуляцию** `MOCK-PRB-...-R...` и `insight_mock_published`. **Нет** реальных Jira/YouTrack/API/webhook calls или post в продуктовую команду.
4. Полный replay `operation_key` с теми же аргументами возвращает тот же объект без нового audit, повтор с другими аргументами отвергается. Повтор publish с другим ключом не создаёт второй mock issue. Split/изменение ревизии делает старое решение неприменимым к новому состоянию.

## TDD и known limits

- Unit tests: доказательство членства, root cause unknown, model-output injection/forged citations, idempotency, rollback/split, serialisation.
- PostgreSQL16 integration: signed JWT, tenant/role, approved-but-unmerged negative case, explicit merge, approve separately from mock publish, audit + restart.
- No organizer-provided real tickets, no accuracy/ROI/impact claims. Existing Russian PII redactor and 5000 limit are NOT production-ready. Lead reason is human input and may need stronger DLP/length policy before real corporate data.
- Next increments: reviewer console proposal UI, provider-neutral LLM call (masked input only) with offline eval, actor-independent editorial approval policy, true external tracker connector only after security+policy approval.
