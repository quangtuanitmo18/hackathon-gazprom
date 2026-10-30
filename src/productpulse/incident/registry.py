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


    def merge(
        self, primary_id: str, secondary_id: str,
        *, actor: str, reason: str, operation_key: str,
        expected_primary_revision: int, expected_secondary_revision: int,
    ) -> ProblemRecord:
        """Explicit complete-link approved merge; rejects unsafe transitive chains."""
        actor = self._required(actor, "actor")
        reason = self._required(reason, "reason")
        op = self._required(operation_key, "operation_key")
        signature: tuple[object, ...] = (
            "merge", primary_id, secondary_id, actor, reason,
            expected_primary_revision, expected_secondary_revision,
        )
        replay = self._replay(op, signature)
        if replay is not None:
            assert isinstance(replay, ProblemRecord)
            return replay
        if primary_id == secondary_id:
            raise ValueError("merge requires distinct problems")
        primary, secondary = self.get_problem(primary_id), self.get_problem(secondary_id)
        if primary.status != "active" or secondary.status != "active":
            raise ValueError("cannot merge a non-active problem")
        if primary.scope_id != secondary.scope_id:
            raise ValueError("cannot merge across scope boundaries")
        if (
            primary.revision != expected_primary_revision
            or secondary.revision != expected_secondary_revision
        ):
            raise ValueError("stale revision; reload before merging")
        missing = [
            pair_identity(self._tickets[a], self._tickets[b])
            for a in primary.ticket_keys for b in secondary.ticket_keys
            if pair_identity(self._tickets[a], self._tickets[b]) not in self._approved
        ]
        if missing:
            raise ValueError(
                f"all approved cross-pair evidence required before merge; missing {len(missing)} link(s)"
            )

        all_members = tuple(sorted(primary.ticket_keys + secondary.ticket_keys))
        merged = ProblemRecord(
            problem_id=primary_id, scope_id=primary.scope_id,
            ticket_keys=all_members, revision=primary.revision + 1,
        )
        retired = ProblemRecord(
            problem_id=secondary_id, scope_id=secondary.scope_id,
            ticket_keys=(), revision=secondary.revision + 1,
            status="merged", merged_into=primary_id,
        )
        # No state mutation occurs before every validation above succeeds.
        self._problems[primary_id] = merged
        self._problems[secondary_id] = retired
        for key in secondary.ticket_keys:
            self._owners[key] = primary_id
        self._event(
            "problems_merged", actor, op, (primary_id, secondary_id),
            all_members, reason,
        )
        self._operations[op] = (signature, merged)
        return merged
