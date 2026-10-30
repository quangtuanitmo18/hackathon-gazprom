# Release gates — AI Product Feedback Agent (design-only)

**Official brief:** `Кейс_Искусственный интеллект.pdf`, pages 2–4 and 7. **Not executed / no business signoff.** No real Qwen endpoint, customer tickets, deployment or measured baseline has been used. User approved Hybrid C and documentation-only scope.

## Gate ordering: failure blocks later rollout

| Stage | Purpose | Admission / evidence required | Fallback on failure |
|---|---|---|---|
| **G0 — Data & authorization** | No illegal/unsafe ingestion | Approved ticket-source access and one-year source retention policy; explicit rights for audio/image; egress deny; trustworthy `scope_id`, `product_id`, timestamps and owner registry | No sensitive data to model; offline synthetic-only work |
| **G1 — Static/specification** | Check tools, prompt, trust and source evidence | `RequestAnalysisV1` strict JSON, no model-authored root cause, owners, counts, or action approval; source ID allowlist, replay/idempotency and non-transitive topic pairing documented | Rules-only diagnostic shortlist |
| **G2 — Offline model & security test** | Demonstrate benefit and avoid leaks | Two-labeler gold holdout; BM25/rules baseline; per-class support, precision/recall and uncertainty; Webneft PDF #1–#7; prompt injection via ASR/OCR; Russian PII and OTP tests | No auto-routing; expert review on demand |
| **G3 — Shadow pilot** | Measure without business side effects | Log `ingested_at`, `qualified_at`, `sent_at?` as applicable; evaluate correctness on same event stream; no actual delivery to product team, support SLA unchanged | Observe only |
| **G4 — Limited internal advisory** | Validate useful actionable feedback | Signed internal policy + authoritative product routing, human escalation, outbound internal outbox with idempotency, product review feedback, measured no-SLA regression | Disabled auto-send / human queue |
| **G5 — Monitored expansion** | Business and risk threshold sustained | Stable p50/p90 TPI, coverage, accepted signal quality, reviewed fraction, duplicate rate and safety in all slices; weekly business monitoring and rollback procedure | Roll back to G3 or rules-only |

## Proposed thresholds (NOT measurements or official requirements)

| Measure | Candidate release rule | Required denominator and caveats |
|---|---|---|
| Actionable precision | ≥0.80 **on independent judged test cases** | Compare to rules-only baseline; include abstentions and selection bias in a separate report; **not** raw accepted/reviewed rate |
| Correct routing | ≥0.95 on cases with known authoritative team; unknown routes go to human | Also report route coverage across all relevant items, otherwise trivial abstention could game accuracy |
| Asynchronous delivery p90 | ≤4 hours from auditable `qualified_at` to `sent_at` among eligible delivered signals | Also report undelivered/backlogged share; no fake clocks for historic data |
| Recurring topic recall | **Unset** until independent gold labels and prevalence are available | Must report with interval, by category/channel and coverage |
| Prompt injection / confidential egress | **0 allowed unauthorized external sends or credential disclosure** in the test suite | Requires actual network/permissions tests before rollout, not only prompt samples |
| Duplicate internal delivery | **0 duplicate business effects** under fault injection and retries | Transport can be at-least-once; outbox idempotency required |
| Urgent support SLA | **No degradation** from AI pipeline compared with verified support baseline | #4 operational contact request must bypass clustering |
| Missing source completeness | No unsupported growth/overall-frequency claim | Observed count with `unknown_coverage` may be shown under approved policy |
| PII from call/image | Corporate restrictions applied **before** audio/image ASR/VL processing; text minimized before Qwen | Russian names, contract numbers, phone, OTP and secrets adversarially tested |

These figures are **candidate business targets** that need negotiation based on actual volumes, class prevalence and present support process. Setting `0` for security test violations is a policy goal, **not proof of absolute zero risk**.

## Event schema and evidence-based Time-to-Product-Insight (TPI)

| Clock | Producer | Meaning | Potential missing-data issue |
|---|---|---|---|
| `source_created_at` | Source ticket DB, if accessible | User contacted support | PDF examples contain no timestamps |
| `ingested_at` | Trusted ingestion journal | First observed by AI, recorded online | Historical backfill cannot fabricate original first observation |
| `qualified_at` | Trusted signal rule engine | First observed time at which *required evidence* satisfied policy | May be unknown for the old manual process |
| `sent_at` | Internal outbox/delivery receipt | Advisory digest was delivered to product inbox | No contact if no authorized route |
| `acknowledged_at` | Product inbox | Product team confirmed receipt | Ack isn't a product decision |
| `decision_at` | Human product reviewer | Accepted/rejected/needs-info/in progress/resolved | Missingness and right-censoring |

Compute p50/p90 on UTC timestamps with `sent_at >= qualified_at`. Report `eligible_signals`, `delivered_signals`, `undelivered_signals`, censoring and source watermark status. Define observation end so slow/unanswered signals cannot simply be dropped to make p90 look fast. For old manual baseline, if `qualified_at` unrecorded, do not compare a made-up reconstructed TPI: use separately named `source_created_at→documented_product_ack` proxy for both groups where possible, with cohort restrictions.

## Quality definitions with bias controls

- Primary independently judged **actionable precision**: useful emitted/eligible-for-send signals / all independently adjudicated *emitted or selected-for-send* signals in a stratified sample, including those with no product feedback. **Abstained/unsent** traffic is separately sampled to assess actionable recall and selection coverage, not placed in the precision denominator. Disclose confidence intervals, reviewer disagreements and sampling weights.
- Product team observed acceptance: `accepted/(accepted+rejected+needs_info)` among reviewed after maturation; separately report `reviewed/sent` and fraction without response. Do **not** conflate this conditional ratio with model population precision.
- Routing: `correct/(correct+wrong)` among verifiable routed items; additionally `auto_routed/eligible` to expose trivial "abstain all" strategies.
- Recurrence: unique source-ticket keys per product/topic/window; multi-symptom one ticket counts once. Without trusted source coverage cannot claim total volume or rising trend; counts from available sample are explicitly lower bounds, not complete inference.
- Feedback closure: `decisions_within_SLA/sent_eligible`; report `needs_info` separately; raw `ack` measured separately.

## Offline evaluation matrix and data leakage prevention

- Baseline: rules/lexical + BM25; Hybrid C must provide measurable benefit vs this simpler approach on identical independent holdout to justify Qwen complexity.
- At least two independent human labelers and arbiter; prospective/temporal holdout; stratify by product, ticket vs call, language/noisy audio, rare class, organization and service urgency; no source pair from same organization/time leaking into multiple folds.
- 20 stress/attack cases in `docs/evaluation/prompt-adversarial-cases.md` are test **definitions**, not runs against Qwen.
- Source data 1-year retention, separate policy for derivations and logs, enterprise privacy check. No real PII in public repo.
- Failure injection: incomplete pagination, ASR/VL job retries, Qwen timeout/invalid JSON, unavailable product routing, duplicate outbox ACK, mismatched scope.
- Sensitivity: sampling and label uncertainty, unknown coverage, time leakage, low-volume classes, product mix drift.

## Rollout, monitoring and rollback

1. Measure manual baseline via operator/product-team interviews, retrospective source audit and prospective time study (example proposal: two work weeks), noting logging gaps and work-hours/peak differences.
2. G3 shadow tracks candidates but sends **nothing** externally and does not perturb staff workflow.
3. G4 product-approved trial: one or a few teams receive **internal-only advisory** digest, not auto-created development tasks; owner/lead signs off on routing and stopping rules.
4. At least weekly dashboard of feedback, delivered-vs-eligible share, precision by slice, p90 delay including backlog, access-policy violations, source watermark. Monthly causal/business review.
5. On safety violation, repeated wrong routing, duplicate-effects or breach of support SLA: disable auto-digest, preserve audit, return to shadow/manual path; source requests continue.

## Signoff checklist

- [ ] Corporate data-source owner / privacy officer approves read-only permitted audio/image processing.
- [ ] Security team verifies internal egress blocks, tenant isolation and prompt-injection defenses.
- [ ] Two labelers + arbiter sign off on gold set and uncertainty; product owner accepts quality thresholds.
- [ ] Ops/architecture reviewer signs off on load/worker resource sizing and failover.
- [ ] Product teams approve advisory channel, feedback workflow and honest KPI baseline comparison.
- [ ] Financial stakeholder confirms whether saved time is actually redeployed, not merely a time-equivalent.

**Status:** all signoffs above are explicitly outstanding. A passing Markdown validator or synthetic tests alone can never move a stage to G4/G5.
