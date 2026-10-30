# ProductPulse AI — Intelligence Cup 2026

> **Статус: направление архитектуры Hybrid AI Agent выбрано владельцем репозитория (ADR-001); согласование с командой и реализация ещё впереди.** Работающий прототип и измеренные результаты пока НЕ заявлены.

Командный репозиторий для кейса «Искусственный интеллект» чемпионата **Intelligence Cup 2026 от «Газпром нефти»**. Цель — спроектировать проверяемого ИИ-агента, который превращает обращения пользователей цифровых продуктов в доказательные и своевременные сигналы для продуктовых команд.

## Задача и ценность

**Пользователь → техническая поддержка → выявление повторяющейся проблемы → ответственный владелец продукта → подтверждённый insight / issue → обратная связь.**

Мы оптимизируем не только классификацию заявок, но и **Time-to-Actionable-Insight (TTAI)**: время от первого релевантного обращения до принятой продуктовой командой информации, по которой можно действовать. При этом отдельно контролируем долю пропущенных проблем, ложные предупреждения, трудозатраты и экономическую эффективность.

## Принципы

- **Evidence first:** утверждения о проблеме подтверждаются ID обращений; причины неисправности не выдумываются.
- **Human-in-the-loop:** изменение внешних тикетов и эскалации — только согласно политике и полномочиям.
- **Hybrid > LLM-only:** ML/статистика для поиска и измерений; LLM для анализа сложного контекста и отчёта.
- **Russian-first:** проверка на русскоязычных запросах, включая коды ошибок, версии и сокращения.
- **Data safety:** никаких реальных персональных данных, закрытых выгрузок или секретов в публичном репозитории.
- **Reproducibility:** разметка, baseline, фиксированные разбиения, логи, воспроизводимый эксперимент.
- **Claims discipline:** различать проверенные цифры, гипотезы и сценарные оценки.

## Начните здесь

| Артефакт | Что читать |
|---|---|
| [ADR-001 — Hybrid AI Agent](docs/architecture/decisions/ADR-001-hybrid-ai-agent.md) | Выбранное архитектурное направление и trade-offs |
| [Design spec](docs/superpowers/specs/2026-10-30-productpulse-system-design.md) | Архитектура, ограничения, альтернативы, бизнес-процесс |
| [Requirements & unknowns](docs/requirements/requirements-and-assumptions.md) | Требования, предположения, вопросы наставникам |
| [Data contracts](docs/architecture/data-contracts.md) | Сущности, инварианты, API/события |
| [Evaluation protocol](docs/evaluation/experiment-protocol.md) | Как получать реальные измерения |
| [Public dataset catalog](docs/data/dataset-catalog.md) | Два реальных открытых источника и ограничения лицензий |
| [Original-source verification](docs/data/source-verification-report.md) | Скачанные издательские CSV, MD5/SHA-256, реальная структура и CI evidence |
| [Dataset validation design](docs/superpowers/specs/2026-10-30-public-dataset-validation-design.md) | Проверяемые гипотезы и protocol до получения данных заказчика |
| [Financial model](docs/business/financial-model.md) | ROI без подмены данных предположениями |
| [Roadmap](docs/project/roadmap.md) | Этапы и критерии готовности |
| [31 октября: архитектурное ревью](docs/project/review-2026-10-31.md) | Индивидуальные предложения и решение команды |
| [Engineering workflow](AGENTS.md) | Superpowers, TDD, review, условия мержа |

### Реализационные планы

1. [Ticket intelligence core](docs/superpowers/plans/2026-10-30-ticket-intelligence-core.md)
2. [Agent, approvals and demo](docs/superpowers/plans/2026-10-30-agent-and-demo.md)
3. [Evaluation and business case](docs/superpowers/plans/2026-10-30-evaluation-and-business.md)
4. [Public dataset baseline (DRAFT)](docs/superpowers/plans/2026-10-30-public-dataset-baseline.md) — первый этап после согласования дизайна

**Важно:** планы — для обсуждения и утверждения. Они не являются отчётом о выполненных задачах или тестах. Внешние datasets для предварительной проверки: Zenodo Classification of IT Support Tickets (2,229 размеченных обращений) и Mendeley Help Desk Tickets v3 (операционные события). Оригиналы скачаны и проверены GitHub Actions 30.10.2026, см. [source verification](docs/data/source-verification-report.md). Zenodo CSV включены в репозиторий, Mendeley оригиналы доступны из краткоживущего workflow artifact. ML benchmark ещё не запускался.

## Выбор архитектуры

**Hybrid AI Agent** — выбранный владельцем репозитория вариант: deterministic ingestion и policy, ML/NLP для classification/retrieval/clustering, ограниченный evidence-based LLM workflow, human approval и измеряемая бизнес-ценность. Команда подтверждает детальный дизайн на архитектурном ревью 31.10.2026. См. [ADR-001](docs/architecture/decisions/ADR-001-hybrid-ai-agent.md).

## Техническая гипотеза

Python 3.11+, FastAPI, PostgreSQL/pgvector, локальный/разрешённый multilingual encoder, BM25, scikit-learn, LangGraph для контролируемого workflow, простой React/Streamlit UI, Docker Compose. Модель и стек должны быть выбраны **по результатам baseline и ограничений заказчика**, а не по популярности библиотек. Монолитный backend с модулями предпочтительнее преждевременных микросервисов.

## Временные ориентиры

- **31.10.2026** — совместное архитектурное ревью и утверждение гипотез;
- **01–10.11** — данные, ground truth, baseline и ML core;
- **11–15.11** — прототип agent workflow и mock-интеграция;
- **16–22.11** — воспроизводимые эксперименты, ROI, итоги;
- **23–25.11** — материалы защиты, репетиции, backup demo;
- **26.11** — объявленный очный финал в Санкт-Петербурге (подтвердить организационные детали).

## Источники о кейсе

- [Объявление СПбГЭУ (06.10.2026)](https://unecon.ru/announcements/uchastvuj-v-ezhegodnom-kejs-chempionate-intelligence-cup-ot-gazprom-nefti/)
- [Обзор кейсов CNews (19.10.2026)](https://www.cnews.ru/news/line/2026-10-19_otkryt_priem_zayavok_na_ezhegodnyj)
- [Энергия+ (23.10.2026)](https://e-plus.media/news/ot-ii-agenta-do-klientskoj-analitiki-rossijskie-studenty-predlozhat-czifrovye-resheniya-dlya-biznesa/)

Детальное ТЗ, scoring rubric, формат датасета, внутренние системы и ограничения развёртывания пока не подтверждены. Не выдавайте выбранные здесь архитектурные допущения за инфраструктуру «Газпром нефти».

## Лицензия и данные

До выбора лицензии команды **не считать материалы разрешёнными для стороннего коммерческого использования**. Публичные примеры — синтетические или из открытых источников с указанием происхождения и прав. Никаких коммерческих секретов или персональных данных.
