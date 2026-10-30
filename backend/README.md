# Jjenga Code backend

FastAPI owns the LMS application rules and APIs. Supabase provides PostgreSQL only.

## Windows setup

Install Python 3.12, uv, and Node.js 24 LTS. From the repository root:

```powershell
Copy-Item backend\.env.example backend\.env
uv sync --project backend --frozen
uv run --project backend uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The copy is needed once; retain your existing `.env` on later setups. The setup script
in `scripts/setup-backend.ps1` does this without overwriting local configuration.

The Windows development command deliberately includes `--reload`. Uvicorn uses a
Selector event loop in reload mode, which is compatible with Psycopg's async driver.
The VS Code debugger uses the same mode and enables subprocess debugging. Validate
the event-loop choice again when defining production deployment commands.
References: https://uvicorn.dev/concepts/event-loop/ and
https://www.psycopg.org/psycopg3/docs/advanced/async.html

- API documentation: http://127.0.0.1:8000/api/docs
- Process health: http://127.0.0.1:8000/api/v1/health/live
- Database readiness: http://127.0.0.1:8000/api/v1/health/ready

Readiness returns HTTP 503 until database connectivity is configured. Liveness does
not claim that the database or LMS workflows are ready.

## Supabase database connection

Put your PostgreSQL connection URL in `LMS_DATABASE_URL` in `backend/.env`. Use the
session pooler for an IPv4 development environment, or a direct connection where IPv6
is available. Download the database CA certificate from your Supabase project and
set `LMS_DATABASE_SSLROOTCERT` to its local path. Connections verify the CA and hostname.
Encode special password characters in the URL. Never put this URL in Nuxt public
configuration. No Supabase JavaScript client, Auth, Storage, or Edge Functions are configured.

The probe executes only `SELECT 1`. It never creates tables or applies migrations.
Schema design, the runtime database role, RLS execution context, and real database
integration tests remain future work. Do not deploy application queries using a
privileged migration/owner account. A server connection does not automatically get
the identity represented by `auth.uid()`.

## Verification

```powershell
uv run --project backend ruff check backend
uv run --project backend ruff format --check backend
uv run --project backend pytest backend/tests
Push-Location backend
uv run mypy app
uv run lint-imports
Pop-Location
```

Feature folders reserve `domain`, `application`, `api`, and `infrastructure`
boundaries. They contain no implemented LMS use cases yet. Import-linter enforces
the initial dependency rules. Files are added when their responsibility is implemented.
