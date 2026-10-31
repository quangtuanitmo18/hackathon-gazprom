# Audit plan — verify final solution against original 7-page case

**Status:** user requested a strict correctness review against two images (official PDF pp5–6). This is a **review-only / corrections to factual diagram wording** task, not authorization to rewrite the final submission or merge PR #24.

## Ground truth
- Local original `Кейс_Искусственный интеллект (1).pdf`, pages 1–7, including mandatory questions 1–6 and rubric p7.
- Two user screenshots show exact pp5–6 requirements and all seven example requests.
- Exported `Intelligence_Cup_2026_GazpromNeft_MultiProduct_Reshenie_Professional.docx`, PDF, `gazpromneft_05_effect_metrics.ru.md` and latest 10-slide `Intelligence_Cup_2026_GazpromNeft_Jury_Review_v2.pptx`.
- Latest GitHub source `submissions/main-solution.ru.md`, `submissions/05-effect-metrics.ru.md`, diagram source/gallery, 3-year financial input assumptions.

## Steps
- [x] Read all 7 PDF pages, not just screenshots.
- [x] Compare seven source examples semantically to main answer and slide 3; ensure grouping 7→5 cards isn't mistaken as five tickets.
- [x] Verify format 1–4 and 6 together in DOCX/DOC/PDF, Q5 separate Markdown, ~10 slides, ≤15k visible characters, no document hyperlinks used to bypass cap.
- [x] Recompute all three scenario PV calculations; distinguish provided N≈40 from invented m/a/w/k/r/g.
- [x] Verify scoring rubric p7: all six answers, detailed microservice rationale and service-load estimates, measurable KPI/fallbacks, macro sensitivity, alternate investments, visual slides.
- [ ] Correct clear ambiguity in sequence diagram's handling of incomplete coverage; preserve policy-allowed observed-only digests.
- [ ] Record actionable P1/P2 improvements while avoiding changes to byte-synced export source without regeneration.
- [ ] Check CI on new exact HEAD, log author self-review in draft PR; no merge/deploy/submission.

**Acceptance:** accurately report what's correct and what is only assumed. Cannot certify actual performance/ROI or independent judge scoring without real data.
