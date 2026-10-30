# Fit–Gap: Rereflect for ProductPulse AI

**Date:** 2026-10-30. **Status:** COMPLETE FOR THE PRE-REGISTERED BACKEND/API + FRONTEND-HTML SCOPE. Backend/API: 9/9 HTTP checks PASS; Next.js Docker build and HTML HTTP PASS. Worker task processing, interactive browser journeys, production tenant security and real Jira remain UNTESTED.

**Upstream pinned:** https://github.com/haqaliz/rereflect/tree/987dd9f0611c693524ec0cfba880517fa4d5ec57 (2026-10-21), MIT.
**Runtime evidence:** [Backend/API 41047762951](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41047762951) (PASS), [Frontend 41048082865](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41048082865) (PASS), [language probe 41047578460](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41047578460) (PASS). Initial [41046817009](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41046817009) recorded invalid email test-fixture failure; corrected.
**Test suite:** [scripts/spikes/rereflect_api_probe.py](../../scripts/spikes/rereflect_api_probe.py).
**Plan:** [2026-10-30-rereflect-fit-gap-plan](2026-10-30-rereflect-fit-gap-plan.md).

## Source inspection results (verified in upstream source; no runtime claim)

| Requirement | Evidence | Finding |
|---|---|---|
| MIT license | Upstream LICENSE + GitHub metadata | PASS: permissive reuse subject to attribution |
| Docker self-hosting | docker-compose.prod.yml | EXISTS; Postgres 16, Redis 7, Python 3.12 FastAPI backend, Celery worker, Next.js UI |
| HTTP API + RBAC | services/backend-api/src/api/routes/auth.py, public_api.py | PASS: JWT org signup and cross-tenant read isolation verified over HTTP; scoped public API key create/ingest path exists in code but not exercised over HTTP |
| Create ticket/feedback | services/backend-api/src/api/routes/feedback.py | **GAP:** FeedbackCreateRequest only \`text\`, \`source\`; public create accepts \`text\`, \`source\`, \`customer_email\` |
| Preserve ProductPulse incident fields | services/backend-api/src/models/feedback.py | **GAP:** no native product_id/component_id/problem_id/approved pair links or versioned merge/split; source_metadata JSON is populated through integration machinery, not public create |
| Dashboard KPIs | services/backend-api/src/api/routes/dashboard.py | PASS: HTTP dashboard reflects new feedback item; still customer feedback/sentiment/churn KPIs, not incident problem trends |
| Jira issue draft | services/backend-api/src/api/routes/feedback_issue_draft.py | PASS: HTTP issue-draft returned 409 without LLM, no actual Jira write attempted |
| Russian language baseline | services/analysis-engine/src/analyzer/categorizer.py | **GAP:** English keyword-based default pain-point classification; no native Russian incident taxonomy verified |
| Dependency complexity | services/backend-api/Dockerfile | PASS build but cost RISK: xmlsec source-build, Torch/transformers and large dependency footprint; cold GitHub Actions build was several minutes |
| Enterprise separation | docker-compose.prod.yml | Plain HTTP exposed on 8000/3000; TLS reverse proxy and on-prem security configuration needed |
| Workload/no API key | README, compose prod | Defaults to local rule-based analysis with LLM disabled; does not mean same-incident verification exists |

## Upstream fields vs ProductPulse

| ProductPulse | Rereflect native public feedback API | Adapter requirement |
|---|---|---|
| Ticket source + original ID | free-form \`source\`; no source ticket ID in create DTO | Own mapping table keyed by namespace and original ID |
| Product/component/version/error codes | Not in public create DTO | Keep as ProductPulse structured metadata, not packed into text |
| Problem Registry + member tickets | No Problem entity for incident membership | Own database/service + custom API/UI |
| Human pair annotation/approval | General workflow statuses/corrections, not 4-category pair review | Keep ProductPulse approval store |
| Trend/impact for product owner | General feedback analytics | Build domain-specific Problem insight endpoints/widgets |
| Jira issue draft | Present, but feedback-centric | May reuse UI or tracker adapter after policy/LLM check |
| Auth/RBAC | Auth and scoped org IDs | Decide trusted identity bridging; never trust user-supplied org/scope |

## Integration options

**Option 1 (preferred if runtime PASS, integration effort modest):** Rereflect remains a separate read/workflow UI. ProductPulse keeps all truth and publishes *sanitized issue summaries* through a thin outbound adapter. Store Rereflect feedback_id and ProductPulse problem_id mapping on ProductPulse side. Rereflect dashboard cannot natively render full incident links and auditing; add custom panel, do not treat its feedback_count as incident_count.

**Option 2 (fastest MVP if UI customization is significant):** Keep ProductPulse Python service and build a very narrow dashboard (Streamlit or lightweight Next.js) for problems/review/insights; use open-source libraries for components, LangGraph, Label Studio, Langfuse. This avoids maintaining a fork of Rereflect's unrelated churn/CRM/marketing modules.

**Option 3 (NOT recommended without substantial proof):** Fork and modify Rereflect core tables/async workflows deeply. Broad schema migration and upstream merge burden, English-centric default pipeline and sensitive data duplication.

## Runtime verification status

- Docker Compose manifest: **PASS** on [first Actions run](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41046817009).
- Postgres/Redis/backend startup: **PASS**; Alembic completed and GET /health returned HTTP 200 on the same run.
- Signup in initial probe: **TEST FIXTURE ERROR** (HTTP 422). Investigated: python email-validator rejects special-use domain `example.invalid`; changed fixture to syntactically valid reserved `example.com`. This does **not** demonstrate an upstream defect.
- **Backend API corrected run: PASS**, [Actions 41047762951](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41047762951): `GET /health` 200; `POST /auth/signup` for two orgs 201/201; `GET /auth/me` 200; `POST /feedback/` one synthetic Russian sample 201; `GET /feedback/{id}` 200; cross-org GET by ID 404; `GET /dashboard/` 200 and count >= 1; `POST /feedback/{id}/issue-draft` with no LLM 409. **9 assertions passed.**
- **Frontend Docker image built and Next.js HTML served: PASS**, [Actions 41048082865](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41048082865): `GET /` returned HTTP 200 with 14,897 bytes of HTML, no backend started during frontend test.
- Celery worker task processing: **NOT TESTED**. Feedback was successfully enqueued through Redis; completion and derived ML fields not verified.
- Interactive browser navigation, login forms, Kanban workflow and real dashboard render: **NOT TESTED**.
- Public API-key create + `POST /api/public/v1/feedback`: **NOT TESTED OVER HTTP**; supported routes verified from source only.
- Real Jira tracker write: **NOT TESTED AND WILL NOT BE ATTEMPTED** without explicit safe test instance credentials.
- Actual Russian incident ML quality: **NOT EVALUATED**.

## Tiny direct default-language behavior check

[Actions run 41047578460](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41047578460) executed the pinned upstream `PainPointCategorizer` directly on 3 English/Russian synthetic pairs. It completed successfully:

| Pair | English output | Russian output |
|---|---|---|
| Account login issue | functionality_broken | functionality_broken |
| App slow/freeze | system_crash | functionality_broken |
| Lost data | functionality_broken | functionality_broken |

This **is not an accuracy benchmark**. The rule sets are English-keyword-heavy, and the 6-sentence probe shows important category collapse on one RU/EN pair. Actual Russian technical incident labels still require ProductPulse and domain annotation.

## Decision — go for limited integration, no deep fork

**Ruling:** Rereflect is technically feasible to self-host (API + frontend smoke PASS), and is the better of the previously discussed Rereflect/ITARS options for polished dashboard and existing ticket workflow. But **DO NOT fork Rereflect as the ProductPulse core**. It is a feedback/churn analytics product, not an incident/problem registry, and the API cannot preserve canonical incident evidence natively.

1. **Preferred hackathon build:** use current ProductPulse engine + purpose-built thin Russian-first Incident/Problem dashboard (FastAPI + Streamlit or Next.js). Reuse MIT/open-source components for UI, Label Studio and LangGraph; no extra CRM/churn state to maintain. This minimizes semantic mismatch and supports credible incident-specific KPIs.
2. **Optional companion demo:** run Rereflect as a separate feedback portal. Export **sanitized ProblemInsight summary** to Rereflect via its public ingest API **after** adding a tested adapter, keep `rereflect_feedback_id ↔ productpulse_problem_id` mapping on ProductPulse side. Do not count a ProblemInsight as original support ticket or use Rereflect customer churn metrics as incident evidence.
3. **Avoid:** copying all Rereflect source, reusing its English-centric keyword model for Russian tickets, or mapping all ProductPulse metadata into a single text field.
4. **Integration gate before any production use:** exercise API key create/ingest/revoke and scope enforcement; end-to-end worker and UI on one stack; auth/rate limits, tenant ID propagation, secrets/TLS, availability, Russian labeling, and license/security audit.

**Fit-gap outcome:** Docker backend + frontend run successfully, but full domain integration would require custom schema/widgets and cannot be justified just by startup smoke. **No Gazprom Neft effectiveness or benchmark is claimed.**
