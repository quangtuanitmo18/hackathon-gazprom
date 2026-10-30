# ProductPulse AI — System Design Spec

**Date:** 2026-10-30  
**Status:** HYBRID ARCHITECTURE SELECTED by repository owner (ADR-001, 2026-10-30); detailed specification still awaits team review on 2026-10-31  
**Business:** Intelligence Cup 2026, кейс «Искусственный интеллект»  
**Audience:** разработчики MVP, ML/AI-инженеры, product/business lead, наставники

## 1. Intent / why

Десятки цифровых продуктов получают обращения пользователей. Нужен механизм, который обнаруживает повторяющиеся и существенные проблемы, агрегирует доказательства и передаёт значимые сигналы ответственным продуктовым командам, сохраняя контроль специалистов. Результат — не чат-бот, а **actionable feedback loop** между support и product engineering.

## 2. Stakeholders и цели

- Support specialist: меньше ручной классификации/поиска дублей; возможность быстро отклонить ошибочное предложение.
- Support lead: видеть повторяемость, рост сигналов, backlog эскалаций и нагрузку.
- Product owner: получать релевантные, не дублирующиеся и проверяемые issue summaries.
- Developer: видеть конкретные симптомы, версии, ссылку на подтверждающие обращения, а не придуманный root cause.
- Security / IT: хранение данных и tool permissions в допустимом корпоративном контуре.

**North star:** Time-to-Actionable-Insight (TTAI), от первого релевантного обращения до принятого product team actionable insight; обязательно вместе с incident detection recall и alert precision. Нельзя улучшать TTAI ценой игнорирования сложных проблем.

## 3. Goals

G1. Multi-dimensional classification: intent, product/component, symptom, error codes, version and confidence/unknown.  
G2. Semantic candidate retrieval с сохранением точных кодов ошибок и версий.  
G3. Incident-level grouping, а не только тематические clusters; неизвестные/спорные пары идут на review.  
G4. Problem registry: lifecycle, linked tickets/issues, update instead of duplicate creation.  
G5. Trend/impact signals, включая критичные единичные инциденты.  
G6. Agent report, grounded in ticket IDs, ownership registry и issue lookup.  
G7. Human feedback, audit, permissioned publishing.  
G8. Reproducible experiment + честный финансовый сценарий с явными предположениями.

## 4. Non-goals / anti-goals

- Не заменять поддержку чат-ботом и не пытаться автоматически устранять ошибки инфраструктуры.
- Не управлять производственными/OT-системами и не выполнять произвольный SQL или shell от имени LLM.
- Не заявлять production readiness, SLA или ROI до испытаний.
- Не вводить Kafka/Kubernetes/микросервисы без измеренной необходимости.
- Не кластеризовать по одному similarity threshold без анализа ложного объединения.

## 5. Constraints and unverified assumptions

- Команда 2–4 участника; финал планируется на 26.11.2026.
- Внутренний ITSM vendor, объём заявок, организационная структура и разрешённые модели **не известны**.
- Dataset может быть небольшим по устному пересказу встречи; подтвердить с организаторами.
- Рабочая гипотеза для prototype: Python **3.11+**, FastAPI, PostgreSQL + pgvector, scikit-learn, BM25, multilingual encoder; LangGraph agent только для actionable clusters; Docker Compose. Выбор не является обязательством заказчика.
- Личные/корпоративные данные запрещено публиковать в открытом GitHub. Исследовать возможность локальной inference и требования размещения.
- Внешние действия по умолчанию **read-only/mock**, публикация после policy check и approval.

## 6. Alternatives

| Approach | Benefits | Tradeoffs |
|---|---|---|
| A. LLM-only triage | Быстрый proof of concept, мало отдельных моделей | Стоимость per-ticket, нестабильность, hallucinations, трудная калибровка |
| B. Rules/ML-only | Дешево, детерминированно, объяснимо | Сложный свободный текст, summary/insights менее гибкие |
| C. Hybrid agent-assisted (owner-selected, team review pending) | ML + metadata для core, LLM для evidence-based recommendations; измеримость и controls | Больше интеграции и ответственности за контракты |

**Owner-selected direction:** C — Hybrid AI Agent, documented in [ADR-001](../../architecture/decisions/ADR-001-hybrid-ai-agent.md). LLM не источник числовой статистики, прав доступа или подтверждённой причины дефекта. Это выбор архитектурного подхода владельцем репозитория, а не окончательное согласование всех деталей с командой/заказчиком.

## 7. Logical architecture

1. **Input adapters:** CSV/JSON для MVP; дальнейшая поддержка webhooks/polling.
2. **Normalizer + privacy guard:** дедупликация events, timestamps UTC, минимизация PII, исходные ID.
3. **Classifier + extractor:** intent/product/component/symptoms/error_codes/version, nullable/unknown.
4. **Candidate retriever:** BM25 + multilingual dense search с product/component metadata constraints.
5. **Pair verifier + clusterer:** same_incident / related_topic / different / uncertain; не допускать transitive chain merging без проверки.
6. **Problem registry:** identity, lifecycle, linked ticket IDs and optional external issue ID; idempotent updates.
7. **Trend and severity:** rolling counts, distinct users, historical baseline, critical bypass.
8. **Agent workflow:** tools get_evidence, search_existing_issues, get_owner, get_metrics, generate grounded JSON.
9. **Policy + human approval:** verify claims, permission and idempotency; no arbitrary external writes.
10. **Evaluation + dashboard:** event replay, precision/recall, cost and latency by run ID.

Single modular app + worker; PostgreSQL source of truth; optional pgvector; no needless distributed infrastructure.

## 8. Workflow and state

Ticket: received → normalized → classified → candidates_retrieved → matched|uncertain → indexed.  
Problem: candidate → monitored → review_needed → approved|rejected → published|updated → investigating → resolved|reopened.

Every transition has timestamp, actor (system/person), input evidence and audit event. A notification must have stable idempotency key based on problem ID + event type + revision. Existing problem gets updated; a new task must not be created for every repeated ticket.

## 9. Data and trust boundaries

Canonical contracts in [data-contracts](../../architecture/data-contracts.md). Core entities: Ticket, TicketEvent, TicketClassification, TicketMatch, Problem, ProblemEvidence, InsightProposal, ReviewDecision, ExternalIssueLink, EvaluationRun.

- Text from tickets is **untrusted data**, not instructions for the agent.
- Ticket ID references are mandatory for material report claims.
- Unknown product or owner => needs_review; never invent the owner team.
- Access to ticket evidence must be filtered by authorized product scope; redact PII before inference.
- No inference API without security sign-off where real corporate data is involved.
- All side effects go through backend-controlled tools with audit.

## 10. Error handling

- Duplicate webhook: idempotency; do not recount.
- Missing timestamps / invalid product: validation error or quarantine; do not silently infer.
- Very short or ambiguous ticket: abstain / manual queue.
- Embedding outage: keyword/rule fallback; ticket preserved for retry.
- LLM timeout/invalid JSON: retry budget → deterministic summary / human review; no unverified send.
- False merge: split with lineage and reviewer rationale; reversible history.
- False split: review merge; never conflate distinct issue IDs silently.
- Missing owner or existing tracker unavailable: do not publish and do not claim duplicate-checked.
- Confidential content/prompt injection: ignore embedded commands, permissions enforced by runtime.

## 11. Evaluation and acceptance

Protocol: [experiment-protocol](../../evaluation/experiment-protocol.md). Two independent result types:
- **Technical:** macro F1, retrieval Recall@K, same-incident pairwise P/R/F1, B-cubed F1, alert precision/recall, routing accuracy, evidence validity.
- **Business:** TTAI distribution with undetected incidents counted, manual vs assisted effort incl. corrections, alerts per accepted insight, OPEX measured, modelled capacity-value ROI.

No fabricated target metrics or claimed gains. Provisional gate for MVP: repeatable evaluation, inspectable hard negatives, no uncontrolled external writes, working offline/mock demo.

## 12. Deliverables and rollout

- 31.10: approved architecture/alternatives, open questions, ownership, scope.
- 01–10.11: dataset profile, annotation, benchmarks, ML core.
- 11–15.11: agent proposal + human review + mock issue integration.
- 16–22.11: chronological replay, experiment, financial sensitivity.
- 23–26.11: presentation, risk discussion, recorded backup demo.

Pilot path: read-only historical → shadow mode → team-approved actions → limited production rollout, contingent on permissions, security and measurement.

## 13. Open decisions (team and mentors)

D1: source ITSM and its actual workflow; D2: dataset fields/quality and privacy approval; D3: what exactly counts as same incident; D4: primary business metric; D5: permitted models/deployment; D6: who approves issue creation; D7: evaluation resources and participation of real support specialists; D8: детальный scope/stack и критерии готовности согласованы командой. Направление Hybrid выбрано владельцем репозитория в ADR-001, окончательная командная проверка ещё предстоит.

See [assumptions](../../requirements/requirements-and-assumptions.md) and [31 Oct review](../../project/review-2026-10-31.md). Until the remaining decisions are recorded and the team signs off, this document is a **proposal with a selected architectural direction**, not an approved implementation specification.
