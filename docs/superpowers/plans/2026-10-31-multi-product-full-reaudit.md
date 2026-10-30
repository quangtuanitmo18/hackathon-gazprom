# Superpowers Plan — Scope-first Full Reaudit for Gazprom Neft Intelligence Cup

**Date:** 2026-10-31. **State:** approved direction from conversation: review everything from original PDF; no runtime code or deployment. This plan is a work plan, not a claim of independent approval.

## Primary evidence and hierarchy
1. **Normative:** original user-supplied 7-page `Кейс_Искусственный интеллект.pdf`.
   - **p1–2:** AI Agent serves **dozens of internal and external digital products** at Gazprom Neft; recurring **questions, wishes and non-critical difficulties** from support → relevant product teams without adding support workload.
   - **p2:** architecture/tools/annotated prompt/testing and release acceptance.
   - **p3:** item 5 effect/KPI (separate .md) and item 6 economic value and 3-year payback reasoning.
   - **p4:** ~40 support managers **across the addressable products**, source ticket DB and 1-year storage, calls+recordings, attachments, internal `Qwen 3.8`/`Qwen-ASR`/`Qwen-VL`, external API/LLM forbidden, cost side in money not required.
   - **p5:** main self-contained answer 1–4,6 ≤15,000 chars DOC/DOCX/PDF; item 5 separately .md; ~10-slide presentation; no linked supplementary workaround.
   - **p6:** exactly seven **sample requests from ONE product Webneft**, not the entire company scope or ground-truth same-incident pairs.
   - **p7:** justified microservices and load, KPIs with fallback, alternative investments and macro impact.
2. **Secondary:** DeepSeek analysis and historical Webneft public articles are context only, not current source/API truth.
3. **Project proposals:** hybrid Qwen + deterministic tools, 5 logical blocks / 3 MVP physical processes, thresholds, finance assumptions, any taxonomy and synthetic demo. Mark as assumptions.

## Critical risks observed before edits
- **P0 Scope confusion:** README, spec and presentation title/footer overemphasize Webneft. Must clearly state company-wide multi-product AI Agent; Webneft only a source case, no assumption every product is B2B fuel.
- **P0 Taxonomy leakage:** prompt and schema hardcode Webneft `business_journey` values as universal allowed list; make `product_id` and `taxonomy_version` backend-signed and per-product `business_journey` domain. Every product receives an independent product→team map, safe fallback when unconfigured.
- **P1 Metrics:** ~40 support managers is **total** within reach, not ~40 per Webneft; financial baseline applies whole multi-product scope. Distinguish per-product vs aggregate KPI, macro-average weighted by volume vs per-product fairness and feedback coverage.
- **P1 Example validity:** Webneft PDF #1 vs #2 related journey not verified incident, #3 and #5 one ticket even with two symptoms; no invented root cause, real times, same-incident labels or claims about current UI/API.
- **P1 Final format:** existing binary exports not synchronized byte-to-byte with GitHub source; all DOCX/PDF/PPTX need refreshed and visually audited, Russian source max 15k.
- **P2 Complex architecture:** explain proportional and illustrative sizing; never invent throughput, Qwen endpoints or real business results.

## Task 1 — Audit first, write evidence gap table
**Files:** `docs/reviews/2026-10-31-multi-product-source-audit.md`, `docs/requirements/pdf-traceability.md`.
- [x] Map exact PDF evidence to all 6 questions, submission constraints, and the difference between product scope and illustrative case.
- [x] Identify fact/hypothesis/model split; review all seven ticket examples and their sensitivity.
- [x] Record source-to-output gaps and proposed fixes with severity.
**Gate:** no assertion of current Webneft backends or production model endpoints without source.

## Task 2 — Correct multi-product design contracts, not just labels
**Files:** README, `docs/agent/{system-prompt.ru.md,output-contracts.md,tool-contracts.md}`, `docs/superpowers/specs/*`, `docs/architecture/webneft-v2-architecture.md`, `docs/requirements/implementation-strategy.md`.
- [x] Define trusted `product_id`, per-product `taxonomy_version` and routing registry, `product_id`-scoped retrieval/recurrence and `unknown_product` human fallback.
- [x] Keep Qwen semantic-only, internal-only media, deterministic scope/counters/routing.
- [x] Prevent cross-product aggregation by default; allow cross-product patterns only through explicitly approved harmonized taxonomy and evidence.
- [x] Record Webneft-specific codes exclusively as one example taxonomy; text model may not invent category IDs.
**Gate:** multi-product acceptance examples cover at least two distinct products (second product synthetic), including unconfigured product and cross-product leakage.

## Task 3 — Correct final Russian submission and presentation
**Files:** `submissions/main-solution.ru.md`, `submissions/05-effect-metrics.ru.md`, `submissions/presentation-outline.ru.md`, local editable DOCX/PDF/PPTX source.
- [x] Main narrative explains company-level problem and `product_id`-scoped agent tools, Webneft explicitly illustrative; no extra supplementary references in final main content.
- [x] KPI per product/team/channel + aggregate; ~40 managers across whole coverage only, never Webneft-specific financial total.
- [x] Slides have generic Gazprom Neft concept brand/headers; only the business example slide labels Webneft.
- [ ] Update title/metadata, 10 slides, review Russian typography, preserve diagrams with editable PowerPoint native shapes.

## Task 4 — Verify & review
**Files:** validator, `docs/reviews/*`, Draft PR #24.
- [x] Run regression checking main <15k, seven PDF examples still labeled provisional, Webneft limited to illustration, multi-product taxonomy/routing, finance recomputation and 10 slides.
- [x] Render DOCX page PNG and slide deck PDF/PNG; **visually inspect** all pages.
- [ ] Verify exact GitHub HEAD CI (not old SHA), and local exported artifacts independently.
- [ ] Critical self-review: distinguish source truth, hypotheses, outstanding independent review and lack of real Qwen/data.
- [ ] Update PR #24 COMMENT (not approve), keep Draft; no merge/deploy.

**Stop condition:** If final slide/PDF exports fail render, do not claim they're final. Do not substitute background work or promise later delivery.


## Author execution checkpoint (2026-10-31)

- [x] Independent-of-code source audit documented in `docs/reviews/2026-10-31-multi-product-source-audit.md` (PDF pages 1–7).
- [x] Multi-product taxonomy/route boundaries fixed in README, design spec, architecture, prompt, output/tool contracts; original Webneft examples remain unadjudicated.
- [x] Cross-product design adversarial scenarios T21–T24 and per-product KPI slices added. No real Qwen evaluation claimed.
- [x] Main DOCX/PDF (3 A4 pages, 12,449 visible characters), separate KPI .md and 10-slide editable PPTX/PDF exported locally and inspected.
- [x] GitHub Actions source contract **SUCCESS** at [41136745286](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41136745286) on source-check commit `b15c2c0`; later documentation commits require final-HEAD check.
- [x] Review report: `docs/reviews/2026-10-31-full-source-alignment-verification.md`. Specific source/export mismatch is disclosed.
- [ ] Confirm CI on the **latest** SHA after final review comments; independent Russian/business approval, organizer submission, and optional synchronization of binary artifact source to repo still pending.
