"""Service-to-service FastAPI facade for a scoped ProductPulse demo.

No public merge, human review, incident approval, tracker action or Jira write.
The internal token is a shared service secret, NOT end-user OIDC/RBAC.
Do not expose to the public Internet without gateway/firewall protection.
"""
from __future__ import annotations

import os
from dataclasses import asdict
from secrets import compare_digest
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine

from productpulse.data.canonical import CanonicalTicketV1
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


def create_app(
    store: PersistentProblemRegistry, scope_id: str, internal_token: str,
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
            result = store.transact(
                scope_id, lambda r: r.register_ticket(ticket, scope_id),
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

    return app


def app_from_env() -> FastAPI:
    """Uvicorn factory. Secrets from deployment env ONLY, never repo defaults."""
    db_url = os.environ["DATABASE_URL"]
    scope_id = os.environ["PRODUCTPULSE_SCOPE_ID"]
    internal_token = os.environ["PRODUCTPULSE_INTERNAL_TOKEN"]
    engine = create_engine(db_url, pool_pre_ping=True)
    return create_app(PersistentProblemRegistry(engine), scope_id, internal_token)
