# Public Dataset Discovery and Validation — Design Spec

**Status:** PROPOSED FOR REVIEW — research completed, ingestion/benchmark implementation not approved
**Date:** 2026-10-30
**Parent architecture:** [ProductPulse Hybrid AI Agent](2026-10-30-productpulse-system-design.md)
**Catalog:** [Candidate data sources](../../data/dataset-catalog.md)

## Intent
We need empirical evidence before the organizer delivers a real dataset. External public data must enable baseline research and interface validation **without misrepresenting findings as Gazprom Neft performance**. First objective: establish clean, reproducible local data pipelines and testable ground-truth definitions, not fake incident-level metrics.

## Goals
- G1: Pin and audit two legally usable source datasets with explicit provenance/licenses.
- G2: Build adapter that maps input columns into canonical ticket records; preserve source labels and splits.
- G3: Train and evaluate a **simple classification baseline** on a real human-labeled corpus.
- G4: Validate time-based handling/assignment analytics on a separate actual helpdesk event log.
- G5: Prepare 12–20 human-designed Russian hard-negative cases and annotation instructions for same-incident evaluation.
- G6: Produce measured reproducible reports (git SHA, checksum, missingness, class balance, confusion matrix, macro F1), not invented improvements.

## Non-goals
- No claim of Russian ticket performance from mostly EN/DE/PT/ES sources.
- No evidence-based clustering F1 without true incident-pair annotations.
- No uploading corporate/private data to external model endpoints.
- No costly fine-tuning or speculative ROI before baselines.
- No automatic training on metadata only available after resolution in an arrival-time classifier.

## Approaches considered
A. **One large synthetic ticket dataset:** quick and complete fields; fails empirical validity and domain shift.
B. **One multilingual ticket CSV:** easy classification/routing demo; insufficient for incident time/replay ground truth, may have NC license.
C. **Two complementary real datasets + small explicit Russian fixtures (recommended):** independent classification and process/replay experiments, inspectable domain gaps. Requires separate adapters and careful claims.

**Preferred approach C** based on user goal of reproducibility, pending approval to implement.

## Technical design
A: Zenodo 7648117, use preserved author split. Normalize ticket text to redacted internal `Ticket`; label taxonomy remains source-specific. B: Mendeley btm76zndnt v3, preserve event timestamps, assignee and project; only reporter-authored text can be used for arrival-time features when it existed. For HF processed B, note only 357 message-bearing issues. Annotation fixture set C is synthetic and exclusively for behavior regression tests.

Source adapters are independent. Shared `CanonicalTicket` fields: `source: str`, `source_id: str`, `created_at: datetime|None`, `text_redacted: str`, `source_label: str|None`, `product_id: str|None`. Missing timestamps remain null and such rows are excluded from replay, never filled with fake dates.

Use a provenance manifest with URL, license, source version/commit, download checksum, number of input/output rows, column mapping, transformations, split provenance. Temporary raw files live under `data/raw/` and are gitignored.

## Evaluation gates
- Data profiling before preprocessing; identify class imbalance, duplicates, empty texts and languages.
- No training on held-out test; use existing author test for A.
- Classification baseline TF-IDF (word/char features) + Logistic Regression, compare majority-class predictor; compute macro F1, support/count per class, confusion matrix, evaluation duration.
- Mendeley B: verify real time fields and their completeness before replay. **Do not** report baseline manual TTAI without escalation timestamps.
- Duplication: benchmark only with adjudicated pair labels; otherwise label demonstration only.
- Prior to integrating LLM, run local baseline and record resource/runtime costs.

## Privacy/license
CC BY 4.0 attribution for A/B. Original datasets claim anonymization; nevertheless inspect samples for residual personal data and never commit raw. Treat helpdesk text as untrusted. Do not adopt CC BY-NC corpus as default when commercial-company use rights are unclear.

## Failure cases
- Source schema or split changes → fail with explicit reason and version pin.
- Missing text/ID → quarantine with count, not silent fill.
- No timestamp → no time-based metric.
- Missing duplicates gold → no incident detection F1.
- Multilingual mismatch → report language distribution and generalization limit.
- Source license uncertainty → stop public sharing of copied data.

## Deliverable / handoff
Output is a dataset catalog, approved transformation design, locked holdout protocol and a sequenced implementation plan under `docs/superpowers/plans/`. The **first implementation task only begins after the design is approved**, using Superpowers TDD with RED/GREEN evidence on an isolated branch.
