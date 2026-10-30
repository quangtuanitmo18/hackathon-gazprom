# Phase 19: verified Problem activity signals

**Scope:** hackathon MVP, read-only. This is not statistical anomaly detection, duplicate-classification evaluation, root-cause analysis, a recommendation to deploy, or a tracker-write agent.

## Source of truth / gating

- Use `PersistentProblemRegistry.read(trusted_scope)`. It is NOT allowed to take tenant scope, Problem membership or timeline from browser input.
- Only **active Problems with two or more explicitly grouped members** are eligible. The `pair_approved` event **does not** merge those two ticket groups. A grouping requires explicit, independently reviewed complete-link `merge` (or an approved persisted group). This avoids turning lexical BM25 matches into "confirmed incidents".
- Use source event-time `CanonicalTicketV1.created_at` (UTC-normalized by data contract), **not** ingestion time, current status, report generation time or review event-time.
- A single missing or future timestamp among Problem members returns `insufficient_timestamps`, never a positive trend. Older than both windows is valid but does not count. Unknown corpus coverage/backfill means that 0 in the previous period is **not proof that 0 tickets occurred**.

## Deterministic, non-statistical trigger

Read-only `GET /internal/v1/trends?window_hours=24`, requiring BOTH `X-Internal-Token` and signed, tenant-matched Keycloak reviewer OIDC Bearer token.

Adjacent half-open event-time windows:
- previous: `[as_of - 2W, as_of - W)`
- current: `[as_of - W, as_of)`

Default fixed policy: `current_count >= 3` and `current_count - previous_count >= 2`. Status:
- `volume_increase`: thresholds met and previous window count > 0. A measured **count increase**, NOT a statistically proven "spike".
- `new_activity`: thresholds met and previous window count = 0. No assumption of complete historical coverage.
- `monitor`: thresholds not met.
- `insufficient_timestamps`: missing or future source timestamp. Do not promote it to positive.

Result contains problem ID, revision, UTC `as_of`, window, raw counts, delta, and source-scoped evidence ticket keys; **no raw description**, guessed owner, inferred root cause, model score or notification. Order is deterministic by status / descending current count / problem ID. Idempotent read; no audit mutation or external side effects.

Scope cap: 5,000 source tickets/Problem inputs; overflow fails with HTTP 503, not partial unnoticed results. PostgreSQL's existing per-tenant JSONB snapshot remains unsuitable for large-scale streaming analytics.

## Testing and limitations

RED first: [GitHub Actions 41066911180](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41066911180) (missing insights module). GREEN evidence should be linked from the final PR once available.

Unit tests: nonzero baseline, new activity, stable/declining volume, missing/future time, UTC window boundaries, tenant mismatch, duplicate identities, capacity and deterministic ordering.

PostgreSQL API tests: unauthorized calls, cross-tenant, approved-but-unmerged pair produces **no group trend**, 3 independently approved pair links followed by **explicit complete-link merge** produces one read-only evidence-backed signal; no unapproved merge or automatic tracker writes.

**Known limitations:** No independently verified source coverage interval, missing or late event-time records may affect comparisons, no backfill watermark or delayed event reconciliation, no deduplicated upstream event feed beyond ticket identity, no seasonality, exposure denominator, variance or confidence interval. Suitable for a reviewer dashboard and replay research, **not** automatic incident escalation. Next: organization adapter with coverage metadata + deduplication, offline replay/effectiveness, grounded insight proposal with human approval and mock issue tracker.
