"""Evidence-grounded proposal controller. No raw ticket text or live LLM call.

Only a trusted ProblemRegistry may create VerifiedEvidence. An optional model
can select one *fixed* action enum via strict JSON with exact evidence IDs,
but can never author root cause, owner, executable instructions or citations.
Malformed, adversarial or unsupported outputs deterministically abstain.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

ActionType = Literal["investigate_regression", "improve_diagnostics", "review_documentation"]

_ACTIONS: dict[ActionType, str] = {
    "investigate_regression": "Проверить воспроизведение и наличие регрессии; причина пока неизвестна.",
    "improve_diagnostics": "Проверить полноту технических логов и диагностических данных.",
    "review_documentation": "Проверить пользовательскую документацию и возможные пробелы; требуется экспертная оценка.",
}


@dataclass(frozen=True)
class VerifiedEvidence:
    scope_id: str
    problem_id: str
    revision: int
    ticket_keys: tuple[str, ...]


class ModelSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    action_type: ActionType
    evidence_ticket_keys: tuple[str, ...]


@dataclass(frozen=True)
class InsightProposal:
    proposal_id: str
    problem_id: str
    scope_id: str
    revision: int
    evidence_ticket_keys: tuple[str, ...]
    evidence_digest: str
    action_type: ActionType
    title: str
    recommended_action: str
    root_cause_status: Literal["unknown"] = "unknown"
    owner_team_id: None = None
    requires_human_review: Literal[True] = True
    approval_status: Literal["pending", "approved"] = "pending"
    mock_issue_id: str | None = None


def _validate_evidence(evidence: VerifiedEvidence) -> None:
    if (not isinstance(evidence, VerifiedEvidence) or
        not isinstance(evidence.scope_id, str) or not evidence.scope_id.strip() or
        not isinstance(evidence.problem_id, str) or not evidence.problem_id.strip() or
        type(evidence.revision) is not int or evidence.revision < 2 or
        len(evidence.ticket_keys) < 2 or
        any(not isinstance(k, str) or not k.strip() for k in evidence.ticket_keys) or
        len(set(evidence.ticket_keys)) != len(evidence.ticket_keys)):
        raise ValueError("invalid verified Problem evidence")


def evidence_digest(evidence: VerifiedEvidence) -> str:
    """Bind consent to tenant, Problem, exact revision AND sorted ticket IDs."""
    _validate_evidence(evidence)
    material = json.dumps(
        [evidence.scope_id, evidence.problem_id, evidence.revision,
         sorted(evidence.ticket_keys)],
        separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return sha256(material).hexdigest()


def build_proposal(
    evidence: VerifiedEvidence,
    *,
    trusted_scope: str,
    model_output: str | None = None,
) -> InsightProposal:
    """Read-only, fact-limited proposal from an explicitly merged active group.

    Model output is a hint only; malformed/hostile JSON causes fallback.
    No claims based on user-controlled text, no external writes.
    """
    _validate_evidence(evidence)
    if evidence.scope_id != trusted_scope:
        raise ValueError("Problem scope mismatches trusted scope")
    keys = tuple(sorted(evidence.ticket_keys))
    action: ActionType = "investigate_regression"
    if model_output is not None:
        try:
            suggestion = ModelSuggestion.model_validate_json(model_output)
            if tuple(sorted(suggestion.evidence_ticket_keys)) == keys and len(
                set(suggestion.evidence_ticket_keys)
            ) == len(keys):
                action = suggestion.action_type
        except (ValidationError, ValueError, TypeError):
            pass
    return InsightProposal(
        proposal_id=f"{evidence.problem_id}:v{evidence.revision}",
        problem_id=evidence.problem_id,
        scope_id=evidence.scope_id,
        revision=evidence.revision,
        evidence_ticket_keys=keys,
        evidence_digest=evidence_digest(evidence),
        action_type=action,
        title=f"Проверить повторяющуюся проблему {evidence.problem_id} ({len(keys)} обращения)",
        recommended_action=_ACTIONS[action],
    )
