"""Conservative evidence screen before human incident-pair adjudication.

This is NOT a ground-truth same-incident classifier. Its only possible output
is an actionable review candidate or abstention; both require human review.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from productpulse.data.canonical import CanonicalTicketV1, ticket_key


class PairScreening(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal[
        "candidate_for_human_review", "insufficient_or_conflicting_evidence"
    ]
    evidence: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    requires_human_review: Literal[True] = True


def _normalized_codes(values: tuple[str, ...]) -> frozenset[str]:
    return frozenset(" ".join(value.upper().split()) for value in values if value.strip())


def _same_field(
    left: str | None,
    right: str | None,
    name: str,
    evidence: list[str],
    blockers: list[str],
) -> None:
    # Product/component/version IDs are opaque identifiers; do not erase case
    # differences or infer aliases without a tenant-specific normalization map.
    if not left or not left.strip() or not right or not right.strip():
        blockers.append(f"missing_{name}")
    elif left.strip() != right.strip():
        blockers.append(f"{name}_conflict")
    else:
        evidence.append(f"same_{name}")


def screen_pair(
    a: CanonicalTicketV1,
    b: CanonicalTicketV1,
    symptom_a: str | None,
    symptom_b: str | None,
) -> PairScreening:
    """Collect explicit evidence; never auto-confirm links or touch external tools.

    The symptom must come from a separately versioned, arrival-time attribute
    extraction step; no NLP/LLM instructions in raw ticket text are read here.
    """
    if ticket_key(a) == ticket_key(b):
        raise ValueError("cannot screen the same ticket against itself")

    evidence: list[str] = []
    blockers: list[str] = []
    _same_field(a.product_id, b.product_id, "product", evidence, blockers)
    _same_field(a.component_id, b.component_id, "component", evidence, blockers)
    _same_field(a.reported_version, b.reported_version, "version", evidence, blockers)

    codes_a, codes_b = _normalized_codes(a.error_codes), _normalized_codes(b.error_codes)
    if not codes_a or not codes_b:
        blockers.append("missing_error_codes")
    elif codes_a != codes_b:
        blockers.append("error_code_conflict")
    else:
        evidence.append("same_error_codes")

    if not symptom_a or not symptom_a.strip() or not symptom_b or not symptom_b.strip():
        blockers.append("missing_symptom")
    elif symptom_a.strip() != symptom_b.strip():
        blockers.append("symptom_conflict")
    else:
        evidence.append("same_symptom")

    return PairScreening(
        status=(
            "insufficient_or_conflicting_evidence"
            if blockers else "candidate_for_human_review"
        ),
        evidence=tuple(evidence),
        blockers=tuple(blockers),
    )
