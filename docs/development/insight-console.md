# Phase 23 — Keycloak Insight Console + privacy-safe offline LLM adapter

**Status:** Draft PR #23 stacked on #22. No merge, deploy, external issue tracker or live model API access.

## User-facing workflow

The new sidebar **Предложения** points to `/insights` and is visible only when `PRODUCTPULSE_AUTH_MODE=oidc`. The page redirects unauthenticated users to Keycloak sign-in. Shared Basic demo access cannot access approval UX. Only already explicitly merged multi-ticket Problems create proposals: lexically similar/lead-approved but not merged tickets **cannot** generate a product recommendation.

After loading via `GET /api/insights`, reviewer can inspect the source-scoped evidence IDs, sanitized ticket texts, revision, evidence digest, action template, **unknown root cause** and **no assigned owner**. Proposal and complete paginated evidence are validated server-side; missing evidence aborts the entire response rather than allowing misleading UI.

Lead must enter a reason and make two independent signed POST requests:
1. `action=approve` — verifies active revision and evidence digest, persists audited approval. **Does not publish.**
2. `action=mock-publish` — only enabled once approved and requires a **new reason**; writes one internal mock issue. Never calls an external tracker. Exact operation keys prevent duplicate audit. The backend enforces lead OIDC + private service token and denies ordinary reviewers even if browser UI is tampered with.

The Next.js `/api/insights` route follows the same encrypted Auth.js JWT design as pair review; GET/POST use `Cache-Control:no-store`, same-origin CSRF checks, fixed upstream allowlist and strict Zod. Browser responses do not include OIDC credentials or service token; root cause/owner cannot be model-authored.

## Provider-neutral LLM adapter

`src/productpulse/agent/llm_adapter.py` is intentionally **offline** and not wired to inference in API routes. The deterministic `build_proposal` path remains the only currently active runtime. `suggest_with_model(evidence, trusted_scope, model_call, http_statuses)` accepts a trusted *injected callback* and constructs a prompt with **only** `E1..En` pseudonymous evidence aliases, count, and numeric allowlisted HTTP 4xx/5xx statuses. No source ticket keys, tenant identifier, raw text, root cause, owner or private names are included in the prompt. Returned JSON must name exactly those aliases, choose one enum action, have no extra fields, no duplicate JSON keys, and be bounded. The alias→actual evidence translation happens locally and passes through the existing `build_proposal` verification. Timeout/unavailable/hostile/invalid output falls back to the safe action. **No provider secret, endpoint, HTTP request or prompt transmission exists in this PR.**

The restricted input has very low information density: a model cannot infer root cause, engineering solution, impact, or reliability from it. This is a **safe integration contract**, not a tested quality improvement over deterministic action selection. For meaningful LLM inference, first establish a privacy-reviewed typed signal extractor, a local or explicitly consented provider, offline human-judged gold test sets, latency/cost/grounding evaluation, and policy approval.

## Real E2E contract

`.github/workflows/keycloak-review-e2e.yml` first runs the existing 3-identity review E2E; PostgreSQL audit confirms **no automatic merge**. A *trusted CI-only Python operator* then **explicitly** merges the human-approved pair in the synthetic database. A second Chromium test checks reviewer-A can only inspect proposal, cannot approve (401), while a distinct lead can approve then mock-publish with separate reasons. Audits must show **one** `insight_proposal_approved` and **one** `insight_mock_published`. This is a synthetic CI fixture, **not a GitHub PR merge and not a production mutation**.

## Known limitations
- Domain backend `GET /internal/v1/insight-proposals` still has a 5000-ticket cap; UI BFF evidence pagination caps at 500, and intentionally **fails closed** if any proposal evidence is outside the accessible pages. The next indexed evidence lookup should support high-volume tenants without partial citation visibility.
- Raw source-scoped identifiers and human-entered reasons may contain confidential information; scrubadub is not sufficient DLP for Russian names and business identifiers. Need policy/retention and validated source adapters before real corporate deployment.
- No actual live model calls, model accuracy/ROI claims, owner routing, source ingestion watermark, reliable time-to-insight, external Jira/YouTrack. This PR only makes the **verified, human-gated, mock-only pipeline demonstrable**.
