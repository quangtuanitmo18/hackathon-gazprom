# Critical self-review — KPI, release criteria and economics, 2026-10-31

**Reviewed source:** user-uploaded official 7-page Intelligence Cup PDF, specifically pages 3 (KPI + economic question), 4 (unknown reporting baseline, ~40 support staff, internal Qwen and no external APIs, cost-model exception), and 7 (selection of metrics/fallbacks, macro dynamics and alternative investments). Additional reference: Hybrid-C design (approved architectural approach), case source taxonomy and seven unadjudicated Webneft tickets.

**Scope:** document-only branch `feat/webneft-case-v2`, Draft PR #24. **This is author self-review, NOT an independent reviewer or Gazprom Neft signoff.** No real support records, model inference, dataset labeling, production actions or deployed service.

## Source claim trace

| Claim | Evidence | Decision |
|---|---|---|
| Need baseline retrospective and prospective KPI measurement | PDF p3 question 5; p4 specifically says current reporting frequency/workload **unknown** | Measured baselines marked unknown, no invented historic TPI |
| Need estimate 3-year benefit and conditional payback | PDF p3 question 6; p4 says monetary cost side needn't be computed | Show gross and realizable discounted benefit, **C unknown**, cost ceiling conditional |
| Count staff about 40 | PDF p4 | Use N=40 in examples, not tickets/day throughput |
| Source call audio and tickets retained 1 year | PDF p4 | Limit data authorization, source retention only; derivative policy requires separate approval |
| Internal Qwen, Qwen-ASR, Qwen-VL, no external API | PDF p4 | No external inference/provider in architecture |
| Alternatives + macro conditions | PDF p7 assessment criteria | Manual reporting, BM25, Hybrid C compared; r/g scenario sensitivity, no unverified current CPI or central bank assumptions |

## Findings, corrections and independent checks

1. **F1 — statistical denominator (corrected):** first KPI draft put unselected/abstained cases in the *precision* denominator. This is conceptually wrong: independent actionable **precision** estimates fraction useful among all selected-for-delivery samples; sample abstained/unselected separately to estimate missed opportunities, **recall** and routing coverage. Corrected in KPI, annotation and release gates.
2. **F2 — feedback selection bias (corrected):** product team's `accepted/reviewed` is conditional on response and must not be described as unconditional useful-signal precision. Add `reviewed/sent`, maturity windows, sampling including delivered signals with no feedback and independent blind adjudication.
3. **F3 — TPI time bias (corrected):** p90 among delivered insights alone ignores backlog and absent `qualified_at`. Add undelivered/eligible, censored window, audited source-observation timestamps, distinct historical proxy when clocks unavailable. No future timestamp leakage permitted.
4. **F4 — finance time-to-money gap (corrected):** staff time freed is **not** cash saving. Add explicit `k` for realizable value, `C` unknown and 3-year nominal discounted PV, compare costs on the same PV basis. Macro `r/g` are assumptions, not official Russian rates. Qualitatively compare manual, rules+BM25 and Hybrid C.
5. **F5 — service-count contradiction (corrected):** requirements trace formerly mentioned 4 logical service groups, architecture specifies **five logical components** grouped into **three proposed physical processes**. Updated trace to align with architecture; real deployment remains unknown.
6. **F6 — arithmetic (verified by CI):** `scenario-inputs.json` covers three gross/realizable financial cases and four discounted growth/interest sensitivity rows. `scripts/validate_case_submission.py` recalculates them independently, compares to `financial-assumptions.md` and to the main Russian answer (rather than asserting hard-coded header strings).
7. **F7 — submission cap (verified by CI):** the main Russian Markdown still satisfies ≤15,000 characters, required sections 1–4 & 6, separate question-5 `.md`, ten-slide *outline*, 7 explicitly unadjudicated examples, diagram source sync, JSON schema examples.

## Remaining unresolved gates — important

- **No actual baseline** (manual reporting frequency, historical product-team delivery times, average support minutes), no call volume or source completeness data. Economic assumptions can't be promoted to measured company impact.
- **No gold dataset** or confirmed labels for same-problem recurrence, topical grouping and actionable; no real Qwen model test, ASR error rate, precision/recall or causal pilot.
- **No actual costs**. Conditional `PV_3 > C` is not a proven 3-year payback, ROI or realistic expenditure ceiling for Gazprom Neft.
- **No independent reviewer approval** of architecture, Russian claims, data governance or economics; no user/company authorization to merge/deploy.
- **No final rendered DOCX/PDF/PPTX**; Mermaid previews exist but final 16:9 visual/Cyrillic verification pending. The Markdown compliance checker does not validate slide rendering or business truth.
- **No current official macro data** was provided or verified; sensitivity covers possible parameter movements but is not a forecast.

## Release decision

**Documentation draft may proceed to editorial review; NOT ready to be submitted as final deliverables, merged, deployed or presented as measured AI/system effectiveness.** Keep Draft PR #24. Independent signoff and final artifact inspection are separate follow-up gates.
