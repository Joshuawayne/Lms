# Jjenga Code Learning Management System

Initial development foundation: Nuxt/Vue with Nuxt UI and Pinia, FastAPI for internal
APIs and application rules, and Supabase PostgreSQL for the database.

## 1. Extract the project

Extract the archive so this README is at `C:\LearningManagementSystem\README.md`.
The archive contains one `LearningManagementSystem` folder. Keep existing project
work separately if that directory already contains files.

Install Node.js 24 LTS (24.15 or newer) and uv. The backend selects Python 3.12;
uv can obtain it if it is missing. Open the project root in VS Code.

- Node: https://nodejs.org/
- uv: https://docs.astral.sh/uv/getting-started/installation/

## 2. Set up the backend first

In PowerShell:

```powershell
Set-Location C:\LearningManagementSystem
.\scripts\setup-backend.ps1
```

Or use the underlying commands directly:

```powershell
uv sync --project backend --frozen
```

The optional environment file is created by the script. To create it manually,
copy `backend/.env.example` to `backend/.env` once, retaining any existing settings.

## 3. Set up the frontend

```powershell
.\scripts\setup-frontend.ps1
```

Equivalent dependency and preparation commands:

```powershell
npm ci
npm ci --prefix frontend
npm run postinstall --prefix frontend
npm run contracts:check
```

The root npm package owns shared tooling and its `package-lock.json`. The frontend
owns application dependencies and `frontend/package-lock.json`. Setup installs both
from their lockfiles. Python packages are isolated in `backend/.venv` and locked in
`backend/uv.lock`. Dependency directories are excluded from the download.

## 4. Start both applications

Terminal one, from the project root:

```powershell
npm run backend:dev
```

Terminal two, also from the project root:

```powershell
npm run frontend:dev
```

- Frontend: http://127.0.0.1:3000
- FastAPI documentation: http://127.0.0.1:8000/api/docs
- API liveness: http://127.0.0.1:8000/api/v1/health/live
- Database readiness: http://127.0.0.1:8000/api/v1/health/ready

Click **Check backend** on the frontend. A successful check confirms browser-to-API
connectivity. Database readiness returns 503 until credentials and TLS verification
are configured; see `backend/README.md`. No database changes run during setup.

## 5. Verification

Run `.\scripts\check.ps1` to check backend linting, formatting, types, dependency
boundaries and tests, then API contracts, frontend linting, types, tests and build.
The individual commands are documented in `docs/testing/strategy.md`.

The browser connection check is available separately:

```powershell
npx playwright install chromium
npm run test:e2e
```

## Current implementation boundary

Implemented: framework startup, health/readiness checks, safe problem responses,
request IDs, explicit local CORS origins, a PostgreSQL connectivity adapter,
OpenAPI export and generated frontend types, Pinia registration, Nuxt UI, testing
and linting configuration, VS Code recommendations, and the connectivity page.

The agreed business-feature directories are reserved. Future route, domain and
service files are created as those features are implemented, rather than making
empty application files. Authentication, authorization, enrolments, lessons,
the activity builder, assessments, growth guidance, reports and integrations
still require implementation. Authentication, private file storage, durable
job delivery and production hosting providers remain undecided.

Supabase is used as PostgreSQL. Database schema migrations will live only in
`supabase/migrations`; the application must not automatically create its schema.
The database connection URL belongs exclusively in the backend environment.

See `FILE_STRUCTURE.txt` for the actual scaffold, and `docs/product` for the
requirements and system algorithm preserved from our discussion.
