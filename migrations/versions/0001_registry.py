"""Create registry states and scoped append-only audit.

Revision ID: 0001_registry
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision="0001_registry"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "registry_states",
        sa.Column("scope_id",sa.String(length=128),primary_key=True),
        sa.Column("revision",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("audit_seq",sa.BigInteger(),nullable=False,server_default="0"),
        sa.Column("state",JSONB(),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
    )
    op.create_table(
        "registry_events",
        sa.Column("id",sa.BigInteger(),sa.Identity(),primary_key=True),
        sa.Column("scope_id",sa.String(length=128),
                  sa.ForeignKey("registry_states.scope_id",ondelete="RESTRICT"),nullable=False),
        sa.Column("seq",sa.BigInteger(),nullable=False),
        sa.Column("kind",sa.String(length=60),nullable=False),
        sa.Column("actor",sa.String(length=128),nullable=False),
        sa.Column("operation_key",sa.Text(),nullable=False),
        sa.Column("occurred_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("payload",JSONB(),nullable=False),
        sa.UniqueConstraint("scope_id","seq",name="uq_registry_event_scope_seq"),
    )
    op.create_index("ix_registry_events_scope_id","registry_events",["scope_id"])

def downgrade():
    op.drop_index("ix_registry_events_scope_id",table_name="registry_events")
    op.drop_table("registry_events")
    op.drop_table("registry_states")
