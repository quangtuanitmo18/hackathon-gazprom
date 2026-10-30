# Incident Verification & Human Annotation Design

**Date:** 2026-10-30. **Status:** proposed policy for Hybrid AI Agent; NOT an approved production incident classifier.

## Business objective
Similar support tickets may be unrelated incidents. A false merge hides defects; false alerts waste developer time. Retrieval similarities alone are insufficient to decide common root cause.

## Separation of concerns
1. Existing BM25/dense/RRF yields candidates, not final incident labels.
2. A deterministic evidence gate evaluates *arrival-time* product, component, version, error code and derived symptom key, returning candidate_for_human_review or insufficient_or_conflicting_evidence. **Neither output confirms that incidents are same or different.**
3. Independent human reviewers adjudicate same_incident, related_topic, different_incident, uncertain; agreement is required for gold (or an adjudicator resolves disagreement).

## Runtime fields and policy
Use CanonicalTicketV1 (strict source-scoped identity, product/component/version/error_codes). Symptom key must be an explicit enrichment derived from arrival-time information by a future extractor, not inferred here or invented by the verifier. Never feed eventual resolution, duplicate-of labels or final assignment into online features.

If the two tickets have known conflicting product/component/version, disjoint error codes, or conflicting symptoms, **abstain** with reasons; shared dependencies may still connect them. Candidate_for_human_review requires matching known product, component, version, symptom and at least one shared error code. Missing values => abstain. Every result requires reviewer approval before cluster merge. This intentionally conservative gate trades coverage for safety; coverage/review effort must be measured.

## Human review contract
Annotation is a separate immutable record with source-scoped pair identity, reviewer ID, timestamp, label and rationale. Different reviewers may agree or disagree. Disagreement => disputed; no automatic majority. The same reviewer cannot certify their own decision as independent. Keep original reviewer decisions and adjudicator versioning.

## Russian fixtures
12–20 short hand-written synthetic ticket pairs: same HTTP code and version; forgot-password vs HTTP403; same error in different products; version mismatch; component mismatch; different error codes; shared dependency uncertainty; unknown metadata; injected ticket text telling an AI to ignore policy. Fixtures test **behavioral invariants**, not precision/F1 or real Russian domain accuracy.

## Acceptance/metrics
Run TDD for policy and annotation. Hold raw inputs private; never publish private customer text. For real pairwise precision/recall/F1, obtain independently annotated positives and hard negatives with a holdout split by incident family. Do not treat missing GitBugs edges as verified negatives; GitBugs duplicate links are only a proxy for support incident identity. Human review time, abstention coverage and false merges must be measured before ROI claims.

## Integration later
Hybrid Retrieval -> Evidence Screening -> Human Pair Review -> Approved link -> Versioned Problem Registry -> Trend Detection -> Evidence-Based Agent -> Product Owner approval -> permissioned issue tracker.

No transitive similarity-only cluster unions: A~B and B~C does not imply A~C.

**Decision ruling:** choose conservative review-first rules until source domain label quality allows calibration; risk is low coverage/high review cost, which must be reported honestly.
