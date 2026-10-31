# Final Deck candidate — slide 4 capacity and slide 9 end-to-end KPI QA

**Date:** 2026-10-31. **Review type:** author's reproducible source/visual QA, NOT independent approval, live model evaluation, real-company benchmark or organizer submission.

## Source grounding and precise scope

- Authoritative written answer: `submissions/main-solution.ru.md` (14,225 Unicode chars; Git blob `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c`), professional DOCX/PDF produced from this source, previously rendered at three A4 pages, under 15k.
- Separate mandatory `submissions/05-effect-metrics.ru.md` defines qualified→sent TPI; first_relevant_ingested→sent **end-to-end**; undelivered/eligible and backlog; independent precision; conditional routing accuracy; timely product decision (not issue resolution).
- `docs/architecture/per-service-capacity-scenario.json` is the **machine-checkable version of all workload assumptions**. Only staff N≈40 originates in PDF case p4; other parameters unverified.
- Webneft's original p6 #5 is **one** illustrative support request. Slide 7's 3 `SYN-QUEUE` ticket IDs are entirely invented and correctly labeled **SYNTHETIC**; slide 9's clock demonstration is **a distinct unrelated synthetic example**, not actual timestamps for those invented ticket IDs.
- No external inference/API, no real ticket corpus, no organization routing IDs invented, no source completeness guaranteed.

## Slide-by-slide review / changed scope

| Slide | Status | Reviewer conclusion |
|---:|---|---|
| 1 | Unchanged | Gazprom Neft multi-product scope; concept not deployment |
| 2 | Unchanged | Currently unknown manual reporting baseline; avoids claiming support does nothing |
| 3 | Unchanged | Seven original PDF Webneft examples grouped into five business journeys, not incident labels |
| **4** | **REVISED** | Five logical blocks with **units and scenario workload**, distinct from 3 possible physical MVP processes: ingress 300 tickets/h; ASR 4 + VL 1 slot-equivalents; text Qwen 2 slots, input ~100 tok/s + output ~16.7 tok/s; DB ~0.25 writes/s; delivery ~7.5 digests/h; clearly says slots ≠ GPU. Driven by q=20 tickets/manager/day, active 8 h, peak 3×, RTF=.5, VL=8s/image, text model 12s/req, 20 digests/day — ALL assumptions |
| 5 | Unchanged | Internal-only media, security boundaries and scope data |
| 6 | Unchanged | Qwen suggests, backend counts/routes/writes; unknown product routes to human |
| 7 | Preserved | Three SYN-QUEUE IDs are invented. Insight remains DRAFT, not sent, no root-cause/trend proof |
| 8 | Unchanged | Six proposed testing/release gates, 2 independent reviewers + adjudicator |
| **9** | **REVISED** | Separate synthetic clocks: first relevant ingest 26.10.2026 09:00 UTC; qualified 30.10 09:00; sent 30.10 09:05. E2E **96 h 05 min** vs qualified→sent **5 min**. Suggested p90 TPI ≤4h applies **only** to the latter; report undelivered/eligible + backlog; actionable precision ≥0.80 and routing ≥0.95 are **proposed release targets**, not measured. Decision SLA ≠ real resolution |
| 10 | Preserved | 3-year realized-value PV estimates 123k/1.64m/7.39m RUB; conditional scenario with unknown project costs, NOT actual ROI |

## Validation executed on actual session artifacts

- PPTX `Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pptx`, **10 editable native slides**, 16:9.
- Presentation PDF `Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pdf`, **10 rendered pages**; real slide text extracted with MuPDF, no glyph boxes outside PDF page boundaries; all native slide shape bounding boxes inside PPTX canvas.
- Rendered all ten slides to individual PNGs, inspected actual slide 4 and 9 at presentation resolution plus 10-slide contact sheet. Fixed slide9 Russian wording `Доставка продукта` → `Доставка команде` before final render; no visible clipped/overlapping elements found in inspected output.
- Executable local QA asserts exact 10-slide/10-page count, editable PPTX shapes, 16:9 ratio, zero off-canvas shapes, 3 synthetic IDs, all sizing figures, TPI/E2E numbers, stated proposed KPI thresholds and unchanged financial amounts. **This is render/source QA, not real Qwen, capacity/load testing, model validation, or full accessibility audit.**
- Reusable `build_final.js` included in download ZIP alongside QA JSON, 10-slide contact sheet, PPTX and PDF. The attached GitHub connector accepts UTF-8 text, but binary slide export and builder have not been pushed to PR; downloadable session artifact remains the precise file handed to the user.

## Exact artifact SHA-256

| File | SHA-256 |
|---|---|
| Final PPTX | `7a8e22057885e6692b9a14dcca211b60bdf5e56b8558d05293e203d5b11caf83` |
| Final slide PDF | `f46805ba42cd823d4731a2404e2a61f8ce66284d7ebaa7649e713850a3848083` |
| Source JS builder in ZIP | `e32e3e9932a57e0e2c7028336f9c1bc7d417d3ca685345c58e55e49b0e0fbec8` |
| Final contact sheet | `7051881b2075c8e3e1cc8b7acc5916851ed59bac9351cdc857562353d0f0524e` |

## Outstanding review gates / caveats

1. Independent Russian business/technical/editorial review and actual rehearsal to validate readability at projector size.
2. No empirical RTF/GPU/p95 Qwen or customer traffic. The `4+1+2` values are scenario concurrency **equivalents**, not physical worker/GPU promises.
3. The 96h05 clock and the 5m TPI are **fully synthetic**, and describe a distinct timeline example from slide7's fictional complaints.
4. Sources in GitHub (main+KPI+storyboard) are versioned; PPTX/PDF and generator JS live in a session review ZIP, not in the GitHub repo. A future text edit must trigger regeneration/re-QA, not silent divergence.
5. Organizer submission cutoff and actual portal upload receipt remain unverified; no submission/merge/deploy performed.

**Disposition:** final PPTX candidate **passes author visual and numeric QA**, source storyboard is updated. Not independently approved or submitted. Keep Draft PR #24.
