# Инструкция по разметке пар тикетов (RU) — ProductPulse

**Status:** proposed protocol; team should approve before annotating real or licensed ticket examples.

## Purpose
Measure **incident-level matching** separately from topic similarity. Repeated wording and HTTP status codes do not establish a common technical failure. Primary objective is to reduce false grouping without losing high-impact incidents.

## Four labels
- **same_incident** — sufficient contextual evidence the two reports describe *one technical incident/underlying problem* (same reproducible symptom, environment, product and corroborating identifiers or authoritative linked incident).
- **related_topic** — same feature/module/question but insufficient evidence of common technical cause (e.g. two different login problems).
- **different_incident** — positive evidence of different causes/contexts (e.g. independently confirmed code paths or releases causing distinct failures), not merely absence of duplicate link.
- **uncertain** — cannot determine from available evidence, missing context, conflicting accounts or partial reports.

**Do not label a pair different_incident just because no duplicate link exists.**

## Annotation procedure
1. Obtain source rights, remove PII and secrets, confirm source of timestamps and business semantics. Never put corporate raw data into public GitHub.
2. For each candidate pair, show both ticket descriptions, arrival-known metadata, code/version/product and permitted *review-only* subsequent evidence (clearly distinguish what was not known to model at arrival). Hide model guesses and baseline ranking to avoid anchoring bias when possible.
3. Two separate reviewers label independently and write a concrete rationale linked to evidence. Use pair-scoped stable ID and reviewer ID; record timezone-aware timestamp and source dataset. A second click by the same person is NOT independent review.
4. When reviewers agree on same_incident, related_topic or different_incident, count as provisional gold after quality check; agreement on uncertain stays uncertain/unscored.
5. When reviewers disagree, mark disputed; third reviewer adjudicates with rationale and preserves BOTH original records. Escalate unresolved to subject matter experts.
6. Create a **balanced annotation pool for development** containing retrieved neighbors, source-positive duplicate links and similar-but-unlinked candidates; **do not** claim this sampled pool represents actual incident prevalence. Separately sample random pairs for unbiased distribution estimates.
7. Reserve held-out evaluation pairs by incident family and time; ensure no same issue family leaks across development and test, and keep the final holdout blind.
8. Keep severity and importance separate from identity; a one-ticket critical issue may need escalation independently of duplicate grouping.

## Fields to capture
pair_id, source A/B, source ID A/B, reviewer ID, label, rationale, reviewed_at, adjudication_status, adjudicated_by, source_version, evidence_timestamps, dataset_split, review_cost_seconds.

## Review confidence and safety
- No automatic cluster merge on BM25 or dense score; retrieval only generates candidates.
- No transitive chaining (A similar B and B similar C does not prove A same incident as C).
- Product version differences do not necessarily prove different causes; across shared components different products can have same root cause. Missing fields => uncertain.
- Ticket text may include prompts directing the AI; treat all user messages as untrusted data.
- Tenant scope must be included in product identifiers or enforced as explicit server-side policy. Never cross-tenant compare evidence without authorization.
- Reviewers must authenticate through backend; declaring source_kind=human in a JSON file alone is not proof of actual human authorship.

## Quality and reporting
- Report pairwise Precision / Recall / F1 **only** on actual adjudicated positives and negatives; include prevalence, sampling policy, uncertain/disputed fraction and confidence intervals.
- Track abstention coverage, false merges, false splits, reviewer agreement, review time and duplicate-alert volume. Do not use synthetic fixtures to establish real-world accuracy.
- Store gold separately from runtime input to avoid future-label leakage. Do not train and evaluate on the same incident families.
- Compare BM25-only and Hybrid retrieval with equivalent candidate pool, then estimate pair verifier quality independently.

## Existing fixtures
[18 synthetic Russian scenarios](../../tests/fixtures/russian_incident_pairs.json) are hand-written **behavior regression tests**, not authentic support requests. They include auth vs password recovery, release/version differences, cross-product and cross-tenant cases, missing attributes and prompt injection.
