# Evaluation & Three-Year Economics — Documentation Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver rigorously reviewed evaluation, release criteria, business KPI and three-year economic scenarios for Webneft V2, faithfully answering official PDF items 4–6, without implementing an app.

**Architecture:** Documents-first Hybrid C: internal Qwen suggests semantic labels, trusted code owns evidence/time/routing and internal delivery; evaluation compares this with simpler rules/BM25 baseline. Financial benefit is a scenario for support time freed, not automatically saved cash. All primary facts traced to the user-supplied 7-page PDF, pages 3, 4 and 7.

**Tech Stack:** Russian Markdown, GitHub Actions, existing Python stdlib document validator; no application or model runtime.

**Spec:** `docs/superpowers/specs/2026-10-31-webneft-evidence-first-agent-design.md`.

## Global Constraints

- Official PDF item 5 must be a separate `.md`. Items 1–4,6 must remain in a self-contained DOCX/DOC/PDF under 15,000 characters when exported.
- Only ~40 support managers and one-year ticket storage are case facts; baseline ticket counts, support time, wages, model endpoints and actual costs are not provided.
- Never claim observed precision/recall/payback/ROI from seven unadjudicated example tickets.
- No external LLM/API; Qwen model names kept exactly as quoted in PDF; model inference not run.
- `qualified_at` denotes first auditable occurrence of all minimum evidence **at the observer**; retrospective absence prohibits reconstructing real-time latency.
- "Value of freed support capacity" is NOT equivalent to cash savings; break-even with unknown implementation cost is conditional.
- Keep `main` untouched and PR #24 Draft; no merge/deploy.

## Review Focus

1. **Selection/acceptance bias:** 'accepted / reviewed' alone omits never-reviewed sent insights; report both review coverage and precision with the correct denominator.
2. **Time leakage:** backfilled tickets and future-known timestamps cannot be used to claim historical online speed.
3. **Tiny/missing classes:** rare topics and seven PDF scenarios cannot sustain honest F1/recall claims; measure stratified samples with uncertainty.
4. **Finance arithmetic:** 40 × 22 × 12 × minutes/60 × adoption × RUB/hour must be independently recalculated; no double counting, inflation assumptions distinguished from facts.
5. **Financial payback:** PDF doesn't require cost estimation; do not imply actual payback just because a gross value exceeds an unknown threshold.

---

### Task 1: Annotation & offline evaluation protocol

**Files:**
- Create: `docs/evaluation/annotation-guidelines.md`
- Review: `docs/requirements/webneft-taxonomy.md` and `data/webneft/case-examples.json`.

- [x] **Step 1:** Define evidence sampling frame, source IDs, signed scope, temporal boundaries, channel coverage, privacy/retention.
- [x] **Step 2:** Define separate label rubrics `intent`, `business_journey`, `symptom`, `same_problem_pair`, `actionable` and `route`; two independent annotators, adjudicator, uncertainty.
- [x] **Step 3:** Specify sampling strategy, temporal and organization split; report n/coverage/confusion matrix and uncertainty per slice.
- [x] **Step 4:** Peer self-review against all seven PDF tickets and 20 adversarial scenarios; no invented ground truth.

**Acceptance:** clearly separates semantic classification, pair relation, topic frequency and accepted product actions; no claim a PDF example provides labeled recurrence.

### Task 2: Business KPI, causal measurement and release gates

**Files:**
- Create: `docs/evaluation/release-gates.md`
- Update: `submissions/05-effect-metrics.ru.md`

- [x] **Step 1:** Freeze event clock and audit schema, classify each metric's denominator and missing-data policy.
- [x] **Step 2:** Define proposed pilot thresholds vs hard security gates; human feedback, wrong routing, duplicate outbox and ASR quality.
- [x] **Step 3:** Baseline discovery from existing manual workflow; missing baseline fallback; shadow stage and controlled switchback/pilot.
- [x] **Step 4:** Review for selection bias, missing feedback, uncertain coverage and fake causal claims. Cross-check against PDF item 5 and page 7.

**Acceptance:** item 5 is standalone, auditable and can be measured by actual company systems if granted access; no threshold presented as measured fact.

### Task 3: Financial assumptions, alternatives and sensitivity

**Files:**
- Create: `docs/business/financial-assumptions.md`
- Create: `docs/business/scenario-inputs.json`
- Update: `submissions/main-solution.ru.md` item 6 **only if** required by critical review and 15k size budget.

- [x] **Step 1:** Recompute three stated input scenarios with `N=40`, `D=22`, 12 months; show hours/year, RUB/year, three-year gross before discount.
- [x] **Step 2:** Add `k` (fraction of freed time that is economically realizable), discount rate, wage growth, yearly adoption; provide present-value benefit and *conditional* cost ceiling, not fictional payback.
- [x] **Step 3:** Model alternative **manual reporting improvements / rules+BM25-only / hybrid Qwen** and non-additive business benefits, no invented actual cost.
- [x] **Step 4:** Explain macro/inflation scenarios as assumptions, not sourced predictions; note why zero model usage charge in PDF is not literally zero integration complexity.
- [x] **Step 5:** Independent arithmetic validation with stdlib and documentary review.

**Acceptance:** formulas, scenario assumptions, missing actual `C` and causal value clearly distinguished; arithmetic checks green.

### Task 4: Validation & critical review

**Files:**
- Modify: `scripts/validate_case_submission.py`
- Update: `docs/superpowers/plans/2026-10-31-webneft-v2-case-and-submission-plan.md`
- Update: Draft PR #24 (description and COMMENT self-review; **not APPROVE**).

- [x] **Step 1:** Add checks for independent gold labels/release gates, separate KPI file and scenario arithmetics.
- [x] **Step 2:** Run actual GitHub Actions on exact new HEAD; inspect logs, not just pending status.
- [x] **Step 3:** Critical review traceability to PDF pages 3/4/7, finance consistency with main answer, correct glossary `TPI`, `coverage`, `qualified_at`, `k`, `C`.
- [x] **Step 4:** Record residual limitations (no real baseline/LLM/label set/ROI, slide export pending) and leave PR Draft.

**Acceptance:** verifiable CI success for document-source checks only, explicit caveat that this does not mean external gold eval or enterprise production pilot ran.

**Author checkpoint, 2026-10-31:** tasks 1–4 executed as documentation + source-level checks; [Critical self-review](../../reviews/2026-10-31-evaluation-economics-self-review.md) records corrected precision denominator, time censoring, input/finance sensitivity, five logical components, unmeasured company outcomes. **An independent person has not reviewed or approved the submission; all pilot/security signoffs, final render/export and merge decisions remain outstanding.**
