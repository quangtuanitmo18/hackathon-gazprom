# Synchronize final exported Markdown to GitHub — Plan

**Scope:** user-authorized text-only sync on Draft PR #24, no app code/merge/deploy. Export sources: conversation-generated files `gazpromneft_main_reviewed.ru.md` and `gazpromneft_05_effect_metrics.ru.md` (the source used to produce the multi-product review document).

## Step 1 — Source identity & discrepancy review
- [x] Verify both exported files exist and can be read **without re-authoring**.
- [x] Compare them with GitHub `submissions/main-solution.ru.md` and `submissions/05-effect-metrics.ru.md` at current V2 branch HEAD.
- [x] Confirm expected original main is 13,037 Unicode characters (below 15,000), sections 1–4 and 6; item 5 is a separate Markdown source.
- [x] Note discrepancies: previous GitHub text has 14,535 chars vs 13,037 export; item-5 GitHub has 11,384 vs 9,466 export. Previous validator assumed `один год` instead of equivalent `1 год` and a nonessential three-year gross total shown in the main table.

## Step 2 — Exact synchronization
- [x] Replace **only** the two GitHub submission Markdown files with the exported sources, preserving UTF-8 and trailing newline.
- [x] Re-fetch both GitHub files and compare exact text content to the exported originals; no paraphrases, truncation, or extra sections.
- [x] Tighten/adjust document validator to test *equivalent required semantics* and independent financial arithmetic, not specific old prose or whether full scenario detail is duplicated in the capped main document.
- [x] Preserve all other documents and the separate 10-slide presentation; exported DOCX/PPTX binary files are not being rewritten.

## Step 3 — Verify and review
- [x] Run GitHub Actions on exact new commit SHA; inspect job conclusion/logs, not just a previously successful run.
- [x] Record source lengths, SHA/hash-based provenance, compliance with official 7-page PDF and remaining editorial/binary export limitations.
- [x] Add COMMENT-only self-review to PR #24; keep it Draft and do not merge or deploy.

**Critical distinction:** source Markdown exactly matching the original exported Markdown does not mean GitHub CI has rendered the DOCX/PPTX. Actual document output was previously created and visually inspected separately; future edits must regenerate binary exports, not merely modify Markdown.

## Verification checkpoint

- Both files matched the originals **byte-for-byte** based on re-fetched GitHub blob hashes and full text equality. Main 13,037 Unicode characters, item-5 9,466.
- Source-level CI **SUCCESS**: [Actions 41137544563](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41137544563) on validator SHA `7954bc82745cd768c5e3271a1bd696faf2dd2880`.
- [Critical self-review and source hashes](../../reviews/2026-10-31-export-markdown-github-sync-review.md).
- PR COMMENT-only author self-review posted (review ID `5719309313`). No independent approval implied.
