# План презентации (10 слайдов) — Intelligence Cup 2026 / «Газпром нефть»

**Область решения:** десятки внутренних и внешних цифровых продуктов компании, в пределах допустимого доступа. **Webneft — лишь один продукт с семью примерами на стр. 6 PDF**, не название или цель всей AI-системы. Это source-storyboard, а не подтверждение внедрения; реальные результаты моделей и внедрения не измерены.

| № | Заголовок (RU) | Главная мысль / визуал | Критерий |
|---:|---|---|---|
| 1 | «От обращений к развитию цифровых продуктов» | Одна корпоративная петля Product Feedback Intelligence для разных продуктов | Цель PDF стр. 1–2 |
| 2 | «Десятки продуктов, два канала, нет исходного baseline» | Тикеты+звонки → внутренняя AI аналитика → разные product teams; ≈40 сотрудников на весь охват | Контекст стр. 2,4 |
| 3 | «Webneft — один иллюстративный кейс» | Семь обращений Webneft из PDF; same topic ≠ same technical incident | Иллюстрация стр. 6 |
| 4 | «Пять логических блоков — три процесса MVP» | Векторная архитектура + **сценарная** нагрузка 300 обращений/ч, 4 ASR + 1 VL слота, 2 Qwen text слота, 0,25 DB writes/s и 7,5 дайджестов/ч; **slots ≠ GPU, реальные замеры отсутствуют** | Архитектура, microservice rationale и нагрузка (PDF p.7) |
| 5 | «Данные и границы доверия» | source → product_id + taxonomy_version + PII controls → internal model; no external egress | Безопасность |
| 6 | «LLM предлагает, backend проверяет» | Tools, доверенный product_id→team, фолбек при unknown product и счетчик tickets | Tools |
| 7 | «Что получает продуктовая команда: проверяемый сигнал» | Три **полностью синтетических** ticket по теме Webneft PDF №5 → Qwen topic → trusted count=3 в наблюдаемом наборе → evidence-backed Product Insight Draft, feedback pending; причина и тренд не установлены | Prompt + end-to-end business outcome |
| 8 | «Offline → Shadow → Controlled» | Одинаковый holdout A/manual → B/rules+BM25 → C/internal Qwen; two-labeler gold; выигрыш C не предполагается, а проверяется; release gate по 95% Wilson CI | Тестирование |
| 9 | «Два времени сигнала: 5 минут ≠ 96 часов» | **Отдельный полностью синтетический пример часов**: 26.10 09:00 first_relevant_ingested → 30.10 09:00 qualified → 30.10 09:05 sent; TPI 5 мин vs E2E 96 ч 05 мин. undelivered/eligible, backlog, независимая precision ≥0,80, routing ≥0,95, net support minutes, своевременное решение ≠ разрешение проблемы; все пороги предложены, НЕ достигнуты | KPI и честные знаменатели (пункт 5 .md) |
| 10 | «3 года, 3 сценария и альтернатива без AI» | PV 123 тыс./1,64 млн/7,39 млн ₽ (учебные сценарии); макро: ключевая ставка РФ 14% на 30.10.2026, CPI 6,35% сентябрь г/г; стресс PV базы r=14% → 1,53 млн ₽, это НЕ ставка WACC. Выбор Hybrid только при доказанном приросте над BM25 | Финансовая модель |

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

## Final Word/Deck alignment checkpoint (2026-10-31)

- **GitHub Word source**: `submissions/main-solution.ru.md` = **VERSIONED CURRENT LENGTH (recompute before export)**. Previous 4-page Professional DOCX/PDF was generated **before quality upgrades** and must NOT be treated as synced final export until rebuilt. This storyboard is updated source, not the old binary.  Calculated values are **scenario-only**, not Gazprom Neft production metrics.
- **Slide 4** embeds five independently recalculated workload blocks: `300 tickets/hour`, ASR 4 and VL 1 hypothetical concurrency equivalents, Qwen text 2 equivalents, DB `0.25 write/s`, outbox `7.5 digests/hour`. Source [scenario JSON](../docs/architecture/per-service-capacity-scenario.json).
- **Slide 9** is a **separate synthetic clock illustration** from the three SYN-QUEUE story tickets on slide 7. KPI source [question-5 Markdown](./05-effect-metrics.ru.md): TPI `qualified_at→sent_at` = 5 minutes but E2E `first_relevant_ingested_at→sent_at` = 96h05 in a fictional example; pilot threshold ≤4h applies ONLY to the former. Include unsent backlog to prevent delivered-only selection bias.
- **Slides 8 and 10 need synchronized binary re-export** to show pre-specified model comparison/CI and dated macro-stress result; the existing slide binaries from earlier session are prior revision and are not claimed current. Other slides remain conceptually unchanged. Independent review of real data/Qwen not performed.
