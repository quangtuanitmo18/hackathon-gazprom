# ADR-001: Hybrid AI Agent for ProductPulse AI

- **Date:** 2026-10-30
- **Status:** ACCEPTED — **architecture direction selected by repository owner**; team review and detailed spec sign-off pending 2026-10-31
- **Decision scope:** architectural approach; **not** selection of exact models, clustering thresholds, licensed dataset, deployment location or live integration
- **Context:** Intelligence Cup 2026 case «Искусственный интеллект»
- **Related specification:** [ProductPulse AI system design](../../superpowers/specs/2026-10-30-productpulse-system-design.md)

## Context / Decision drivers

Компания эксплуатирует десятки цифровых продуктов и хочет передавать повторяющиеся, действительно значимые обращения из техподдержки продуктовым командам быстрее и с проверяемыми доказательствами. Кроме архитектурной концепции необходимы промпты и инструменты агента, механизм обратной связи, показатели эффективности и финансовая оценка.

Constraints: небольшая команда и короткий срок соревнования; ещё неизвестны формат исходного датасета, ITSM-системы, политика моделей и требования к размещению. Ошибки группировки, повторные задачи и ненужные уведомления создают реальные издержки.

## Options considered

| Option | Advantage | Risk / limitation |
|---|---|---|
| A — LLM-only | Быстрый демонстрационный PoC и гибкая обработка текста | Трудно контролировать точность, стоимость на тикет, groundedness и стабильность |
| B — ML/rules only | Базовые метрики, детерминированность и сравнительно низкая цена | Недостаточно гибкая подготовка содержательных reports и проверка многоисточниковых доказательств |
| **C — Hybrid AI Agent** | Измеримые ML-компоненты, ограниченный LLM agent, понятные policy gates | Требует согласованных интерфейсов и интеграционных тестов |

## Decision

**Choose C — Hybrid AI Agent as the baseline direction for the proposal and MVP planning.**

1. **Deterministic pipeline** принимает, нормализует и обезличивает обращения, обеспечивает event deduplication и журналирование.
2. **ML/NLP pipeline** классифицирует тикеты, находит кандидатов через BM25 + multilingual embeddings, выполняет pairwise incident verification и контролируемое clustering.
3. **Problem Registry** хранит жизненный цикл проблемы, версии и связь с исходными ticket IDs; различает *topic similarity* и *same incident*.
4. **Statistical analysis and policy** считает объем, тренд, уникальных пользователей и impact; триггеры не полагаются на свободную генерацию LLM.
5. **Agent workflow** подключается **только к actionable problems**, использует read-only scoped tools для получения evidence, existing-issue lookup, owner routing и формирует structured insight proposal.
6. **Policy engine + human-in-the-loop** проверяет evidence, права и действия; изменение внешнего issue tracker в MVP — только mock и после явного подтверждения.
7. **Evaluation and economics** измеряют и отдельно показывают качество classification/clustering, обнаружение важных проблем, false alerts, время ручной проверки и экономические сценарии.

**Key restriction:** LLM не создаёт статистику, не назначает продуктового владельца из головы, не подтверждает root cause без данных, не получает произвольных SQL/shell/external-write capabilities.

## Proposed MVP technology (not yet binding)

Python 3.11+, FastAPI, scikit-learn, BM25, multilingual embedding model, PostgreSQL/pgvector, optional Redis workers, LangGraph for gated workflow, Docker Compose, simple local review UI. Model selection and runtime/deployment must be confirmed from baselines and policy.

## Expected benefits (hypotheses, NOT measured results)

- Less manual review and false duplicate issue creation.
- Faster actionable insights to product/development teams.
- Traceable routing decisions, failure handling and feedback loop.
- Control of inference cost by calling LLM on a subset of problems instead of every ticket.

## Tradeoffs and risk controls

- **Complexity:** build modular monolith, versioned contracts and mock integration first; avoid unnecessary distributed architecture.
- **False merge / false split:** hard-negative test set, evidence constraints, abstention, reversible registry lineage.
- **Hallucinations / prompt injection:** ticket text untrusted, validated output schema, source IDs, backend permission checks.
- **Operational failures:** retry/idempotency, fallback to rules/manual support, no silent writes.
- **Privacy:** no corporate ticket data or PII in public repository; private model/hosting subject to company approval.
- **Economic uncertainty:** distinguish observed measurements from scenario-based ROI, count human correction time.

## Validation and review gates

- **Owner choice:** complete (2026-10-30).
- **Team design review:** pending (2026-10-31). Discuss A/B/C openly; revise this ADR if team overturns the selected direction.
- **Dataset assessment:** pending; report actual labels and permissions.
- **Baseline comparison:** pending; BM25/dense/hybrid and incident-level metrics.
- **Agent security & approval tests:** pending.
- **Chronological replay and cost measurements:** pending.

## Consequences / work order

Follow the proposed plans, once design is approved by the team:

1. [Ticket intelligence core](../../superpowers/plans/2026-10-30-ticket-intelligence-core.md)
2. [Governed agent and demo](../../superpowers/plans/2026-10-30-agent-and-demo.md)
3. [Evaluation and business case](../../superpowers/plans/2026-10-30-evaluation-and-business.md)

**Status rule:** selected architecture direction does **not** imply approved product requirements, tested code or measured improvements. Record material changes as new ADR entries rather than rewriting history.
