# Setup verification — 27 October 2026

Verified in the development environment using Python 3.12.14 and Node.js 24.22.1.

| Check | Result |
| --- | --- |
| Backend pytest | 13 passed |
| Backend Ruff lint and formatting | Passed |
| Backend strict mypy | Passed |
| Backend import boundaries | 2 contracts kept |
| FastAPI OpenAPI snapshot | Matched |
| Generated frontend API types | Matched |
| Frontend ESLint | Passed |
| Nuxt type checking | Passed |
| Frontend Vitest | 4 passed |
| Production Nuxt build | Passed |
| Production frontend HTTP and 16 assets | Served successfully |
| API liveness and CORS over HTTP | Passed |
| Unconfigured database readiness | Correctly returned 503 problem details |
| npm audit: root tooling and frontend | Zero reported findings at setup |

The frontend lockfile resolves esbuild to the patched 0.28.2 version. The frontend
and root tooling use independent dependency roots; see the architecture decisions.

The browser test is configured but was not run because this environment could not
download Playwright Chromium. Windows PowerShell scripts and native Windows runtime
behavior have not been executed here. Run the included checks on the target PC.
No real Supabase credentials were supplied, no live database connection was verified,
and no SQL migrations were applied. LMS business workflows remain future work.
