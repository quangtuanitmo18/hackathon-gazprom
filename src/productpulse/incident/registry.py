"""In-memory, review-gated Problem Registry for a trusted, scoped backend.

No persistence or authenticating reviewer identities here; caller must validate
scope and actor via RBAC. No similarity-based auto merges or tracker writes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Literal

from pydantic import ValidationError

from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.insights.trends import ProblemTimeline
from productpulse.incident.annotation import (
    PairAnnotation, PairLabel, adjudicate_pair, pair_identity,
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
class ReviewProgress:
    pair_id: str
    status: Literal[
        "awaiting_first_review", "awaiting_second_review", "ready_for_lead",
        "disputed", "uncertain", "classified", "approved"
    ]
    reviewer_ids: tuple[str, ...] = ()


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
        self._reviews: dict[str, tuple[PairAnnotation, ...]] = {}
        self._revoked_at: dict[str, datetime] = {}
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

    def list_active(self) -> tuple[ProblemRecord, ...]:
        """Read-only active Problem snapshots for scoped dashboard queries."""
        return tuple(
            self._problems[pid] for pid in sorted(self._problems)
            if self._problems[pid].status == "active"
        )

    def candidate_inputs(self, *, corpus_cap: int = 500) -> tuple[tuple[str, CanonicalTicketV1, str], ...]:
        """All tickets of ONE already authenticated scope; never truncate silently.

        Registry instances are instantiated per tenant by the persistent adapter.
        Large tenants require a separate indexed retrieval service.
        """
        if len(self._tickets) > corpus_cap:
            raise ValueError("candidate indexing capacity exceeded")
        return tuple(
            (key, self._tickets[key], self._owners[key])
            for key in sorted(self._tickets)
        )

    def trend_inputs(self, *, corpus_cap: int = 5000) -> tuple[ProblemTimeline, ...]:
        """Read-only event times of EXPLICITLY grouped active Problems only.

        Do not infer grouped incidence from approved pair links or shared words.
        Snapshot stays within this registry's server-authenticated tenant scope.
        """
        if type(corpus_cap) is not int or corpus_cap < 1:
            raise ValueError("invalid trend corpus capacity")
        if len(self._tickets) > corpus_cap:
            raise ValueError("trend corpus capacity exceeded")
        return tuple(
            ProblemTimeline(
                problem_id=problem.problem_id,
                scope_id=problem.scope_id,
                revision=problem.revision,
                ticket_times=tuple(
                    (key, self._tickets[key].created_at)
                    for key in problem.ticket_keys
                ),
                source_systems=tuple(sorted({
                    self._tickets[key].source_system for key in problem.ticket_keys
                })),
                # NO inferred completeness. An audited per-source coverage
                # manifest is a separate future ingestion contract.
                coverage=(),
            )
            for problem in self.list_active()
            if len(problem.ticket_keys) >= 2
        )

    def list_review_tickets(self, *, limit: int = 50, offset: int = 0) -> tuple[tuple[str, CanonicalTicketV1], ...]:
        """Bounded read-only trusted reviewer input, not an incident verdict."""
        if not 1 <= limit <= 50 or offset < 0:
            raise ValueError("invalid review ticket page")
        keys = sorted(self._tickets)
        return tuple((key, self._tickets[key]) for key in keys[offset:offset + limit])

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
            if pair not in self._approved:
                raise ValueError("revoked approval cannot be replayed")
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
        revocation_time = self._revoked_at.get(pair)
        if revocation_time is not None and (
            first.reviewed_at <= revocation_time or second.reviewed_at <= revocation_time
        ):
            raise ValueError("fresh post-split human reviews required for revoked pair")
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



    def _review_progress(self, pair_id: str) -> ReviewProgress:
        reviews = self._reviews.get(pair_id, ())
        if pair_id in self._approved:
            status = "approved"
        elif not reviews:
            status = "awaiting_first_review"
        elif len(reviews) == 1:
            status = "awaiting_second_review"
        else:
            first, second = reviews
            if first.label == "uncertain" or second.label == "uncertain":
                status = "uncertain"
            elif first.label != second.label:
                status = "disputed"
            elif first.label == "same_incident":
                status = "ready_for_lead"
            else:
                status = "classified"
        return ReviewProgress(
            pair_id=pair_id, status=status,
            reviewer_ids=tuple(review.reviewer_id for review in reviews),
        )

    def review_statuses(self) -> tuple[ReviewProgress, ...]:
        """Only review metadata; no ticket contents or claims of gold accuracy."""
        return tuple(self._review_progress(pair) for pair in sorted(
            set(self._reviews) | set(self._revoked_at) | set(self._approved)
        ))

    def submit_review(
        self, a_key: str, b_key: str, *,
        reviewer_id: str, label: PairLabel, rationale: str, operation_key: str,
    ) -> ReviewProgress:
        """Record one human decision for a registered pair.

        reviewer_id MUST originate from a cryptographically validated OIDC
        access token in the API, not from an arbitrary HTTP request body.
        """
        reviewer_id = self._required(reviewer_id, "reviewer_id")
        operation_key = self._required(operation_key, "operation_key")
        if a_key not in self._tickets or b_key not in self._tickets:
            raise ValueError("both tickets must be registered")
        if self._scopes[a_key] != self._scopes[b_key]:
            raise ValueError("cannot review a pair across scope boundaries")
        pair = pair_identity(self._tickets[a_key], self._tickets[b_key])
        signature: tuple[object, ...] = (
            "review", pair, reviewer_id, label, rationale,
        )
        old = self._replay(operation_key, signature)
        if old is not None:
            if reviewer_id not in (x.reviewer_id for x in self._reviews.get(pair, ())):
                raise ValueError("revoked review cannot be replayed")
            assert isinstance(old, ReviewProgress)
            return old
        if pair in self._approved:
            raise ValueError("pair already approved; cannot submit further votes")
        existing = self._reviews.get(pair, ())
        if any(x.reviewer_id == reviewer_id for x in existing):
            raise ValueError("reviewer already reviewed this pair")
        if len(existing) >= 2:
            raise ValueError("pair already has two independent reviews")
        annotation = PairAnnotation(
            pair_id=pair, label=label, reviewer_id=reviewer_id,
            rationale=rationale, reviewed_at=datetime.now(timezone.utc),
        )
        revocation_time = self._revoked_at.get(pair)
        if revocation_time and annotation.reviewed_at <= revocation_time:
            raise ValueError("fresh post-split review required")
        self._reviews[pair] = (*existing, annotation)
        result = self._review_progress(pair)
        self._event("pair_review_submitted", reviewer_id, operation_key,
                    (self._owners[a_key], self._owners[b_key]),
                    tuple(sorted((a_key, b_key))))
        self._operations[operation_key] = (signature, result)
        return result

    def approve_reviewed_pair(
        self, a_key: str, b_key: str, *,
        actor: str, reason: str, operation_key: str,
    ) -> PairApproval:
        """Third-person approval; NEVER merges problems as a side effect."""
        actor = self._required(actor, "actor")
        reason = self._required(reason, "reason")
        operation_key = self._required(operation_key, "operation_key")
        if a_key not in self._tickets or b_key not in self._tickets:
            raise ValueError("both tickets must be registered")
        pair = pair_identity(self._tickets[a_key], self._tickets[b_key])
        signature: tuple[object, ...] = ("lead_review", pair, actor, reason)
        old = self._replay(operation_key, signature)
        if old is not None:
            if pair not in self._approved:
                raise ValueError("revoked approval cannot be replayed")
            assert isinstance(old, PairApproval)
            return old
        if self._review_progress(pair).status != "ready_for_lead":
            raise ValueError("pair must be ready_for_lead to approve")
        first, second = self._reviews[pair]
        if actor in (first.reviewer_id, second.reviewer_id):
            raise ValueError("third independent reviewer lead is required")
        result = self.approve_pair(
            self._tickets[a_key], self._tickets[b_key],
            first, second, actor=actor,
            operation_key="lead-approval:" + operation_key,
        )
        self._event("pair_review_lead_approved", actor, operation_key,
                    (self._owners[a_key], self._owners[b_key]),
                    tuple(sorted((a_key, b_key))), reason)
        self._operations[operation_key] = (signature, result)
        return result

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


    def split(
        self, problem_id: str, partitions: tuple[tuple[str, ...], ...] | list[tuple[str, ...]],
        *, actor: str, reason: str, operation_key: str,
        expected_revision: int,
    ) -> tuple[ProblemRecord, ...]:
        """Correct a merge with explicit partitions and revoke obsolete approvals.

        Only active membership changes. Prior approvals remain in audit events,
        not in the set authorizing new merges. No persistent/automatic undo.
        """
        actor = self._required(actor, "actor")
        reason = self._required(reason, "reason")
        op = self._required(operation_key, "operation_key")
        parts = tuple(tuple(p) for p in partitions)
        signature: tuple[object, ...] = (
            "split", problem_id, parts, actor, reason, expected_revision,
        )
        previous = self._replay(op, signature)
        if previous is not None:
            assert isinstance(previous, tuple)
            return previous

        original = self.get_problem(problem_id)
        if original.status != "active":
            raise ValueError("cannot split non-active problem")
        if original.revision != expected_revision:
            raise ValueError("stale revision; reload before split")
        if len(parts) < 2 or any(not part for part in parts):
            raise ValueError("partitions must include at least two nonempty groups")
        flat = tuple(key for part in parts for key in part)
        if len(flat) != len(set(flat)) or set(flat) != set(original.ticket_keys):
            raise ValueError("partitions must exactly cover each member once")

        groups = {key: i for i, part in enumerate(parts) for key in part}
        to_revoke = tuple(sorted(
            pid for pid, approval in self._approved.items()
            if all(key in groups for key in approval.ticket_keys)
            and groups[approval.ticket_keys[0]] != groups[approval.ticket_keys[1]]
        ))

        # Validation complete. Every mutation below is local to one process.
        main = ProblemRecord(
            problem_id=problem_id, scope_id=original.scope_id,
            ticket_keys=tuple(sorted(parts[0])), revision=original.revision + 1,
        )
        new_records = [
            ProblemRecord(
                problem_id=self._new_id(), scope_id=original.scope_id,
                ticket_keys=tuple(sorted(part)), parent_id=problem_id,
            )
            for part in parts[1:]
        ]
        records = (main, *new_records)
        for record in records:
            self._problems[record.problem_id] = record
            for key in record.ticket_keys:
                self._owners[key] = record.problem_id
        revocation_time = datetime.now(timezone.utc)
        for pair in to_revoke:
            self._approved.pop(pair)
            self._reviews.pop(pair, None)
            self._revoked_at[pair] = revocation_time

        self._event(
            "problem_split", actor, op,
            tuple(record.problem_id for record in records),
            tuple(sorted(flat)), reason, to_revoke,
        )
        self._operations[op] = (signature, records)
        return records


    def to_state(self) -> dict:
        """Versioned, JSON-only domain snapshot. Never use pickle or eval."""
        def pack_operation(value: object) -> dict:
            if isinstance(value, ProblemRecord):
                return {"kind": "problem", "value": asdict(value)}
            if isinstance(value, PairApproval):
                return {"kind": "approval", "value": asdict(value)}
            if isinstance(value, ReviewProgress):
                return {"kind": "review_progress", "value": asdict(value)}
            if isinstance(value, tuple) and all(isinstance(v, ProblemRecord) for v in value):
                return {"kind": "problems", "value": [asdict(v) for v in value]}
            raise TypeError("unsupported domain operation result")

        return {
            "version": 1,
            "tickets": {key: value.model_dump(mode="json") for key, value in self._tickets.items()},
            "scopes": dict(self._scopes),
            "owners": dict(self._owners),
            "problems": {key: asdict(value) for key, value in self._problems.items()},
            "approved": {key: asdict(value) for key, value in self._approved.items()},
            "reviews": {key: [review.model_dump(mode="json") for review in values]
                        for key, values in self._reviews.items()},
            "revoked_at": {key: value.isoformat() for key, value in self._revoked_at.items()},
            "events": [dict(asdict(event), at=event.at.isoformat()) for event in self._events],
            "operations": {
                key: {"signature": signature, "result": pack_operation(result)}
                for key, (signature, result) in self._operations.items()
            },
            "sequence": self._sequence,
        }

    @classmethod
    def from_state(cls, payload: dict) -> "ProblemRegistry":
        """Fail closed on unsupported versions and malformed/cross-referenced state."""
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise ValueError("unsupported or missing registry snapshot version")
        required = (
            "tickets", "scopes", "owners", "problems", "approved",
            "revoked_at", "events", "operations", "sequence",
        )
        if any(name not in payload for name in required):
            raise ValueError("incomplete registry snapshot")
        if not all(isinstance(payload[name], dict) for name in required[:-1] if name != "events"):
            raise ValueError("invalid snapshot map types")
        if not isinstance(payload["events"], list) or type(payload["sequence"]) is not int:
            raise ValueError("invalid registry event list or sequence")
        reg = cls()
        def restore_problem(v):
            return ProblemRecord(
                problem_id=v["problem_id"], scope_id=v["scope_id"],
                ticket_keys=tuple(v["ticket_keys"]),
                revision=v["revision"], status=v["status"],
                merged_into=v.get("merged_into"), parent_id=v.get("parent_id"),
            )
        def restore_approval(v):
            return PairApproval(pair_id=v["pair_id"], ticket_keys=tuple(v["ticket_keys"]),
                                reviewer_ids=tuple(v["reviewer_ids"]))
        def nested_tuple(v):
            return tuple(nested_tuple(x) for x in v) if isinstance(v, (list, tuple)) else v

        reg._tickets = {key: CanonicalTicketV1.model_validate(v)
                        for key, v in payload["tickets"].items()}
        reg._scopes = dict(payload["scopes"])
        reg._owners = dict(payload["owners"])
        reg._problems = {key: restore_problem(v) for key, v in payload["problems"].items()}
        reg._approved = {key: restore_approval(v) for key, v in payload["approved"].items()}
        if not isinstance(payload.get("reviews", {}), dict):
            raise ValueError("invalid reviews snapshot mapping")
        reg._reviews = {key: tuple(PairAnnotation.model_validate(x) for x in values)
                        for key, values in payload.get("reviews", {}).items()}
        reg._revoked_at = {key: datetime.fromisoformat(value)
                           for key, value in payload["revoked_at"].items()}
        reg._events = [
            AuditEvent(
                kind=e["kind"], actor=e["actor"], operation_key=e["operation_key"],
                at=datetime.fromisoformat(e["at"]), problem_ids=tuple(e["problem_ids"]),
                ticket_keys=tuple(e["ticket_keys"]), reason=e["reason"],
                revoked_pair_ids=tuple(e["revoked_pair_ids"]),
            ) for e in payload["events"]
        ]
        for key, rec in payload["operations"].items():
            data = rec["result"]
            kind = data["kind"]
            if kind == "problem":
                result = restore_problem(data["value"])
            elif kind == "approval":
                result = restore_approval(data["value"])
            elif kind == "review_progress":
                v = data["value"]
                result = ReviewProgress(pair_id=v["pair_id"],status=v["status"],
                                        reviewer_ids=tuple(v["reviewer_ids"]))
            elif kind == "problems":
                result = tuple(restore_problem(p) for p in data["value"])
            else:
                raise ValueError(f"unknown operation result kind: {kind}")
            reg._operations[key] = (nested_tuple(rec["signature"]), result)
        reg._sequence = payload["sequence"]

        # No snapshot may rebind a ticket to a different scope, retired
        # problem, or mismatched source identity without detection.
        keys = set(reg._tickets)
        if any(ticket_key(ticket) != key for key, ticket in reg._tickets.items()):
            raise ValueError("snapshot contains mismatched ticket identity")
        if set(reg._scopes) != keys or set(reg._owners) != keys:
            raise ValueError("snapshot missing ticket scope or owner")
        for key, pid in reg._owners.items():
            problem = reg._problems.get(pid)
            if (problem is None or problem.status != "active"
                    or key not in problem.ticket_keys
                    or reg._scopes[key] != problem.scope_id):
                raise ValueError("snapshot contains invalid active ticket ownership")
        for pid, problem in reg._problems.items():
            if pid != problem.problem_id or any(
                reg._owners.get(key) != pid for key in problem.ticket_keys
            ):
                raise ValueError("snapshot contains invalid Problem membership")
        if any(any(key not in keys for key in ap.ticket_keys)
               for ap in reg._approved.values()):
            raise ValueError("snapshot contains unknown ticket approval")
        for pair, reviews in reg._reviews.items():
            if len(reviews) > 2 or len(set(x.reviewer_id for x in reviews)) != len(reviews):
                raise ValueError("invalid independent reviews in snapshot")
            if any(x.pair_id != pair for x in reviews):
                raise ValueError("invalid pair identity in review snapshot")
            if pair in reg._revoked_at and any(
                x.reviewed_at <= reg._revoked_at[pair] for x in reviews
            ):
                raise ValueError("revoked old reviews in snapshot")
        if any(value.tzinfo is None or value.utcoffset() is None
               for value in reg._revoked_at.values()):
            raise ValueError("snapshot contains naive revocation timestamp")
        return reg
