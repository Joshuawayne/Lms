# Verification strategy

Current backend tests cover process/database readiness separation, injected database
success/failure, RFC problem responses, CORS allowlisting, unexpected-error redaction,
secret masking, explicit origin validation and TLS connectivity configuration.
Current frontend unit tests check parsing and safe fallback for API problem responses.
The browser test checks the actual Nuxt-to-FastAPI connection.

```powershell
uv run --project backend --frozen ruff check backend scripts/export_openapi.py
uv run --project backend --frozen ruff format --check backend scripts/export_openapi.py
uv run --project backend --frozen pytest backend/tests
Push-Location backend
uv run --frozen mypy app
uv run --frozen lint-imports
Pop-Location
npm run contracts:check
npm run frontend:check
npm run frontend:build
npm run test:e2e
```

The browser test needs Playwright Chromium installed. VS Code recommendations include
Python/pytest support, Vitest, Playwright, Ruff, ESLint, Vue and SonarQube for IDE.
Install the recommended extensions through the VS Code Extensions panel.

As business features are implemented, add domain-rule unit tests, real database
integration/constraint/RLS/migration checks, resource contract checks, denied-access
cases and end-to-end role workflows. Add concurrency/retry/interruption/third-party
failure tests where the implemented behavior requires them. Validate accessibility,
mobile usability, teacher workload and the fairness/explainability of guidance.

Use synthetic test data. Do not reuse real learner records or credentials. An arbitrary
coverage percentage is not a substitute for checking meaningful behavior.
