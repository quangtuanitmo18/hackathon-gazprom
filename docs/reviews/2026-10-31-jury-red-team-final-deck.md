# Final 10-slide Jury Red-Team Review — Gazprom Neft Intelligence Cup 2026

**Date:** 2026-10-31. **Scope:** final real exported PPTX `Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pptx` (10 slide native shapes; matching PDF), last reviewed main Word/PDF and latest Q5. **This is an adversarial AUTHOR review using simulated technical/business/finance judge personas, NOT independent human signoff, NOT official score and NOT a demonstration of deployed AI.**

## 1. The real-world P0 eligibility/registration blocker

The organizer's [Intelligence Cup Telegram channel](https://t.me/s/gpnintelligencecup?before=24) explicitly says **registration until 30 October 2026 inclusive**, with **1 November** opening of expert discussions. [CNews 19 October 2026](https://www.cnews.ru/news/line/2026-10-19_otkryt_priem_zayavok_na_ezhegodnyj) and [SPbGEU](https://unecon.ru/announcements/uchastvuj-v-ezhegodnom-kejs-chempionate-intelligence-cup-ot-gazprom-nefti/) describe eligibility **students in bachelor years 3–4 or master's**, team **2–4**, **in-person final 26 November St Petersburg**; CNews/RB use **29 October** as registration end, inconsistent with the more directly relevant organizer Telegram 30 October. **As of 31 October registration window appears past; there is no evidence this team was registered or accepted**. Portal `cup-gpn.ru` and `gpn.intelligence.cup.hack.aim.club` could not be verified by the external reader; **actual submission deadline remains UNKNOWN** and is not equal to PDF cover's event period 01.10–26.11.

The candidate has previously mentioned studying in **ITMO aspirantura (postgraduate/PhD)**; the published rule does **NOT list аспирантура**. This is **not proof of rejection**—only the organizer can authorize admission, a mixed team or mentor status. Do not use AI to assert approval/registration. Written neutral organizer inquiry: `docs/submission/organizer-eligibility-and-upload-inquiry.ru.md`.

**Gate:** check the actual captain/team portal status and organizer decision immediately. If the first-stage file cutoff is 31 October as previously discussed, do not treat the November final as a reason to delay uploading an already-authorized entry.

## 2. Six organizer rubric dimensions, qualitative only

| p7 assessment dimension | Evidence actually present | Red-team verdict | Remaining vulnerability |
|---|---|---|---|
| Answer all questions | Q1–4,6 self-contained 14,225-char main; Q5 separate exact .md | **Strong concept coverage** | Actual organizer acceptance/submission is not verified; avoid extra external annex links |
| Justified metrics, collection, fallbacks | qualified→sent and first-relevant-observed→sent, delivery coverage, independent precision, team routing, work minutes, source missingness, proxy | **Strong methodological proposal** | None of the achieved outcomes or the retrospective baseline is measured. KPI cohorts and backlog denominator must be defined on real data |
| Financial model + alternatives + macro | 3 discounted hypothetical PVs (123,099 / 1,641,322 / 7,385,950 ₽), manual/BM25/Hybrid, discount sensitivity | **Sound arithmetic; evidence risk** | (C) (investment) unknown; (m,a,k,w,r,g) assumptions; not revenue/cash benefit, macro sensitivity not a dated market forecast |
| Microservice architecture + load | 5 functions/3 MVP processes, scenarios 800/day, 300/h, ASR=4, VL=1, text=2 equivalent slots, DB/outbox modeled | **Good design, not measured** | 4/1/2 are NOT GPU/worker counts under company Qwen benchmark; token prefill/decode and memory cannot be inferred from queueing-only formula |
| Visual presentation | actual 10 editable 16:9 slides, rendered PDF, diagrams and one explicit synthetic E2E example | **Strong visual structure with density caveat** | Slides 4,7,9 are densest (~809,906,819 characters respectively in PowerPoint shape text); rehearse at projector view; 10-slide contact sheet is not human font accessibility signoff |
| Oral defense and expert Q&A | ten-slide Russian script & 22 hard Q&As | **Previously stale; script/Q&A updated in this phase** | Need actual speaking rehearsal and two independent humans: Russian/domain + technical/finance. No organizer speech time confirmed |

**No organizer numerical weights are published. Do not invent a numeric “98/100” estimate or predict a prize.**

## 3. Critical questions to simulate before submission

| Persona | Judge's challenge | The answer must admit | Acceptable evidence or next action |
|---|---|---|---|
| Business | “The team already sends user feedback. Why add this agent?” | Baseline current manual reporting unknown | Explain measurable **incremental** improvement over rules/manual, not a claim of no present communication |
| Product | “Show ONE insight a product manager can act on” | Slide7's three tickets invented; **DRAFT not sent**, no root cause | Evidence IDs, observed count, action to investigate, authoritative routing, human feedback |
| Technical | “300/hour and 4+1+2 GPUs — where from?” | 300/h, 4+1+2 **conditional service slots**, not GPUs | N=40 only sourced, all other scenario variables named, real RTF/VRAM/p95 benchmark gate |
| Model | “Prove similar support tickets share one incident” | Similar topic ≠ common root cause | independent pairwise gold labels, false-merge negative cases, no automatic transitive union |
| Privacy | “What if incoming tickets contain ‘ignore your rules’ or OTP?” | Sanitization doesn't erase all risks | authenticated product scope, retrieval/LLM prompt isolation, deny external egress, read-only model tools, approved send gate |
| Product Ops | “How will you avoid wrong-team alerts and new operator work?” | product→team registry/permissions unknown until discovery | owner-unknown→human, measure reviewer time net of saved minutes, bounded policy-only low-risk digests |
| KPI | “How did you improve speed when a ticket was waiting four days?” | 5m qualified→sent is NOT 96h05 first→sent | separate two real-time KPI distributions, missingness, undelivered and censored backlog |
| Evaluation | “Why is product accepted rate called precision?” | It is NOT a valid independent precision proxy | blind labeled sample covering sent, reviewed, unreviewed; independent recall over eligible population |
| Finance | “How can it pay off within three years if cost is unknown?” | **Cannot yet claim payback** | conditional PV(B)>PV(C), transparency about opportunity value vs budget saving, compare manual/BM25/Hybrid |
| Finalists | “Why so much system architecture if you were asked for a concept?” | Architecture is requested by Q1 and p7; code not required | five-block diagram, resource sizing, one end-to-end business outcome, limited release plan |

## 4. Author red-team findings with severity

- **P0 (external, not technical):** **registration/team eligibility unknown** as of 31 Oct. Rules published bachelor's year 3–4/master's; user’s postgraduate status not explicitly listed. **Organizer confirmation before further cosmetic work.**
- **P0 (conditional):** if team has a real first-stage deadline 31 Oct and is registered, the final review zip must be submitted by the **portal-confirmed** cutoff, not assumed 26 Nov final. Do not claim upload happened.
- **P1 (script drift fixed here):** older `submissions/jury-defense-script.ru.md` referred to a previous deck, didn't say slide4 **300/h+4/1/2 slots**, and presented only generic TPI on slide9. Corrected actual source.
- **P1 (unmeasured effect):** no Qwen actual calls, true support data, gold set, measured accuracy, time-to-insight, acceptance/feedback baseline, or actual implementation cost. Describe only proposed pilot criteria.
- **P2 (slide density):** slides 4,7,9 have 800–900 Russian characters in many native shape boxes; content is on-page, but true projector readability needs a human test. Do not add slides or clutter under the “~10” instruction.
- **P2 (speaker fluency):** original speech roughly 7–9 minutes, the new capacity/KPI explanation may run slightly longer. Timed oral rehearsal needed; official duration unconfirmed. 3-minute backup still provided but must be practiced.

## 5. Decision and review gate

**Author conclusion:** the **technical concept and submission artifact** are coherent enough for an actual peer jury rehearsal. **Business validation/award outcome remain unverified**. The most urgent dependency is actual organizer registration + eligibility; next, run 2-person independent red-team rehearsal with **Russian/product** and **technical/finance** roles.

**Do not:** merge Draft PR #24, deploy V1 app, claim a model was tested, claim Webneft has three real identical incidents, assert achieved ROI, or submit through an unconfirmed portal.

**Positive acceptance for final review:** one reviewer can explain *who gets what, why, when, source and feedback* in 15 seconds. Another can reconstruct **300/h** and **5m vs 96h05** from assumptions and event timestamps; both explicitly distinguish design from measured results. Organizational eligibility confirmed by contest administrator.
