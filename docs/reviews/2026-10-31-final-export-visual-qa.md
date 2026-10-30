# Final Export and Visual QA — Self-review 2026-10-31

**Scope:** User-approved Hybrid C, **no application code**. 7-page official PDF is the normative source; Webneft sample tickets are illustrative and unadjudicated. This is an **author's self-review**, not independent approval, not a contest submission receipt, not a live pilot.

## Delivered conversation-session artifacts (not GitHub-committed binary files)

| Artifact | Format | Verified result | SHA-256 |
|---|---|---|---|
| `Intelligence_Cup_2026_Webneft_Reshenie.docx` | Editable Russian main document answering **1–4 and 6** | **3 A4 pages**; extracted **11,570 DOCX-visible characters** (source Markdown 12,130 chars), below 15,000 | `c07304f0b2261da70a7b49bfae70d9b5e22e4b75affca2997fe37b3b3d05501a` |
| `Intelligence_Cup_2026_Webneft_Reshenie.pdf` | Submission-style main PDF | **3 pages**, Cyrillic text extractable and inspected | `2c5730f2552934494f95f23c8d6c64b6ee2b3eccb547d71952376b8672a6e203` |
| `webneft_05_effect_metrics.ru.md` | **Separate mandatory item 5** | **8,496 Unicode characters**; independent precision denominator, TPI censoring, missing-baseline fallback, pilot governance | `579b23f059d019256a3b8c121e79841bfffd7538241ac3b4d20069cb024abc03` |
| `Intelligence_Cup_2026_Webneft_Presentation.pptx` | **10-slide editable PowerPoint** | LibreOffice export to 10 PDF slides, visual QA/contact sheet inspection; native shapes redrawn using Mermaid V2 spec | `9ffd2ff7922f21b7c1da2332b5d71d0b1ddbf8789317024867e4ad919039e1a5` |
| `Intelligence_Cup_2026_Webneft_Presentation.pdf` | Presentation PDF preview | **10 PDF pages**, slide 10 annotation overlap fixed after inspecting original render | `710e3a2682d42723fdd83ed4a800b1810bc14b0f30568c9e8c8ec739ea8f79e1` |

**Where binaries live:** generated in the current ChatGPT conversation's artifact container (`/mnt/data`) and shared with the user via download links in chat. **The GitHub connector currently accepts UTF-8 text-only content**, so these binary exports were NOT uploaded into repository or added to Draft PR #24. Do not claim the PR contains the binaries; the versioned Markdown, Mermaid diagrams, plans and reviewed storyboard remain in GitHub.

**Source-of-truth disclosure:** The binary **main DOCX/PDF** was editorially adapted from the V2 Russian draft, with aligned five logical functions and strict Qwen JSON model output, and is **not byte-for-byte the same as** `submissions/main-solution.ru.md`; a narrower source patch was applied to bring the GitHub Markdown draft's terminology in line. Similarly the downloadable item-5 Markdown is an edited standalone submission copy, not a byte-identical export of the longer GitHub work draft. Independent reviewer should select the final rendition for submission and, if desired, reconcile repo source precisely.

## Review of each contest criterion

- **Item 1:** architecture from ticket/call/media through internal Qwen/Qwen-ASR/Qwen-VL, trusted aggregation, risk-based internal delivery and feedback, five logical functions grouped into three hypothetical processes. Load uses **explicit hypothetical assumptions**: 40 managers from PDF; 20 tickets/person/day, 30% calls, 3-min audio, RTF=0.5 are NOT company facts.
- **Item 2:** bounded tool table and source scoped read/ASR/VL/retrieval/aggregation/routing/internal delivery. Counts, product routing and writes governed by trusted backend; no external URL/LLM.
- **Item 3:** commented Russian Qwen prompt with example strict JSON, source alias E1, no confirmation of same incident or root cause; NOT actual Qwen output.
- **Item 4:** unit/model/adversarial/integration/load evaluation, gold labels with two reviewers+arbiter, shadow→controlled pilot, thresholds explicitly marked **proposed not achieved**.
- **Item 5:** delivered in **separate .md**, not hidden in the main: p50/p90 TPI including undelivered/backlog, independent actionable precision rather than accepted/reviewed, routing+coverage, time study, fallback when retrospective clocks unavailable and monetization.
- **Item 6:** economic benefit is *not* salary saving. Three assumptions-based scenarios: PV of realizable benefit under hypothetical r=10%, g=0% is **123,099 / 1,641,322 / 7,385,950 RUB over three years**. **Actual C unknown**; no achieved payback/ROI claim. Manual reporting/rules+BM25/Hybrid C alternatives and macro sensitivity covered.
- **Slides:** 10 editable native PowerPoint slides: task, gap, seven tickets, 5-block architecture, trust/DFD, tools, Qwen example, evaluation stages, KPIs and finance. No image assets outside the competition context required.

## Visual and source checks performed

1. Created DOCX from edited Russian source; `render_docx.py --emit_pdf` produced **3 A4 pages**, inspected all page thumbnails and pages for Cyrillic glyphs, text flow and tables. An intermediate 4-page render ended in an almost-empty fourth page; formatting was corrected and the final artifact re-rendered at 3 pages.
2. Created PPTX with editable vector shapes (based on conceptual Mermaid diagrams). LibreOffice export created exactly 10 PDF pages. Inspected slide contact sheet and high-resolution spot checks of slides **4, 7, 10**; corrected page-10 note/footer collision, unsupported manual-reporting assertion on slide 2, and cramped alignment in architecture slide 4.
3. Extracted text from DOCX and PDF, checked **all items 1,2,3,4,6** exist and total DOCX visible character count is below cap; checked Cyrillic PDF extraction is successful.
4. Case-data facts distinguished from historical hypotheses and scenarios: seven sample tickets are not an incident benchmark; no current auction SLA, real transaction data, company performance or Qwen integration claimed.
5. The existing GitHub CI validates **repo source** but **does not execute these binary exports or validate live business truth**; the local document/PPTX generation underwent separate render and manual inspection.

## Outstanding / blockers

- [ ] Independent Russian-language editorial/domain review and signoff (required before actual submission).
- [ ] Final review of any changed visual and prompt wording by the project team; source/export byte-level sync if binaries will be managed in GitHub later.
- [ ] Actual baseline interviews, annotated company data, on-prem Qwen endpoint and model quality: **not available in PDF** and not represented as performed.
- [ ] Final confirmation on organizer portal's precise upload naming/form requirements and actual submission action (not done).
- [ ] Current standalone .mmd source diagrams have not been rendered and certified as four separate Mermaid files; PPTX redrawn vector diagrams **were** rendered/inspected.

**Decision:** artifacts are **submission drafts prepared for independent review**. Keep PR #24 Draft; no merge, deploy, real company data access or external tracker write.
