# Phase 23 — Insights UI with explicit lead consent (design)

**Status:** Draft; independent human review required. Stacked #23 on #22, no merge/deploy.

## Scope and rationale
Close hackathon demonstrability gap: Phase22 has tested `/internal/v1/insight-proposals`, explicit lead `/approve`, `/mock-publish`, but no front-end. Reuse existing Keycloak / Auth.js / Next.js server BFF, without second auth stack. No actual AI provider integration in this PR: model output would be ungrounded if the only sent features are ticket IDs. Offline, privacy-reviewed safe feature extraction + measured model value is needed before real inference.

## Trust and layout
- New `/insights` page only when `PRODUCTPULSE_AUTH_MODE=oidc`, auth() redirects anonymous to /login, disabled otherwise. Navbar shows only in OIDC mode.
- New `/api/insights` GET/POST (separate from pair review, less chance of cross-action confusion); server-only `X-Internal-Token` + encrypted Auth.js JWT reviewer access token; GET returns strict source-scoped proposals and sanitized, paginated evidence (up to 500) only when both sources are retrievable; unknown/missing evidence: fail closed 502/503; no partial fake success. No public backend origin/control.
- POST accepts exactly `{action: "approve"|"mock-publish", payload:{problem_id,expected_revision,evidence_digest,reason,operation_key}}`; strict Zod on IDs, digest, revision and reason. Server constructs allowlisted backend path from validated `/^PRB-[0-9]{6,}$/`. Authenticate signed Keycloak lead in FastAPI and refuse ordinary reviewers. Require exact Origin match, JSON-only, request body <= 12k, server no-store, no credentials leak in response.
- Render group cards with strong "Verified Problem membership does not prove root cause/volume surge"; evidence key list links to sanitized reviewer ticket summaries, `unknown` root cause, unassigned owner, deterministic action. Action approve and mock-publish are separate buttons with independent confirmation reason and explicit permission; only allow local publish button when status approved; backend still authoritative. No external link or write. After action clear data, reload; network error leaves no stale approvals clickable.
- Keycloak E2E must create one explicitly merged Problem **after** independent pair votes/lead approval by a trusted CI-only backend actor (not a public merge endpoint), then as ordinary reviewer inspect proposal and verify approve is denied; as lead approve then mock-publish, inspect mock ID and audit persisted, verify no external write. Use deterministic synthetic data with no real customer contents.
- Coverage: current proposal API is backend-only; `ModelSuggestion` parser is already available but no real model call. This phase remains deterministic, no fake precision/ROI claims.

## Non-goals
No live LLM egress/API keys, real Jira/YouTrack, auto-notifications, real incident metrics, new dependencies; only explicit signed human steps with strict evidence. Next: privacy-reviewed feature extraction, adapter offline prompt injection and efficacy study, then opt-in provider.
