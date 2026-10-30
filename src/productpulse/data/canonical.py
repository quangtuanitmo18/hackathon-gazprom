"""Dataset-independent, arrival-time ticket and separate evaluation labels.

These models check structural integrity. Actual PII redaction and authorization
must occur upstream. Never pass GoldDuplicateLink to online predictor inputs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class CanonicalTicketV1(BaseModel):
    """Source-scoped support event with only fields known at arrival."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    source_system: str
    source_ticket_id: str
    provenance_id: str
    title: str | None = None
    body_redacted: str | None = None
    created_at: datetime | None = None
    product_id: str | None = None
    component_id: str | None = None
    reported_version: str | None = None
    error_codes: tuple[str, ...] = ()
    pseudonymous_user_id: str | None = None

    @field_validator("source_system", "source_ticket_id", "provenance_id")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("source identity and provenance must not be blank")
        return value.strip()

    @field_validator("created_at", mode="before")
    @classmethod
    def reject_numeric_timestamp(cls, value: object) -> object:
        if isinstance(value, (int, float, bool)):
            raise ValueError("timestamp must have explicit timezone information")
        return value

    @field_validator("created_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must have explicit timezone information")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def require_usable_text(self) -> "CanonicalTicketV1":
        if not (self.title and self.title.strip()) and not (
            self.body_redacted and self.body_redacted.strip()
        ):
            raise ValueError("ticket requires a non-empty title or body")
        return self


def ticket_key(ticket: CanonicalTicketV1) -> str:
    """Collision-free length-prefixed source-scoped identity."""
    s = ticket.source_system
    i = ticket.source_ticket_id
    return f"{len(s)}:{s}{len(i)}:{i}"


class DatasetCapabilities(BaseModel):
    """Controls which metrics are evaluable with an upstream corpus."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    classification_gold: bool = False
    duplicate_links: bool = False
    timestamps: bool = False
    owner_gold: bool = False
    status_events: bool = False


class GoldDuplicateLink(BaseModel):
    """Separate evaluation-only duplicate-of evidence; not a ticket feature."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_system: str
    issue_id: str
    master_id: str
    evidence_type: str

    @field_validator("source_system", "issue_id", "master_id", "evidence_type")
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("gold link field cannot be blank")
        return value.strip()

    @model_validator(mode="after")
    def reject_self_link(self) -> "GoldDuplicateLink":
        if self.issue_id == self.master_id:
            raise ValueError("duplicate link cannot reference self")
        return self
