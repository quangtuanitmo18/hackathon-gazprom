# Intelligence Cup 2026 — Award-focused Finalization Master Plan

**Status:** PLANNING ONLY. User requested a complete, rigorous plan; do not interpret this as authorization to merge, deploy, submit, introduce live Qwen, or access company data. **Branch:** feat/webneft-case-v2; Draft PR #24. **Goal:** maximize judging competitiveness, not promise a prize.

## 0. Source hierarchy, immutable constraints and evidence ledger

**Normative document:** the original seven-page organizer PDF (not DeepSeek or public Webneft website).
- PDF p1: event header says 01.10–26.11. Treat this as an EVENT WINDOW, **not a verified submission deadline**. Verify the actual portal cutoff and speaking format before final upload.
- PDF p2: dozens of internal/external Gazprom Neft products; support already passes information; find repeatedly appearing **non-critical requests/wishes** without extra support work. Mandatory Q1 architecture, Q2 tools, Q3 annotated prompt, Q4 testing/release.
- PDF p3: Q5 retrospective + future actual KPI collection; Q6 financial benefit, investment alternatives and conditional break-even within three years. Optional AI Footnotes are **not judged**.
- PDF p4: roughly 40 support managers across all products in scope; actual current reporting baseline UNKNOWN; voice recordings, ticket forms, image/file attachments retained one year in a single ticketing database; only internal Qwen 3.8 (exact interface unspecified), Qwen-ASR and Qwen-VL; NO external LLM/API. Monetary cost-side estimation is explicitly not required, but resource complexity matters.
- PDF p5: main independent DOC/DOCX/PDF answering Q1–Q4 and Q6, **at most 15,000 characters**; Q5 in separate Markdown; presentation about 10 slides. Main doc and slides must NOT use links to annexes/tables to evade the 15k cap.
- PDF p6: seven example requests from **ONE** product Webneft, not independent same-incident labels and not a company-wide taxonomy.
- PDF p7: SIX published assessment dimensions: all answers; metric justification/data collection/fallback; finance incl alternatives/market dynamics/macro; technically justified per-microservice architecture AND load math; visually concise presentation; oral presentation and response to experts. No published numerical weights.

**Claim legend for EVERY deliverable:** [PDF FACT], [DESIGN CHOICE], [ILLUSTRATIVE ASSUMPTION], [SYNTHETIC DATA], [TO BE MEASURED]. These labels need not occupy every slide but every quantitative or operational claim must be classifiable in an evidence ledger. No actual Qwen quality, 3 real repeated Webneft tickets, verified common incident, reached KPI, ROI or company API functionality may be fabricated.

**Scope guard:** Multi-product Gazprom Neft agent, separate product_id/taxonomy/routing and authorization; Webneft is a worked example. Externally sourced Webneft business detail from prior DeepSeek analysis is not official ticket evidence.

## Critical path — do these before polishing anything else

The 52 checkboxes are an **exhaustive quality/control inventory**, NOT 52 equally urgent writing tasks. To avoid over-engineering, apply this execution order:

| Order | Essential improvement | Precise outputs | Completion proof |
|---:|---|---|---|
| **1** | **B1–B6: per-service capacity** | reproducible ingress/ASR/VL/Qwen/retrieval/DB/outbox mini-table in Q1; same architecture across Word+slide 4 | all units/peaks/assumptions recomputed, no invented model throughput |
| **2** | **D1–D7: KPI credibility** | new first-observed→delivered + existing qualified→delivered, backlog and bias fixes in item5 | judge can calculate from sample audit log and explain no data |
| **3** | **E1–E5: financial defensibility** | locked scenario inputs, explicit m/adoption/k definitions, A/B/C incremental decision | independent CI math and clear unknown C |
| **4** | **F1–F5: business outcome** | Before→After and slide7 SYNTHETIC draft with product owner/feedback loop | a non-technical judge explains value in <15 seconds |
| **5** | **G1–G7: regenerate final files** | stand-alone Word/PDF under 15k, separate Q5 .md, 10 slides, visual QA, hash manifest | source+Office+PDF review, current-HEAD CI |
| **6** | **H1–H7: defense and independent signoff** | technical/financial/Russian mock jury, corrections and confirmed portal packaging | zero open P0, independent reviewers signed off |

**Maintenance only:** A/C material already reviewed remains unchanged unless the re-audit identifies a contradiction; do not churn working prompts, tools, contracts and diagrams just because a phase exists. **Bonus only if capacity permits:** optional AI Footnotes, more diagrams, dated official macro context, extra UI demo. **Explicitly do NOT build app code** to satisfy a design-only competition rubric.

## 1. Current baseline (verified, not a task to repeat)

- Source main Russian Markdown: 13,037 characters; Q5 separate Markdown: 9,466 chars. Both exact-matched to exported text source in GitHub.
- Professional Word main: previously reviewed four A4 pages, Office Math, below the cap; editable PPTX: ten slides, with visual render and synthetic Webneft draft product insight.
- Four canonical Mermaid diagrams with source-gallery synchronization and Mermaid 11 parser CI; workflow and feedback sequence corrected.
- Three conditional 3-year financial PV scenarios in RUB: 123,099 / 1,641,322 / 7,385,950; these are not measured company savings.
- 24 documented test scenarios and Russian ten-slide speaker notes plus 22 defense Q&A. These are **designed** scenarios, not proof of model testing on real company datasets.
- Last official-PDF audit found no established P0 violation; P1 gaps: resource/load drivers for individual services, first-observed-to-delivered latency; P2: feedback decision ≠ actual issue resolution. Document source PR remains Draft.

**Core thesis to defend:** “A bounded internal AI agent that reliably converts repeated support needs into evidence-linked, policy-authorized, actionable product-team feedback; Qwen understands text, trusted tools verify facts; simple rules/BM25 remain an alternative.”

## 2. Priorities and execution order (not organizer weightings)

- **P0 COMPLIANCE (block submission):** wrong format/character cap, omitted Q1–Q6, false claim of realized Qwen/ROI, external LLM/API, privacy/scope leakage, Webneft mistaken as whole product portfolio, source links used as unbounded appendices, 10-slide export broken.
- **P1 SCORE CRITICAL:** incomplete per-service sizing, ambiguous metric clocks, unsupported benefit assumptions, weak operational integration or feedback ownership, poor slide business storyline, internal contradictions between final source/doc/slides.
- **P2 QUALITY:** optional Before→After business graphic, separate resolution outcome, optional honest AI Footnotes, script simplification, 16:9 design polish, dated official macro reference if it genuinely improves p7 (cite source; do not invent).
- **P3 AVOID:** rebuilding V1 runtime, deploying production agent, collecting private company ticket data without authorization, speculative new architecture, real-world Webneft root cause guesses, overly complex new vector infrastructure, cosmetic diagram proliferation.

Each phase below is **Plan → RED evidence/failing check or documented gap → targeted fix → independent arithmetic/quality review → render/verify → checkpoint**. No step counts complete merely because its Markdown was written.

## Phase A — Freeze scoring and resolve factual contradictions

**Files:** docs/reviews, requirements/PDF traceability, submissions/main-solution.ru.md, submission outline.

- [ ] A1: Create a compact **six-question rubric matrix** mapping PDF p2–7 criterion → exact paragraph/slide → strength → gap severity → fix owner → measurable acceptance.
- [ ] A2: Source ledger separate PDF facts, design proposals, synthetic demo and business assumptions for every numeric statement; verify event 26.11 is NOT automatically the final submission deadline.
- [ ] A3: Red-team seven Webneft stories. #1/#2 one journey not same defect; #3 one ticket two symptoms; #4 historical 11.07.2026 shipment change (not current urgency); #5 one 404/time-unavailable narrative; #6 credentials handled by authorized support; #7 SMS restoration unproven cause.
- [ ] A4: Ensure all three deliverables consistently say: many Gazprom products, Webneft example only; no independent incident/root-cause labels. No contradictory API/tool privileges.
- [ ] A5: Critical reviewer signs off P0=0. P1 ledger maintained and assigned.

**Acceptance:** every mandated scoring criterion has one verifiable answer location; no unsupported causal/business claims; main remains independent.

## Phase B — Maximize Q1 architecture and service load score (HIGHEST PRIORITY)

**Deliverable:** clear five-logical-block / three-deployment-process Hybrid C architecture with **calculable workload per block**, transparent assumptions and alternative design justification; update one meaningful architecture diagram, not 10.

- [ ] B1: Define common scenario inputs clearly: N≈40 from PDF; q tickets/manager/day, 8h vs 24h observation window, call share p_call, audio duration, image/attachment share, image bytes, average text tokens in/out, model slots, Qwen throughput, DB writes, retry/peak factor, target utilization. Every unspecified value labeled **hypothetical**.
- [ ] B2: Recompute request average and peak separately: N*q/day; active 8h peak rates, not just a misleading 24h RPS; peak = peak_factor × active-hour average. Example q=20 => 800/day; 8h avg 0.0278/s, 3x peak ≈0.0833/s. Never call the number a measured company rate.
- [ ] B3: For **each of 5 logical blocks** supply workload unit, formula, scaling bottleneck and failover: ingestion (source pages/s, I/O); ASR/VL (audio seconds×RTF, images per second/image size, GPU concurrency); text Qwen/retrieval (tokens/s, embeddings only if allowed, top-k, query latency); deterministic aggregation/routing (DB QPS, distinct counts, watermark audits, index/retention); delivery/feedback (insights per day, outbox retries, idempotency).
- [ ] B4: State real worker count = ceil(total service demand/(available service capacity×utilization)); ASR 4 workers from previous **specific hypothetical** 720 audio minutes/day, RTF .5, factor3, 8h, .7 utilization; do NOT extrapolate to all model GPU workers without throughput benchmark.
- [ ] B5: Document how to measure missing input from source system telemetry and authorized shadow traffic. Include latency budget / queue backlog and graceful fallback, no invented infra specs.
- [ ] B6: Critically compare Option A manual, B rules+BM25, C bounded Qwen. Why five **logical** blocks do not mandate five network microservices; describe deployment threshold to split services later, and privacy read-only integrations.
- [ ] B7: One visual C4/flow arrow shows product_id → authorized taxonomy → scoped retrieval → source evidence → team registry; avoid suggesting unrestricted multi-product joins.

**Acceptance:** reviewer can recreate every displayed workload estimate from explicitly stated inputs; DB/LLM/ASR/VL/outbox all addressed; no false “measured production capacity” or GPU guarantee.

## Phase C — Strengthen Q2 tools, Q3 annotated prompt, Q4 acceptance

- [ ] C1: Exact tool matrix: actor (model/backend/human), input schema, output, rate budget, authorization boundary, retry/idempotency, failure behavior. Model READ context and candidate search only; **no** free SQL/HTTP, raw secrets, direct delivery or account edits.
- [ ] C2: Product-specific taxonomy selected by authorized backend; no Webneft categories globally. Unknown product/team/coverage, OCR/ASR prompt injection, PII/OTP, empty source and late/backfilled timestamps have explicit fallback.
- [ ] C3: One compact Russian prompt with role/inputs/trust/allowed tools/outputs/abstain and comments; strict JSON sample tied to one PDF Webneft example. Claim “expected output example”, never live Qwen inference.
- [ ] C4: Explicitly separate SAME TOPIC vs SAME SYMPTOM CANDIDATE vs VERIFIED COMMON ROOT CAUSE; no transitive cluster merging. A label on a support topic is NOT a same-incident label.
- [ ] C5: Test matrix with reproducible fixtures for 7 official scenarios + synthetic hard negatives + prompt injection; document unit/security/integration/performance tests, source-coverage faults, signed human feedback and outbox duplicate-effects checks.
- [ ] C6: Independent two-annotator/arbiter protocol, genuine held-out product/channel/time splits; baseline rules/BM25 vs Hybrid C; abstention/missingness and per-product confidence intervals. These are **test plans** until real authorized data/model is accessible.
- [ ] C7: Release gates G0–G5 with strict privacy and no-regression support SLA, shadow (no sends) → authorized limited internal advisory → rollback. No autonomous ticket mutations.

**Acceptance:** one concrete negative case proves the design refuses a false merge, an unauthorized cross-product query and an auto-send; tests and claims clearly distinguish documentation from execution.

## Phase D — Repair Q5 KPI causality, denominators and baseline fallback

**Main success question:** “How much earlier and more reliably does actionable, well-evidenced user feedback reach the right product team, without extra support work?”

- [ ] D1: Keep distinct event clocks: source_created_at (optional), first_relevant_ingested_at (trusted online observation), qualified_at (minimum eligible evidence), sent_at (internal delivery confirmed), acknowledged_at, decision_at, resolved_at if available. Do not use future admission/source states or retrospectively invented ingestion timestamps.
- [ ] D2: Preserve qualification→delivery TPI p50/p90, but add **first-relevant-observed→sent end-to-end insight delay**, plus percent undelivered/eligible, backlog age and time-to-ack. Separate first complaint waiting time from delivery pipeline latency; define cohort window and censoring.
- [ ] D3: Define independent actionable precision **among selected-for-delivery**, recurring-topic recall **over annotated eligible population**, correct routing **among evaluated routes** plus auto-route coverage, net support reporting minutes, timely product **decision** vs actual resolution, source completeness/coverage. Never use accepted/reviewed as unconditional precision.
- [ ] D4: State unit of count = distinct source_system+ticket_id (not ASR segments or symptom count). Under unknown_coverage can show approved **observed minimum only**, not overall frequency or growth trend.
- [ ] D5: Baseline discovery: audit historical year only as actually accessible, source and product-team timestamps, at least a proposed two-week forward time study; document seasonal/product mix and comparison cohorts. If historic qualified_at unavailable: choose a clearly differently named proxy; do not compare unlike clocks as if equal.
- [ ] D6: Include practical collection example table: KPI → exact numerator/denominator → event producer → retrospective source → prospective log → missing-data fallback → reviewer.
- [ ] D7: Ensure Q5 standalone Markdown stays self-contained, per-product breakdown and company-wide weighted aggregate disclosed. No unmeasured pilot success claim.

**Acceptance:** any judge can take an example event log, reproduce KPI, and tell when a metric is “not estimable”; headline latency cannot be improved by ignoring never-delivered signals.

## Phase E — Fortify Q6 financial reasoning without invented outcomes

- [ ] E1: Freeze the audited three original scenarios; explicitly define N=40 from PDF and D=22, m, a, w, k, r, g as hypothetical inputs. m is **time saved per participating manager per working day**, NOT across all staff already; avoid double multiplication by adoption a.
- [ ] E2: Verify annual gross value = N×D×12×(m/60)×a×w; 3-year present value of realizable benefit = sum annual gross×k×(1+g)^(t−1)/(1+r)^t for t=1..3. Recalculate in Python/independent CI, assert output rounded RUB for all rows.
- [ ] E3: Clarify freed time ≠ wage cuts, profit or cash. State conditional 3-year break-even if PV(benefits)>PV(real lifecycle costs C), but **C unknown** and no achieved payback/ROI can be claimed. Organizer explicitly exempts monetary cost-side; still explain extra Qwen complexity risk.
- [ ] E4: A/B/C investment alternatives compared by **incremental** realized benefit vs incremental cost. Explicitly choose baseline that could win if AI uplift is absent (manual workflow improvement or BM25).
- [ ] E5: Sensitivity on minute savings/adoption/realizable k, peak product mix and nominal discount/growth. If citing *actual current macroeconomics*, verify dated official Russian source, cite within allowed text, and avoid treating hypothetical r=10% as a fact or forecast.
- [ ] E6: In deck: show a single legible comparison, plus “сценарий, не измеренный ROI”. Avoid over-precise misleading finance numbers dominating the narrative.

**Acceptance:** all formula outputs independently reproducible; every assumed parameter clearly identified; business value argued cautiously and linked to measurable support time.

## Phase F — Illustrate a real business process without fabricating real data

- [ ] F1: One concise BEFORE→AFTER picture (prefer slide 2, **not an extra competing architecture diagram**): support input → existing product teams versus source→agent evidence review→advisory→product team feedback. Do not suggest existing company operation is 100% manual.
- [ ] F2: Make slide 7 the signature business example: source PDF #5 is **one** original narrative; three SYN-QUEUE IDs are **entirely fictional** for an end-to-end illustration. Proposed Qwen topic only, trusted observed count=3, unknown source coverage/root cause/trend, unverified advisory draft, not sent, feedback pending.
- [ ] F3: Distinguish “related topic” and “same incident”; unauthorized owner/product mapping blocks send; product team is the decision maker.
- [ ] F4: Show exact sample insight fields and one follow-up feedback outcome as **hypothetical** if needed; never assert actual acceptance/delivery.
- [ ] F5: Explain how the feedback would improve governance and evaluation (future human labels, not self-certified learning).

**Acceptance:** independent business reviewer can answer in 15 seconds: WHO receives WHAT, WHY this is better, WHAT evidence supports it, WHAT remains unknown, WHO approves.

## Phase G — Final documents & visual polish (single canonical source)

- [ ] G1: Freeze canonical Russian Markdown main Q1–4+6 under 15,000 Unicode characters and Q5 separate .md, plus versioned scenario JSON and authoritative 10-slide storyboard. PDF p5 forbids external references that expand the answer.
- [ ] G2: Refactor main copy to follow PDF order, remove repeated technical explanations to make room for sizing mini-table and clear risk caveat; do not simply append text beyond cap.
- [ ] G3: Regenerate **editable** professional DOCX with consistent Cyrillic typography, Word-native equations, accessible headings and 1–2 compact inline diagrams/tables where they materially add clarity. Export PDF; inspect every actual page for wrapping, legibility and visible text count below 15k. Do not confuse Markdown characters with DOCX visible text.
- [ ] G4: Regenerate exactly ~10 16:9 PPTX slides, editable native shapes; slide-by-slide storyline and whitespace, color/contrast, typography, no unsupported slide fact. Keep total 10 if possible by replacing weak content, not adding.
- [ ] G5: Render slide PDF and PNG all pages, check overlap/off-canvas, font glyphs, all Mermaid sources parse with real parser, and slide7 **SYNTHETIC** label visually obvious.
- [ ] G6: Export final item5 .md **exactly** from canonical source. Re-fetch GitHub repo paths and compare Unicode/UTF-8 hashes to each final source; do not silently diverge from exported Office/PDF wording.
- [ ] G7: Prepare final file manifest: exact filenames, hashes, version/commit, question mapping, page/slide counts, character count, proof of no external appendix links. Keep earlier drafts archived as drafts and clearly label “final candidate”.
- [ ] G8: Optional AI Footnotes truthful separate table (not scored and not a loophole for the 15k cap); include only if it helps ethics/process transparency without extra churn.

**Acceptance:** main file stand-alone, ≤15k visible characters, Q5 stand-alone .md, PPTX ~10 clean slides, 0 P0 issues, exact canonical sources synchronized, **no final-export layout issue**.

## Phase H — Jury rehearsal, independent review and submission readiness

- [ ] H1: Final Russian 7–9 minute **practice** script and 3-minute backup; PDF has no explicit oral duration, so confirm actual organizer rules. Align speech to exact final PPTX.
- [ ] H2: Review 22 prepared jury questions; perform mock jury with **at least two reviewers or roles**: technical/security and product/financial/Russian-language. One person must actively find counterexamples, not just confirm the concept.
- [ ] H3: Pressure-test five questions: Why AI vs BM25? How can you prove repetition from only seven examples? How to measure earlier arrival without historical clocks? How can 3-year payback be claimed without C? How do you protect PII and avoid wrong-team delivery?
- [ ] H4: Reviewers tag P0/P1/P2; P0 must be zero, remaining P1 explicitly accepted or corrected with specific evidence. Author self-review ≠ independent approval.
- [ ] H5: Verify organizers' real submission time, team eligibility, accepted attachment forms, speaking duration and rubric with the official portal (p1's 01.10–26.11 should **not** be assumed to be upload cutoff).
- [ ] H6: Final release gate: repository CI **success on exact new HEAD**, all diagram parses, independent arithmetic, packaging checks, actual DOCX/PDF/PPTX render inspect, source/export consistency, human reviewer signoff; PR stays Draft until user explicitly authorizes otherwise.
- [ ] H7: Human owner uploads the exact approved files and verifies portal receipt; never claim submitted unless portal confirms.

**Acceptance:** one clean, defensible file set and rehearsed defense; no unresolved material issues or misleading claims. Do not submit/merge/deploy automatically.

## 3. Suggested team responsibilities (assign if actual members available)

| Role | Main deliverable | Independent review partner |
|---|---|---|
| System architecture & privacy | B + C: 5 block sizing, multi-product trust, prompt & tools | Business/KPI owner checks simplicity and no accidental automated changes |
| Data/metrics | D + evaluation/testing: numerator, denominator, time leakage, gold, fallback | Architecture owner checks event availability |
| Business & financial | E + F: realizable time value, alternatives, product insight | Metrics owner checks causality and scenario math |
| Editorial & defense lead | A + G + H: Russian DOCX, slide narrative, mock jury, packaging | Another Russian-speaking reader does final independent language pass |

For two-person team, combine roles but still **cross-review** each other's work. Do not invent named team members, company reviewers or signoffs.

## 4. Trackable Definition of Done / score-protection gates

| Gate | Required evidence | Status at planning |
|---|---|---|
| PDF answer coverage 6/6, formatting & no appendix evasion | source-to-final mapping, DOCX visible character count, item5 separate, slides ~10 | Current draft largely compliant; recheck after edits |
| Technical score: all 5 logical blocks workload model | formula/input/resource/peak/fallback mini-table + reviewer arithmetic | **OPEN P1** |
| KPI reproducibility & unbiased latency | qualified→sent, first-observed→sent, undelivered rate, review denominator, missing data | **OPEN P1** |
| Financial reproducibility & uncertainty | 3 scenarios, 4 sensitivity cases, investment alternatives, company assumption legend | Existing maths PASS; uncertainty review still required |
| Business story and governance | before/after + SYNTHETIC ticket-to-insight + feedback + owner policy | Signature synthetic deck exists; improve framing |
| Source and security boundaries | internal-only Qwen, PII/rights, no external egress, schema strict and no auto business mutation | Designed, not production verified |
| Visual quality | Word/PDF per-page inspection, slide PDF/PNG inspection, 4 real Mermaid syntax parses | Existing artifacts reviewed; final regeneration pending |
| Mock jury and approval | two critical reviews + exact slide script & top-5 hard Qs | **OPEN** |
| Final package | manifest, hashes, organizer portal format/cutoff verified, human upload receipt | **OPEN** |

**Scope stop rule:** no new coding/opensource/deployment unless it concretely closes a rubric gap that cannot be proven with diagrams, calculations, a sample insight and test design. The PDF requires an agent **design**, not a working application demonstration.

## 5. Execution contract

For each implementation phase, the assistant or team must:
1. Post proposed changes and assumptions before editing, keep a bounded file list.
2. Make the minimum source change; never silently overwrite synchronized final artifacts.
3. Recompute/test relevant formulas and source contract; run real Mermaid parser for changed diagrams.
4. Obtain critical review with counterexamples and record P0/P1/P2 with resolutions.
5. Regenerate affected DOCX/PDF/PPTX, inspect rendered pages, compare sources, run CI on **exact HEAD**.
6. Report what passed, what was NOT tested (real Qwen, business ticket history, measured ROI), and retain Draft PR/no merge pending owner authorization.

**Project readiness:** planning/document review may proceed now. Independent company data access, gold labels, measured improvements, and award outcome remain unknowable from the PDF; never claim otherwise.
