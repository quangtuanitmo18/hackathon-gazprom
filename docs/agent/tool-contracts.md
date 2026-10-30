# V2 — Контракты инструментов ИИ-агента (проектная спецификация)

**Status:** проектный документ для пункта 2 официального кейса **обо всех цифровых продуктах в охвате**, не перечень существующих Webneft API. **Architecture:** утверждённый пользователем подход C — локальные Qwen + доверенные детерминированные tools. `Кейс_Искусственный интеллект.pdf`, стр. 2–4 и 6. **Внешние API/LLM запрещены.** Права доступа и маршруты ниже — предлагаемые.

## 1. Actor, trust boundary и execution model

Вместо автономного «агента с root-доступом» используем **оркестратор с конечным автоматом**: ingestion event → источник/право → ASR/VL при необходимости → минимизация данных → локальная Qwen классификация → строго типизированные tools → policy → internal digest → feedback.

- Истинные `scope_id`, `product_id`, `actor_id`, разрешения, `taxonomy_version`, разрешённые категории и `trace_id` устанавливает **backend** на основе проверенной сессии/источника, а не пользовательский текст и не LLM. Вызов любого tool выполняется только через allowlist + Pydantic/JSON Schema.
- Доверенность: `source_ticket_key` = source-scoped ID без предположения о времени/причине; `source_created_at` optional, `ingested_at` фиксирует фактическое **первое наблюдение агентом**. Ссылки на evidence разрешены только после RBAC и проверки существования.
- Qwen получает ограниченный очищенный текст или признаки в **закрытом корпоративном контуре**. Для Qwen-ASR/Qwen-VL исходное аудио/изображение может содержать PII ещё до распознавания: их обрабатывает ограниченный internal media worker; redaction после распознавания предшествует **текстовой Qwen**. Внешнего HTTP egress быть не должно.
- `allowlisted tool output` остаётся недоверенным для выполнения инструкций. Текст «ignore instructions» внутри тикета, OCR или ASR **никогда** не может добавить tool, изменить scope или разрешить write.
- LLM может **предложить** тему, тип запроса и кандидатную связь; подсчёт уникальных заявок, задержки, completeness, routing и политики доставки вычисляет доверенный код. Любой response с выдуманным source ID, `owner_team`, count, root cause или произвольной командой отвергается.

## 2. Tools: интерфейсы, права и отказобезопасность

| Tool | Инициатор / режим | Строгий вход (помимо context scope) | Результат | Ошибка / правило |
|---|---|---|---|---|
| `list_new_tickets` | Scheduler / READ | `cursor: opaque`, `limit <= 100` | `source_ref[]`, `next_cursor`, `snapshot_status` | Invalid cursor = retry/stop; **нет** silent empty success |
| `get_ticket_context` | Agent / READ | `ticket_keys[] <= 30` | `redacted_text`, product, timestamps, provenance, `redaction_status` | Missing/unauthorized = `needs_human`; модель не видит оригиналы |
| `transcribe_recording` | Internal media worker / READ+PROCESS | `asset_ref`, `consent_policy_id`, `job_key` | `transcript_ref`, Qwen-ASR version, `quality_status` | No permission/PII policy = skip/human; raw audio not forwarded externally |
| `analyze_attachment` | Internal media worker / READ+PROCESS | `asset_ref`, `mime_allowlist`, `job_key` | `image_cues_ref`, Qwen-VL/parser version | File type/size blocked; never run scripts/macros from attachment |
| `classify_request` | Qwen adapter / READ+COMPUTE | `redacted_context_ref`, доверенные `product_id`, `taxonomy_version`, разрешённые journey/symptom коды | `request_intent`, `business_journey`, `symptom_codes[]`, `abstain` | Strict schema, untrusted model output, root cause **unknown** |
| `find_related_requests` | Agent / READ | backend-scoped `ticket_key`, `product_id`, `top_k<=20`, `time_window` | `{related_ticket_key,score,lexical_evidence}[]` | Similarity ≠ same incident, no transitive merge |
| `aggregate_recurrence` | Backend / READ+COMPUTE | доверенный `product_id`, `candidate_ticket_keys[]`, `window_start_utc`, `window_end_utc`, `grouping_mode` | `observed_unique_ticket_count`, `window`, `coverage_status`, `evidence_refs[]` | No fabricated time/window; if `unknown_coverage`, report **observed count only**, not increase/overall prevalence |
| `resolve_product_team` | Backend / READ | доверенный `product_id`, `topic_code` | `team_ref` **from approved registry** or `needs_human` | No model-generated team ID |
| `create_insight_draft` | Backend policy / WRITE INTERNAL | `source_refs`, `signal_id`, `rule_version`, `source_coverage` | `draft_id`, immutable evidence/provenance digest | Dedup and validation; model text never authorizes send |
| `send_internal_digest` | **Backend policy only** / WRITE INTERNAL | `draft_id`, `approved_route_id`, `idempotency_key` | `outbox_id`, `delivery_status`, `sent_at?` | Low-risk advisory only; **not callable autonomously by LLM**; no external issue tracker |
| `record_product_feedback` | **Authenticated product team** / WRITE INTERNAL | `signal_id`, `decision`, `actor_ref`, `operation_key` | Audited `ProductFeedbackV1` | Actor role + scope checked; LLM cannot impersonate a team member |

Здесь `WRITE INTERNAL` означает **проектную** запись в корпоративный outbox/feedback table, а **не** вызов внешней Jira/YouTrack/вебхука и не изменение основного ticket-source. Физические API и названия существующих сервисов не известны из PDF.

## Обязательное multi-product правило

Новый тикет всегда обрабатывается в доверенно определённом `scope_id + product_id`; backend загружает индивидуальную `taxonomy_version`, разрешённые `business_journey`/`symptom_codes` и актуальный `product_id → owning_team` registry. Нет продукта/таксономии/team — `unknown`, human triage, никакой автоматической доставки. Поиск и подсчёт **по умолчанию не пересекают продукты**. Корпоративный межпродуктовый дайджест — отдельно авторизуемая функция с гармонизированной таксономией, доступом и проверкой данных, а не автоматическое объединение отраслевых категорий Webneft.

## 3. Request / Response examples (design-only JSON)

### `classify_request` — Qwen предсказывает признаки, не решение

```json
{
  "input": {
    "redacted_context_ref": "internal://redacted/PDF6-05",
    "product_id": "webneft",
    "taxonomy_version": "webneft-proposed-v1"
  },
  "output": {
    "request_intent": "bug_report",
    "business_journey": "electronic_queue_booking",
    "symptom_codes": ["booking_404_or_slot_missing"],
    "relation_type": "insufficient_evidence",
    "root_cause_status": "unknown",
    "abstain": false
  }
}
```

`PDF6-05` — лишь ссылочный номер примера из текста конкурса, **не реальный ID записи ticket system**. Пример `relation_type` не доказывает повторяемость.

### `aggregate_recurrence` — только доверенный расчёт

```json
{
  "input": {
    "candidate_ticket_keys": ["SYN-BOOKING-001", "SYN-BOOKING-002"],
    "window_start_utc": "2026-10-01T00:00:00Z",
    "window_end_utc": "2026-10-02T00:00:00Z",
    "grouping_mode": "related_topic_only"
  },
  "output": {
    "observed_unique_ticket_count": 2,
    "coverage_status": "unknown_coverage",
    "growth_claim_allowed": false,
    "evidence_refs": ["SYN-BOOKING-001", "SYN-BOOKING-002"]
  }
}
```

**Все ID и даты этого примера синтетические**; здесь нет фактической аналитики Webneft. Вторая запись не доказывает общую root cause. При `unknown_coverage` разрешена формулировка «в доступной части данных замечено 2 обращения» при сохранении evidence, **не** «все обращения» или «число случаев выросло».

## 4. Routing and write authorization policy

| Класс сигнала | Маршрут | Согласование | Что запрещено |
|---|---|---|---|
| Некритичный recurring `question` / `feature_request` с проверяемыми evidence, известным product owner | Внутренний продуктовый **advisory digest** | По заранее утверждённым правилам, без новой ручной нагрузки support | Утверждать root cause, назначать задачу на разработку автоматически |
| Candidate `bug_report`, неполное source coverage | Черновик / monitor **или** внутренний digest с маркировкой `observed_partial`, если policy это допускает | Product owner рассматривает; delivery зависит от approved low-risk rule | Выдавать counts как полную статистику или velocity/growth |
| High-risk / security / credentials / юридический спор / неясный product owner | Человек / существующая команда обработки | Обязательно | OTP, password retrieval, данные другой организации, external egress |
| Срочная сервисная операция (PDF #4: телефон к отгрузке) | Сразу в существующий support SLA | Текущие полномочия ответственного сотрудника | Ждать, пока AI соберёт статистику |

Решение `send_internal_digest` принимается **отдельной policy state machine**, а не LLM. Нет необходимости требовать 2 reviewers+lead для каждого безопасного **информационного** дайджеста: это противоречило бы цели «не увеличивать нагрузку».

## 5. Reliability, observability and governance

- Read-only ingestion: immutable source identity, incremental cursor, reconciliation + source watermark, retries; partial import ≠ zero tickets.
- Internal media jobs: concurrency cap, retry with jitter, media size/MIME, bounded retention, no secrets in logs.
- Strict Qwen output: JSON Schema, enum, max output size, no external tool commands, timeout, rejection + deterministic fallback / abstain.
- Durable delivery: outbox write atomic with approved draft, stable idempotency key `scope:signal_id:window:revision`; at-least-once transport with **idempotent effect** rather than unproven network exactly-once.
- Evaluation audit: `source_created_at`, `ingested_at`, `qualified_at`, `sent_at`, `ack_at`, model_version, taxonomy_version, policy_version, `unknown_coverage`, feedback status; redact human reason and honor retention.
- Existing enterprise infra is **unknown**. Do not claim any of these tools exist in Webneft production or that Qwen ASR/VL APIs were called during this contest.

**Acceptance for this document:** every tool lists rights, input, evidence, failure mode; exact authorization boundary is explicit and distinct from model-generated advice; PDF #4/5/6/7 sensitive use-cases addressed.
