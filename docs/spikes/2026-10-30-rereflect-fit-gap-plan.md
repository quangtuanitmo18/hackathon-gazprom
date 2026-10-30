# Rereflect Fit–Gap Spike (Superpowers)

**Status:** Executing. Exploratory verification, not incorporation of upstream code.
**Reference implementation:** [Rereflect](https://github.com/haqaliz/rereflect), upstream revision `987dd9f0611c693524ec0cfba880517fa4d5ec57` (2026-10-21); MIT license.
**Project objective:** Decide whether Rereflect is safe to integrate as UI/workflow layer while ProductPulse retains classification, hybrid retrieval, incident evidence, approval and Problem Registry.

## Hypotheses

H1: Upstream stack can be configured and launched headlessly (Postgres + Redis + FastAPI) on a clean GitHub Actions Ubuntu runner without external credentials.

H2: Using local authentication, a synthetic Russian support ticket can be created and retrieved through an actual HTTP API, then appear in dashboard statistics.

H3: Issue draft endpoint is present and safely refuses when LLM not configured; no Jira write is attempted.

H4: Source, incident/problem registry and review-evidence fields have an API-safe representation that preserves ProductPulse's invariant. **Likely gap:** Rereflect feedback creation only accepts text/source, while incident membership requires structured IDs and provenance; test API response and field contract.

H5: Multi-tenant scope is enforced for read access, even when ticket ID is known.

## Plan

1. **Inspect pinned upstream**: Docker configs, exact route source, RBAC, migrations, env vars and dependency complexity. No change to upstream source.
2. **Create reproducible test-first API probe**: code asserts H2–H5 and records HTTP status/count evidence; never logs secrets or real ticket text.
3. **Run isolated GitHub Actions**: read-only token, ephemeral generated credentials, upstream pinned ref, `docker compose config` and limited backend stack start. Only localhost ports, no external integrations, no real Gazprom data. Runner cleanup on all outcomes.
4. **Review gaps and risks**: rate as PASS/FAIL/BLOCKED/UNTESTED, estimate adapter/migration scope; never claim frontend, worker or Jira delivery works if not exercised.
5. **Report decision**: choose API adapter/integration, reference-only, or reject. No merge until reviewed.

## Pre-registered acceptance tests

- Config validated with `docker compose -f docker-compose.prod.yml config --quiet`.
- `GET /health` returns 200.
- `POST /api/v1/auth/signup` creates test org with no external IdP.
- `POST /api/v1/feedback/` creates one synthetic Russian ticket.
- `GET /api/v1/feedback/{id}` same-org returns 200.
- `GET /api/v1/dashboard/` returns HTTP 200 with total >= 1.
- `POST /api/v1/feedback/{id}/issue-draft` without configured LLM returns 409; not 200 or silent external action.
- Second org token cannot retrieve first org feedback by ID (expect 404).
- Upstream API schema confirms preservation/loss of product_id, component_id, problem_id, source_ticket_id, evidence links.

## Safety and scope

- All GitHub operations confined to `spike/rereflect-fit-gap`; no change to `main`.
- No secrets from user or upstream integrations; generated only in ephemeral runner.
- No persistent deployment, test only; do not publish synthetic credentials, user tokens or ticket text.
- Do not import all of Rereflect into ProductPulse: integration is subject to licensing/security/schema review.
- Runner resource limits may block heavy Docker/PyTorch/xmlsec build. A failed build is recorded as evidence, not quietly treated as a pass.
- Do NOT infer UI readiness, AI analysis accuracy, real Jira integration or data privacy from an HTTP-only smoke test.

## Decision criteria

**Adopt as a shell** only if runtime smoke works, tenant isolation and safe draft gate hold, and data mapping does not require intrusive changes to core product behavior. Otherwise use components selectively or build a thin dashboard over ProductPulse API. Existing custom domain engine and benchmark remain canonical; MIT attribution if code copied.
