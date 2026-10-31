# Расчёт нагрузки по микросервисам — Gazprom Neft Intelligence Cup 2026

**Статус:** **проектный сценарий, а не измерение**. Исходный PDF, стр. 4, сообщает примерно **40 сотрудников поддержки** по всему охватываемому контуру продуктов. В PDF **нет** числа обращений в день, доли звонков/картинок, длительности звонков, измеренного Qwen RTF, token throughput, времени обработки, дневного профиля, конфигурации GPU или SLO. Ни один приведённый ниже результат нельзя приписывать реальной инфраструктуре «Газпром нефти».

**Machine-readable assumptions:** [`per-service-capacity-scenario.json`](./per-service-capacity-scenario.json); автоматическая независимая пересчётная проверка выполняется валидатором документов. Разделять три понятия: потребность в обработке, нижняя оценка конкуррентных слотов и фактическое число процессов/GPU **после** benchmark.

## Входные гипотезы и единицы

| Параметр | Значение | Основание |
|---|---:|---|
| Support managers `N` | ≈40 | **Единственная количественная исходная величина из PDF** |
| Обращений на сотрудника за сутки `q` | 20 | гипотеза |
| Активное окно поступления `H` | 8 ч/сутки | гипотеза; 24-часовую интенсивность нельзя принимать за рабочий пик |
| Максимальный час / средний активный час `F` | 3 | гипотеза, **не фактический p95** |
| Целевая занятость вычислительного слота `u` | 0,70 | запас на burst, retry, деградацию; гипотеза |
| Доля телефонных обращений `p_a` | 30% | гипотеза |
| Средний аудиофайл `L_a` | 3 минуты | гипотеза |
| Скорость ASR `RTF` | 0,5 (30 с вычислений на 60 с аудио) | **не измерена**, учебное значение |
| Доля обращений с 1 разрешённым изображением `p_v` | 20% | гипотеза |
| Время обработки 1 изображения `s_v` | 8 с | гипотеза, **не Qwen-VL benchmark** |
| Текстовая Qwen на обращение | 1 вызов, 1200 входных + 200 выходных токенов | гипотеза, не контекстное окно/производительность модели |
| Время модельного запроса `s_t` | 12 с | гипотеза, **не измеренная скорость Qwen 3.8** |
| BM25 retrieval | 1 запрос на обращение | гипотеза |
| Запись метаданных/аудита в DB | 3 операции на обращение | гипотеза, не реальные SQL-запросы |
| Внутренние дайджесты | 20 в день **отдельной гипотезой** | **не** «20/800 = реальная доля подтверждённых проблем» |

## Расчёт спроса: 24-часовой средний ≠ рабочий peak

```text
Tickets/day                     Q = N × q = 40 × 20 = 800
24-hour mean arrival rate       800 / (24 × 3600) = 0.00926 tickets/s
8-hour active mean arrival rate 800 / (8 × 3600) = 0.02778 tickets/s
Assumed peak within active H    λpeak = (800/8) × 3 = 300 tickets/h = 0.08333 tickets/s
Conservative slot requirement   c = ceil(λpeak × measured_service_seconds /(3600 × u))
```

`c` is a *service-concurrency-equivalent lower bound* under a simple average-work model. It is NOT a reliable p95 latency guarantee, because arrival bursts, service variance, dynamic GPU batching, memory and correlated retries are excluded. The factor `F=3` is a **hypothetical maximum observed hour**, not an extra ×3 demand continuously throughout eight hours; an eight-hour mean remains 100/h.

## Расчёт по всем пяти логическим блокам

| Логический блок | Исходная единица и расчёт | При гипотетическом пике | Ресурс и горизонтальное масштабирование | Безопасный fallback |
|---|---|---|---|---|
| **1. Ingestion** | 800 tickets/day; `λpeak=300/h`; источник read-only, cursor, source ID, `ingested_at` | **0,0833 ticket/s**, объём аудио/файлов отдельно (не предполагать нулевой) | DB/API I/O, bounded pagination, checkpoint and replay; не нагружать исходный support transactional DB без лимитов | Полнота = unknown; backfill с теми же source IDs |
| **2. Multimodal ASR/VL** | ASR `800×0,30×3=720 аудиомин/день`. `c_ASR=ceil(720×0,5×3/(480×0,7))=4` | **90 calls/h**, **270 audio-min/h** по входу; `135 worker-min/h` при RTF .5. Для изображений `800×0,20=160/день`, `60 images/h`; `ceil(60×8/(3600×0,7))=1` VL-slot | GPU/CPU/model memory, отдельные очереди, токены доступа к медиа; **4 и 1 — только слоты при выдуманной скорости, НЕ число GPU** | Retry/idempotency, статус `media_unavailable`, human analysis без откладывания срочных запросов |
| **3. Intelligence + Retrieval** | Текст: 1 вызов/ticket; `300 × 1200 /3600 =100 input tok/s`, `300×200/3600=16,67 output tok/s` на пике. `c_Qwen=ceil(300×12/(3600×0,7))=2` | **300 inferences/h**, ~**2 условных concurrent slots**, BM25 **0,0833 retrieval QPS** (1/ticket) | Реальное профилирование prefill, decode, model batching, p95 ответа и VRAM обязательно; retrieval CPU/index можно масштабировать отдельно | Rules+BM25 и human review; нельзя подменять root cause или own team LLM-догадками |
| **4. Aggregation + Routing** | Пример: 3 служебные записи/ticket ⇒ `300×3/3600 =0,25 DB writes/s`; source evidence top-k ограничен, индекс по `scope+product+source_ticket` | **0,25 write op/s** при выбранной модели записи; фактическая SQL нагрузка зависит от join, retrieval, окон, coverage audits | CPU/PostgreSQL I/O, indexes, limited window queries, dedup, watermark and per-product partitions; **не** считать `0.25` полной нагрузкой БД | Unknown coverage ⇒ **только** observed count по policy, не рост; unknown owner ⇒ human triage |
| **5. Delivery + Feedback** | Отдельная гипотеза **20 advisory digest/day**: `20/8×3=7,5/h` | **≈0,00208 digest/s** без retransmission; retries могут увеличить фактические события | Internal outbox, unique delivery key, ACK and human feedback journal; capacity by message endpoint SLO | Queue, retry/backoff, idempotent effects, no external delivery or unauthorized routing |

**Что здесь принципиально:** число обращений и размеры модели не измерены; даже `c_Qwen=2` нельзя выдать за «две GPU». Потребность во входных/выходных токенах надо benchmark-ить отдельно из-за различий в prefill/decode. VL слот =1 относится **только** к одному гипотетическому типу изображения; PDF допускает и другие вложения (не обязательно картинки), которые требуют разрешённого parser pipeline и size/MIME policy.

### Почему не пять отдельных сетевых микросервисов с первого дня?

Пять **логических зон ответственности** — это хороший способ оценить нагрузку и права. На старте достаточно предложенных **трёх физически разворачиваемых процессов**: `ingestion worker`, `bounded media+text model worker pools`, `API+aggregation+delivery worker` с общим Postgres и внутренним broker. При этом ASR, VL и text inference имеют **отдельные лимиты очередей**, чтобы длинные звонки не блокировали краткие текстовые обращения. Разделять новые процессы/узлы следует после измерения saturation, p95 queue wait, GPU VRAM, failure blast radius и требования независимого обновления моделей.

**Trade-off:** это сокращает число deployment/monitoring границ и interservice hops; недостаток — потенциально общая точка отказа API/aggregation/delivery в MVP. Компенсировать outbox, bounded retries, replay, health checks; при реальном отказе разделять worker и API по измерениям, а не по желанию «микросервисности».

## Что измерить для реального sizing перед production

1. **Ticket source:** реальные `tickets/hour` p50/p95/p99, доли звонков, распределения длительности (не только среднее), типы/размеры attachments, все доступные продукты/каналы, источник может не охватывать всё.
2. **ASR/VL:** `RTF` и p95 на реальных разрешённых типах медиа, число независимых model slots с ограничениями VRAM и batching, ошибки/повторы.
3. **Qwen text:** input/output токены, p50/p95/p99 latency и token-per-second под целевым concurrency, retry/invalid JSON, VRAM. Название **«Qwen 3.8»** берётся из PDF как есть; endpoint и параметры неизвестны.
4. **DB + retrieval:** фактические SQL statements/event, индекс/scope, percentile latency, query load, growth under one-year source retention. Retention derived data согласовать отдельно.
5. **Delivery:** число созданных/approved отправленных product insights, latency outbox/ACK, retries, undelivered backlog, product-team feedback, strict idempotency.

**Sizing exit gate:** модель очередей и service concurrency должна пройти shadow load tests (сSynthetic anonymized data), включая 1h outage/replay, 3× peak, oversized audio/image, missing Qwen and late backfill. После фактического benchmark заменить все обозначенные иллюстративные параметры. Не делайте закупочные выводы из этой учебной таблицы.

**Финансовая связка:** стоимость ASR/Qwen для внутренних сервисов по условию не тарифицируется, но complexity/time/risks интеграции не равны нулю. Сравнение rules/BM25-only остаётся обязательным. Не путать финансовые сценарии (5/15/25 минут экономии) с числом обращений (20 на менеджера) — это независимые гипотезы.
