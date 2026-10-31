# Superpowers plan — final 10-slide jury defense & organizer eligibility gates

**Started:** 2026-10-31. **User instruction:** continue next phase after integrated submission QA; current PR #24 remains Draft. **Scope:** review presentation script/Q&A, simulate a critical jury, verify current organizer participation deadlines/eligibility from external sources. No external email, actual submission, merge/deploy, or confidential Qwen API work.

## Normative hierarchy
1. Original seven-page official PDF (case facts, Q1–6, p5 formats and p7 six *unweighted* criteria).
2. Selected final session deliverables (latest 4-page DOCX/PDF, exact Q5 Markdown, PPTX/PDF 10 slides).
3. GitHub canonical source main and Q5 and the versioned synthetic case. Slides are delivered binaries, not GitHub artifacts.
4. Third-party 2026 announcements **only** for registration and logistics (do not alter PDF technical case facts).

## Task A — Actual final deck drift detection
- [x] Extract text from **the currently delivered final PPTX**, all ten slides, and compare to older speaker notes and 22 Q&As.
- [x] Flag any stale assertions: slide 4's 300/h + 4 ASR / 1 VL / 2 text equivalent slots, slide 9's 5m vs 96h05 separate fully synthetic timeline; pilot targets not measured.
- [x] Update Russian speech **for actual final deck**, not earlier Jury Review v2, with 7–9-minute rehearsal and ≤3-minute fallback if organizer times are unknown.
- [x] Revise Q&As to challenge invented capacity, financial assumptions, incomplete coverage, time clocks, tool permission and multi-product claims. No fictional confidence intervals or enterprise outcomes.

## Task B — Organizer real-world participation blocker
- [x] Verify current 2026 sources: reports 29 October registration cutoff vs official Intelligence Cup Telegram **30 October inclusive**, event final 26 November Saint Petersburg. Do NOT infer actual file submission deadline from either registration date or event end.
- [x] Flag published eligibility: only bachelor 3–4 / masters; postgraduate / aspirantura eligibility **not explicitly confirmed**. Team size 2–4.
- [x] No verified user/team registration or acceptance in available evidence; do NOT claim rejection/approval. Prepare a respectful Russian organizer inquiry asking registration acceptance, postgraduate eligibility, submission window and defense time.
- [x] Attempted official portals `cup-gpn.ru` and `gpn.intelligence.cup.hack.aim.club`; neither yielded a verifiable user-registration status. External updates provide divergent 29/30 October registration dates; organizer's Telegram says 30 Oct inclusive. Do not send organizer message without user action.

## Task C — Critical mock jury, independent-style author analysis
- [x] Score each of six **actual p7 rubric dimensions** as qualitative Strong / Needs improvement / Blocking, **not invented organizer scores**.
- [x] For each major weakness record challenge question, falsifiable acceptance test, priority and owner; separate conceptual design evidence from unmeasured live tests.
- [x] Business reviewer persona must explain WHO gets WHAT, WHEN, and how feedback affects decision; technical persona challenges abuse/PII, LLM-only inference and false-merge; financial persona challenges 3-year payback without cost C.
- [x] Script & Q&A corrected and reproducible against current PPTX; add format/source lint guards, exact headings, links and clear limitations.

## Task D — Execute, verify, document
- [x] Change only speech, Q&A, review materials, validator if necessary; **do not modify user-approved final DOCX/PPTX** without a concrete discovered error and explicit QA regeneration.
- [x] Run source CI [41202759977](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41202759977) (SUCCESS) on script/validator commit `00a50af`; after this documentation-only checkpoint commit, **re-verify final HEAD** before claiming final pass.
- [ ] Post COMMENT-only author's red-team review to Draft PR #24; no auto approval, merge or deployment.
- [x] Produce downloadable rehearsal pack in session (Markdown/PDF if useful) plus report of eligibility/deadline limitations.

**Acceptance:** corrected Russian script matches final ten actual slides and numbers; realistic high-pressure Q&A, no real Qwen/ROI assertion; user gets a clear actionable warning on registration & postgraduate eligibility and a ready-to-send inquiry; **only independent team/domain reviewer can sign off**, author role-play is not independent approval.

## Authored results & residual blockers

- Final deck extracted from actual PPTX: 10 slides (heaviest slides 4,7,9 are 809,906,819 native shape characters); Q&A retains **22** numbered problems and additional critical counterexamples.
- Speaker script updated on slides 4 and 9: 300/h and hypothetical 4/1/2 service slots, QPI qualified→sent=5m vs E2E=96h05 on a separate SYNTHETIC example. Spoken body approx 833 Russian words (~6.4–7.6 min at 130–110 wpm, excluding pauses/transitions), NOT an organizer-defined duration.
- [Red-team review](../../reviews/2026-10-31-jury-red-team-final-deck.md): six actual PDF p7 rubric dimensions, 10 challenge questions, evidence limits, organizer P0 gate. 
- [Organizer inquiry draft](../../submission/organizer-eligibility-and-upload-inquiry.ru.md): team registration and aspirantura permission unresolved. NOT sent.
- Local user download: 1-page Cyrillic `Intelligence_Cup_2026_Jury_Defense_Quick_Card_ru.pdf` with visual rendering checked, plus editable Markdown and unsent inquiry, packaged as `Intelligence_Cup_2026_Jury_Rehearsal_Pack.zip`.
- **NOT completed:** independent external Russian/business reviewer signoff, official portal team acceptance/eligibility, real measured pilot/ROI, submission/upload receipt. No merge/deploy.
