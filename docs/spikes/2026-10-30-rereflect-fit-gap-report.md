# Fit–Gap: Rereflect for ProductPulse AI

**Date:** 2026-10-30. **Status:** PARTIAL — pinned source inspected, runtime smoke scheduled; do not present API runtime as passed without Actions evidence.

**Upstream pinned:** https://github.com/haqaliz/rereflect/tree/987dd9f0611c693524ec0cfba880517fa4d5ec57 (2026-10-21), MIT.
**Local evidence workflow:** [GitHub Actions run 41046817009](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41046817009).
**Test suite:** [scripts/spikes/rereflect_api_probe.py](../../scripts/spikes/rereflect_api_probe.py).
**Plan:** [2026-10-30-rereflect-fit-gap-plan](2026-10-30-rereflect-fit-gap-plan.md).

## Source inspection results (verified in upstream source; no runtime claim)

| Requirement | Evidence | Finding |
|---|---|---|
| MIT license | Upstream LICENSE + GitHub metadata | PASS: permissive reuse subject to attribution |
| Docker self-hosting | docker-compose.prod.yml | EXISTS; Postgres 16, Redis 7, Python 3.12 FastAPI backend, Celery worker, Next.js UI |
| HTTP API + RBAC | services/backend-api/src/api/routes/auth.py, public_api.py | EXISTS JWT signup/login and scoped API keys; actual tenancy isolation needs runtime verification |
| Create ticket/feedback | services/backend-api/src/api/routes/feedback.py | **GAP:** FeedbackCreateRequest only \`text\`, \`source\`; public create accepts \`text\`, \`source\`, \`customer_email\` |
| Preserve ProductPulse incident fields | services/backend-api/src/models/feedback.py | **GAP:** no native product_id/component_id/problem_id/approved pair links or versioned merge/split; source_metadata JSON is populated through integration machinery, not public create |
| Dashboard KPIs | services/backend-api/src/api/routes/dashboard.py | EXISTS; customer feedback/sentiment/churn KPIs, not proven incident problem trends |
| Jira issue draft | services/backend-api/src/api/routes/feedback_issue_draft.py | EXISTS; returns 409 without LLM; actual behavior needs HTTP verification |
| Russian language baseline | services/analysis-engine/src/analyzer/categorizer.py | **GAP:** English keyword-based default pain-point classification; no native Russian incident taxonomy verified |
| Dependency complexity | services/backend-api/Dockerfile | RISK: xmlsec native dependencies, Torch/transformers and heavy build; requires measured runtime |
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

- Docker Compose manifest: **PENDING workflow result**.
- Postgres/Redis/backend startup: **PENDING**.
- Signup, feedback import, feedback readback, dashboard count, issue draft default-deny and cross-org read isolation: **PENDING**.
- Celery worker execution: **NOT IN SCOPE** of initial backend HTTP smoke.
- Next.js build and interactive UI: **NOT IN SCOPE** of initial backend HTTP smoke.
- Real Jira tracker write: **NOT TESTED AND WILL NOT BE ATTEMPTED** without explicit safe test instance credentials.
- Actual Russian incident ML quality: **NOT EVALUATED**.

## Decision gate

Do not promote Rereflect as the ProductPulse core. After HTTP smoke, choose between integration-as-shell and minimal own UI based on measured build friction, preserved data semantics, and review effort. If the backend cannot pass a clean ephemeral test without patching upstream, treat integration as high risk until resolved.
