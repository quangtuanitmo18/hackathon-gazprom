# Webneft V2 Case & Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a defensible, Russian-language Intelligence Cup Webneft submission (PDF answers 1–4,6; mandatory standalone item 5 Markdown; ~10 presentation slides), with a rigorously traceable evidence-first internal AI agent design and an **optional** isolated synthetic demo only after human design approval.

**Architecture:** Hybrid deterministic-aggregation + internal Qwen interpretation, grounded in one corporate ticket source with call recordings and attachments; risk-based internal delivery, feedback and audit. No live private data/API, no external LLM or actual Webneft infrastructure implied.

**Tech Stack:** Markdown and Mermaid diagram source; Python stdlib submission validator already in V2; optional DOCX/PDF/PPTX export after authoring; optional synthetic Python FastAPI MVP *only in a separate approved plan*. No compulsory runtime dependencies for the submission.

**Spec:** [`docs/superpowers/specs/2026-10-31-webneft-evidence-first-agent-design.md`](../specs/2026-10-31-webneft-evidence-first-agent-design.md).

**Status: APPROACH C APPROVED by user (2026-10-31); DOCUMENT-ONLY execution now in progress.** No application code or demo is required or authorized by this decision; no merge/deploy. Detailed diagrams and submission files still need content review.

## Global Constraints

- **Normative source:** user-provided `Кейс_Искусственный интеллект.pdf` (7 pages), not DeepSeek / third-party news. See `docs/requirements/pdf-traceability.md`.
- **Submission:** question 1–4 and 6 in one **self-contained** Russian DOCX/DOC/PDF **≤15 000 characters**, question 5 in a separate `.md`, accompanying ~10 slide presentation. AI Footnotes optional.
- **Context:** ~40 support managers (NOT ticket RPS), one ticket DB and 1-year retention, calls+recordings, ticket attachments and images, internal **“Qwen 3.8”**, Qwen-ASR, Qwen-VL (exact text model/API unverified), **no external LLM/API**.
- **Evidence:** seven PDF examples are `proposed_unadjudicated`, with unknown timestamps, root causes and recurrence; never fabricate gold same-incidents.
- **Business:** recurring questions/wishes/noncritical friction to product teams without adding support work; urgent operational items continue existing support route, not AI aggregation delay.
- **Security:** avoid real PII, login, OTP, secrets in public repo; output may cite only trusted source evidence. All Webneft live features beyond PDF are historical/unverified until owner confirmation.
- **Git:** branch `feat/webneft-case-v2` based on `main`; V1 preserved at `archive/productpulse-v1`; PR #24 Draft. No automatic merge/deploy.

## Review Focus

1. **Research trust:** 2020 auction mechanics / 2023 ecosystem can be historical facts, never current Webneft SLA. Test: every non-PDF claim either cites a dated source or marked hypothesis.
2. **Label leakage:** #1+2 and #6+7 are related journeys, not confirmed common defects; #3 and #5 are each **one** PDF ticket despite multiple symptoms. Test: examples count exactly seven, no invented timestamps, recurrence or same-incident ground truth.
3. **Data/PII boundary:** original audio/images may contain PII before ASR/VL. Test: architecture shows internal-only, initial secure boundary and post-extraction redaction, not external OCR/API.
4. **Time-series & delivery:** no `ingested_at` in source PDF and no assumed complete event window. Test: missing timestamps/coverage produce abstention; retry idempotent with no duplicate digest.
5. **Economic causality:** value of saved staff hours ≠ immediate salary/cash saving; 3-year payback cannot be asserted without costs and monetization. Test: financial formulas have explicit assumptions and sensitivity, no invented actual ROI.

---

### Task 1: Freeze the evidence register and correct the Webneft taxonomy (research deliverable)

**Files:**
- Read: `docs/research/deepseek-webneft-evidence-audit.md` (already added as evidence audit; any further changes require sourced corrections)
- Modify: `docs/requirements/webneft-taxonomy.md`
- Modify: `data/webneft/case-examples.json`
- Modify: `docs/requirements/pdf-traceability.md` only if a PDF criterion is demonstrably missing
- Test: `scripts/validate_case_submission.py`

**Interfaces:** `PDF6-01` through `PDF6-07` remain source reference IDs, **not true ticket system IDs**. Each proposed example exposes business journey, request intent, symptom and `label_status=proposed_unadjudicated`; `same_incident_ground_truth=null`.

- [ ] **Step 1:** Compare DeepSeek claims against PDF and audit; classify each as P/H/D/U, with dated links for H.
- [ ] **Step 2:** Extend the seven JSON examples with explicit `request_intent_proposed`, `urgency_proposed` and `relation_type=null` or `unknown`; never include hypothesized cache, PK or KYC causes.
- [ ] **Step 3:** Run `python3 scripts/validate_case_submission.py`; confirm seven cases, all unadjudicated; inspect the JSON manually against PDF page 6.
- [ ] **Step 4:** Commit `docs(v2): separate Webneft observed symptoms from unproven root causes`.

**Acceptance:** 7/7 match source examples; one PDF ticket is counted once even with multiple symptoms; #4 handled as operational service request; #6 never asks agent to provide passwords.

### Task 2: Architecture + microservice rationale + capacity worksheet

**Files:**
- Create: `docs/architecture/webneft-v2-architecture.md`
- Create: `docs/diagrams/c4-containers.mmd`
- Create: `docs/diagrams/data-flow-trust-boundaries.mmd`
- Create: `docs/diagrams/agent-workflow.mmd`
- Create: `docs/diagrams/feedback-sequence.mmd`
- Reference: `docs/superpowers/specs/2026-10-31-webneft-evidence-first-agent-design.md`

**Interfaces:** `SupportEventV1`, `RequestAnalysisV1`, `ProductSignalV1`, `ProductFeedbackV1` defined in spec, including `ingested_at` and `source_coverage`. Diagrams are conceptual; do not imply deployed endpoints.

- [ ] **Step 1:** Write four Mermaid source diagrams with enterprise trust boundary, internal ASR/VL/Qwen, backend rule gates, source ID/retention and feedback; separate service *logic* from physical deployments.
- [ ] **Step 2:** Add microservice table `component → why independent → CPU/GPU/IO → scaling → failure/fallback → evidence`.
- [ ] **Step 3:** Add quantitative scenario **(not factual throughput)**: `N=40`, `tickets_per_agent_day=20`, `tickets/day=800`, `lambda=800/86400`; `share_calls=0.30`, `avg_call_min=3`, `audio_minutes/day=720`; define p95 peak factor and RTF throughput parameter instead of inventing GPU model/QPS.
- [ ] **Step 4:** Verify source diagrams render and text remains legible on 16:9 slides; cross-check both direction and names of data transfer against architecture; commit with source files.

**Acceptance:** diagram shows correct PII trust boundary from raw media onward; no external egress; service count and sizing reasons trace to PDF rubric; all numeric capacities flagged illustrative.

### Task 3: Agent tool contracts + production-safe prompt + evaluator cases

**Files:**
- Create: `docs/agent/tool-contracts.md`
- Create: `docs/agent/system-prompt.ru.md`
- Create: `docs/agent/output-contracts.md`
- Create: `docs/evaluation/prompt-adversarial-cases.md`

**Interfaces:** backend-supplied trusted scope; tool read/write matrix; `relation_type` enum `same_problem_candidate|related_topic_only|unrelated|insufficient_evidence`; `root_cause_status=unknown` if no independent evidence. Qwen returns *suggestions*, not self-authorizing commands.

- [ ] **Step 1:** Specify allowlisted read tools for sanitized ticket text, ASR/VL, retrieval and aggregation; map role, allowed inputs, failure result, idempotency and evidence.
- [ ] **Step 2:** Specify internal output-only draft and policy-gated digest/feedback tools; no arbitrary HTTP/SQL, OTP/password return, external provider call or autonomous account change.
- [ ] **Step 3:** Create Russian system prompt annotated by role, trust boundary, classification axes, when to abstain, source citations, allowed tools and strict JSON examples for PDF #4 and #5.
- [ ] **Step 4:** Write at least 12 adversarial/ambiguity scenarios: injection via phone ASR/OCR, missing source time, wrong tenant, empty transcript, duplicated call segments, #1 vs #2 same journey not incident, #3 single record/two symptoms, #4 urgent deadline, #6 credential request, #7 misleading SMS provider cause, source coverage unknown and no product owner route.
- [ ] **Step 5:** Reviewer verifies each adversarial input has explicit expected safe outcome and no ungrounded diagnosis; commit.

**Acceptance:** model cannot choose transport recipient, counts, notification rules or root cause without backend verification.

### Task 4: Gold annotation, quality metrics and operational acceptance

**Files:**
- Create: `docs/evaluation/annotation-guidelines.md`
- Create: `docs/evaluation/release-gates.md`
- Modify: `submissions/05-effect-metrics.ru.md`

**Interfaces:** label sets `topic`, `same_problem`, `actionable`, `routing`; `qualified_at`, `sent_at`, `ingested_at` clocks; independent adjudication & confidence intervals.

- [ ] **Step 1:** Define two human labelers + arbiter, sampling across channels/time/product, identity/time split, per-class breakdown; 7 PDF examples treated as illustrations only.
- [ ] **Step 2:** Specify p50/p90 Time-to-Product-Insight, actionable precision, topic recall, routing accuracy, support reporting effort, feedback closure, unknown coverage and duplicate delivery.
- [ ] **Step 3:** Define retrospective baseline study with fallback if historical `qualified_at` or reporting logs unavailable.
- [ ] **Step 4:** State staged release: offline → shadow (no delivery) → policy-approved internal digest → monitored pilot; proposed thresholds (not measured): actionable precision ≥0.80, routing accuracy ≥0.95, p90 qualified→sent ≤4h; no worse urgent support SLA.
- [ ] **Step 5:** Independent reviewer traces each KPI to collection event/source and business value, then commit.

**Acceptance:** no precision/recall or latency sourced from synthetic data masquerades as measured performance; business and safety gates both present.

### Task 5: Three-year benefit model with explicit macro sensitivities

**Files:**
- Create: `docs/business/financial-assumptions.md`
- Modify: `submissions/main-solution.ru.md` section 6

**Interfaces:** `annual_value=N*D*12*(minutes_saved/60)*adoption*hour_value`; monetization coefficient `k`, discount rate `r`, implementation cost `C` (unknown). Final scope respects the PDF: expense pricing is **not** demanded, but a break-even ceiling is useful.

- [ ] **Step 1:** Freeze assumption table with known `N=40` and illustrative `D=22`, 5/15/25 minutes, 25/50/75% adoption and 900/1000/1200 RUB per hour. Add observed-baseline gap and reason each is scenario-only.
- [ ] **Step 2:** Independently recalculate annual and 3-year values, add `k` (realizable value factor), discount sensitivity and break-even cost ceiling; distinguish saved capacity from headcount reductions and revenue.
- [ ] **Step 3:** Show non-AI manual-reporting alternative and minimum benefit needed to justify ASR/VL complexity; discuss inflation/wage trends as assumptions, **not future facts**.
- [ ] **Step 4:** Re-run submission length validator and commit.

**Acceptance:** no ROI/payback reported as fact without actual cost and causal measurement.

### Task 6: Assemble and validate the required final Russian deliverables

**Files:**
- Modify: `submissions/main-solution.ru.md` (must answer 1–4,6, **≤15 000 characters**, standalone)
- Modify: `submissions/05-effect-metrics.ru.md` (separate standalone section 5)
- Modify: `submissions/presentation-outline.ru.md`
- Create (after requested artifact tooling and template checks): `submissions/main-solution.ru.docx` and/or `submissions/main-solution.ru.pdf`, `submissions/intelligence-cup-webneft.ru.pptx`
- Modify: `scripts/validate_case_submission.py` only to enforce previously accepted contract, never inflate counts or loosen the 15k constraint

- [ ] **Step 1:** Replace placeholders in existing Russian prose, preserving exact rubric 1–4,6 order; fit diagrams/argument without linked appendices that expand beyond character cap. Target **≤12.5k** source chars before final polishing to leave margin.
- [ ] **Step 2:** Recheck `python3 scripts/validate_case_submission.py`; manually inspect each page of official PDF vs main text and separate item 5.
- [ ] **Step 3:** Export with actual artifact tooling to DOCX/PDF and 10-slide PPTX (not a mere `.md` outline), visually inspect every page/slide, typography, 16:9 diagram readability and Cyrillic rendering; re-evaluate **final** rendered text length ≤15k.
- [ ] **Step 4:** Source/logic reviewer signs off on P/H/D/U claim boundaries, counts, regulatory privacy controls and honesty of financial scenarios; commit only generated artifacts that are intentional and reproducible.

**Acceptance:** PDF-format, self-contained main, item 5 separate, slide deck ~10 complete slides, no unverified Webneft current feature claims, no invented code/demo metrics.

### Task 7: Optional synthetic demonstration — independent decision gate

**Files (ONLY IF user explicitly approves software scope):**
- New separate spec and plan, starting with `docs/superpowers/specs/YYYY-MM-DD-webneft-demo.md` and `docs/superpowers/plans/YYYY-MM-DD-webneft-demo.md`
- Do not modify V1 archive or silently cherry-pick its whole feature stack.

- [ ] **Step 1:** Choose one demonstrable route: PDF #5 electronic queue recurring signal, with extra fake tickets and explicit `synthetic` provenance.
- [ ] **Step 2:** Define read-only ingest, deterministic baseline, safe Qwen mock (no external calls), product inbox with feedback and TPI event clock; thin UI optional.
- [ ] **Step 3:** Test-first RED→GREEN including one source ticket containing two symptoms, same-topic/different-bug pair, wrong tenant, prompt injection, missing time and retries.
- [ ] **Step 4:** Evaluate behavior using independent fixture labels, compare rules/BM25 baseline, and report no real accuracy/ROI claims.
- [ ] **Step 5:** New Draft PR and independent review; no merge/deploy/external issue tracker unless expressly authorized.

**Gate:** the submission must not depend on this optional code being completed.

## Execution order and approvals

- **Step 0 (DONE, 2026-10-31):** user selected **hybrid C** from [design](../specs/2026-10-31-webneft-evidence-first-agent-design.md) and confirmed **no runtime code** is needed. Detailed components still require editorial/content review.
- **Highest priority:** Tasks **1→2→3→4→5→6**, each task reviewed with its own evidence/quality gate; avoid parallel modification of the 15k main text before architecture and economics are reconciled.
- **Optional Task 7:** separate decision after Task 6 plan is on track; not a required contest deliverable.
- **Verification rule:** after source edits, run actual checker and inspect CI; do not infer correctness from authored Markdown. Leave `feat/webneft-case-v2` and PR #24 Draft until independent review; no automatic merge/deploy.

**Superpowers self-review:** spec coverage: PDF rubric 1–6 and all source/privacy constraints mapped to Tasks 1–6; optional implementation Task 7 isolated. Review focus 1–5 mapped explicitly. No model/provider endpoints fabricated. Each task has a directly inspectable artifact and acceptance.

## Current execution checkpoint — 2026-10-31

- [x] User decision: Hybrid C + documents-first, no application code.
- [x] DeepSeek evidence audit written: `docs/research/deepseek-webneft-evidence-audit.md`.
- [x] Four **Mermaid source drafts** written: `docs/diagrams/{c4-containers,data-flow-trust-boundaries,agent-workflow,feedback-sequence}.mmd`.
- [x] Architecture tradeoffs, service load formulas and assumptions written: `docs/architecture/webneft-v2-architecture.md`.
- [ ] Render and **visually inspect** source diagrams, correct any Mermaid parse or Cyrillic-layout errors; diagrams not yet considered final presentation assets.
- [ ] Human editorial verification against original PDF and Webneft source assumptions.
- [ ] Complete tasks for detailed prompt, KPI, economics and actual DOCX/PDF/PPTX deliverables.

