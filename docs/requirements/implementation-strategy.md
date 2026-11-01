# Стратегия V2: сначала кейс, потом узкий прототип

## Phase A — Обязательное содержание прежде кода
1. Архитектура и границы интеграции: 40 менеджеров — сценарное число, не traffic.
2. Tools, prompt, governance: три класса (`same_problem`, `topic`, `actionable`) и проверяемая ссылка на источник.
3. KPI/ретроспективный baseline и financial scenarios; документы в официальных форматах.
4. План интеграции: ticket DB 1 год + звонки + изображения/вложения; внутренние модели без внешнего egress.
5. Проверка собственных материалов на полное соответствие PDF, затем ревью финальных артефактов.

## Phase B — Только демонстрационный vertical slice
- `TicketIngest` с idempotency, two clocks `source_created_at`/`ingested_at` и доказуемым source ID.
- Псевдонимизация; bounded internal-only ASR/VL adapters и локальный text model mock. Никакого «Qwen 3.8» как конкретного package/API, пока владелец окружения не подтвердит модель и доступ.
- `TopicClassifier` и `RecurringSignalAggregator` + hybrid baseline (BM25 / lexical) и полностью отдельные support requests.
- `ProductInsightDraft` evidence-linked, conservative fallback, outbox, fake internal inbox; feedback accepted/rejected/needs-info.
- Тестовый Webneft storyline №5 + **явно помеченные синтетические** повторения, реальные 7 примеров никогда не объявлять gold repetitions.
- Учебный dashboard только после демонстрации правильного routing и измеримых метрик. Стабильная оценка release не зависит от demo UI.

## Что из V1 переносить — выборочно
| V1 | Решение | Критерий переноса |
|---|---|---|
| Source-scoped ticket identity, canonical DTO | Адаптировать | Сохраняет provenance и новый `ingested_at` |
| PostgreSQL, idempotency, audit | Перенести паттерн | Простой migration path и tenant boundary |
| BM25 | Baseline, не единственный группировщик | Gold-set eval и non-transitivity |
| Keycloak auth | Опционально для demo | Важен только если UI требует реальных ролей |
| Двухуровневый 2+1 human merge | Изменить | Не блокирует обычные product digests |
| Pending verified-only insight | Расширить | Передаёт **некритичные повторяющиеся** темы без false-incident claim |
| Safe alias-only LLM adapter | Оставить как security skeleton | Не считать AI-интеллектом без содержательного сигнала |

## V2 non-goals
- Новая production ticketing platform / 15 микросервисов; деплой в контур «Газпром нефти»; внешние LLM API.
- Псевдорепрезентативные метрики из семи PDF-примеров, выдуманные повторения в реальной компании.
- Гарантированная окупаемость без данных о стоимости, выдуманный доступ к Qwen endpoint.
- Запись в реальный task tracker или автоматическое изменение бизнес-систем без явного согласования.

## Отдельные acceptance gates
- **Submission:** пункты 1–4,6 <=15k символов, пункт 5 .md, 10 слайдов, русские формулировки, 6/6 по критериям и реалистичные unknowns.
- **Optional software:** offline unit + integration, privacy and prompt-injection tests; replay temporal correctness, real model eval only when available and permitted; no external egress.
- Keep `main` untouched and no merges without independent human review.


## Обязательная поправка об охвате (PDF p.2 vs p.6)

Решение конкурсного кейса рассчитано на **множество цифровых продуктов**; `Webneft` — один из примеров для объяснения и проверки. Для каждого подключённого продукта нужен доверенный `product_id`, независимая версия taxonomy, отдельные source authorization, per-product retrieval и обновляемый `product→team` registry. Отсутствие конфигурации блокирует auto-send; универсальные issue intent общие, отраслевые journey/symptom codes — **нет**. Базовые KPI и ~40 support personnel относятся ко всему контуру, а не к Webneft как отдельному продукту. Прототип остаётся опциональным.
