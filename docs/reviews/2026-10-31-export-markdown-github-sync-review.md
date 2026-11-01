# Self-review: exact exported Markdown synchronized with GitHub

**Date:** 2026-10-31. **Status:** author self-review and source-validation, **not** independent approval or new competition submission.
**Branch:** `feat/webneft-case-v2` / Draft PR #24, based on `main`. V1 archive unchanged, no application code, merge or deployment.

## Scope and provenance (unchanged export sources)

| GitHub path | Conversation export source | Unicode characters | UTF-8 bytes | SHA-256 local source | Git blob SHA-1, re-fetched on GitHub |
|---|---|---:|---:|---|---|
| `submissions/main-solution.ru.md` | `gazpromneft_main_reviewed.ru.md` | **13,037** | 20,417 | `cec470911a328779ecb44b79feae36b313bb759ff4f5afc9c72da745ad35dcf3` | `b7a564f39cf4c83bd72f480353f0e650b1ddf247` |
| `submissions/05-effect-metrics.ru.md` | `gazpromneft_05_effect_metrics.ru.md` | **9,466** | 15,011 | `e476d9e01e81fe667aa1ce43e8a073d3294e421f12f17f23bb57c2c64e370867` | `dd64b06712a4161e39e21648d97f827ecd7144d2` |

**Exact-match proof:** Retrieved both original conversation-generated Markdown files in full, preserved UTF-8 and final newline, replaced only the two submission Markdown paths in GitHub, re-fetched both from `feat/webneft-case-v2` and compared complete strings for equality. Both GitHub blob SHA-1s independently equal locally computed `SHA1("blob <UTF8-bytes>\\0" + bytes)`. No manual paraphrasing, truncation, or altered content.

**Prior drift resolved:** main GitHub file was 14,535 Unicode characters vs export 13,037; KPI GitHub file 11,384 vs export 9,466. After synchronization both match exactly.

## Validator review and risk control

The previous validator was tied to older prose rather than PDF semantics:
- old `один год` accepted alongside exported `1 год`;
- old literal `сценарные` accepted via `сценар`/ `гипотез`, preserving mandatory disclosure;
- Webneft as one illustrative product and `Мультипродуктовый контроль` accepted as semantically equivalent to old phrases;
- export source shows `taxonomy` in prose rather than literal `taxonomy_version`, while full per-product taxonomy schema remains in the dedicated agent spec;
- three-year **gross total** no longer required redundantly in the ≤15,000 character main when it is independently recomputed, present in financial assumptions, and the main retains **gross annual and 3-year discounted realizable benefit** for all three cases.

The validator still checks original PDF answer sections 1–4 and 6, separate KPI, Qwen/one-year/40 facts, enterprise multi-product scope, per-product agent scope, 7 deliberately unadjudicated Webneft examples, ten-slide outline, Mermaid source consistency, test definitions, JSON examples and **independent arithmetic recalculation** of all three financial scenarios plus 4 sensitivity rows.

**Verified GitHub Actions after validator update:** [run #41137544563](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41137544563), **success** on commit `7954bc82745cd768c5e3271a1bd696faf2dd2880`. Workflow checks source documents; does not render DOCX, validate a real Qwen endpoint, collect company baseline or independently approve the analysis.

## Artifact & submission caveats

- Existing conversation-generated **DOCX/PDF/PPTX** binaries were not re-exported or modified in this sync. Main DOCX visible text count (12,449) differs from Markdown character count (13,037) due to document formatting; this is **not** a content-identity proof for DOCX.
- **Source Markdown drift is resolved**, but the binary artifacts are still only available as conversation downloads, not checked into GitHub.
- The official PDF requires a human-readable main DOCX/DOC/PDF and a separate item-5 `.md`, plus ~10 slides. This change only aligns two sources, not a new formal submission.
- Independent human language/business review and enterprise data/PII/model verification remain outstanding.

**Disposition:** Exact exported Markdown is now the versioned GitHub source-of-truth. Do not merge PR #24 without independent review and explicit owner authorization.
