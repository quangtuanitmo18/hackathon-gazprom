"""Alembic environment; URL from env; no credentials in repo."""
import os
from alembic import context
from sqlalchemy import create_engine, pool
from productpulse.storage.models import Base

config = context.config
target_metadata = Base.metadata
url = os.getenv("DATABASE_URL") or os.getenv("PG_REGISTRY_TEST_URL")
if not url:
    raise RuntimeError("DATABASE_URL or PG_REGISTRY_TEST_URL required")

def offline():
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle":"named"})
    with context.begin_transaction():
        context.run_migrations()

def online():
    engine=create_engine(url,poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()

if context.is_offline_mode():
    offline()
else:
    online()
