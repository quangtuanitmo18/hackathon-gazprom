# Webneft V2 — diagrams (GitHub Mermaid preview)

**Project-only draft** for Intelligence Cup 2026, approved conceptual approach C (Hybrid). These diagrams **do not** describe actually deployed Webneft microservices or interfaces. Source of truth for competition rules: 7-page PDF `Кейс_Искусственный интеллект.pdf`. No external LLM/API. The exact text model version called «Qwen 3.8» in the PDF remains unverified.

**How to use:** the Mermaid source files next to this page are canonical; GitHub renders the fenced code blocks below, but rendered layout, Cyrillic text and export must still be visually checked before using in PowerPoint/PDF. For final slides, use a clean vector export and **do not** count linked docs as part of the 15k-character answer.

## 1. C4-inspired Container / логическая архитектура

[Editable source](./c4-containers.mmd)

```mermaid
%% C4-inspired logical container diagram for an internal-only conceptual system.
%% NOT evidence that the named components or interfaces are deployed at Gazprom Neft.
flowchart LR
  subgraph IN["Корпоративный контур — без внешних API/LLM"]
    subgraph SOURCE["Существующие источники"]
      T["Единая ticket-система<br/>обращения, записи звонков, вложения"]
    end
    subgraph PLATFORM["Предлагаемая система Product Feedback Intelligence"]
      I["Ingestion Adapter<br/>cursor, dedup, provenance, ingested_at"]
      M["Multimodal Workers<br/>internal Qwen-ASR + Qwen-VL"]
      R["Data Minimization<br/>маскирование PII/секретов"]
      Q["Intelligence Engine<br/>внутренняя Qwen «3.8»* + lexical baseline"]
      G["Deterministic Aggregator<br/>distinct tickets, окна, coverage"]
      P["Policy & Routing<br/>справочник команд, риск, abstain"]
      O["Delivery / Outbox<br/>идемпотентный внутренний дайджест"]
      S[("PostgreSQL<br/>сигналы, evidence refs, audit")]
    end
    subgraph HUMAN["Люди и процессы"]
      OPS["Техподдержка<br/>штатный процесс срочных запросов"]
      PT["Product Team Inbox<br/>решение + feedback"]
      REV["Эксперт<br/>спорные/чувствительные случаи"]
    end
  end
  T -->|"ticket metadata + media ref"| I
  T -->|"существующий SLA"| OPS
  I -->|"разрешённые media"| M
  I -->|"text"| R
  M -->|"транскрипт/признаки"| R
  R -->|"минимизированные сигналы"| Q
  Q -->|"кандидаты тем"| G
  I -->|"IDs + timestamps"| G
  G -->|"числа + доказательства"| P
  P -->|"только allowlisted канал"| O
  P -->|"нужно решение человека"| REV
  REV -->|"разрешение/отказ"| P
  O -->|"internal digest"| PT
  PT -->|"accepted / rejected / needs_info"| O
  I -.-> S
  G -.-> S
  O -.-> S
  %% * Model name is quoted exactly from PDF, actual endpoint/version unconfirmed.
  classDef boundary fill:#eaf4ff,stroke:#3d76a2,color:#1e3554;
  classDef model fill:#f2ebff,stroke:#7151a9,color:#2b1f48;
  classDef gate fill:#fff2d9,stroke:#a66b17,color:#4d3210;
  class T,I,R,G,S boundary;
  class M,Q model;
  class P,REV gate;
```

## 2. Data Flow Diagram / ролевые границы и данные

[Editable source](./data-flow-trust-boundaries.mmd)

```mermaid
%% Data Flow Diagram (DFD) — proposed security zones; not deployed.
flowchart TB
  subgraph Z0["Зона источника: ограниченные права чтения"]
    SRC[("Ticket DB / call media / attachments<br/>хранение источника: 1 год")]
  end
  subgraph Z1["Внутренний защищённый контур обработки"]
    ING["Ingest: IDs, timestamps, provenance"]
    AV["Internal ASR/VL workers<br/>исходные media могут содержать PII"]
    SAN{"Data minimization<br/>PII/секреты, разрешения"}
    TEXT["Internal Qwen text analysis<br/>только разрешённый очищенный контекст"]
    DBASE[("Operational store<br/>minimum metadata, evidence refs, audit")]
    AGG["Trusted aggregation<br/>dedup, coverage, time windows"]
    POLICY{"Trust / policy gate<br/>owner map, risk, source evidence"}
    DELIVERY["Internal outbox<br/>no duplicate delivery"]
  end
  subgraph Z2["Авторизованные корпоративные получатели"]
    INBOX["Product Team Inbox"]
    REVIEWER["Human reviewer<br/>неясное/срочное/чувствительное"]
  end
  EXT["Внешний интернет / внешние LLM API<br/>ЗАПРЕЩЕНО"]:::blocked
  SRC -->|"read-only permitted records"| ING
  ING -->|"разрешённые media refs"| AV
  ING -->|"содержимое заявки"| SAN
  AV -->|"transcript / image cues"| SAN
  SAN -->|"только после политики обработки"| TEXT
  TEXT -->|"тип/тема/симптом — гипотезы"| AGG
  ING -->|"source IDs + ingestion time"| AGG
  AGG -->|"counts + evidence + coverage"| POLICY
  POLICY -->|"низкий риск + утверждённое правило"| DELIVERY
  POLICY -->|"неясно, секрет или срочная операция"| REVIEWER
  REVIEWER -->|"человеческое решение"| POLICY
  DELIVERY -->|"корпоративный маршрут"| INBOX
  INBOX -->|"feedback"| DELIVERY
  ING -.-> DBASE
  AGG -.-> DBASE
  DELIVERY -.-> DBASE
  %% NO EDGE to EXT by design: external LLM, Internet and tracker API are forbidden.
  %% Absence of a connection must be enforced by enterprise network egress policy.
  classDef blocked fill:#ffe3e3,stroke:#bf4444,color:#782020;
  classDef guard fill:#fff2d9,stroke:#a66b17,color:#4d3210;
  class SAN,POLICY guard;
```

## 3. AI Agent Workflow / условные решения

[Editable source](./agent-workflow.mmd)

```mermaid
%% Source: official PDF case + user-approved Hybrid C (2026-10-31).
%% CONCEPTUAL diagram only. Urgent support SLA remains independent of AI.
flowchart TD
  A(["Новое обращение: ticket / звонок / вложение"]) --> B["Ingest: права, provenance,<br/>source ID и время первого наблюдения"]
  A -->|"штатный SLA не зависит от ИИ"| H["Существующий процесс поддержки<br/>срочные операции без задержки"]
  B --> C["Только внутренние ASR/VL для разрешённых media<br/>+ локальная минимизация PII"]
  C --> D{"Preflight: доступ, риск,<br/>секреты, deadline?"}
  D -->|"Sensitive / urgent"| H
  D -->|"Низкий риск"| E["Внутренняя Qwen: intent, journey,<br/>symptom; root cause = unknown"]
  E --> F{"Строгий JSON валиден?<br/>Evidence aliases существуют?"}
  F -->|"Нет"| F0["Abstain / human triage<br/>нет автоматической отправки"]
  F -->|"Да"| G["Локальный поиск похожих обращений<br/>same topic ≠ same incident"]
  G --> I["Trusted aggregate_recurrence<br/>distinct source tickets, окна, coverage"]
  I --> J{"Есть повторяемый или значимый<br/>сигнал в наблюдаемом наборе?"}
  J -->|"Нет"| J0["Monitor candidate<br/>недостаточно evidence"]
  J -->|"Да"| K{"Полнота источника<br/>подтверждена?"}
  K -->|"Нет"| K0["Только observed count + caveat<br/>нет заявления о росте"]
  K -->|"Да"| L["Тренд по проверенным окнам<br/>при выполнении правил"]
  K0 --> M["Resolve product team<br/>только из авторитетного справочника"]
  L --> M
  M --> N{"Маршрут и внутренний<br/>policy gate разрешают дайджест?"}
  N -->|"Нет"| F0
  N -->|"Да"| O["Evidence-linked advisory draft<br/>root cause = unknown"]
  O --> P["Transactional outbox<br/>idempotent internal delivery"]
  P --> Q["Product team feedback<br/>accepted / rejected / needs_info"]
  Q --> R["Audit и KPI<br/>проверка экспертами"]
  H --> R
  F0 --> R
  J0 --> R
  classDef safe fill:#e6f4ee,stroke:#398767,color:#204e3b;
  classDef uncertain fill:#fff1d9,stroke:#b57a17,color:#60400d;
  class H,F0,J0,K0 uncertain;
  class P,Q,R safe;
```

## 4. Feedback Sequence / передача продуктовой команде

[Editable source](./feedback-sequence.mmd)

```mermaid
%% Sequence: a candidate insight is NOT a confirmed technical incident.
sequenceDiagram
  autonumber
  participant S as Ticket System
  participant I as Ingestor
  participant M as Internal Qwen ASR/VL/Text
  participant A as Trusted Aggregator
  participant P as Policy & Routing
  participant O as Internal Outbox
  participant T as Product Team
  participant H as Human Reviewer
  S-->>I: read-only ticket/call refs
  I->>I: capture source_created_at / ingested_at
  opt permitted audio / image
    I->>M: internal-only media processing (restricted PII boundary)
  end
  I->>M: minimized text / approved signals
  M-->>A: proposed intent, topic, symptom; not a diagnosis
  I->>A: authoritative source IDs + timestamps
  A->>A: distinct count, time window, coverage
  A-->>P: evidence-linked unverified candidate
  alt urgent, sensitive, incomplete or no routing
    P->>H: route to existing human process
    H-->>P: decision / need more evidence
  else policy allows advisory product digest
    P->>O: create digest with stable idempotency key
    O->>T: approved internal channel (no external API)
    T-->>O: ack + accepted / rejected / needs_info
    O-->>A: feedback for evaluation and KPIs
  end
  Note over A,T: Same business topic ≠ same technical incident
  Note over S,T: No actual company API, time-to-insight or LLM quality is claimed
```

## Review checklist

- [ ] All four Mermaid blocks **render successfully** in GitHub (the repo itself does not include a Mermaid renderer yet).
- [ ] Cyrillic and arrow labels are legible in 16:9 export.
- [ ] Raw media is handled exclusively within the corporate boundary (it may carry PII before ASR/VL).
- [ ] No network link into external-API/LLM blocked entity.
- [ ] Urgent support remains on its existing SLA independent of AI.
- [ ] Unknown source coverage allows an observed lower bound, **not** a complete count/growth claim.
- [ ] Team routing comes from enterprise registry, not model inference.
- [ ] Feedback loops into evaluation, not into an automatic issue declaration.

Referenced in [architecture document](../architecture/webneft-v2-architecture.md), [Superpowers spec](../superpowers/specs/2026-10-31-webneft-evidence-first-agent-design.md) and [agent tool contracts](../agent/tool-contracts.md).
