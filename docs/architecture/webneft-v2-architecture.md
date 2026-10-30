# Архитектура V2 — Webneft / Product Feedback Intelligence

**Решение, выбранное командой:** Hybrid Option C — внутренняя Qwen для анализа смысла + детерминированные инструменты для подсчёта, evidence, routing и delivery. Подтверждено пользователем 2026-10-31. **Это архитектурная документация, а не deployed application.**

## Источники и основания
- **Обязательно по PDF:** 7-страничный кейс Intelligence Cup, стр. 2 (архитектура, микросервисы, tools), стр. 4 (около 40 менеджеров, единая ticket DB на 1 год, звонки, файлы, Qwen 3.8/ASR/VL, запрет external LLM/API), стр. 6 (7 обращений Webneft), стр. 7 (обоснование разделения сервисов и расчёт нагрузки).
- **Не подтверждено:** названия систем-источников, интерфейсы REST/API, версия и стоимость GPU, peak load, endpoints Qwen, маршруты реальных product teams, идентификаторы/даты заявок, текущая организация отчетности.
- **DeepSeek:** некоторые бизнес-процессы описаны как исторический контекст или проектные гипотезы, но root causes технических симптомов из семи ticket **не установлены**.

## Диаграммы (редактируемые исходники)

| Диаграмма | Файл | Что доказывает |
|---|---|---|
| **C4-inspired Container** | [`c4-containers.mmd`](../diagrams/c4-containers.mmd) | Функциональные контейнеры в корпоративном контуре и связи с support/product team |
| **Data Flow & Trust Boundary** | [`data-flow-trust-boundaries.mmd`](../diagrams/data-flow-trust-boundaries.mmd) | Где находятся raw audio/images, PII, модель, хранилище и egress-ban |
| **AI Agent Workflow** | [`agent-workflow.mmd`](../diagrams/agent-workflow.mmd) | Policy gate, same-topic ≠ same-incident, abstention и human path |
| **Sequence & Feedback** | [`feedback-sequence.mmd`](../diagrams/feedback-sequence.mmd) | Шаги data→insight→internal digest→product team feedback и idempotency |

**Диаграммы — проектный черновик для review.** Физическое количество микросервисов, границы контуров и интеграция с существующим ПО должны быть согласованы после discovery. Mermaid файлы можно версионировать в Git, затем готовые визуальные версии экспортировать в презентацию. Нельзя заменять самостоятельный текст основного конкурсного решения ссылкой на эти файлы.

**GitHub Mermaid preview:** [открыть галерею всех четырёх диаграмм](../diagrams/README.md). Рендеринг в итоговом документе/слайдах требуется отдельно проверить визуально.

**Детальная спецификация Agent:** [tool contracts и права](../agent/tool-contracts.md), [промпт на русском с комментариями](../agent/system-prompt.ru.md), [строгий JSON output](../agent/output-contracts.md), [20 adversarial/acceptance сценариев](../evaluation/prompt-adversarial-cases.md). Тексты — **design-only**, не результат вызова Qwen.

## Ответ на вопрос «зачем именно эти сервисы»

| Логический блок | Нагрузка | Обоснование отдельного масштаба | Контроль отказов |
|---|---|---|---|
| Ticket Ingestion | I/O / source-cursor | Выгрузки и инкрементальный импорт не должны тормозить основной support | checkpoint + source-scoped idempotency + read-only rights |
| Multimodal ASR / VL | GPU/CPU / media seconds | Звонки и OCR могут быть намного тяжелее текстовых ticket; отдельный bounded worker pool | очередь, retry, backpressure, encrypted media refs |
| Intelligence + Retrieval | GPU inference + CPU/index | Внутренний Qwen классифицирует смысл; BM25 baseline и детерминированные проверки независимы | strict JSON, no model-owned counts, source IDs verified |
| Aggregation / Routing | SQL/CPU + read | Считает уникальные ticket, окна, coverage; карта product→team авторитетна | transaction, permission, abstain при неизвестных |
| Delivery + Feedback | queue/DB + internal messaging | Получатель и подтверждение могут быть недоступны при исправной модели | transactional outbox, replay-safe key, ack+feedback audit |

Пять **логических** блоков можно упаковать в три физических процесса MVP: `ingestion worker`, `ASR/VL/Qwen worker pool`, `API + aggregator + delivery worker`, с одной PostgreSQL и внутренним брокером. Это выбор для **учебного deployment plan**, а не описание реальной инфраструктуры заказчика. Создавать пять отдельных микросервисных сетевых сервисов без реального масштаба — лишняя сложность. Если нужна полная независимость развёртывания GPU и бизнес-API, выделять её по замерам.

## Проход одного нового обращения

1. Источник зарегистрировал заявку: фиксируем `source_created_at` **если доступен** и наш собственный `ingested_at` **при первом наблюдении**. Не задаём задним числом искусственный `ingested_at` для ретроспективных PDF-примеров.
2. Для звонка запускаем внутренний Qwen-ASR, для разрешённого изображения — Qwen-VL. **До ASR/VL** raw media содержит PII: доступ ограничен корпоративной границей; после распознавания минимизация/редакция предшествует текстовому Qwen.
3. Текстовая Qwen выбирает кандидата темы, намерение пользователя, симптом, степень неопределённости. Ни модель, ни similarity score не подтверждают root cause или принадлежность к одному incident.
4. Backend сверяет source IDs, tenant/product, временное окно, независимые ticket и охват источника; `unknown_coverage` не выдаём за полный ряд.
5. Backend выбирает маршрут только из корпоративного справочника, проверяет risk/policy. Срочная смена номера перед отгрузкой (ticket PDF #4) остаётся обычным SLA support; недоступность Qwen не задерживает обработку.
6. Доставляем *неподтверждённый по причине* advisory digest в авторизованный внутренний канал при наличии соответствующего правила, иначе — человеку. Сохраняем audit и feedback `accepted/rejected/needs_info/in_progress/resolved`.
7. Оцениваем outcome по timestamps и human-labeled feedback; это ещё не доказательство эффекта без baseline.

## Пример расчёта нагрузки — **полностью сценарный**

**Из PDF известно только N≈40 менеджеров.** Для проверки жизнеспособности примем:
- `t=20` заявок на менеджера в день; `D=N*t=800` обращений/день. Средняя интенсивность за 24h: `λ=800/86400 ≈ 0.00926` ticket/s. При 8h смене ≈`800/28800=0.02778` ticket/s. Это **не** реальные RPS компании.
- Для иллюстрации `share_calls=0.30`, `avg_call=3 min`: `800×0.30×3=720` minutes audio/day.
- **RTF** (real-time factor, elapsed processing time / audio duration) для Qwen-ASR неизвестен и должен измеряться на реальном разрешённом оборудовании. Если гипотетически `RTF=0.5`, `peak_factor=3`, `utilization=0.7` и worker available `8h/day`, грубая нижняя оценка `workers≥ceil(720×0.5×3/(8×60×0.7))=4`. Это нагрузочная иллюстрация, **не закупочное решение**: тайминг подачи звонков, concurrent GPU memory, batching и model-specific latency сильно меняют расчёт.
- Text Qwen slots: `requests_in_window × model_service_seconds` относительно `available_worker_seconds × target_utilization`; нельзя оценить конкретные GPU или токен/сек без benchmark.
- Storage: исходные звонки/tickets находятся в ticket DB 1 год (PDF); наша деривативная retention должна быть отдельно согласована. Не считать, что у новой системы автоматически есть право хранить raw media ещё один год.
- План испытаний: p95 daily/weekly peaks, 1h outage+replay, burst attachments, 100% idempotent resend, degraded ASR/Qwen fallback, p90 digest delivery. Значения SLA и cost задаются только после интервью с владельцами процессов.

## Минимальные contracts и границы безопасности

- Input `SupportEventV1` с `source_system`, `source_ticket_id`, `product_id`, `ingested_at`, `source_created_at?`, media refs, provenance, policy scope.
- Output `RequestAnalysisV1` с независимыми полями `business_journey`, `request_intent`, `symptom_code`, `relation_type`, `urgency`, `root_cause_status=unknown`.
- `ProductSignalV1`: `evidence_ticket_keys` только разрешённые, `observed_unique_ticket_count` считает код, `coverage_status` явный, `routing_status=resolved|needs_human`.
- `ProductFeedbackV1`: роли продукта, решения, timestamps и audit; нет внешних LLM/API, нет автоматической выдачи паролей, OTP и изменений юридических документов.
- Внутренняя идемпотентность доставки через составной ключ `scope+signal+window+revision`; для replays отсутствие дублирования *effect* проверяется по журналу. Отказ чтения источника != отсутствие жалоб.

## Условия перед окончательным утверждением архитектуры

Требуется обсудить с владельцами данных: источник/политика PII, возможность полнотекстовой выгрузки, сроки правомерного хранения дериватов, точный внутренний Qwen endpoint, owner registry и правила создания авто-дайджеста. Отдельно — сколько support team сейчас тратит на отчётность, чтобы экономический эффект не базировался на выдуманном baseline.

**Реализация приложения и подключение модели не входят в этот утверждённый documents-first scope.** Данные и diagrams служат только для конкурсных материалов.
