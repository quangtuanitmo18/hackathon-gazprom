# Jury review — Gazprom Neft V2 10-slide deck with synthetic E2E case

**Date:** 2026-10-31. **Author self-review (not independent approval).** User-approved Phase F focus: polish the pitch and prove an example of product team output **without coding an app**. Normative reference: supplied official 7-page PDF, p.2 (dozens of products / recurring wishes), p.4 (source channels, ~40 staff, internal Qwen, no external APIs), p.5 (about ten slides), p.6 (seven Webneft example requests), p.7 (clarity, financial/technical rationale).

## Jury-facing review matrix, every slide

| # | Review question | Verdict | Severity / action |
|---|---|---|---|
| 1. Product goal | Is the AI for all Gazprom Neft digital products, not only Webneft? | **PASS**: company-wide goal stated, Webneft explicitly one example | None |
| 2. Business problem | Does it avoid falsely claiming current manual reporting volume or workload? | **PASS**: current baseline unknown, ~40 staff belong to covered product scope | None |
| 3. Webneft | Are all seven narrative examples preserved without fabricated same-incident labels? | **PASS**: 7 represented as 5 journey-group rows; one narrative may contain multiple symptoms | Group rows should not be misread as 5 true recurring categories |
| 4. Architecture | Do product-specific pipelines make sense, and is deployment split justified? | **PASS with caveat**: five logical blocks and three *proposed* MVP processes | P2: sizing detail is in main written solution, not slide |
| 5. Privacy | Are calls, images and data kept inside the corporate environment? | **PASS**: raw audio/vision boundary, PII minimization, no external egress | Actual enterprise PII policy unknown |
| 6. Tools | Who is allowed to count and send to teams? | **PASS**: Qwen semantic proposal only, deterministic tools and policy-authorized writes | No real tool API present, by design |
| 7. Tangible insight | Can a judge see the output for the product team, not just model JSON? | **IMPROVED / PASS**: three conspicuously SYNTHETIC tickets; Qwen→trusted count=3→human-policy-gated Product Insight Draft, no claimed delivery or established root cause | **Original P1 fixed**: prior slide only displayed a model JSON; new slide displays a specific business artifact |
| 8. Acceptance | Is the rollout testable, with baseline, experts and shadow mode? | **PASS**: six proposed gates, two labelers + adjudicator, BM25 comparator | Gates are proposals; no real implementation/test claim |
| 9. KPIs | Is value measured with honest denominators and missing-data controls? | **PASS with caveat**: TPI/precision/routing/support time and suggested targets | P2: recall, reviewed fraction and completeness detailed in mandatory item5 .md rather than slide |
| 10. Economics | Is the financial story clear without inventing ROI or costs? | **PASS**: three assumed realizable 3-year PV figures and alternatives; ROI conditional on unknown cost C | P1: evidence of saved minutes is absent, per PDF — requires time study |

## End-to-end source integrity

- **Source fact:** PDF p6 #5 mentions a Webneft electronic queue-booking issue (404 / unavailable time). It is **one illustrative request**, not a repeated-incident label.
- **Demo-only input:** `SYN-QUEUE-001`, `SYN-QUEUE-002`, `SYN-QUEUE-003` are three *invented independent* ticket identities inspired by that topic, NOT derived live support records. No actual created/ingested timestamps.
- **Proposed logic:** backend-approved `product_id=webneft`/taxonomy; internal Qwen suggests `electronic_queue_booking`; trusted aggregator counts **3 in the synthetic observed sample** with unknown coverage; no statistically defensible growth or common root cause.
- **Business output:** draft `Затруднения с бронированием электронной очереди` with synthetic source refs, recommended investigation, team resolved only from an authoritative registry, **delivery not sent** and **feedback pending**. In an actual pilot this requires a policy-approved internal channel.
- [Versioned full scenario/JSON/Mermaid](../case-studies/webneft-synthetic-product-insight.md).

## Verified rendered deliverables (current container session)

| Artifact | Result | SHA-256 |
|---|---|---|
| `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pptx` | **10 editable slides, 16:9, 0 off-page shapes** | `4af725cb5674474869d751eef21cef5c53403a576b8083c27b46d065ea956ed9` |
| `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pdf` | **10 pages**, Russian text extractable; all pages rendered to PNG and contact sheet visually reviewed | `18ca77dc84725e4547b106d668423feaff7bee219972df68162324c869f7837b` |
| `Intelligence_Cup_2026_GazpromNeft_Jury_Review_Contact.png` | Visual overview of all 10 pages | `1da79609e4c519dcc3eeafdc4d57a07f4e04d51f5886e2655d2c2ebb756c9644` |
| `Intelligence_Cup_2026_GazpromNeft_Jury_Review_Pack.zip` | PPTX + PDF + contact sheet + QA JSON + source JS | Created and verified locally |

**How checked:** PowerPoint inspected using `python-pptx` slide/shapes/text extraction, PDF rendered through LibreOffice and MuPDF, with visual check of slide 7 and whole-deck contact sheet. Script verifies 10 pages/slide count, no off-canvas objects or PDF text boxes, 3 synthetic IDs, no claim of sending, scope/financial strings. These checks **do not** prove visual perfection or correctness of actual Qwen model outputs.

## Remaining risks

- **P1 business validation:** original PDF does not provide real manual baseline, gold labels, throughput or company-specific costs. Proposed KPI thresholds and 3-year financial PV are illustrative only.
- **P1 independent review:** only author review performed; request review from a Russian-speaking teammate/mentor before actual submission.
- **P2 detailed tooling:** slide 7 is the desired ProductInsight **business artifact**, not an exact already deployed API. JSON in scenario document is a demonstration extension of the existing V2 system contracts.
- **P2 artifact provenance:** GitHub connector accepts only UTF-8 text; binaries and build script were generated in current conversation session and packaged for download. `submissions/presentation-outline.ru.md` and this review are in GitHub, not binary PPTX/PDF.
- No real customer data, no external LLM/API, no app code, no merge/deploy, no actual product-team delivery.

**Disposition:** content and visual-source QA passed for a **final-candidate presentation** pending independent editorial/business review. Draft PR #24 stays open and unmerged.
