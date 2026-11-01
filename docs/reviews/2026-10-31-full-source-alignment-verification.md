# Full PDF-first scope correction — final author review, 2026-10-31

**Primary normative source:** original user-provided 7-page `Кейс_Искусственный интеллект.pdf`. **Status:** author self-review; NOT independent business, engineering or Russian editorial approval. The project remains on clean docs-first V2, Draft PR #24.

## Most important correction

- **PDF p2** speaks about **dozens of internal and external digital products** at Gazprom Neft and transferring repeated non-critical user requests/wishes to appropriate product teams without added support workload.
- **PDF p6** says exactly: seven examples are provided from **one** product, `Вебнефть` (B2B small-wholesale fuel ordering). This product is **illustration**, not exclusive target.
- **PDF p4** ~40 support managers belong to **all covered products**, not 40 managers of Webneft.

## What changed after critical review

| Finding | Correction / evidence |
|---|---|
| Incorrect Webneft-only framing in old cover/footer, spec and docs | README, requirements, architecture, 10-slide deck and exported cover now identify a **multi-product** Gazprom Neft agent |
| Model prompt embedded a fixed Webneft-specific business_journey enum for all products | `docs/agent/system-prompt.ru.md` now uses `allowed_business_journeys` and `allowed_symptom_codes` selected per **backend-verified product_id + taxonomy_version**. Webneft issue classes are case examples, not universal enums |
| Retrieval/counts might mix tickets from different products | Default `scope_id+product_id` boundary for retrieval, recurrence, coverage and routing; unconfigured product/owner → human triage; separate consented normalized taxonomy required for cross-product insights |
| Multi-product acceptance was not tested at design level | T21–T24 added: synthetic second product, unknown product, unauthorized cross-product join, stale routing; 24 scenarios total (test **design**, no live Qwen run) |
| KPI/finance could be interpreted as Webneft-only results | Company-wide scope ≈40 across covered products, with per-product/team/channel metrics and transparent corporate aggregation; no company baseline or verified ROI claimed |
| Visual presentation remained Webneft-branded in footer | All slide footers now say `ЦИФРОВЫЕ ПРОДУКТЫ`, Webneft stays as one worked example on slide 3 and prompt on slide 7 |
| Binary exports were editorially separate from GitHub Markdown source | New multi-product DOCX/PDF/PPTX/mandatory item-5 .md generated and packaged with exact final Markdown source and SHA-256 manifest. **They are not in GitHub** and repo's long Markdown draft is not byte-identical with shorter export source |

## Real verification performed

**GitHub Actions exact source HEAD:** [#41136745286](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41136745286) **SUCCESS**, including:
- source main=14,535 characters (limit 15,000), sections 1–4,6, standalone item 5, seven source examples and ten-slide storyboard;
- four synchronized Mermaid sources, **24 adversarial scenario definitions**, seven syntactically valid design JSON blocks;
- explicit multi-product/taxonomy/route boundary regression checks;
- independent arithmetic recalculation of the three financial scenarios and sensitivity values.

**Local actual artifact QA:** generated from edited export Markdown and inspected with the DOCX renderer, LibreOffice, PDF text extraction and ten-slide PDF contact sheet:
- Main Russian DOCX text **12,449 visible characters**, source Markdown **13,037 characters**; **3 A4 pages** in exported PDF.
- Question 5 is a **separate .md**, **9,466 Unicode characters**.
- PPTX has **10 editable vector slides**; PDF rendering has **10 pages**. Verified a company-wide footer on every slide, Webneft as a single illustrative product, enterprise product ID boundaries and corrected finance subtitle.
- The initial DOCX renderer produced a sparse fourth page; adjusted page margins/paragraph spacing and re-rendered **three full clean pages**.
- Combined review ZIP contains DOCX/PDF, item-5 Markdown, PPTX/PDF, reviewed main Markdown source, SHA-256 manifest.
- Artifacts live in the **current conversation container/session**, not in GitHub binary attachments; the UTF-8 text-only GitHub connector cannot upload them. In particular, do not assert that PR #24 includes the generated DOCX/PPTX.

## Rubric final status

| PDF item | Draft state | Important limitation |
|---|---|---|
| Q1 Architecture | Covered: logical services, multi-product routing, load assumptions | No live enterprise API or real throughput verified |
| Q2 Tools | Covered: read-only + verified aggregation + policy writes | Proposed, not deployed |
| Q3 Prompt | Covered: product-scoped allowlist, JSON, evidence, abstention | Not run against a real internal Qwen endpoint |
| Q4 Evaluation/release | Covered: labels, threat tests, stages | No company gold labels, pilot or actual model scores |
| Q5 Effect metrics | Separate Markdown | Missing actual manual baseline, time clocks and product/team sample |
| Q6 Economic model | Three scenarios, macro sensitivity, alternatives, conditional 3-year benefit ceiling | These are **assumptions**, not actual cash savings/ROI; real C unknown |
| Submission | Main DOCX+PDF under cap; 10 slide PPTX and PDF | Still requires independent human Russian/business review before upload |

## Open corrections / risks

1. **Independent reviewer approval is missing**; this remains self-review. The team must validate terminology, presentation narrative and business assumptions with the original PDF before actually filing the competition response.
2. There is **no source-to-export byte identity** between GitHub `submissions/main-solution.ru.md` (14,535 characters) and download `gazpromneft_main_reviewed.ru.md` (13,037 characters). Both pass the same PDF scope and <15k constraints, but **the downloadable Markdown in review ZIP is authoritative for the generated DOCX/PDF**. Any future edits should reconcile them before submission.
3. No internal Qwen API, ticket DB access, real customer dataset, product ownership map or external-source performance claim has been verified.
4. PowerPoint slides were rendered and visually checked; standalone `.mmd` files have passed GitHub-source sync checks, not all Mermaid layout cases independently.
5. PR must remain Draft; no merge, deploy or submission automation.

**Disposition:** source and newly generated review artifacts corrected and verified for **multi-product Gazprom Neft scope**, with Webneft only as example. Draft ready for **independent content review**, not certified final by company/organizers.
