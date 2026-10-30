# Webneft V2 — Final Submission Export and Visual QA Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Assemble final contest-ready Russian DOCX + readable PDF (official answers 1–4,6, ≤15,000 characters), mandatory standalone question-5 Markdown, and a visually clear 10-slide PPTX, with verifiable source and visual QA. **No app code.**

**Architecture:** Use user-approved Hybrid C, with the official 7-page case PDF as normative source, V2 authored Russian submission and diagram sources as editable material. Diagram illustration can be redrawn as native PPTX shapes for legibility; Mermaid source remains versioned. Do not imply a live deployed service or real model evaluation.

**Tech stack:** Python docx, PowerPoint generator, LibreOffice, PDF/slide rendering, existing GitHub source validator; diagram editing in Mermaid and vector-native slides. Final binaries may be delivered as session artifacts and only attached to GitHub if an authenticated binary-capable workflow is explicitly available.

**Spec:** `docs/superpowers/specs/2026-10-31-webneft-evidence-first-agent-design.md`.

## Global Constraints
- Source PDF pages 2–5, 7: mandatory response items 1–4+6 in a self-contained DOC/DOCX/PDF under 15,000 characters; item 5 separately as .md; ~10-slide visual deck.
- Need architecture microservice sizing, tool/prompt examples, testing and acceptance, three-year conditional finance and investment alternatives.
- No external Qwen/LLM/API, no real ticket/customer data, no invented model performance or company ROI.
- Historical Webneft description and seven PDF sample narratives are not ground-truth duplicate labels or incident root causes.
- The final output must preserve Cyrillic, remain readable after PDF/slide rendering, and not rely on GitHub links to expand the 15k limit.
- No automatic merge, deploy, external tracker write or production data access; keep draft PR #24.

## Review Focus
1. 15k source Markdown vs *exported visible DOCX text*: check **both**, allowing no appended external supplement inside document.
2. Mermaid syntax and Cyrillic layout may differ between GitHub markdown and raster exports: inspect **actual rendered pages** or create PPT-native legible flow.
3. Script/programmatic slide exports may clip content, especially tables and long Russian labels: inspect every slide.
4. Final slide claims must be distinguishable as PDF-confirmed, proposal or hypothetical finance.
5. Question-5 .md must be standalone (not hidden in the main document) and KPI denominator must not conflate accepted/reviewed with independent precision.

---

### Task 1: Source & contract proof
**Files:** `submissions/main-solution.ru.md`, `submissions/05-effect-metrics.ru.md`, `submissions/presentation-outline.ru.md`, `docs/requirements/pdf-traceability.md`.
- [x] Compare final narrative against official PDF pages 2–5 and 7.
- [x] Check exact math and separate KPI definitions against existing CI-verified scenario inputs.
- [x] Review unsupported claim risk, especially 2026 Webneft features, Qwen endpoint, real throughput, ROI and root cause.
- [x] Record source-to-slide/script mapping in final QA report.

### Task 2: Real formatted main submission
**Output:** `main-solution.ru.docx`, `main-solution.ru.pdf` (no extra appendix); check at most 15k Cyrillic/Unicode characters in visible DOCX text.
- [x] Author using edited Russian source (not fabricated case claims) with consistent headings, tables, prompt code block, finance.
- [x] Render via docx skill `render_docx.py --emit_pdf` and visually inspect every page.
- [x] Extract visible DOCX text and measure length; PDF extract sanity check for glyphs and clipping; fix and re-render.

### Task 3: Ten-slide 16:9 presentation
**Output:** `intelligence-cup-webneft.ru.pptx`; no external photo fetching necessary.
- [x] Use editable native vector shapes/dataflow in PowerPoint, based on four existing Mermaid diagrams. Export diagram sources remain preserved in `docs/diagrams/*.mmd`.
- [x] Match outline 10 key slides, one main message each. Use small, sparse text and no off-slide elements.
- [x] Render every PPTX slide to PDF/PNG, inspect Cyrillic and layout at presentation size; iterate.

### Task 4: Final review, CI, handoff
**Files:** `docs/reviews/2026-10-31-final-export-visual-qa.md`; optionally update README submission links.
- [x] Verify exact artifact paths exist in current runtime and attach them directly in chat.
- [ ] Run existing Github CI on final source HEAD and verify job logs.
- [x] Record factual limits (no real baseline or inference, independent editorial approval missing).
- [x] Keep PR Draft; no merge, deploy or external writes; if binary repository upload not available, explain session artifacts remain downloadable but aren't in GitHub yet.

**Human approval required:** independent domain/editorial review before competition submission; generated PDFs/slides are *deliverables for team review*, not confirmed filed contest entries.


## Execution checkpoint (author self-review, 2026-10-31)

- Russian DOCX + PDF generated and visually inspected; **3 A4 pages**, 11,570 extracted DOCX-visible characters and 12,130 source Markdown chars (<15k).
- Q5 standalone Markdown copy 8,496 Unicode characters; NOT a second section in the DOCX.
- Presentation **10 actual slides** (editable native PPTX shapes) and 10-page PDF render, visually inspected, with two initial visual problems corrected (slide 10 note collision and slide 4 last block position).
- [Detailed artifact hashes, review and remaining risks](../../reviews/2026-10-31-final-export-visual-qa.md).
- **Outstanding:** verify latest repo-source GitHub CI run and obtain independent external Russian/business review and organizer upload confirmation. The chat-delivered binaries are **not committed to GitHub** because only text file writes are available in the linked GitHub workflow.
