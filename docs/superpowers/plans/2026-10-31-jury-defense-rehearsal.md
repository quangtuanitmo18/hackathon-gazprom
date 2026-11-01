# Superpowers — Jury Defense Speaker Notes & Q&A Plan (2026-10-31)

**Status:** documents-only, in Draft PR #24; previous user agreed next step after deck review. No app code, real Qwen calls, merge, deploy or organizer submission.

## Normative sources

- Actual rendered **10-slide PPTX** `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pptx`, independently extracted slide text.
- Official 7-page PDF `Кейс_Искусственный интеллект.pdf`: p.2 problem & evaluated Q1–Q4; p.3 KPI/finance; p.4 40 support managers within coverage / one-year ticket DB / internal Qwen 3.8, ASR, VL / external API prohibited / real reporting baseline unknown; p.5 submitted document and ~10 slides; p.6 7 illustrative Webneft user requests; p.7 presentation/rubric.
- Version-controlled `submissions/main-solution.ru.md` and `submissions/05-effect-metrics.ru.md` and `docs/case-studies/webneft-synthetic-product-insight.md`.

## Task 1 — Script aligned to actual PPTX, not outline alone
- [ ] Write Russian **slide 1–10** speaker notes, approximate **7–9 minute** optional rehearsal length (organizer has NOT supplied a mandatory duration). Each slide: claim, transition, cautions on unmeasured data and responsible speaker cue.
- [ ] Avoid unnecessary advanced Russian jargon; technical terms are supported by plain explanations.
- [ ] Explain Webneft only as the PDF's single example; example slide7 uses exactly three **SYN-QUEUE** invented IDs (NOT measured Webneft incidence).

## Task 2 — Difficult judge questions and rebuttal
- [ ] 18–20 Russian Q&A items covering business process, multi-product scope, hybrid vs BM25, what is an AI agent, autonomy, unknown coverage, time/data leakage, PII/multimodal, taxonomy/owner governance, external APIs, human feedback, gold labels, metrics denominator, TPI censoring, cloud/Qwen restrictions, 3-year PV and break-even without C.
- [ ] Mark a small set of questions high risk, state what is **not known**; no fabricated actual benchmark or enterprise API.

## Task 3 — Review & verification
- [ ] Verify exact speaker headings match slide 1–10 extracted from actual PPTX, plus 7 illustrative tickets and 3 fictional story IDs.
- [ ] Cross-check financial figures (123k/1.64m/7.39m RUB) and proposed pilot thresholds (p90 ≤4h, precision ≥.80, routing ≥.95) are labelled unachieved targets.
- [ ] Record author self-review: factual accuracy, language usability, timing conditional, unknowns.
- [ ] Run GitHub CI on exact final head, inspect jobs/logs; post COMMENT-only self-review on Draft PR #24. No merge/deploy.

**Acceptance:** defensible Russian presentation **from actual slide deck**, clear story, concise and transparent answers, no overclaims. A Russian-speaking teammate's independent edit is outstanding.
