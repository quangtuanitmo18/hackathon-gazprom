# Auditable Problem Registry — Design Specification

**Status:** PROPOSED MVP design; team/production approval pending. **Date:** 2026-10-30.
**Parent architecture:** Hybrid AI Agent → candidate retrieval → evidence screening → human pair adjudication → this Problem Registry → trend/agent draft.
**Scope:** in-memory domain implementation + tests, NO persistence, external tracker writes or asserted business improvements.

## Business need
Support teams need a stable record for one recurring problem and evidence-linked tickets, avoiding duplicate Jira issue proposals. Retrieval does not prove incident identity. Two experts agreeing a pair is same incident is evidence for a connection, but **A=B and B=C must NOT silently become A=C**.

## Selected policy
1. Each distinct source-scoped ticket creates one singleton candidate Problem. Repeated registration with same identity and same payload is idempotent; conflicting content with reused identity fails (future event-update ingestion is separate).
2. Each ticket is assigned exactly one active Problem; each Problem belongs to one explicitly supplied authorization scope, such as tenant/product security boundary. The registry assumes scope is provided by authenticated backend, not by the LLM.
3. Source-scoped pair approval requires **two independent PairAnnotation records**, internally adjudicated to confirmed same_incident, matching the registered pair IDs. Uncertain, related_topic, different_incident and disputed decisions cannot establish merge permission.
4. Merge two problems is a **distinct explicit reviewer decision** with reason, idempotency key and expected revisions. It requires approved links for **every cross-product of members** (complete-link condition), not a similarity chain or one convenient bridge. Scope must match. A merged-away ID becomes a tombstone with merged_into; primary ID remains stable.
5. Split is a **distinct explicit reviewer correction** with reason, idempotency key and expected revision; its partitions must cover each existing member exactly once, each nonempty. Primary remains assigned to first partition and receives revised version. New Problems are created for subsequent partitions, with parent lineage. Cross-partition approvals are revoked from current permissions, but the historical audit shows their former approval and revocation; new approval requires a new decision event.
6. Active Problem snapshots are immutable. Audit is append-only immutable entries, containing actor, event type, key, before/after refs, timestamp, reason; no ticket body or PII in log.
7. Mutations are atomic **in one in-memory registry instance** and serial by assumption. Production persistence requires DB transaction, unique idempotency constraint, optimistic locking and scoped RBAC. No external writes in this increment.

## Invariants and failure cases
- Source ID collision across systems cannot attach wrong ticket.
- Duplicate API retries do not cause extra events, versions or tickets; same idempotency key with different payload rejects.
- Stale revisions reject before mutation; no partial modification on failed merge/split.
- Cross-scope pairs or merges reject.
- No merge based purely on retrieval or screen_pair status.
- No transitively inferred membership; require all cross-links approved.
- Rejected/uncertain reviewer label cannot accidentally become a confirmed link.
- Split revokes approvals across new partitions; old pair approvals remain in audit for forensics.
- Same source ID with changed content does not silently overwrite a ticket.
- A merged-away ID never stays active; its contents can be traced through merge event/tombstone.

## Interfaces (MVP)
- Registry.register_ticket(ticket, scope_id) -> ProblemRecord
- Registry.approve_pair(ticket_a, ticket_b, first, second, actor, operation_key) -> PairApproval
- Registry.merge(primary_id, secondary_id, actor, reason, operation_key, expected_primary_revision, expected_secondary_revision) -> ProblemRecord
- Registry.split(problem_id, partitions, actor, reason, operation_key, expected_revision) -> tuple[ProblemRecord, ...]
- Registry.get_problem(problem_id), problem_for_ticket(ticket), audit_events() read-only snapshots.

## Out of scope
Durable event sourcing/postgres, real RBAC authentication, distributed concurrency, automatic incident severity scoring, alerting, GraphDB, Jira API, multi-tenant production security and measured real incident precision/F1. Do not claim any of these are implemented.

## Review gate
TDD RED→GREEN, Python 3.11/3.13 CI, 12+ safety-focused tests, explicit replay and split lineage documented. Then draft PR (no merge). Next task integrates verified Problem with trend detection and approved IssueProposal as mock-only write.
