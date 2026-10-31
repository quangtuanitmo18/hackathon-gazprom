# Final 10-slide deck alignment plan — after Professional Word export

**Date:** 2026-10-31. **Scope:** update editable 10-slide PPTX and PDF to reflect current final Word/source and mandatory item-5 KPI. User explicitly authorized the next step. **No app code, merge, deploy or organizer submission.**

## Canonical source and provenance
- Main: `submissions/main-solution.ru.md`, Git blob SHA `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c`, 14,225 chars, 5 logical blocks/3 MVP processes, illustrative `800 tickets/day`, peak `300/h`, 4 ASR/1 VL/2 text slots, 0.25 DB writes/s, 7.5 digests/h.
- KPI: `submissions/05-effect-metrics.ru.md`, with **distinct** qualified→sent TPI and first relevant ingested→sent E2E, together with undelivered/backlog, independent precision, correct route and **timely product decision** (not issue resolution).
- Baseline deck: `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pptx`; actual PowerPoint native shapes, 10 slides/16:9; source builder extracted from session review ZIP.
- Original contest PDF: many digital products, Webneft p6 example only, Q5 separate MD, no external LLM/API, all finance and model throughput scenarios hypothetical.

## Implementation & review tasks
- [ ] **1. Build reproducible editable deck:** preserve ten-slide order and corporate presentation look. Use native PPTX shapes/text, no rasterized diagrams. Version the final JS deck builder in repo or explain export provenance.
- [ ] **2. Revise slide 4:** clearly distinguish five logical blocks from three deployment processes. Display scenario-only peak `300 tickets/h`; per block show 300 ticket/h, 4 ASR+1 VL slots, 2 text slots & input/output token demand, 0.25 write/s, 7.5 digests/h. These are workload/slot equivalents and NOT production GPU numbers. P95 and sizing still need real benchmarks.
- [ ] **3. Revise slide 9:** add both qualified→sent TPI and first-relevant-observed→sent E2E; illustrate **5 min versus 96h05** with explicitly synthetic timestamps. Show proposed p90 TPI ≤4h only qualified→sent, actionable precision ≥0.80, route accuracy ≥0.95, support time saved, plus undelivered/eligible and decision/feedback. Never imply these targets were measured.
- [ ] **4. Protect other slides:** Webneft example #5 is one official request; slide7 uses three separate SYN-QUEUE **fictional** records. Slide10 amounts 123k/1.64m/7.39m RUB are hypothetical 3-year realized-value PV, **not measured ROI**.
- [ ] **5. Render and inspect:** export PPTX to PDF, render ten page PNGs and montage, visually inspect all pages and detail slides 4,7,9,10. Assert slide count=10, 16:9, no shapes off canvas, PDF text extractable/no overflow, correct strings, Cyrillic legibility.
- [ ] **6. Verify consistency:** compare exact text/numbers with GitHub source and current Word artifact, Q5 standalone. Check no unsupported actual Qwen inference, no external APIs, no invented root cause or shared incident. Recalc workload and KPI sample; create self-review and hashes.
- [ ] **7. Repository & CI:** update `submissions/presentation-outline.ru.md` and final slide build source, record source-file hash and explicit limitations. Run GitHub Actions on exact new HEAD and post COMMENT-only self-review in Draft PR #24; **no merge/deploy**.

**Acceptance:** handoff verified downloadable PPTX + PDF + contact sheet; full source and QA manifest, no hidden slide count reduction, no confusion of synthetic sizing/timing with measured company facts. Independent Russian language/jury editorial review remains outstanding.
