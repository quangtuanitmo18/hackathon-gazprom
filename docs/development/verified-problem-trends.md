# Phase 19: verified Problem activity signals

**Scope:** hackathon MVP, read-only. This is not statistical anomaly detection, duplicate-classification evaluation, root-cause analysis, a recommendation to deploy, or a tracker-write agent.

## Source of truth / gating

- Use `PersistentProblemRegistry.read(trusted_scope)`. It is NOT allowed to take tenant scope, Problem membership or timeline from browser input.
- Only **active Problems with two or more explicitly grouped members** are eligible. The `pair_approved` event **does not** merge those two ticket groups. A grouping requires explicit, independently reviewed complete-link `merge` (or an approved persisted group). This avoids turning lexical BM25 matches into "confirmed incidents".
- Use source event-time `CanonicalTicketV1.created_at` (UTC-normalized by data contract), **not** ingestion time, current status, report generation time or review event-time.
- A single missing or future timestamp among Problem members returns `insufficient_timestamps`, never a positive trend. Older than both windows is valid but does not count.
- `SourceCoverage(source_system, complete_from, complete_through, evidence_ref)` is an explicit **trusted adapter** contract. Each participating source must have an independently verified, timezone-aware coverage interval from at or before the previous window start through at least `as_of`. Merely having tickets in both windows does **not** prove coverage. Source-system evidence references must be supplied by a future audited importer, never from UI payloads or inferred from min/max ticket dates. **Current runtime supplies no such manifests, so all observed increases are marked `unknown_coverage`.**

## Deterministic, non-statistical trigger

Read-only `GET /internal/v1/trends?window_hours=24`, requiring BOTH `X-Internal-Token` and signed, tenant-matched Keycloak reviewer OIDC Bearer token.

Adjacent half-open event-time windows:
- previous: `[as_of - 2W, as_of - W)`
- current: `[as_of - W, as_of)`

Default fixed policy: `current_count >= 3` and `current_count - previous_count >= 2`. Status:
- `volume_increase`: thresholds met and previous window count > 0 **and** source coverage proven complete. A measured count increase, NOT a statistically proven "spike".
- `new_activity`: thresholds met, previous window count = 0, and source coverage proven complete.
- `unknown_coverage`: the same raw observed increase but **without** complete independently verified source coverage. Exposes `observed_pattern` as a hypothesis, never as a confirmed alert.
- `monitor`: thresholds not met; coverage status is still provided.
- `insufficient_timestamps`: missing or future source timestamp. Do not promote it to positive.

Result contains problem ID, revision, UTC `as_of`, window, raw counts, delta, coverage status, observed pattern, explicit `eligible_for_alert=false`, and source-scoped evidence ticket keys; **no raw description**, guessed owner, inferred root cause, model score or notification. Order is deterministic by status / descending current count / problem ID. Idempotent read; no audit mutation or external side effects.

Scope cap: 5,000 source tickets/Problem inputs; overflow fails with HTTP 503, not partial unnoticed results. PostgreSQL's existing per-tenant JSONB snapshot remains unsuitable for large-scale streaming analytics.

## Testing and limitations

First RED: [GitHub Actions 41066911180](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41066911180) (missing insights module). First GREEN: [Python 41067617536](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41067617536) and [PostgreSQL 41067617566](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41067617566). Follow-up review RED and GREEN evidence are recorded in PR #19.

Unit tests: nonzero baseline, new activity, stable/declining volume, missing/future time, exact -48h UTC boundary, equivalent timezone offset, source coverage intervals/watermarks, multisource missing coverage, late backfill observed-count changes, tenant mismatch, duplicate identities, capacity and deterministic ordering.

PostgreSQL API tests: unauthorized calls, cross-tenant, approved-but-unmerged pair produces **no group trend**, 3 independently approved pair links followed by **explicit complete-link merge** produces one read-only count signal flagged `unknown_coverage`; missing event time yields `insufficient_timestamps`; post-split group signal disappears. No unapproved merge or automatic tracker writes.

**Known limitations:** There is now an explicit coverage/watermark *schema*, but the runtime has **no verified source manifests**; missing/late event-time records may affect comparisons and historical evaluations, no retroactive as-of observation ledger/backfill reconciliation, no deduplicated upstream event feed beyond ticket identity, no seasonality, exposure denominator, variance or confidence interval. The source timestamps alone cannot establish what was knowable at past ingestion times. The verified endpoint is intentionally silent until a human explicitly merges; ranked candidates belong to a **separate explicitly unverified early-review workflow**, not this API. Suitable for reviewer inspection, **not** automatic incident escalation or time-safe replay evaluation. Next: organizer adapter + audited coverage/watermark metadata, explicit ingest/observed-time replay, early candidate activity under a distinct API name, grounded insight proposal with human approval and mock issue tracker.
