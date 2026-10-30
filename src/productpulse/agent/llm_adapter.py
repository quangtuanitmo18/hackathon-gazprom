"""Offline-testable LLM adapter boundary: aliases, no ticket text/IDs in prompts.

There is intentionally NO provider URL, API key, credential handling or
outbound network call in this module. The optional synchronous callback is
injected by a trusted service after independent privacy review. Without a
provider, or on invalid output, the controller uses the safe default.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Sequence

from pydantic import BaseModel, ConfigDict

from productpulse.agent.proposals import (
    InsightProposal, VerifiedEvidence, build_proposal, evidence_digest,
)


class _AliasSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    action_type: str
    evidence_aliases: tuple[str, ...]


_ALLOWED = ("investigate_regression", "improve_diagnostics", "review_documentation")


def _safe_statuses(values: Sequence[int]) -> tuple[int, ...]:
    if len(values) > 50 or any(type(n) is not int or n < 400 or n > 599 for n in values):
        raise ValueError("HTTP status must be a bounded 4xx or 5xx integer")
    return tuple(sorted(set(values)))


def build_prompt(
    evidence: VerifiedEvidence, *, http_statuses: Sequence[int] = (),
) -> str:
    """Construct prompt JSON without private IDs, source names or text.

    This schema's coarse HTTP status hints have very low information density.
    Do not claim that a model can infer root cause or a real business action
    from this prompt. Local alias mapping is the only citation mechanism.
    """
    evidence_digest(evidence)  # validates structured source evidence
    statuses = _safe_statuses(http_statuses)
    return json.dumps({
        "task": "Choose one cautious action. No diagnosis, owner or causal claim.",
        "evidence_aliases": [f"E{i}" for i in range(1, len(evidence.ticket_keys)+1)],
        "ticket_count": len(evidence.ticket_keys),
        "http_statuses": list(statuses),
        "allowed_actions": list(_ALLOWED),
        "response_schema": {
            "action_type": "one allowed action string",
            "evidence_aliases": "exactly the aliases above",
        },
    }, ensure_ascii=False, separators=(",", ":"))


def _object_unique(pairs: list[tuple[str, object]]) -> dict:
    obj={}
    for key,value in pairs:
        if key in obj:raise ValueError("duplicate JSON field")
        obj[key]=value
    return obj


def suggest_with_model(
    evidence: VerifiedEvidence, *, trusted_scope: str,
    model_call: Callable[[str], str] | None = None,
    http_statuses: Sequence[int] = (),
) -> InsightProposal:
    """Strict, optional model hint. Never publishes or changes approval state."""
    # Validate scope and fixed-schema prompt BEFORE invoking any callback.
    baseline = build_proposal(evidence, trusted_scope=trusted_scope)
    prompt=build_prompt(evidence,http_statuses=http_statuses)
    if model_call is None:
        return baseline
    try:
        raw=model_call(prompt)
        if not isinstance(raw,str) or len(raw)>4096:
            return baseline
        parsed=_AliasSuggestion.model_validate(
            json.loads(raw,object_pairs_hook=_object_unique),
        )
        aliases=tuple(f"E{i}" for i in range(1,len(evidence.ticket_keys)+1))
        if (parsed.action_type not in _ALLOWED or
            len(set(parsed.evidence_aliases))!=len(aliases) or
            tuple(sorted(parsed.evidence_aliases))!=tuple(sorted(aliases))):
            return baseline
        # This translation happens LOCALLY. Ticket IDs are never sent in prompt.
        return build_proposal(
            evidence,trusted_scope=trusted_scope,
            model_output=json.dumps({
                "action_type":parsed.action_type,
                "evidence_ticket_keys":list(evidence.ticket_keys),
            }),
        )
    except Exception:
        # No untrusted exception text/PII in a response or audit.
        return baseline
