"""Transactional PostgreSQL adapter over the existing reviewed domain rules.

One JSONB snapshot row per scope, serialized by SELECT FOR UPDATE; adequate
for hackathon demos, not large multi-tenant analytics at production scale.
This module is NOT an authorization boundary. Never call it with arbitrary
scope or reviewer identity from untrusted user input.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Callable, TypeVar

from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from productpulse.incident.registry import ProblemRegistry
from productpulse.storage.models import RegistryEventRow, RegistryStateRow

T = TypeVar("T")


def _scope(scope_id: str) -> str:
    if not isinstance(scope_id, str) or not scope_id.strip() or len(scope_id.strip()) > 128:
        raise ValueError("scope_id must be nonempty and <= 128 characters")
    return scope_id.strip()


class PersistentProblemRegistry:
    def __init__(self, engine: Engine):
        if engine.dialect.name != "postgresql":
            raise ValueError("PersistentProblemRegistry requires PostgreSQL FOR UPDATE + JSONB")
        self.engine = engine
        self._sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def read(self, scope_id: str, callback: Callable[[ProblemRegistry], T]) -> T:
        """Read-only callback. Side effects in external services are forbidden."""
        scope_id = _scope(scope_id)
        with self._sessions() as db, db.begin():
            row = db.get(RegistryStateRow, scope_id)
            registry = ProblemRegistry.from_state(row.state) if row else ProblemRegistry()
            previous = registry.to_state()
            result = callback(registry)
            if registry.to_state() != previous:
                raise ValueError("read-only callback attempted registry mutation")
            return result

    def transact(self, scope_id: str, callback: Callable[[ProblemRegistry], T]) -> T:
        """Run one domain mutation and its new audit events in one DB transaction.

        PostgreSQL INSERT ON CONFLICT followed by row-level FOR UPDATE
        also serializes concurrent first writes to a previously absent scope.
        The result value is returned only after successful database commit.
        """
        scope_id = _scope(scope_id)
        with self._sessions() as db, db.begin():
            stmt = insert(RegistryStateRow).values(
                scope_id=scope_id,
                state=ProblemRegistry().to_state(),
                revision=0,
                audit_seq=0,
            ).on_conflict_do_nothing(index_elements=[RegistryStateRow.scope_id])
            db.execute(stmt)

            row = db.scalar(
                select(RegistryStateRow)
                .where(RegistryStateRow.scope_id == scope_id)
                .with_for_update()
            )
            if row is None:
                raise RuntimeError("registry row disappeared during transaction")

            registry = ProblemRegistry.from_state(row.state)
            before_state = registry.to_state()
            before_events = registry.audit_events()
            if row.audit_seq != len(before_events):
                raise ValueError("registry audit divergence; refuse write")
            result = callback(registry)
            after_events = registry.audit_events()
            if after_events[:len(before_events)] != before_events:
                raise ValueError("historical audit events must never change")

            after_state = registry.to_state()
            if any(s != scope_id for s in after_state["scopes"].values()):
                raise ValueError("registry operation crossed scope boundaries")
            if any(p["scope_id"] != scope_id for p in after_state["problems"].values()):
                raise ValueError("registry Problem scoped outside trusted transaction")

            if after_state != before_state:
                row.state = after_state
                row.revision += 1
                row.updated_at = datetime.now(timezone.utc)

            new_events = after_events[len(before_events):]
            for index, event in enumerate(new_events, start=row.audit_seq + 1):
                db.add(RegistryEventRow(
                    scope_id=scope_id,
                    seq=index,
                    kind=event.kind,
                    actor=event.actor,
                    operation_key=event.operation_key,
                    occurred_at=event.at,
                    payload={
                        "problem_ids": list(event.problem_ids),
                        "ticket_keys": list(event.ticket_keys),
                        "reason": event.reason,
                        "revoked_pair_ids": list(event.revoked_pair_ids),
                    },
                ))
            row.audit_seq += len(new_events)
            return result

    def audit(self, scope_id: str) -> tuple[dict, ...]:
        """Read persisted audit rows in scope order; never expose raw ticket text."""
        scope_id = _scope(scope_id)
        with self._sessions() as db, db.begin():
            events = db.scalars(
                select(RegistryEventRow)
                .where(RegistryEventRow.scope_id == scope_id)
                .order_by(RegistryEventRow.seq.asc())
            ).all()
            return tuple(
                {
                    "scope_id": scope_id,
                    "sequence": e.seq,
                    "kind": e.kind,
                    "actor": e.actor,
                    "operation_key": e.operation_key,
                    "occurred_at": e.occurred_at.isoformat(),
                    **e.payload,
                }
                for e in events
            )
