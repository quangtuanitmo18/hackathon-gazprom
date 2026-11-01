# Independent-of-claims author audit — case PDF vs submission (2026-10-31)

**Basis:** original organizer 7-page `Кейс_Искусственный интеллект (1).pdf`, including two user-provided page-5/page-6 screenshots; latest GitHub V2 source; actual rendered professional DOCX and actual 10-slide jury-review PowerPoint. **Author review, not independent human signoff.** Scope: factual correctness, competition compliance and conceptual completeness. Not a test of real AI accuracy.

## Executive verdict

**Mostly compliant and conceptually complete, not flawless / not empirically validated.** No fundamental misinterpretation of the organizer's objective: agent is company-wide across many digital products and Webneft only provides one illustrative set of examples. A rigorous answer must not equate seven example tickets with recurring incidents or measured benefits. Correct a source/diagram ambiguity; further strengthen microservice load sizing and a user-to-insight KPI before final submission.

## Official PDF rubric traceability

| Source and mandatory question | What exists in final solution | Review result |
|---|---|---|
| p2 Q1 architecture, access/inputs/outputs, microservice rationale | Five logical functions, three proposed physical MVP processes, corporate-only Qwen-ASR/Qwen-VL/text, read-only ticket ingestion, team delivery and feedback; trust diagrams | **Covered.** P1: p7 asks detailed service-load calculations; current main gives average ticket rate and ASR worker math but does not dimension each of model inference, VL/attachments, retrieval, DB/aggregation and outbox separately |
| p2 Q2 agent tools | Typed/permissioned reads, media, retrieval, deterministic aggregation, product mapping, outbox, authenticated feedback | **Covered.** Proposed interfaces, not deployed company APIs |
| p2 Q3 example prompt with explanations | Russian prompt has ROLE/GOAL/TRUST/CLASSES/TOOLS/ABSTAIN/JSON plus comments | **Covered.** Exact API/version and model accuracy untested |
| p2 Q4 testing, final release criteria | Gold labels, human annotators/arbiter, rules/BM25 baseline, unit/model/security/integration/load, stages G0–G5 | **Covered as plan**, no tests with real corporate data/model |
| p3 Q5 effect, retrospective/prospective measurements | Separate Markdown, TPI, precision/recall, routing, support time, feedback, coverage, 2-week proposed time study, retrospective proxies | **Covered.** P1: TPI from qualification→send omits how long user complaints waited to accumulate, so add a separate first-observed→delivered interval and backlog with appropriate source-clock caveats |
| p3 Q6 economic efficiency, 3-year payback conditions | Three 3-year scenario PV figures, alternatives manual vs rules/BM25 vs Hybrid, r/g sensitivity, unknown C conditional break-even | **Covered analytically**, all outcomes *hypothetical*, no proven ROI or cash saving |
| p4 business facts | Approximately 40 staff in covered product scope, 1-year source data, recorded calls & file/image attachments, on-prem `Qwen 3.8`, Qwen-ASR/VL, no external LLM or API, unknown baseline | **Correctly represented**, without inventing source APIs or current employee workloads |
| p5 submission packaging | Main **professional DOCX contains 12,430 extracted text characters**, 4 A4 pages, with correct headings 1–4 and 6, **no DOCX hyperlinks**, 4 Office Math XML occurrences, 3 tables. Main Markdown is **13,037 Unicode characters**. Separate Q5 `.md` exists. Latest PPTX has **10 editable 16:9 slides** | **Compliant on inspected artifacts.** Do not include linked supplementary technical documents as a way to exceed 15,000 chars; existing README/specs are team working materials only |
| p6 seven Webneft examples | Main text mentions all #1–#7 by ID. Presentation slide 3 shows **five business-topic rows** explicitly grouped by `01–02` and `06–07` (total 7 narratives) | **Correct.** PDF contains sample requests, not labeled same-incident pairs or statistical recurrence |
| p7 jury criteria | Architecture + ASR sizing, metrics/fallbacks, alternatives/macro, clear slides, Russian Q&A | **Mostly covered**, load detail and additional first-to-delivery timing are strongest improvements |

## Seven examples reviewed against original page 6

| Official # | Original meaning | Our summary | Integrity |
|---|---|---|---|
| 1 | Contract offer renders individual entrepreneur for an LLC, cannot correct OПФ | `ИП вместо ООО`, contract onboarding | Accurate shorthand; **root cause unknown** |
| 2 | After filling contract offer step 2, blue `Далее` fails to respond in browsers | `«Далее» не реагирует` | Accurate; not proof of same defect as #1 |
| 3 | Previously saved vehicle not in list, re-adding claims already exists | `Машина исчезла / уже существует` | **ONE request with two symptoms**, not two tickets |
| 4 | Request to change inaccessible contact phone, dispatch scheduled 11.07.2026, requires agreement | `изменение телефона перед отгрузкой` / regular urgent support workflow | Accurate *as described for the scheduled dispatch*; no proof of software bug or current active urgency in October 2026 |
| 5 | Cannot book electronic queue, receives 404 or time-does-not-exist | `404 / время недоступно` | **ONE example only**; no frequency/root-cause evidence |
| 6 | Existing contract on organization, requests old login/password access | `старый договор / восстановление доступа` | Topic correctly summarized; proposed policy correctly prevents direct credential disclosure |
| 7 | SMS code for password reset does not arrive | `SMS восстановления` | Accurate; root cause (SMS gateway etc.) not known |

### Caveat on synthetic example

New jury-review slide 7 depicts **three entirely fictional** `SYN-QUEUE` records inspired by *the topic* in official example #5. It explicitly says SYNTHETIC, `count=3` observed **in invented sample only**, source coverage unknown, root cause/trend unverified, digest *not sent*, feedback pending. It is NOT empirical proof that Webneft has three real identical complaints or that the model was run.

## Financial arithmetic independently checked

For `N=40`, `D=22` hypothetical working days/month, `r=0.10`, `g=0`:
- Conservative: `m=5, a=.25, w=900, k=.25` => `B_year=198000 RUB` and `PV_3=123099 RUB` (rounded).
- Base: `m=15, a=.5, w=1000, k=.5` => `B_year=1320000 RUB` and `PV_3=1641322 RUB`.
- Optimistic: `m=25, a=.75, w=1200, k=.75` => `B_year=3960000 RUB` and `PV_3=7385950 RUB`.

**All three match the original formulas.** However only staff `N≈40` is supplied by the PDF. `m`, `D`, `a`, `w`, `k`, `r`, `g` are modeling assumptions. `m` must be defined as gross time saved **per participating manager/day** before multiplying by participation `a`; if `m` is already an all-staff average, multiplying by `a` again double-weights adoption. `PV_3 > C` is a conditional threshold on *present-value* actual lifecycle cost C; it does not prove a three-year payback because C and actual savings are unknown.

## Actionable findings and disposition

**P0 (material violations): none established** in inspected screenshot requirements, main Word, item 5 source and latest slides.

**P1.1 — under-dimensioned per-service traffic:** for PDF p7, increase the explanatory capacity table with **assumption-labeled** throughput / concurrency / resource drivers for ticket ingest, ASR, VL/attachments, text Qwen token throughput, retrieval/DB and outbox. Do not invent actual company utilization. Existing 800 tickets/day + 4 illustrative ASR worker calculation is a useful start, not full per-microservice capacity proof.

**P1.2 — measurement latency gap:** add `first_relevant_ingested_at → sent_at` (and unsent backlog) as a complementary **end-to-end discovery latency** alongside `qualified_at → sent_at`. A 5-minute qualified→sent result must not conceal 4 days from first user complaint. No historic time reconstruction from unseen future data.

**P1.3 — sequence ambiguity (corrected in source):** old Mermaid alt text `urgent, sensitive, incomplete or no routing` could imply **any** missing source coverage always blocks an internal advisory. Other design allows observed-only count *with explicit caveat* under approved policy. Updated canonical `feedback-sequence.mmd` and inline gallery text: only urgent/sensitive/invalid evidence/no route must bypass, while approved partial-coverage advisory is allowed **only with disclaimer**. Diagram grammar still requires CI parser check on latest HEAD.

**P2.1 — feedback nomenclature:** `Feedback closure` in Q5 currently measures **timely decision rate** (`decision_at`), not verified issue resolution. Rename to `product decision SLA` and use actual `resolved_at`/outcome metrics only when business system supports them.

**P2.2 — optional AI Footnotes:** PDF p3 says separate no-length-limit AI Footnotes table is **optional and not scored**, but may help to disclose AI assistance. Current mandatory package is valid without it. A short truthful table can be prepared if desired.

**P2.3 — source vs export:** the professional DOCX has 12,430 extracted text characters and different formatting than the 13,037-character synced Markdown, which is **expected**; do not claim byte-identical DOCX text solely because Markdown sources were aligned. The latest jury-review PPTX is a *separate updated deck* from earlier general-presentation files; choose it before final upload.

**Current status:** acceptable **concept-level submission candidate**, not empirical implementation/pilot or independent business audit. Better to fix P1/P2 before final external Russian-language review; keep PR Draft, no code/merge/deploy.
