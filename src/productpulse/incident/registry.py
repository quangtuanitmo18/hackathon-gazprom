"""In-memory, review-gated Problem Registry for a trusted, scoped backend.

No persistence or authenticating reviewer identities here; caller must validate
scope and actor via RBAC. No similarity-based auto merges or tracker writes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.annotation import (
    PairAnnotation, adjudicate_pair, pair_identity,
)


@dataclass(frozen=True)
class ProblemRecord:
    problem_id: str
    scope_id: str
    ticket_keys: tuple[str, ...]
    revision: int = 1
    status: Literal["active", "merged"] = "active"
    merged_into: str | None = None
    parent_id: str | None = None


@dataclass(frozen=True)
class PairApproval:
    pair_id: str
    ticket_keys: tuple[str, str]
    reviewer_ids: tuple[str, str]


@dataclass(frozen=True)
class AuditEvent:
    kind: str
    actor: str
    operation_key: str
    at: datetime
    problem_ids: tuple[str, ...] = ()
    ticket_keys: tuple[str, ...] = ()
    reason: str = ""
    revoked_pair_ids: tuple[str, ...] = ()


class ProblemRegistry:
    """One process, one trusted scope-aware application instance; NOT durable."""

    def __init__(self) -> None:
        self._tickets: dict[str, CanonicalTicketV1] = {}
        self._scopes: dict[str, str] = {}
        self._owners: dict[str, str] = {}
        self._problems: dict[str, ProblemRecord] = {}
        self._approved: dict[str, PairApproval] = {}
        self._events: list[AuditEvent] = []
        self._operations: dict[str, tuple[tuple[object, ...], object]] = {}
        self._sequence = 0

    @staticmethod
    def _required(value: str, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must not be blank")
        return value.strip()

    def _new_id(self) -> str:
        self._sequence += 1
        return f"PRB-{self._sequence:06d}"

    def _event(
        self, kind: str, actor: str, operation_key: str,
        problem_ids: tuple[str, ...] = (), ticket_keys: tuple[str, ...] = (),
        reason: str = "", revoked_pair_ids: tuple[str, ...] = (),
    ) -> None:
        self._events.append(AuditEvent(
            kind=kind, actor=actor, operation_key=operation_key,
            at=datetime.now(timezone.utc),
            problem_ids=problem_ids, ticket_keys=ticket_keys, reason=reason,
            revoked_pair_ids=revoked_pair_ids,
        ))

    def _replay(self, operation_key: str, fingerprint: tuple[object, ...]) -> object | None:
        prior = self._operations.get(operation_key)
        if prior is None:
            return None
        if prior[0] != fingerprint:
            raise ValueError("idempotency key reused for different operation")
        return prior[1]

    def register_ticket(self, ticket: CanonicalTicketV1, scope_id: str) -> ProblemRecord:
        scope = self._required(scope_id, "scope_id")
        key = ticket_key(ticket)
        if key in self._tickets:
            if self._scopes[key] != scope:
                raise ValueError("ticket identity already belongs to another scope")
            if self._tickets[key] != ticket:
                raise ValueError("ticket identity conflict: changed content requires explicit update event")
            return self.problem_for_ticket(ticket)
        pid = self._new_id()
        record = ProblemRecord(problem_id=pid, scope_id=scope, ticket_keys=(key,))
        self._tickets[key] = ticket
        self._scopes[key] = scope
        self._owners[key] = pid
        self._problems[pid] = record
        self._event("ticket_registered", "ingestion", f"register:{key}", (pid,), (key,))
        return record

    def get_problem(self, problem_id: str) -> ProblemRecord:
        return self._problems[problem_id]

    def problem_for_ticket(self, ticket: CanonicalTicketV1) -> ProblemRecord:
        return self._problems[self._owners[ticket_key(ticket)]]

    def audit_events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def active_approvals(self) -> tuple[PairApproval, ...]:
        return tuple(self._approved[key] for key in sorted(self._approved))

    def approve_pair(
        self, a: CanonicalTicketV1, b: CanonicalTicketV1,
        first: PairAnnotation, second: PairAnnotation,
        *, actor: str, operation_key: str,
    ) -> PairApproval:
        actor = self._required(actor, "actor")
        op = self._required(operation_key, "operation_key")
        pair = pair_identity(a, b)
        signature: tuple[object, ...] = (
            "approve", pair, first.model_dump_json(), second.model_dump_json(), actor,
        )
        previous = self._replay(op, signature)
        if previous is not None:
            assert isinstance(previous, PairApproval)
            return previous

        ak, bk = ticket_key(a), ticket_key(b)
        if ak not in self._tickets or bk not in self._tickets:
            raise ValueError("both tickets must be registered before approval")
        if self._tickets[ak] != a or self._tickets[bk] != b:
            raise ValueError("registered ticket identity conflict")
        if self._scopes[ak] != self._scopes[bk]:
            raise ValueError("cannot approve incident pairs across scope boundaries")
        if first.pair_id != pair or second.pair_id != pair:
            raise ValueError("pair identity does not match reviewed tickets")
        result = adjudicate_pair(first, second)
        if result.status != "confirmed" or result.label != "same_incident":
            raise ValueError("approval requires confirmed same_incident from independent human reviewers")

        approved = self._approved.get(pair)
        if approved is None:
            approved = PairApproval(
                pair_id=pair, ticket_keys=tuple(sorted((ak, bk))),
                reviewer_ids=result.reviewer_ids,
            )
            self._approved[pair] = approved
            self._event(
                "pair_approved", actor, op,
                (self._owners[ak], self._owners[bk]), (ak, bk),
            )
        self._operations[op] = (signature, approved)
        return approved
