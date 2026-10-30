"""Service-to-service FastAPI facade for a scoped ProductPulse demo.

No public merge, human review, incident approval, tracker action or Jira write.
The internal token is a shared service secret, NOT end-user OIDC/RBAC.
Do not expose to the public Internet without gateway/firewall protection.
"""
from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timezone
from secrets import compare_digest
from typing import Literal, Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine

from productpulse.data.canonical import CanonicalTicketV1
from productpulse.api.reviewer_auth import ReviewerJWTVerifier, ReviewTokenError, ReviewerPrincipal
from productpulse.incident.annotation import PairLabel
from productpulse.incident.candidates import rank_review_candidates
from productpulse.insights.trends import analyze_problem_trends
from productpulse.insights.unverified_activity import list_unverified_activity
from productpulse.privacy.redaction import sanitize_ticket, UnsafeIdentity
from productpulse.storage.repository import PersistentProblemRegistry


class ProblemOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_id: str
    scope_id: str
    ticket_keys: tuple[str, ...]
    revision: int
    status: Literal["active", "merged"]
    merged_into: str | None = None
    parent_id: str | None = None


class AuditOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scope_id: str
    sequence: int
    kind: str
    actor: str
    operation_key: str
    occurred_at: str
    problem_ids: tuple[str, ...]
    ticket_keys: tuple[str, ...]
    reason: str
    revoked_pair_ids: tuple[str, ...]



class ReviewTicketQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=50, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class ReviewTicketOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_key: str
    source_system: str
    source_ticket_id: str
    product_id: str | None = None
    component_id: str | None = None
    reported_version: str | None = None
    error_codes: tuple[str, ...] = ()
    body_redacted: str | None = None


class CandidateQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=20, ge=1, le=30)


class CandidateOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_key_a: str
    ticket_key_b: str
    rank: int
    signals: tuple[Literal[
        "lexical_overlap","same_product","same_component","shared_error_code",
    ], ...]


class UnverifiedActivityQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_hours: int = Field(default=24, ge=1, le=168)
    limit: int = Field(default=20, ge=1, le=30)


class UnverifiedActivityOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_key_a: str
    ticket_key_b: str
    created_at_a: datetime
    created_at_b: datetime
    as_of: datetime
    window_hours: int
    recent_pattern: Literal["both_current", "current_with_previous"]
    current_member_count: int = Field(ge=1, le=2)
    previous_member_count: int = Field(ge=0, le=1)
    rank: int = Field(ge=1)
    signals: tuple[Literal[
        "lexical_overlap", "same_product", "same_component", "shared_error_code"
    ], ...]
    evidence_type: Literal["lexical_candidate"]
    coverage_status: Literal["unknown_coverage"]
    eligible_for_alert: Literal[False]


class TrendQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_hours: int = Field(default=24, ge=1, le=168)


class TrendOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_id: str
    scope_id: str
    revision: int
    status: Literal[
        "volume_increase", "new_activity", "monitor",
        "insufficient_timestamps", "unknown_coverage"
    ]
    as_of: datetime
    window_hours: int
    current_count: int
    previous_count: int
    delta: int
    current_ticket_keys: tuple[str, ...]
    previous_ticket_keys: tuple[str, ...]
    coverage_status: Literal["complete", "unknown_coverage"]
    observed_pattern: Literal["volume_increase", "new_activity", "monitor"]
    eligible_for_alert: bool


class InsightQuery(BaseModel):
    # No client-controlled scope / model / proposal membership. Unknown query
    # parameters are rejected rather than silently ignored.
    model_config = ConfigDict(extra="forbid")


class InsightProposalOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposal_id: str
    problem_id: str
    scope_id: str
    revision: int
    evidence_ticket_keys: tuple[str, ...]
    evidence_digest: str
    action_type: Literal["investigate_regression", "improve_diagnostics", "review_documentation"]
    title: str
    recommended_action: str
    root_cause_status: Literal["unknown"]
    owner_team_id: None
    requires_human_review: Literal[True]
    approval_status: Literal["pending", "approved"]
    mock_issue_id: str | None


class InsightActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=2)
    evidence_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    reason: str = Field(min_length=3, max_length=2000)
    operation_key: str = Field(min_length=1, max_length=160)


class InsightApprovalOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposal_id: str
    problem_id: str
    scope_id: str
    revision: int
    evidence_digest: str
    approved_by: str
    reason: str


class MockIssueOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mock_issue_id: str
    proposal_id: str
    problem_id: str
    scope_id: str
    revision: int
    evidence_digest: str
    created_by: str
    reason: str


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_key_a: str = Field(min_length=1, max_length=512)
    ticket_key_b: str = Field(min_length=1, max_length=512)
    label: PairLabel
    rationale: str = Field(min_length=3, max_length=3000)
    operation_key: str = Field(min_length=1, max_length=160)


class LeadApprovalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_key_a: str = Field(min_length=1, max_length=512)
    ticket_key_b: str = Field(min_length=1, max_length=512)
    reason: str = Field(min_length=3, max_length=3000)
    operation_key: str = Field(min_length=1, max_length=160)


class ReviewProgressOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: str
    status: Literal[
        "awaiting_first_review", "awaiting_second_review", "ready_for_lead",
        "disputed", "uncertain", "classified", "approved",
    ]
    reviewer_ids: tuple[str, ...]


class PairApprovalOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: str
    ticket_keys: tuple[str, str]
    reviewer_ids: tuple[str, str]


def create_app(
    store: PersistentProblemRegistry, scope_id: str, internal_token: str,
    reviewer_verifier: ReviewerJWTVerifier | None = None,
) -> FastAPI:
    """Explicit trusted dependency injection; user requests cannot set scope."""
    if not isinstance(scope_id, str) or not scope_id.strip() or len(scope_id.strip()) > 128:
        raise ValueError("trusted scope_id must be set and at most 128 characters")
    if not isinstance(internal_token, str) or len(internal_token) < 24:
        raise ValueError("a high-entropy internal token is mandatory")
    scope_id = scope_id.strip()

    def require_internal(x_internal_token: str | None = Header(default=None)) -> None:
        # compare_digest avoids secret-dependent short circuiting.
        if not x_internal_token or not compare_digest(
            x_internal_token.encode("utf-8"), internal_token.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid internal service credential",
            )

    app = FastAPI(title="ProductPulse Internal Incident API", version="0.1.0")

    @app.get("/health/live")
    def alive():
        return {"status": "alive"}

    @app.post(
        "/internal/v1/tickets",
        status_code=status.HTTP_201_CREATED,
        response_model=ProblemOut,
        dependencies=[Depends(require_internal)],
    )
    def ingest(ticket: CanonicalTicketV1):
        try:
            # Ingress guarantee: strip detected common PII/secrets BEFORE any
            # persistent JSONB mutation. Identifiers cannot be mutated safely.
            sanitized = sanitize_ticket(ticket)
            result = store.transact(
                scope_id, lambda r: r.register_ticket(sanitized, scope_id),
            )
            return asdict(result)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket identity conflict or invalid operation",
            ) from exc

    @app.get(
        "/internal/v1/problems",
        response_model=list[ProblemOut],
        dependencies=[Depends(require_internal)],
    )
    def list_problems():
        return [asdict(item) for item in store.read(scope_id, lambda r: r.list_active())]

    @app.get(
        "/internal/v1/problems/{problem_id}",
        response_model=ProblemOut,
        dependencies=[Depends(require_internal)],
    )
    def problem_detail(problem_id: str):
        try:
            result = store.read(scope_id, lambda r: r.get_problem(problem_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Problem not found") from exc
        return asdict(result)

    @app.get(
        "/internal/v1/audit",
        response_model=list[AuditOut],
        dependencies=[Depends(require_internal)],
    )
    def audit():
        return list(store.audit(scope_id))


    def authenticated_reviewer(
        authorization: str | None, required_role: str,
    ) -> ReviewerPrincipal:
        if reviewer_verifier is None:
            raise HTTPException(status_code=503, detail="Reviewer identity provider not configured")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="OIDC Bearer token required")
        try:
            return reviewer_verifier.verify(
                authorization[len("Bearer "):],
                expected_scope=scope_id, required_role=required_role,
            )
        except ReviewTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid reviewer identity or permissions") from exc

    def need_reviewer(authorization: str | None = Header(default=None)):
        return authenticated_reviewer(authorization, "productpulse_reviewer")

    def need_lead(authorization: str | None = Header(default=None)):
        return authenticated_reviewer(authorization, "productpulse_review_lead")

    @app.get(
        "/internal/v1/review-candidates",
        response_model=list[CandidateOut],
        dependencies=[Depends(require_internal)],
    )
    def review_candidates(
        params: Annotated[CandidateQuery, Query()],
        principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        def retrieve(reg):
            rows = reg.candidate_inputs(corpus_cap=500)
            approved = {tuple(ap.ticket_keys) for ap in reg.active_approvals()}
            return rank_review_candidates(
                rows, approved_pairs=approved, corpus_cap=500,
                limit=params.limit,
            )
        try:
            return list(store.read(scope_id, retrieve))
        except ValueError as exc:
            # Explicit capacity condition, never silently sample first N
            # and claim corpus-wide recommendation completeness.
            raise HTTPException(
                status_code=503,
                detail="Candidate index capacity exceeded; use larger indexed retrieval service",
            ) from exc

    @app.get(
        "/internal/v1/unverified-activity",
        response_model=list[UnverifiedActivityOut],
        dependencies=[Depends(require_internal)],
    )
    def unverified_activity(
        params: Annotated[UnverifiedActivityQuery, Query()],
        principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        """Non-transitive, evidence-only early reviewer pair shortlist.

        No Problem membership, incident verdict, notification, or tracker
        write. The snapshot has no source coverage/ingest-time guarantee.
        """
        try:
            def evaluate(reg):
                rows = reg.candidate_inputs(corpus_cap=500)
                approved = {tuple(ap.ticket_keys) for ap in reg.active_approvals()}
                return list_unverified_activity(
                    rows,
                    approved_pairs=approved,
                    as_of=datetime.now(timezone.utc),
                    window_hours=params.window_hours,
                    limit=params.limit,
                    corpus_cap=500,
                )
            return [asdict(row) for row in store.read(scope_id, evaluate)]
        except ValueError as exc:
            raise HTTPException(
                status_code=503,
                detail="Unverified activity unavailable or candidate corpus capacity exceeded",
            ) from exc

    @app.get(
        "/internal/v1/review-tickets",
        response_model=list[ReviewTicketOut],
        dependencies=[Depends(require_internal)],
    )
    def review_evidence(
        params: Annotated[ReviewTicketQuery, Query()],
        principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        # Reviewer identity/scope is validated by OIDC before any ticket text
        # is returned. Data MUST already be redacted before ingestion.
        rows = store.read(scope_id, lambda r: r.list_review_tickets(
            limit=params.limit, offset=params.offset
        ))
        return [
            ReviewTicketOut(
                ticket_key=key,
                source_system=ticket.source_system,
                source_ticket_id=ticket.source_ticket_id,
                product_id=ticket.product_id,
                component_id=ticket.component_id,
                reported_version=ticket.reported_version,
                error_codes=ticket.error_codes,
                body_redacted=ticket.body_redacted[:2000] if ticket.body_redacted else None,
            )
            for key, ticket in rows
        ]

    @app.get(
        "/internal/v1/trends",
        response_model=list[TrendOut],
        dependencies=[Depends(require_internal)],
    )
    def verified_problem_trends(
        params: Annotated[TrendQuery, Query()],
        principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        # Neither an approved pair nor a BM25 hit creates Problem membership.
        # Only active, explicitly merged records pass the projection below.
        try:
            rows = store.read(
                scope_id,
                lambda registry: analyze_problem_trends(
                    registry.trend_inputs(corpus_cap=5000),
                    trusted_scope=scope_id,
                    as_of=datetime.now(timezone.utc),
                    window_hours=params.window_hours,
                    corpus_cap=5000,
                ),
            )
        except ValueError as exc:
            # Capacity or domain-corruption guard; no raw ticket contents.
            raise HTTPException(
                status_code=503,
                detail="Verified trend evidence unavailable or capacity exceeded",
            ) from exc
        return [asdict(row) for row in rows]

    @app.get(
        "/internal/v1/insight-proposals",
        response_model=list[InsightProposalOut],
        dependencies=[Depends(require_internal)],
    )
    def insight_proposals(
        params: Annotated[InsightQuery, Query()],
        principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        """Only active explicitly grouped Problems; read-only and tenant-scoped."""
        try:
            return [
                asdict(row)
                for row in store.read(scope_id,lambda r:r.insight_proposals(scope_id))
            ]
        except ValueError as exc:
            raise HTTPException(status_code=503,detail="Verified insight evidence unavailable") from exc

    @app.post(
        "/internal/v1/insight-proposals/{problem_id}/approve",
        response_model=InsightApprovalOut,
        status_code=201,
        dependencies=[Depends(require_internal)],
    )
    def approve_insight_proposal(
        problem_id: str, payload: InsightActionInput,
        principal: ReviewerPrincipal = Depends(need_lead),
    ):
        try:
            outcome=store.transact(scope_id,lambda r:r.approve_insight(
                problem_id,expected_revision=payload.expected_revision,
                evidence_digest=payload.evidence_digest,
                actor=principal.reviewer_id,
                reason=payload.reason,operation_key=payload.operation_key,
            ))
            return asdict(outcome)
        except ValueError as exc:
            raise HTTPException(status_code=409,detail="Stale or unverified insight proposal") from exc

    @app.post(
        "/internal/v1/insight-proposals/{problem_id}/mock-publish",
        response_model=MockIssueOut,
        status_code=201,
        dependencies=[Depends(require_internal)],
    )
    def mock_publish_insight(
        problem_id: str, payload: InsightActionInput,
        principal: ReviewerPrincipal = Depends(need_lead),
    ):
        # Internal transactional MOCK ONLY. No Jira, HTTP, webhook or queue.
        try:
            outcome=store.transact(scope_id,lambda r:r.publish_mock_insight(
                problem_id,expected_revision=payload.expected_revision,
                evidence_digest=payload.evidence_digest,
                actor=principal.reviewer_id,
                reason=payload.reason,operation_key=payload.operation_key,
            ))
            return asdict(outcome)
        except ValueError as exc:
            raise HTTPException(status_code=409,detail="Human approval or verified revision required") from exc

    @app.get(
        "/internal/v1/reviews",
        response_model=list[ReviewProgressOut],
        dependencies=[Depends(require_internal)],
    )
    def review_queue(principal: ReviewerPrincipal = Depends(need_reviewer)):
        return [asdict(v) for v in store.read(scope_id, lambda r: r.review_statuses())]

    @app.post(
        "/internal/v1/reviews",
        status_code=201,
        response_model=ReviewProgressOut,
        dependencies=[Depends(require_internal)],
    )
    def submit_review(
        payload: ReviewInput, principal: ReviewerPrincipal = Depends(need_reviewer),
    ):
        try:
            result = store.transact(scope_id, lambda r: r.submit_review(
                payload.ticket_key_a, payload.ticket_key_b,
                reviewer_id=principal.reviewer_id,
                label=payload.label, rationale=payload.rationale,
                operation_key=payload.operation_key,
            ))
            return asdict(result)
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=409, detail="Review operation conflict or missing registered pair") from exc

    @app.post(
        "/internal/v1/reviews/approve",
        status_code=201,
        response_model=PairApprovalOut,
        dependencies=[Depends(require_internal)],
    )
    def lead_approve(
        payload: LeadApprovalInput, principal: ReviewerPrincipal = Depends(need_lead),
    ):
        try:
            result = store.transact(scope_id, lambda r: r.approve_reviewed_pair(
                payload.ticket_key_a, payload.ticket_key_b,
                actor=principal.reviewer_id,
                reason=payload.reason, operation_key=payload.operation_key,
            ))
            return asdict(result)
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=409, detail="Approval conflict or independent review incomplete") from exc

    return app


def app_from_env() -> FastAPI:
    """Uvicorn factory. Secrets from deployment env ONLY, never repo defaults."""
    db_url = os.environ["DATABASE_URL"]
    scope_id = os.environ["PRODUCTPULSE_SCOPE_ID"]
    internal_token = os.environ["PRODUCTPULSE_INTERNAL_TOKEN"]
    engine = create_engine(db_url, pool_pre_ping=True)
    oidc_fields = (
        os.getenv("PRODUCTPULSE_OIDC_ISSUER"),
        os.getenv("PRODUCTPULSE_OIDC_AUDIENCE"),
        os.getenv("PRODUCTPULSE_OIDC_JWKS_URL"),
    )
    verifier = None
    if any(oidc_fields):
        if not all(oidc_fields):
            raise ValueError("all OIDC issuer, audience and JWKS URL settings are required")
        verifier = ReviewerJWTVerifier(
            issuer=oidc_fields[0], audience=oidc_fields[1], jwks_url=oidc_fields[2]
        )
    return create_app(
        PersistentProblemRegistry(engine), scope_id, internal_token,
        reviewer_verifier=verifier,
    )
