# Superpowers plan — peer-review handoff and actual submission gate

**Date:** 2026-10-31. **Scope:** prepare practical final review/packaging tools and priority actions; no participant acceptance, registration or organizer upload may be inferred from existing files. Keep Draft PR #24 and existing reviewed binary artifacts unchanged.

## Original source & already-completed work
- Official PDF: p2 Q1–4; p3 Q5–6; p4 on-prem Qwen/ASR/VL, company scope and ~40 staff; p5 Word (Q1–4+6, <=15k), Q5 standalone .md, ~10 slides; p6 7 Webneft examples; p7 six **unweighted** evaluation dimensions.
- Main written solution: 14,225 source characters, professionally rendered 4-page Word/PDF; Q5 exact-current Markdown 11,671 characters; presentation ten editable 16:9 slides; 4 Mermaid syntax-validated diagrams.
- Independent reviewer signoff is **not performed**; prior author multi-persona mock jury is *not independent*.
- Actual team registration, account acceptance, aspirantura eligibility and solution upload deadline remain **unknown**. Official channel states registration through Oct 30 inclusive; news reported Oct 29. Both are registration dates, not verified solution upload cutoff.

## Execution steps
- [x] 1. Produce Russian-language reviewer instructions and **separate review form** for Russian editorial/product evaluator and technical/finance evaluator; score PASS/REVISE/BLOCKED/NOT_VERIFIED, one evidence per claim, no invented scoring weights.
- [x] 2. Produce a clear **submission readiness decision tree**: registered and accepted vs awaiting status vs not registered; aspirantura status resolved separately, precise upload time authoritative only from user portal/organizer.
- [x] 3. Check selected final file manifest and exact package roles (Word/PDF alternatives, mandatory Q5 .md, ~10 slide PPTX/PDF), **not** upload all duplicates unless portal specifically allows. No annex hyperlinks to extend 15k content.
- [x] 4. Include five high-risk falsification tests (7→5 group count; synthetic 3 vs real one; 4/1/2 slots vs GPU; TPI 5m vs E2E 96h05; PV=benefit not cash/ROI) and actionable review questions.
- [x] 5. Verify GitHub source references, actual CI pass on HEAD, record author COMMENT only. No merge/deploy/submission or false independent approval.

**Acceptance:** user/team can hand the package to two people and obtain structured, reproducible P0/P1/P2 feedback; the decision to submit is blocked until the portal and eligibility are confirmed. Existing final deliverable content remains frozen absent an identified correction.

## Executed checkpoint

- [Unfilled two-reviewer scorecard](../../submission/2026-10-31-independent-review-scorecard.ru.md) includes the 6 organizer criteria, separate language/business and technical/finance roles, six material falsification tests and deliberately PENDING signature fields.
- [Portal Go/No-Go](../../submission/2026-10-31-portal-submission-go-no-go.ru.md) explicitly distinguishes the organizer's Telegram 30 October registration cutoff from unverified solution upload deadline and asks for platform-confirmed team status and aspirantura eligibility.
- No final deliverable binary or official Q1–Q6 submission source was changed in this phase. These are handoff/review process aids, not attachments to bypass 15k.
- Remaining: CI on exact final HEAD, COMMENT-only author review; independent human evaluation and organizer registration/portal confirmation require user/team action and cannot be certified by assistant.

## Final author verification

- [CI run 41206913052](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41206913052) **SUCCESS** on previous execution HEAD `8f8560d40502208def0894813a82f29f3e2cc1a0`.
- Main source Git blob `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c`, Q5 Git blob `ecd4943f48b9b318ea76477652b74ffae329030b`: unchanged. Six-criterion peer-review template exists with all **real signatures pending**.
- Author COMMENT-only PR review ID `5722972102`; **not** an independent PASS. No team registration, eligibility or upload receipt confirmed.
- This final plan-checklist commit is documents-only. Run CI on its exact HEAD before reporting the final PR state.
