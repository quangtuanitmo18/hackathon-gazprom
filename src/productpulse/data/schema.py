"""Canonical ticket schema for externally sourced, already redacted text.

IMPORTANT: this model validates structure, not the absence of PII. The caller
must redact and authorize the underlying data before passing it here.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class CanonicalTicket(BaseModel):
    """One text-bearing ticket; no resolution-time labels or agent guesses."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
    source_id: str
    text_redacted: str
    created_at: datetime | None = None
    source_label: str | None = None
    product_id: str | None = None
    split: Literal["train", "test"] | None = None

    @field_validator("source", "source_id")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier cannot be blank")
        return value.strip()

    @field_validator("text_redacted")
    @classmethod
    def preserve_nonempty_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ticket text cannot be blank")
        return value

    @field_validator("created_at", mode="before")
    @classmethod
    def reject_numeric_timestamp(cls, value: object) -> object:
        if isinstance(value, (int, float, bool)):
            raise ValueError("timestamp must be an explicit timezone-aware datetime or ISO string")
        return value

    @field_validator("created_at")
    @classmethod
    def require_aware_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone information")
        return value.astimezone(timezone.utc)
