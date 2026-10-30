# Incident Verification + Russian Hard Negatives — Superpowers Implementation Plan

Required workflow: test-driven-development, executing-plans, verification-before-completion (RED → GREEN → refactor → verify). **Status:** in implementation on isolated branch, detailed team review pending.

**Spec:** [Design](../specs/2026-10-30-incident-verification-and-annotation.md).

## Task 1: Evidence gate
**Files:** src/productpulse/incident/verify.py, src/productpulse/incident/__init__.py, tests/incident/test_verify.py.

- [ ] Write failing tests for complete metadata candidate (still human review), conflicts (product, version, component, code, symptom), missing values, same source ticket, malicious command embedded in descriptions.
- [ ] Execute targeted pytest RED and inspect failure reason.
- [ ] Implement screen_pair(ticket_a, ticket_b, symptom_a, symptom_b) returning a strict immutable PairScreening with status, evidence, blockers, requires_human_review; no score masquerading as calibrated probability.
- [ ] Execute targeted GREEN and full Python matrix, record run IDs.

## Task 2: Human annotation / adjudication
**Files:** src/productpulse/incident/annotation.py, tests/incident/test_annotation.py.

- [ ] Write tests for four gold labels, self/mismatched-pair checks, independent reviewer agreement and disagreement, invalid dates/provenance and attempt by same reviewer to certify two opinions.
- [ ] Verify RED; implement immutable PairAnnotation with reviewer, timestamp, rationale, and adjudicate_pair; disagreement returns disputed; no implicit gold.
- [ ] Verify GREEN and complete test suite; commit.

## Task 3: Russian synthetic behavioral regression
**Files:** tests/fixtures/russian_incident_pairs.json, tests/incident/test_russian_fixtures.py, docs/evaluation/russian-annotation-guidelines.md.

- [ ] Author 12–20 explicit SYNTHETIC Russian ticket pairs, including hard negatives and missing data, expected policy screening outcomes.
- [ ] Run full test suite; synthetic pass rate is NOT real model accuracy.
- [ ] Document two-rater labeling and adjudicator protocol, incident-vs-topic distinction, real pair sampling without assuming unlabeled negatives, family-disjoint holdout and privacy controls.
- [ ] Record RED/GREEN evidence and review blockers.

## Not in scope
No incident clustering F1 without real human gold; no automatic issue writes, cluster merges, or claimed Gazprom Neft ROI. Next step is versioned Problem Registry and real annotated pair benchmark.
