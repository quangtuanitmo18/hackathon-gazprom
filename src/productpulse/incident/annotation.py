"""Human-only pair judgment records kept separate from runtime model inputs.

Authorization of reviewer_id must be enforced by a future authenticated service.
Passing source_kind='human' in a record alone does not prove human authorship.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from productpulse.data.canonical import CanonicalTicketV1, ticket_key


PairLabel = Literal[
    "same_incident", "related_topic", "different_incident", "uncertain"
]


def pair_identity(a: CanonicalTicketV1, b: CanonicalTicketV1) -> str:
    """Order-independent, collision-safe pair identity using source-scoped IDs."""
    first, second = ticket_key(a), ticket_key(b)
    if first == second:
        raise ValueError("cannot label the same ticket twice")
    return json.dumps(sorted((first, second)), ensure_ascii=False, separators=(",", ":"))


class PairAnnotation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    pair_id: str
    label: PairLabel
    reviewer_id: str
    rationale: str
    reviewed_at: datetime
    source_kind: Literal["human"] = "human"

    @field_validator("pair_id", "reviewer_id", "rationale")
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("pair/reviewer/rationale cannot be empty")
        return value.strip()

    @field_validator("reviewed_at")
    @classmethod
    def timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("reviewed_at timezone is required")
        return value.astimezone(timezone.utc)


class PairAdjudication(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    pair_id: str
    status: Literal["confirmed", "disputed", "uncertain"]
    label: PairLabel | None = None
    reviewer_ids: tuple[str, str]


def adjudicate_pair(a: PairAnnotation, b: PairAnnotation) -> PairAdjudication:
    """Two different reviewers; disagreement must be escalated, not guessed."""
    if a.pair_id != b.pair_id:
        raise ValueError("cannot adjudicate different pair identities")
    if a.reviewer_id == b.reviewer_id:
        raise ValueError("two independent reviewers are required")
    if a.label != b.label:
        status, agreed = "disputed", None
    elif a.label == "uncertain":
        status, agreed = "uncertain", None
    else:
        status, agreed = "confirmed", a.label
    return PairAdjudication(
        pair_id=a.pair_id, status=status, label=agreed,
        reviewer_ids=(a.reviewer_id, b.reviewer_id),
    )
