# Integrated submission audit — Gazprom Neft Intelligence Cup, 2026-10-31

**Scope:** audit actual final Word/PDF + separate question-5 Markdown + ten-slide editable PPTX/PDF against official 7-page case PDF, current GitHub source and mathematical assumptions. **Author QA only, NOT independent business/Russian review, contest submission or measured model performance.** Source branch `feat/webneft-case-v2`, Draft PR #24, unmerged.

## Actual reviewed final artifact set (conversation-download ZIP, not GitHub binary commits)

| Role | Filename | SHA-256 |
|---|---|---|
| Main Word | `Intelligence_Cup_2026_GazpromNeft_Final_Candidate_Professional_Reviewed.docx` | `e61ed09c2f9ba31e29ffa5533de1fcf26b1810059edaf2f01fbd86b4b8b2b39f` |
| Main PDF | `Intelligence_Cup_2026_GazpromNeft_Final_Candidate_Professional_Reviewed.pdf` | `6ca7cef0f5c86202ee02ad20f0e1bf9c1883181e9cfe7bdfdc0aafa225638bd0` |
| Mandatory Q5 Markdown | `Intelligence_Cup_2026_GazpromNeft_Q5_Effect_Metrics_FINAL.md` | `2d717cecb2448212b4b180d62dbe0aa925b94eeedb5ef900e16a6c2bbb62752d` |
| Presentation editable | `Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pptx` | `7a8e22057885e6692b9a14dcca211b60bdf5e56b8558d05293e203d5b11caf83` |
| Presentation PDF | `Intelligence_Cup_2026_GazpromNeft_Final_Presentation_Candidate.pdf` | `a022bef5333bfda716dcb269374fdda1e680ce80445b764da5594540a326bda4` |

**Important correction identified and fixed:** the earlier `gazpromneft_05_effect_metrics.ru.md` export in the session was **STALE** (9,466 Unicode characters). We reconstructed the latest 11,671-character Q5 source **exactly** from the versioned GitHub changes and independently verified Git blob SHA-1 `ecd4943f48b9b318ea76477652b74ffae329030b`. Only the **FINAL** variant above is in the delivery ZIP. Canonical main source Git blob SHA-1 `93808fee68ec41f0ddf84ddf2b7d4039e53bcc6c` and 14,225 characters. No changes were made to either canonical submission Markdown text.

## Compliance and document findings

- **Main Q1–Q4 and Q6**, and not Q5: 14,225 characters in standalone Markdown, 13,427 flattened DOCX paragraph/table visible characters; **both under 15,000**. No DOCX external hyperlinks used to evade limit.
- The original **3-page** Word formatting was overly dense (9-point Normal body, ~7.5-point tables). We made a **format-only readability revision**: Normal around 11 pt, tables around 9 pt, mono block ~8.4 pt. Final DOCX is **4 A4 pages**, text **exactly equal** to original Word body/table output, **3 editable native tables**, **2 native editable Office Math elements**. Rendered actual final DOCX into four PNG pages; inspected all pages. The tools table legitimately continues onto the following page with a repeated header (not missing rows).
- Q5 is an actual separate UTF-8 Markdown, with **qualified→sent TPI vs first observed→sent E2E**, undelivered/backlog, reviewed-selection bias, precision label rigor and timely **decision**, not confirmed issue resolution.
- Presentation: **10 editable 16:9 slides** and **10 rendered PDF pages**; verified PDF text extraction/Cyrillic and no off-page text/shape bounding boxes. Inspected all slide thumbnails. Seven source Webneft example narratives grouped in five rows; slide 7's three `SYN-QUEUE` IDs conspicuously synthetic, not empirical recurrence; slide 9's time clocks entirely separate synthetic illustration; explicit multi-product Gazprom Neft scope.

## Numerical verification and realism

- Original finance scenarios independently recomputed: 3-year present value of **123,099 / 1,641,322 / 7,385,950 RUB** with stated hypothetical inputs. Only ≈40 support managers originates as a case-provided quantitative fact. No real ROI/payback or company staffing savings claimed.
- Workload recomputed for scenario 40×20 = **800 tickets/day**, 8-hour shift with hypothetical peak=3× gives **300/hour**, ASR=4, VL=1, Qwen text=2 illustrative equivalent model slots. Neither model throughput nor GPU count is known.
- Illustrative KPI: 26.10.2026 09:00 first observed; 30.10 09:00 qualified; 30.10 09:05 sent => **5-minute qualified→sent vs 96h05 first-observed→sent**. Not a true company event.
- **Extra PPTX↔PDF parity:** re-exported the selected PPTX separately via LibreOffice. All ten normalized PDF page texts match, and all ten 72-DPI rendered pages are pixel-identical (100% exact RGB bytes); different file PDF checksums reflect export encoding/metadata and must not be mistaken for a different deck. Manifest lists *actual delivered* PDF SHA, not a stale historical SHA.

## Unresolved (do not mark a contest submission as approved)

- **Independent reviewer:** Russian-speaking human business/technical editorial signoff still required; this is an author's process/semantic audit.
- **Organizer portal:** exact submission deadline, permissible upload details, team eligibility and receipt still need verification; PDF cover's event window is not automatically a file-upload cutoff.
- **Real data & evaluation:** no company support time study or ticket corpus, real Qwen-ASR/VL inference, source completeness, gold labels, measured latency, model precision, benchmarked concurrency or actual investment cost.
- **Binary provenance:** the download ZIP, Office files and PDF are in this ChatGPT session; they are **not stored in the Draft PR via the text-only GitHub connector**. Canonical Markdown source and its Git blob references remain versioned in GitHub.

**Disposition:** **PASS as a verified review-ready artifact set, NOT final approved/submitted**. Keep Draft PR #24 open, don't merge/deploy/submit automatically. Final downloadable ZIP also contains a JSON file checksum manifest and a separate Markdown integrated audit report.
