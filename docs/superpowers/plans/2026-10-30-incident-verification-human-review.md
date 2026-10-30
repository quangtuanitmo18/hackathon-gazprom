# Incident Verification + Russian Hard Negatives — Superpowers Implementation Plan

Required workflow: test-driven-development, executing-plans, verification-before-completion (RED → GREEN → refactor → verify). **Status:** IMPLEMENTED, TDD/CI verified 2026-10-30; detailed team review and merge pending.

**Spec:** [Design](../specs/2026-10-30-incident-verification-and-annotation.md).

## Task 1: Evidence gate
**Files:** src/productpulse/incident/verify.py, src/productpulse/incident/__init__.py, tests/incident/test_verify.py.

- [x] Write failing tests for complete metadata candidate (still human review), conflicts (product, version, component, code, symptom), missing values, same source ticket, malicious command embedded in descriptions.
- [x] Execute targeted pytest RED and inspect failure reason.
- [x] Implement screen_pair(ticket_a, ticket_b, symptom_a, symptom_b) returning a strict immutable PairScreening with status, evidence, blockers, requires_human_review; no score masquerading as calibrated probability.
- [x] Execute targeted GREEN and full Python matrix, record run IDs.

## Task 2: Human annotation / adjudication
**Files:** src/productpulse/incident/annotation.py, tests/incident/test_annotation.py.

- [x] Write tests for four gold labels, self/mismatched-pair checks, independent reviewer agreement and disagreement, invalid dates/provenance and attempt by same reviewer to certify two opinions.
- [x] Verify RED; implement immutable PairAnnotation with reviewer, timestamp, rationale, and adjudicate_pair; disagreement returns disputed; no implicit gold.
- [x] Verify GREEN and complete test suite; commit.

## Task 3: Russian synthetic behavioral regression
**Files:** tests/fixtures/russian_incident_pairs.json, tests/incident/test_russian_fixtures.py, docs/evaluation/russian-annotation-guidelines.md.

- [x] Author 12–20 explicit SYNTHETIC Russian ticket pairs, including hard negatives and missing data, expected policy screening outcomes.
- [x] Run full test suite; synthetic pass rate is NOT real model accuracy.
- [x] Document two-rater labeling and adjudicator protocol, incident-vs-topic distinction, real pair sampling without assuming unlabeled negatives, family-disjoint holdout and privacy controls.
- [x] Record RED/GREEN evidence and review blockers.

## Task 4: Connect retrieval candidates to evidence screening

**Files:** src/productpulse/incident/batch.py, tests/incident/test_batch.py.

- [x] Write failing tests for source-scoped candidate IDs, self-exclusion, stable retrieval ordering, duplicate candidate IDs, unavailable candidate fail-closed, missing symptom abstention, and zero write-side effects.
- [x] Verify RED before creating batch module.
- [x] Implement screen_retrieved_candidates(query, candidate_keys, tickets_by_key, symptom_keys) -> tuple[CandidateReview,...]; no model calls, no external actions.
- [x] Verify targeted and complete CI on Python 3.11/3.13; leave a reproducibility ledger.
- [x] Preserve original retrieval rankings and non-matching statuses as reviewer evidence, never silently interpret a missing candidate as negative.

## Not in scope
No incident clustering F1 without real human gold; no automatic issue writes, cluster merges, or claimed Gazprom Neft ROI. Next step is versioned Problem Registry and real annotated pair benchmark.


## Execution / verification ledger (Superpowers)

- Task 1 RED: [run 41042215360](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042215360), module absent; GREEN: [run 41042316142](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042316142), Python 3.11/3.13 succeeded.
- Task 2 RED: [run 41042422769](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042422769), annotation module absent; GREEN: [run 41042525022](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042525022).
- Task 3: [18 Russian synthetic fixtures](../../../tests/fixtures/russian_incident_pairs.json) + tests and [annotation guide](../../evaluation/russian-annotation-guidelines.md); [run 41042745636](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042745636) succeeded.
- Task 4 RED: [run 41042894760](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042894760), bridge absent; GREEN: [run 41042988128](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41042988128), **131 tests passed** in Python 3.11 (and Python 3.13 CI job succeeded).
- **Ruling:** use strict evidence screening with always-human-review outputs; status does NOT assert same-incident ground truth. This prevents unearned performance claims at cost of high abstention/human workload.
- **Ruling:** source content and reviewer identities are fixtures only; future production integration requires authenticated reviewer identity, tenant-authorized retrieval and PII enforcement in backend.
- **Ruling:** synthetic Russian cases are regression tests, NOT independent evaluation data for measured pair F1.
- **Remaining work:** external expert annotation, source/domain calibration, reversible Problem Registry and time/cost pilot. No merge until review.
