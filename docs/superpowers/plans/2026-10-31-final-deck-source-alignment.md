# Final 10-slide deck alignment plan — after Professional Word export

**Date:** 2026-10-31. **Scope:** update editable 10-slide PPTX and PDF to reflect current final Word/source and mandatory item-5 KPI. User explicitly authorized the next step. **No app code, merge, deploy or organizer submission.**

## Canonical source and provenance
- Main: `submissions/main-solution.ru.md`, Git blob SHA `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c`, 14,225 chars, 5 logical blocks/3 MVP processes, illustrative `800 tickets/day`, peak `300/h`, 4 ASR/1 VL/2 text slots, 0.25 DB writes/s, 7.5 digests/h.
- KPI: `submissions/05-effect-metrics.ru.md`, with **distinct** qualified→sent TPI and first relevant ingested→sent E2E, together with undelivered/backlog, independent precision, correct route and **timely product decision** (not issue resolution).
- Baseline deck: `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pptx`; actual PowerPoint native shapes, 10 slides/16:9; source builder extracted from session review ZIP.
- Original contest PDF: many digital products, Webneft p6 example only, Q5 separate MD, no external LLM/API, all finance and model throughput scenarios hypothetical.

## Implementation & review tasks
- [x] **1. Build reproducible editable deck:** preserve ten-slide order and corporate presentation look. Use native PPTX shapes/text, no rasterized diagrams. Version the final JS deck builder in repo or explain export provenance.
- [x] **2. Revise slide 4:** clearly distinguish five logical blocks from three deployment processes. Display scenario-only peak `300 tickets/h`; per block show 300 ticket/h, 4 ASR+1 VL slots, 2 text slots & input/output token demand, 0.25 write/s, 7.5 digests/h. These are workload/slot equivalents and NOT production GPU numbers. P95 and sizing still need real benchmarks.
- [x] **3. Revise slide 9:** add both qualified→sent TPI and first-relevant-observed→sent E2E; illustrate **5 min versus 96h05** with explicitly synthetic timestamps. Show proposed p90 TPI ≤4h only qualified→sent, actionable precision ≥0.80, route accuracy ≥0.95, support time saved, plus undelivered/eligible and decision/feedback. Never imply these targets were measured.
- [x] **4. Protect other slides:** Webneft example #5 is one official request; slide7 uses three separate SYN-QUEUE **fictional** records. Slide10 amounts 123k/1.64m/7.39m RUB are hypothetical 3-year realized-value PV, **not measured ROI**.
- [x] **5. Render and inspect:** export PPTX to PDF, render ten page PNGs and montage, visually inspect all pages and detail slides 4,7,9,10. Assert slide count=10, 16:9, no shapes off canvas, PDF text extractable/no overflow, correct strings, Cyrillic legibility.
- [x] **6. Verify consistency:** compare exact text/numbers with GitHub source and current Word artifact, Q5 standalone. Check no unsupported actual Qwen inference, no external APIs, no invented root cause or shared incident. Recalc workload and KPI sample; create self-review and hashes.
- [x] **7. Repository & CI:** update `submissions/presentation-outline.ru.md` and final slide build source, record source-file hash and explicit limitations. Run GitHub Actions on exact new HEAD and post COMMENT-only self-review in Draft PR #24; **no merge/deploy**.

**Acceptance:** handoff verified downloadable PPTX + PDF + contact sheet; full source and QA manifest, no hidden slide count reduction, no confusion of synthetic sizing/timing with measured company facts. Independent Russian language/jury editorial review remains outstanding.

## Executed artifact checkpoint

- [Final slide QA report](../../reviews/2026-10-31-final-deck-source-and-visual-qa.md): real **10 editable PPTX slides**, **10 rendered PDF pages**, 16:9, all shape/text bounds on canvas, all pages rendered/checked; slides 4 and 9 inspected at presentation resolution.
- Source of capacity inputs: [scenario JSON](../../architecture/per-service-capacity-scenario.json); source of qualified/E2E clocks: [separate Q5 KPI Markdown](../../../submissions/05-effect-metrics.ru.md); source of business facts: [main written solution](../../../submissions/main-solution.ru.md).
- Final PPTX/PDF, contact sheet, generator JS and machine QA JSON packaged for conversation download; **not committed to GitHub**. The source storyline is updated in `submissions/presentation-outline.ru.md`.
- Repository CI [#41199080414](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41199080414) **SUCCESS** on source/plan commit `043652a`; COMMENT-only author review recorded in PR after this checkpoint. Independent human signoff remains outstanding.
