# Final integrated submission QA — plan (2026-10-31)

**Scope:** user asked to proceed after Word and 10-slide deck regeneration. Review the **actual** current deliverables as one submission, package only verified files and record truthful unresolved blockers. **No new runtime code, merge/deploy or organizer submission.**

**Official source:** user-provided seven-page `Кейс_Искусственный интеллект (1).pdf`, pp.2–7. The company-wide AI Agent is the subject, seven Webneft requests are one product's examples. PDF p5 requires main DOCX/DOC/PDF Q1–4,6 within 15k chars, Q5 standalone .md, presentation ~10 slides and no hyperlink supplements that evade the cap.

## Task 1 — Source integrity and stale-artifact control
- [ ] Confirm main branch source is 14,225 Unicode chars, Git blob `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c`.
- [ ] Fetch exact **current** Q5 source Git blob `ecd4943f48b9b318ea76477652b74ffae329030b` (11,671 chars); do NOT ship older 9,466-character KPI snapshot.
- [ ] Record SHA-256 for selected DOCX/PDF/PPTX/slide-PDF, plus exact Q5 source proof, and current GitHub PR HEAD.
- [ ] Confirm native editable artifacts and page/slide counts.

## Task 2 — Original PDF vs finished outputs
- [ ] Check Q1..4 and Q6 in *visible* DOCX/PDF and 15k limit by two measures (DOCX visible text, main source Markdown).
- [ ] Verify Q5 remains separate and includes qualified→sent and first-ingested→sent measures with missing/backlog treatment and correct independent-precision denominator.
- [ ] Verify seven Webneft source examples remain seven illustrative narratives in slide 3, synthetic slide 7 data remains openly hypothetical, actual multi-product scope preserved.
- [ ] Recalculate all three finance PV assumptions and five-service synthetic load scenarios; no claim of realized savings, measured precision or actual Qwen/GPU benchmark.
- [ ] Cross-check the deck's two synthetic clocks and proposed thresholds match Q5 definitions.

## Task 3 — Rendered visual/layout/accessibility inspection
- [ ] Render **latest** DOCX with canonical renderer and compare actual PDF page count with the selected main PDF; inspect each page.
- [ ] Render actual 10-page presentation PDF to images and inspect all slides; detect off-slide shapes/text overflow/blank pages and clipping with programmatic bounds + visual contact sheet.
- [ ] Record limitations: renderer checks are not independent reviewer signoff or real business evaluation.

## Task 4 — Publish review-ready handoff and GitHub evidence
- [ ] Build a single zip containing exactly approved five final deliverables (main DOCX, main PDF, canonical KPI .md, presentation PPTX, slide PDF), manifest/checksum and one integrated audit report.
- [ ] Compare selected file names/checksums to source and extractable contents.
- [ ] Run GitHub Actions on the **actual final HEAD** and cite exact run; author COMMENT-only self-review on Draft PR #24, no merge/approval.
- [ ] Identify outstanding **independent Russian/business review**, organizer portal actual deadline and upload receipt, actual Qwen/ticket baseline/ROI unknown.

**Acceptance:** 0 detected blocking format/source/semantic issues in reviewed outputs; 15k rule demonstrated; all numerical input assumptions disclosed; 10 editable slides; Q5 current and exact; any remaining blockers explicit, not hidden under PASS badges.
