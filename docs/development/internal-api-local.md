# Run ProductPulse's PostgreSQL + Internal FastAPI locally

**Status:** development/demo only. This is NOT an internet-facing, user-authenticated API.

Open-source dependencies: PostgreSQL 16, SQLAlchemy 2, psycopg 3, Alembic, FastAPI, Uvicorn, pytest. Reuse them instead of implementing ORM/transaction/migration frameworks.

## Start PostgreSQL (development-only password)

```bash
docker run -d --name productpulse-pg \
  -p 127.0.0.1:5432:5432 \
  -e POSTGRES_USER=productpulse \
  -e POSTGRES_PASSWORD=local_change_me \
  -e POSTGRES_DB=productpulse \
  postgres:16-alpine
```

## Install and migrate

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,storage,api]"
export DATABASE_URL="postgresql+psycopg://productpulse:local_change_me@127.0.0.1:5432/productpulse"
alembic upgrade head
alembic current --check-heads
```

## Run internal API

```bash
export PRODUCTPULSE_SCOPE_ID="local-demo"
export PRODUCTPULSE_INTERNAL_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(36))')"
python -m uvicorn productpulse.api.app:app_from_env \
    --factory --host 127.0.0.1 --port 8000
```

This token is printed nowhere by the service. The URL is localhost-only. Never commit the token to Git or expose :8000 directly to the public Internet. For actual deployments, provide env/secrets via a managed store and use a reverse proxy with TLS/mTLS and trusted human identity.

## Smoke check

In a **second terminal**, use the token available in the first terminal (or export the same token to both). Only synthetically generated, redacted input is safe for a public hackathon demo.

```bash
curl -sS http://127.0.0.1:8000/health/live
curl -sS -H "X-Internal-Token: $PRODUCTPULSE_INTERNAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_system":"demo","source_ticket_id":"RU-1","provenance_id":"synthetic","body_redacted":"Тест: вход в ERP возвращает HTTP 403"}' \
  http://127.0.0.1:8000/internal/v1/tickets
curl -sS -H "X-Internal-Token: $PRODUCTPULSE_INTERNAL_TOKEN" \
  http://127.0.0.1:8000/internal/v1/problems
curl -sS -H "X-Internal-Token: $PRODUCTPULSE_INTERNAL_TOKEN" \
  http://127.0.0.1:8000/internal/v1/audit
```

**Important:** commands with `$PRODUCTPULSE_INTERNAL_TOKEN` require a consistent env export in the caller shell. Avoid pasting secrets into CI logs or chat. The endpoint does not accept a client-supplied scope.

## Run tests with an actual PostgreSQL database

```bash
export PG_REGISTRY_TEST_URL="$DATABASE_URL"
python -m pytest -q
```

No `Base.metadata.create_all` shortcut is permitted. Alembic must manage table migrations.

## What the app does NOT do yet

- No human login, RBAC, per-user role, OIDC/SSO.
- No external write to Jira/ITSM, no public approval/merge/split endpoint.
- No raw tickets in GitHub. Caller must already redact PII/secrets.
- No agent output, trend detection, reviewer UI or Russian model performance proof.
- JSONB snapshot rewrites each tenant state on mutation; later scale-up should normalize tickets, problem memberships and pair links.
- `X-Internal-Token` is service-to-service auth only; do not give it to a browser client directly. A frontend needs a trusted BFF with real user authentication.
