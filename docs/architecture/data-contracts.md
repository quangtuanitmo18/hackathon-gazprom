# Data contracts (PROPOSED)

All event timestamps ISO 8601 UTC. No raw private ticket text in this public repository. Unknown is null/unknown, not invented by the model.

## Ticket
```json
{"source":"csv","source_event_id":"evt-1","ticket_id":"T-1","product_id":"erp-demo","created_at":"2026-10-01T09:00:00Z","body_redacted":"HTTP 403 после обновления","pseudonymous_user_id":"u1","metadata":{"version":"2.8.1"}}
```
Unique event key: (source, source_event_id). Retries must not double-count.

## TicketClassification
```json
{"ticket_id":"T-1","intent":"incident","component":"authentication","symptoms":["login_failed"],"error_codes":["HTTP 403"],"reported_version":"2.8.1","model_version":"baseline-v1","confidence":null,"needs_review":false}
```
Intent enum: incident | how_to | feature_request | complaint | other | unknown. Confidence must be measured/calibrated, never hallucinated.

## PairMatch
```json
{"ticket_id":"T-1","candidate_problem_id":"PRB-1","relationship":"uncertain","evidence":["same_product","same_error_code"],"verified_by":null}
```
Relationship enum: same_incident | related_topic | different | uncertain. Similar wording is not identity. No blind transitive chain merges.

## Problem + Proposal
Problem: problem_id, product_id, component, first_seen_at, last_seen_at, status, revision, ticket evidence IDs, external issue link, merge/split lineage.
```json
{"proposal_id":"PROP-1","problem_id":"PRB-1","title":"HTTP 403 после обновления","evidence_ticket_ids":["T-1"],"root_cause_status":"unknown","owner_team_id":null,"existing_issue_id":null,"recommended_action":"Investigate regression","requires_human_review":true}
```
Material claims require resolvable authorized ticket IDs. Counts come from analytics; owner from registry. Missing owner or unavailable issue lookup => human review, not auto-publish.

## State & safety
Ticket: received -> normalized -> classified -> matched/uncertain.
Problem: candidate -> monitored -> needs_review -> approved/rejected -> published/updated -> resolved/reopened.
Each transition logs timestamp, actor, reason, evidence. External writes require backend policy, explicit approval and idempotency key `problem_id:event_type:revision`.

EvaluationRun stores run_id, code SHA, dataset provenance/checksum, split, seed, versions, thresholds, costs, timings, errors and anonymized reviewer decisions.
