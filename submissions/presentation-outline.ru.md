# План презентации (10 слайдов) — Intelligence Cup 2026 / «Газпром нефть»

**Область решения:** десятки внутренних и внешних цифровых продуктов компании, в пределах допустимого доступа. **Webneft — лишь один продукт с семью примерами на стр. 6 PDF**, не название или цель всей AI-системы. Это source-storyboard, а не подтверждение внедрения; реальные результаты моделей и внедрения не измерены.

| № | Заголовок (RU) | Главная мысль / визуал | Критерий |
|---:|---|---|---|
| 1 | «От обращений к развитию цифровых продуктов» | Одна корпоративная петля Product Feedback Intelligence для разных продуктов | Цель PDF стр. 1–2 |
| 2 | «Десятки продуктов, два канала, нет исходного baseline» | Тикеты+звонки → внутренняя AI аналитика → разные product teams; ≈40 сотрудников на весь охват | Контекст стр. 2,4 |
| 3 | «Webneft — один иллюстративный кейс» | Семь обращений Webneft из PDF; same topic ≠ same technical incident | Иллюстрация стр. 6 |
| 4 | «Hybrid C: 5 логических блоков» | Многопродуктовая архитектура с внутренними Qwen ASR/VL/text, trusted registry и outbox | Архитектура |
| 5 | «Данные и границы доверия» | source → product_id + taxonomy_version + PII controls → internal model; no external egress | Безопасность |
| 6 | «LLM предлагает, backend проверяет» | Tools, доверенный product_id→team, фолбек при unknown product и счетчик tickets | Tools |
| 7 | «Что получает продуктовая команда: проверяемый сигнал» | Три **полностью синтетических** ticket по теме Webneft PDF №5 → Qwen topic → trusted count=3 в наблюдаемом наборе → evidence-backed Product Insight Draft, feedback pending; причина и тренд не установлены | Prompt + end-to-end business outcome |
| 8 | «Offline → Shadow → Controlled» | Проверяемость, adversarial cases, 2 human labelers, cross-product holdout и release gates | Тестирование |
| 9 | «Измеряем ценность по каждому продукту» | TPI, routing, actionable precision, reviewed coverage и saved support time; aggregate + slices | МЕТРИКИ (отдельный пункт 5) |
| 10 | «3 года, 3 сценария и альтернатива без AI» | Условная реализуемая выгода, no measured ROI; compare manual/BM25/Hybrid | Финансовая модель |

## Требования к презентации
- Бренд решения — мультипродуктовый агент «Газпром нефти», не Webneft-only продукт.
- Webneft упоминается как один продукт **только на странице 3 и в синтетическом end-to-end примере на странице 7**; возможен подпункт в dataflow как исходное доказательство, не общий ontology.
- Не смешивать данные / политику / taxonomies разных продуктов; product_id, taxonomy_version и product→team справочник задаёт доверенный backend.
- Схемы редактируемые, желательно Mermaid-source плюс native PowerPoint shapes; ~10 слайдов, 16:9, крупный русский текст.
- 40 support managers — весь охват (PDF стр.4), не сорок сотрудников Webneft.
- Пункты 1–4,6 в самостоятельном основном документе <=15k символов; отдельный item-5 .md; никаких ссылок на вложения для обхода лимита.
- Макроэкономические ставки и финансовые результаты являются сценарными; отдельный настоящий pilot и independent human review остаются необходимыми.

## Согласование с пересмотренной презентацией

На слайде 7 показан **только демонстрационный output**, а не результат Qwen или реальная отправка product team: три выдуманных ID `SYN-QUEUE-001..003`, observed count=3 в неполном учебном наборе, source coverage неизвестен, root cause не установлена, owner только из backend registry, `delivery_status=draft`, feedback ожидается. Исходный PDF, стр.6, содержит один текстовый пример аналогичного симптома, НЕ три реальных повтора. [Сценарий, примеры JSON и Mermaid](../docs/case-studies/webneft-synthetic-product-insight.md).
