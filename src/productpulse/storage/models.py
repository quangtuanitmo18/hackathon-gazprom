"""SQLAlchemy 2 mapped rows; migrations applied with Alembic, not create_all."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RegistryStateRow(Base):
    __tablename__ = "registry_states"

    scope_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    audit_seq: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    state: Mapped[dict] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


class RegistryEventRow(Base):
    __tablename__ = "registry_events"
    __table_args__ = (UniqueConstraint("scope_id", "seq", name="uq_registry_event_scope_seq"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    scope_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("registry_states.scope_id", ondelete="RESTRICT"), nullable=False,
        index=True,
    )
    seq: Mapped[int] = mapped_column(BigInteger, nullable=False)
    kind: Mapped[str] = mapped_column(String(60), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    operation_key: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
