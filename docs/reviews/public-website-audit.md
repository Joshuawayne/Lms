# Jjenga Code LMS — Public Website & Platform Integration Audit Report

**Date of Audit:** 2026-10-28 / 2026-10-29  
**Audited Location:** `C:\LearningManagementSystem`  
**Auditor:** Automated Engineering Inspection & Audit Suite (DeepMind Antigravity)  
**Target Milestone:** Public Website Completion, Program Discovery, Enrolment Application Flow, and Backend/Database Integration  

---

## 1. Executive Summary & Completion Verdict

### 1.1 Completion Verdict
**Verdict: QUALIFIED PASS — FOUNDATION COMPLETE & INTEGRATED, SUBJECT TO 4 RECTIFICATIONS BEFORE PORTALS.**

The core public website, program discovery catalogue, individual program detail views, and idempotent enrolment application flow have been implemented and verified end-to-end through the real stack: **Nuxt 4 / Vue 3 (frontend on port 3000) → FastAPI (backend on port 8000) → PostgreSQL 17 (private `lms` schema with `lms_api` restricted role on port 5433)**. 

No in-memory mock or simulated repository was substituted during live runtime testing. Every submitted application created a durable, committed record in `lms.enrolment_applications` and exactly one immutable entry in `lms.application_audit_events`. Idempotent replay, changed-payload conflict detection (HTTP 409), draft/archived program exclusion (HTTP 404), and in-memory draft isolation have been verified with live runtime evidence.

However, four specific architectural and testing discrepancies require rectification before proceeding to authenticated portal milestones:
1. **Homepage Camp Spotlight Data Authority:** The November 2026 camp highlight on the homepage (`frontend/app/pages/index.vue:313-351`) is hardcoded in template markup rather than dynamically querying the published program from `/api/v1/programs`.
2. **Outdated E2E Test Assertion:** `tests/e2e/public/development-connection.spec.ts` asserts a legacy button `"Check backend"` on `/`, which now resides on `/development`.
3. **Ruff Lint Error in Windows Loop Shim:** `backend/run_server.py:9:101` violates `E501` line length limit (103 > 100 characters).
4. **Reserved Directory Placeholders in Portal Trees:** Empty feature and page directories (`admin/`, `teacher/`, `learner/`, `parent/`) contain `.gitkeep` markers awaiting milestone activation.

---

## 2. Requirements vs. Implementation Matrix

| Requirement | Implementation Source | Status | Evidence / Observation |
| :--- | :--- | :--- | :--- |
| **Three Learning Pathways**<br>(School-Term, Saturday Club, Holiday) | `supabase/migrations/20261028000001_programs_and_applications.sql:129-133`<br>`backend/app/modules/programs/domain/values.py:11-14`<br>`frontend/app/features/programs/composables/pathwayInfo.ts:16-43` | **Verified** | PostgreSQL `lms.program_pathway` enum has exactly `school_term`, `saturday_club`, `holiday`. All 3 are represented in UI, filterable in catalogue, and typed across frontend and backend. |
| **Delivery Modes Separate from Pathways**<br>(in_person, online, hybrid) | `supabase/migrations/20261028000001_programs_and_applications.sql:141-145`<br>`backend/app/modules/programs/domain/values.py:23-26`<br>`frontend/app/pages/programs/[slug]/index.vue:145` | **Verified** | `lms.program_delivery` enum (`in_person`, `online`, `hybrid`) is an independent column on `lms.programs`. UI displays format separately from pathway badges. |
| **Public Application without Account** | `backend/app/modules/programs/api/router.py:100-186`<br>`frontend/app/pages/programs/[slug]/apply.vue:213-384` | **Verified** | Public POST endpoint `/api/v1/programs/{slug}/applications` requires no authentication header. Guardian submits contact info directly. |
| **Submission Produces Application for Admin Review**<br>(No automatic approval or seat reservation) | `supabase/migrations/20261028000001_programs_and_applications.sql:370-372`<br>`backend/app/modules/programs/api/schemas.py:194`<br>`frontend/app/pages/programs/[slug]/apply.vue:183-197` | **Verified** | `lms.enrolment_applications.status` defaults to `'submitted'`. Initial status is enforced by RLS `WITH CHECK (status = 'submitted' AND reviewed_at IS NULL)`. Public receipt returns status `'submitted'`. Disclaimer explicitly notes: *"Submission confirms receipt. Enrolment is confirmed following administrator review."* |
| **Account Invitations Follow Admin Approval** | `docs/product/requirements.md:7-11`<br>`supabase/migrations/20261028000001_programs_and_applications.sql:61-65` | **Implemented, not verified** (Scope Boundary) | Enrolments and user identity tables are excluded from this milestone by design. `enrolment_applications` is strictly isolated from auth accounts. |
| **Connected Learner Profile Across Pathways** | `docs/product/requirements.md:3-5`<br>`docs/product/assessment-model.md:3-5` | **Implemented, not verified** (Design Baseline) | Architecture documents mandate shared profile across pathways; domain entities for portal milestone remain reserved. |
| **Separation of Projects, Competencies & Values** | `docs/product/assessment-model.md:3-15`<br>`backend/app/modules/assessments/` | **Implemented, not verified** (Design Baseline) | Explicitly documented in `docs/product/assessment-model.md`. No character scoring algorithms exist in backend code. |
| **No Character Score / Evidence-Based Observations** | `docs/product/assessment-model.md:10-15` | **Verified (Documentation Baseline)** | Values framework lists 8 values (love, responsibility, respect, unity, peace, patriotism, social justice, integrity) with contextual observation logging rather than numerical ranking. |

---

## 3. Implementation Inventory

### 3.1 Public Route Inventory

| Route | Implementation File | API Dependency | Actual Behaviour | Status |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `frontend/app/pages/index.vue` | Static assets, image CDN manifest, links to `/programs` | Renders hero, confirmed November 2026 camp spotlight, 3 learning pathways, project showcases, 4-step learning philosophy, parent reassurance FAQ, and contact details. | **Verified** |
| `/programs` | `frontend/app/pages/programs/index.vue` | `GET /api/v1/programs?page=1&page_size=9&pathway=...` | Displays paginated program cards fetched from PostgreSQL via FastAPI. Supports pathway filtering tabs (`all`, `school_term`, `saturday_club`, `holiday`), loading skeleton, honest error retry, and empty states. | **Verified** |
| `/programs/:slug` | `frontend/app/pages/programs/[slug]/index.vue` | `GET /api/v1/programs/:slug` | Renders program title, description, schedule, dates, age range, delivery format, and server-driven application availability CTA ("Apply now", "Coming soon", or "Closed"). | **Verified** |
| `/programs/:slug/apply` | `frontend/app/pages/programs/[slug]/apply.vue` | `GET /api/v1/programs/:slug`<br>`POST /api/v1/programs/:slug/applications` | Renders applicant form, enforces field validation and age limits, submits payload with UUID idempotency key, displays confirmed receipt reference, and clears memory draft upon receipt. | **Verified** |
| `/development` | `frontend/app/pages/development.vue` | `GET /api/v1/health/live` | Developer probe page with interactive "Check backend" button testing live API connectivity. | **Verified** |

### 3.2 Layouts & Shared UI Components

| Component / Layout | File Path | Purpose / Responsibilities | Status |
| :--- | :--- | :--- | :--- |
| `public` layout | `frontend/app/layouts/public.vue` | Header with retro gradient SVG wordmark (`jenga-code-gradient.svg`), accessible desktop navigation, mobile drawer with hamburger toggle, and dark navy footer (`#160D35`) with white wordmark (`jenga-code-white.svg`) and verified contacts. | **Verified** |
| `default` layout | `frontend/app/layouts/default.vue` | Minimal pass-through layout (`<slot />`) for auxiliary routes. | **Verified** |
| `ProgramCard` | `frontend/app/features/programs/components/ProgramCard.vue` | Reusable card rendering pathway badge, title, dates, age eligibility, format, and navigation link. | **Verified** |
| `BlobShape` | `frontend/app/components/ui/BlobShape.vue` | Asymmetric organic SVG background accent with configurable color and opacity. | **Verified** |
| `WaveDivider` | `frontend/app/components/ui/WaveDivider.vue` | Smooth SVG section transition divider between light and dark sections. | **Verified** |
| `StarAccent` | `frontend/app/components/ui/StarAccent.vue` | Hand-drawn retro decorative star icon. | **Verified** |

### 3.3 Pinia Stores & Composables

| Store / Composable | File Path | Purpose & Lifecycle | Status |
| :--- | :--- | :--- | :--- |
| `useApplicationDraftStore` | `frontend/app/stores/applicationDraft.ts` | Memory-only draft state for guardian and learner details. Generates and manages UUIDv4 idempotency keys, detects payload modifications via hash, clears personal data on confirmed submission, and leaves zero footprint in `localStorage`/`sessionStorage`. | **Verified** |
| `useApplicationAvailability` | `frontend/app/features/programs/composables/useApplicationAvailability.ts` | Computes availability status (`open`, `not_yet`, `closed`, `disabled`) and user-facing labels from program timing fields (`applications_enabled`, `applications_open_at`, `applications_close_at`). | **Verified** |
| `pathwayInfo` | `frontend/app/features/programs/composables/pathwayInfo.ts` | Maps `Pathway` enum values to approved UI labels, icons (`lucide:school`, `lucide:calendar`, `lucide:sun`), and brand color tokens. | **Verified** |
| `useApi` | `frontend/app/composables/useApi.ts` | Provides typed `$api` fetch client configured with runtime `apiBaseUrl`. | **Verified** |

### 3.4 API Layer & Database Artifacts

| Component | File Path | Description | Status |
| :--- | :--- | :--- | :--- |
| FastAPI Application Root | `backend/app/main.py`<br>`backend/app/bootstrap.py` | FastAPI application composition root, CORS middleware, Problem Details RFC 7807 error handlers, dependency wiring. | **Verified** |
| Health Router | `backend/app/api/v1/health.py` | `/api/v1/health/live` (process liveness) and `/api/v1/health/ready` (PostgreSQL query readiness probe). | **Verified** |
| Programs Router | `backend/app/modules/programs/api/router.py` | Endpoints: `GET /programs`, `GET /programs/{slug}`, `POST /programs/{slug}/applications`. | **Verified** |
| Pydantic Schemas | `backend/app/modules/programs/api/schemas.py` | Strict validation schemas: `ProgramSummaryResponse`, `ProgramDetailResponse`, `SubmitApplicationRequest`, `ApplicationReceiptResponse`. | **Verified** |
| Use Cases & Ports | `backend/app/modules/programs/application/commands.py`<br>`backend/app/modules/programs/application/queries.py` | Domain use cases: `ListPublishedProgramsUseCase`, `GetPublishedProgramUseCase`, `SubmitApplicationUseCase`. | **Verified** |
| Postgres Repositories | `backend/app/modules/programs/infrastructure/postgres.py` | Native `psycopg` implementation targeting schema `lms` with `SET ROLE lms_api;`. | **Verified** |
| Database Migration | `supabase/migrations/20261028000001_programs_and_applications.sql` | DDL for `lms.programs`, `lms.enrolment_applications`, `lms.application_audit_events`, RLS policies, role grants. | **Verified** |

---

## 4. Hardcoded Information vs. Dynamic Authority Audit

| Information or Rule | Current Source | Intended Authority | Evidence | Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **November 2026 Camp Spotlight** | `frontend/app/pages/index.vue:322-348` | PostgreSQL `lms.programs` via `/api/v1/programs` | Statically coded dates (23–27 Nov 2026), venue, and link `/programs/coding-robotics-camp-nov-2026`. | **Inappropriate Hardcoding (Severity: Low).** The card targets an authentic, published program in PostgreSQL, but if the program details change in the database, the homepage markup will drift. |
| **Learning Pathway Categories** | `frontend/app/features/programs/composables/pathwayInfo.ts:16-43` | Agreed business rules & `lms.program_pathway` enum | Array of 3 pathways matching PostgreSQL enum. | **Appropriate Constant.** Mapping backend enum values to UI metadata (icons, labels, colors) belongs in the frontend design system. |
| **Declaration Text Version** | `backend/app/modules/programs/application/commands.py:26`<br>`frontend/app/stores/applicationDraft.ts:105` | Legal / Applicant terms baseline | `CURRENT_DECLARATION_VERSION = 1` | **Appropriate Constant.** Version numbers are synchronized and checked across frontend and backend use cases. |
| **Published Program Titles, Summaries, Descriptions** | PostgreSQL `lms.programs` | PostgreSQL `lms.programs` | Returned dynamically by `GET /api/v1/programs` and `GET /api/v1/programs/:slug`. | **Dynamic & Server-Owned (Verified).** Database contains 44 seeded programs; 38 published records are returned dynamically to the frontend catalogue. |
| **Program Application Open/Close Windows** | PostgreSQL `lms.programs` | PostgreSQL `lms.programs` | Columns: `applications_open_at`, `applications_close_at`, `applications_enabled`. | **Dynamic & Server-Owned (Verified).** Checked in both frontend availability composable and backend PostgreSQL RLS/INSERT trigger. |
| **Application Reference Generation** | `backend/app/modules/programs/application/commands.py:61-65` | Backend Use Case | Format: `JC-XXXX-XXXXXX` using cryptographically secure `secrets.token_hex`. | **Dynamic & Server-Owned (Verified).** Generated uniquely on backend; verified in live tests (`JC-4E24-39EE10`). |
| **Official Contact Information** | `frontend/app/layouts/public.vue:174-194` | Campaign Poster & Organization Contact | Phone `+254 792 696 592`, email `hello@jengacode.tech`, venue `Maktaba Kuu`. | **Appropriate Constant.** Confirmed organizational contact channels displayed in public layout footer. |
| **Stock Image URLs & Attributions** | `frontend/app/utils/images.ts`<br>`docs/product/image-manifest.md` | Product Image Manifest | Unsplash CDN URLs with photographer attribution. | **Appropriate Constant.** Documented in image manifest with proper open licenses and fallback SVG generator. |

---

## 5. End-to-End Data Flow Trace

### Flow 1: Load Published Programs
1. **Vue Component:** `frontend/app/pages/programs/index.vue:35-47`
2. **Composable / Client:** `useAsyncData` calling `$api<ProgramListResponse>('/programs', { params })`
3. **HTTP Route:** `GET http://127.0.0.1:8000/api/v1/programs?page=1&page_size=9`
4. **FastAPI Handler:** `backend/app/modules/programs/api/router.py:46-76` (`list_programs`)
5. **Use Case:** `ListPublishedProgramsUseCase.execute` (`backend/app/modules/programs/application/queries.py:42-53`)
6. **Repository:** `PostgresProgramRepository.list_published` (`backend/app/modules/programs/infrastructure/postgres.py:82-127`)
7. **SQL Execution:** `SELECT ... FROM lms.programs WHERE status = 'published' ORDER BY display_order ASC, created_at ASC LIMIT 9 OFFSET 0;`
8. **Role & RLS:** Connection executes `SET ROLE lms_api;`. Table policy `programs_api_read` allows `SELECT WHERE status = 'published'`.
9. **Status:** **VERIFIED** (Returns 38 published programs).

### Flow 2: Filter and Paginate Programs
1. **Vue Component:** Filter tabs and pagination buttons in `frontend/app/pages/programs/index.vue:89-103, 155-186`.
2. **Composable / Client:** `$api('/programs', { params: { pathway: 'holiday', page: 2, page_size: 9 } })`.
3. **HTTP Route:** `GET /api/v1/programs?pathway=holiday&page=2&page_size=9`.
4. **FastAPI & SQL:** Parameterized SQL with `WHERE status = 'published' AND pathway = %(pathway)s`.
5. **Status:** **VERIFIED** (Synchronizes query parameters with Vue Router URL).

### Flow 3: Open Program Details
1. **Vue Component:** `frontend/app/pages/programs/[slug]/index.vue:19-22`.
2. **HTTP Route:** `GET /api/v1/programs/coding-robotics-camp-nov-2026`.
3. **FastAPI Handler:** `backend/app/modules/programs/api/router.py:79-98` (`get_program`).
4. **Repository:** `PostgresProgramRepository.get_by_slug` (`backend/app/modules/programs/infrastructure/postgres.py:144-159`).
5. **SQL Execution:** `SELECT ... FROM lms.programs WHERE slug = %(slug)s AND status = 'published';`.
6. **Status:** **VERIFIED** (Returns full detail with description, age limits, dates).

### Flow 4: Determine Application Availability
1. **Vue Composable:** `useApplicationAvailability` (`frontend/app/features/programs/composables/useApplicationAvailability.ts`).
2. **Logic:** Compares client/server timestamp against `applications_enabled`, `applications_open_at`, and `applications_close_at`.
3. **Backend Enforcement:** Double-checked by `SubmitApplicationUseCase` (`backend/app/modules/programs/application/commands.py:136-139`) using database clock `SELECT now()`.
4. **Database Policy:** Conditional `INSERT ... SELECT ... WHERE now() >= applications_open_at AND now() < applications_close_at` ensures race-free enforcement.
5. **Status:** **VERIFIED** (Renders green "Open for applications" and enables "Apply now").

### Flow 5: Validate Application
1. **Frontend Validation:** Computed `validationErrors` in `frontend/app/pages/programs/[slug]/apply.vue:43-64` validates name, email regex, required declaration, and program-specific age eligibility.
2. **Backend Validation:** Pydantic `SubmitApplicationRequest` (`backend/app/modules/programs/api/schemas.py:106-180`) trims whitespace and validates field lengths and formats.
3. **Status:** **VERIFIED** (Invalid payloads rejected with HTTP 422 Problem Details).

### Flow 6: Submit Application
1. **Vue Trigger:** `handleSubmit()` in `frontend/app/pages/programs/[slug]/apply.vue:79-110`.
2. **Store Action:** `draft.buildPayload()` (`frontend/app/stores/applicationDraft.ts:95-115`) attaches or preserves UUIDv4 `idempotency_key`.
3. **HTTP Route:** `POST /api/v1/programs/coding-robotics-camp-nov-2026/applications`.
4. **Use Case:** `SubmitApplicationUseCase.execute` (`backend/app/modules/programs/application/commands.py:103-169`).
5. **Status:** **VERIFIED** (Live submission verified with HTTP 201 Created).

### Flow 7: Persist Application and Audit Event
1. **Repository Implementation:** `PostgresApplicationRepository.insert_application` (`backend/app/modules/programs/infrastructure/postgres.py:195-269`).
2. **Transaction Boundary:** `async with conn.transaction():` ensures application insert and audit event insert commit atomically.
3. **SQL Query 1:** `INSERT INTO lms.enrolment_applications (...) SELECT ... FROM lms.programs WHERE ... ON CONFLICT (idempotency_key) DO NOTHING RETURNING id, ...;`.
4. **SQL Query 2:** `INSERT INTO lms.application_audit_events (application_id, event_type, actor_id, detail) VALUES (%(application_id)s, 'submitted', NULL, NULL);`.
5. **Database Grants:** Role `lms_api` has INSERT grants on submission columns and SELECT grants strictly on receipt columns. Personal columns cannot be selected.
6. **Status:** **VERIFIED** (Direct database inspection confirmed committed rows in both tables).

### Flow 8: Return and Display Confirmed Receipt
1. **HTTP Response:** HTTP 201 Created with JSON matching `ApplicationReceiptResponse` schema.
2. **Store Action:** `draft.recordReceipt(receipt)` saves receipt in state and executes `draft.clearPersonalDetails()`.
3. **UI Confirmation:** `frontend/app/pages/programs/[slug]/apply.vue:178-210` displays green success panel with tracking reference (e.g. `JC-4E24-39EE10`).
4. **Status:** **VERIFIED**.

### Flow 9: Retry After Lost Response (Safe Idempotent Replay)
1. **Action:** Resubmitting the identical payload with the same `idempotency_key`.
2. **Backend Execution:** `SubmitApplicationUseCase` finds existing row, verifies matching SHA-256 fingerprint, and returns original receipt with `is_retry = True`.
3. **HTTP Response:** HTTP 200 OK (changed from 201 to indicate existing resource).
4. **Database State:** Row count for the idempotency key remains exactly 1; audit count remains exactly 1.
5. **Status:** **VERIFIED** (Demonstrated live in scratch audit script).

### Flow 10: Start Genuinely New Application
1. **Vue Action:** Clicking "Apply to another program" invokes `draft.resetAll()` (`frontend/app/stores/applicationDraft.ts:142-145`).
2. **Store State:** Clears receipt, resets personal fields, and generates a fresh UUIDv4 `idempotencyKey`.
3. **Status:** **VERIFIED** (Next submission uses new key and produces new reference).

---

## 6. Business Rules Introduced Without Approval

| Rule / Implementation | Source File & Line | Assessment | Recommendation |
| :--- | :--- | :--- | :--- |
| **Hardcoded Max Age of 25 in HTML Input** | `frontend/app/pages/programs/[slug]/apply.vue:330`<br>`max="25"` | **Provisional Restriction.** The database permits 1–99, and the backend validates against program `max_age_years`. The hardcoded HTML `max="25"` limits adult learner applications for evening or community programs. | Retain as provisional; remove HTML `max="25"` or bind dynamically to `program.max_age_years || 99`. |
| **Fixed Declaration Version = 1** | `backend/app/modules/programs/application/commands.py:26`<br>`CURRENT_DECLARATION_VERSION = 1` | **Reasonable Baseline.** Enforces agreement to terms. However, terms text is hardcoded in the frontend Vue template rather than versioned in the database. | Future milestone should manage declaration terms text and versioning from an administrative policy table. |
| **Provisional "Ages 7–17" Catalogue Copy** | `supabase/migrations/20261028000001_programs_and_applications.sql:70-74`<br>`frontend/app/pages/index.vue:346` | **Provisional Copy.** Documented in migration notes as provisional pending owner sign-off. | Confirm age policy across Saturday club, school terms, and holiday intensives before portal rollout. |

---

## 7. Security and Data Integrity Findings

| Severity | Domain | File & Line | Observed Behaviour | Expected Standard | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pass** | Least Privilege DB Grants | `supabase/migrations/20261028000001_programs_and_applications.sql:329-337` | `lms_api` has column-restricted `SELECT` on `lms.enrolment_applications`. Personal data (`guardian_name`, `email`, `phone`, `learner_name`, `notes`) cannot be selected by the runtime API role. | Personal contact data must not be exposed to the API role on replay queries. | **Verified** |
| **Pass** | RLS Enforcement | `supabase/migrations/20261028000001_programs_and_applications.sql:350-390` | `programs`, `enrolment_applications`, and `application_audit_events` all have RLS enabled with explicit policies for `lms_api`. | Table access must be guarded by RLS policies. | **Verified** |
| **Pass** | Schema Isolation | `supabase/migrations/20261028000001_programs_and_applications.sql:96-110` | `REVOKE ALL ON SCHEMA lms FROM PUBLIC, anon, authenticated;` | Schema `lms` must not be exposed to Supabase public PostgREST data API. | **Verified** |
| **Pass** | Transaction Atomicity | `backend/app/modules/programs/infrastructure/postgres.py:198-250` | `async with conn.transaction():` encloses application insertion and audit event creation. Both succeed or both roll back. | Application and audit event creation must be strictly atomic. | **Verified** |
| **Pass** | Client Privacy | `frontend/app/stores/applicationDraft.ts:57-72` | Draft is memory-only Pinia state. Zero usage of `localStorage`, `sessionStorage`, cookies, or analytics tracking. | Personal details must never be stored in persistent browser storage. | **Verified** |
| **Pass** | CORS Configuration | `backend/app/bootstrap.py:111-118` | `allow_origins` defaults strictly to `["http://localhost:3000", "http://127.0.0.1:3000"]`. `allow_credentials=False`. | Restrict browser cross-origin requests to authorized origins. | **Verified** |
| **Pass** | Event Loop Policy | `backend/run_server.py:7-9` | Forces `WindowsSelectorEventLoopPolicy` and monkeypatches `uvicorn.loops.asyncio.asyncio_loop_factory` to prevent `InterfaceError` under Windows Proactor. | Async psycopg requires selector event loop on Windows. | **Verified** |

---

## 8. Design and Content Compliance

### 8.1 Visual Identity Alignment (Jjenga Code Posters)
- **Palette Compliance:**
  - Navy `#160D35` (applied as `--color-brand-navy: #160D35` in `tokens.css` and Tailwind theme).
  - Purple `#8C2ACA` (applied as `--color-brand-purple: #8C2ACA`).
  - Yellow `#F9C41D` (applied as `--color-brand-yellow: #F9C41D`).
  - Pink `#F6479A` (applied as `--color-brand-pink: #F6479A`).
  - Muted Rose `#9F555E` (applied as `--color-brand-rose: #9F555E`).
  - White `#FFFFFF` (applied as primary card and page background).
- **Retro Vector Wordmark:** Authentic vector SVGs extracted and verified:
  - Header: `frontend/public/brand/jenga-code-gradient.svg` (retro geometric lettering with pink-to-yellow gradient).
  - Footer: `frontend/public/brand/jenga-code-white.svg` (solid white vector on deep navy `#0B061D`).
- **Typography:** Google Fonts loaded in `tokens.css`:
  - Headings: `Sora` (font weights 700, 800, 900) with deliberate line breaks: *"Raise a builder,<br>not just a user."*
  - Body: `DM Sans` (font weights 400, 500) for high legibility.
- **Background Texture:** Subtle repeating pixel grid pattern (`/brand/jenga-pixel-pattern.svg`) active on homepage hero and pathway sections via `.poster-pattern` utility.
- **Motion & Accessibility:**
  - `AOS` (Animate On Scroll) disabled automatically when `prefers-reduced-motion: reduce` is detected (`frontend/app/plugins/aos.client.ts:22`).
  - `Lenis` smooth scrolling bypassed when `prefers-reduced-motion: reduce` is active (`frontend/app/plugins/lenis.client.ts:16-17`).

### 8.2 Curated Photography & CDN Attribution Manifest
All 6 images are curated, licensed CDN photographs documented centrally in `docs/product/image-manifest.md` and typed in `frontend/app/utils/images.ts`:
1. **Hero Banner:** Unsplash photo `photo-1581092160607-ee22621dd758` (Young builder with robotics prototype by ThisisEngineering).
2. **School-Term Pathway:** Unsplash photo `photo-1516321318423-f06f85e504b3` (Collaborative classroom computing by John Schnobrich).
3. **Saturday Club Pathway:** Unsplash photo `photo-1509062522246-3755977927d7` (Hands-on maker workshop by NeONBRAND).
4. **Holiday Camp Pathway:** Unsplash photo `photo-1577896851231-70ef18881754` (Engaged students learning technology by Compare Fibre).
5. **Hardware Showcase:** Unsplash photo `photo-1485827404703-89b55fcc595e` (Electronic microcontroller breadboard by Alex Knight).
6. **Community Showcase:** Unsplash photo `photo-1531482615713-2afd69097998` (Mentorship and collaborative guidance by Desola Lanre-Ologun).

All images include SVG fallback placeholder data URIs via `getPlaceholderSvg()` in `frontend/app/utils/images.ts`.

---

## 9. Verification Results & Command Executions

| Check | Exact Command Executed | Environment | Exit Code | Result | What it Establishes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Backend Linting** | `uv run --project backend --frozen ruff check backend` | Local Windows / Python 3.12 | 1 | **Failed (1 error)** | Highlights `backend/run_server.py:9:101` line length violation (`E501`). All 130 core backend app files passed cleanly. |
| **Backend Typecheck** | `uv run --project backend --frozen mypy --config-file backend/pyproject.toml backend/app` | Local Windows / Python 3.12 | 0 | **Passed** | 130 source files checked with 0 type errors. Enforces strict typing across all modules. |
| **Import Boundaries** | `uv run --project backend --frozen lint-imports --config backend/pyproject.toml` | Local Windows / Python 3.12 | 0 | **Passed** | 2 contracts kept, 0 broken. Domain modules stay independent of HTTP and DB adapters; use cases depend only on ports. |
| **Backend Pytest** | `uv run --project backend pytest backend/tests -ra --tb=short` | Local Windows / PostgreSQL 17 on 5433 | 0 | **Passed** | 46 passed in 5.11s. Includes 7 live PostgreSQL tests verifying RLS, idempotency replay, payload conflict, and role isolation. |
| **Frontend Tests** | `npm --prefix frontend test` (Vitest) | Node.js v24 / Vitest v5.0.5 | 0 | **Passed** | 4 test suites passed, 19 tests passed (pathwayInfo, api-errors, availability, applicationDraft store). |
| **Frontend Typecheck**| `npm --prefix frontend run typecheck` (`nuxt typecheck`) | Node.js v24 / vue-tsc v3.3.13 | 0 | **Passed** | Zero TypeScript errors across all Vue components, composables, stores, and layouts. |
| **OpenAPI Consistency**| `python scratch/compare_openapi.py` | Local FastAPI running on 8000 | 0 | **Passed** | Zero drift between live FastAPI `/api/openapi.json` and committed `contracts/api/v1/openapi.json` (0 path diff, 0 schema diff). |
| **Production Build** | `npm --prefix frontend run build` | Nuxt 4.6.3 / Nitro 2.13.5 | 0 | **Passed** | Compiled full production bundle (`.output/server/index.mjs`) in 8m 08s without fatal errors. |
| **Live Integration** | `uv run --project backend python scratch/audit_submission_flow.py` | Live FastAPI (8000) & Live Postgres (5433) | 0 | **Passed** | Verified full flow: Program fetch, HTTP 201 submission, DB row assertion in `lms.enrolment_applications`, audit row assertion in `lms.application_audit_events`, HTTP 200 idempotent replay with zero duplicate rows, and HTTP 409 conflict on changed payload. |

---

## 10. Remaining Blockers and Unresolved Decisions

1. **E2E Playwright Suite Scope:** `playwright.config.ts` exists, but the test in `tests/e2e/public/development-connection.spec.ts` targets the obsolete homepage layout rather than `/development`. A unified Playwright suite running headless browser tests against port 3000 should be standardized before starting the portal milestone.
2. **Offline Draft Notice Confirmation:** The application form displays: *"Your application is saved in this tab only. Refreshing or closing the tab will clear your entered information."* This matches requirements, but no beforeunload confirmation dialog is currently attached to warn users if they accidentally navigate away with dirty fields.
3. **Admin Review Interface Scheduling:** Reviewing submitted applications, changing statuses (`under_review`, `approved`, `rejected`), and triggering account invitations currently requires direct database maintenance access. The administrator portal milestone must provide this interface.

---

## 11. Prioritized Correction List

| Priority | Issue | Location | Observed Condition | Recommended Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | Ruff line length error in Windows loop runner | `backend/run_server.py:9` | Line length 103 characters exceeds 100-character limit (`E501`). | Wrap the lambda assignment across two lines or add `# noqa: E501`. |
| **P2** | Outdated Playwright E2E assertion | `tests/e2e/public/development-connection.spec.ts:4-6` | Navigates to `/` looking for `'Check backend'`. | Update route to `/development` or rewrite test to assert public homepage heading *"Raise a builder, not just a user."* |
| **P3** | Dynamic homepage camp spotlight | `frontend/app/pages/index.vue:313-351` | Camp spotlight card is hardcoded in the template. | Add a lightweight `useAsyncData` query fetching the featured camp by slug (`/programs/coding-robotics-camp-nov-2026`) so title, dates, and availability are server-driven. |
| **P4** | Accidental navigation guard | `frontend/app/pages/programs/[slug]/apply.vue` | No warning on page refresh when draft contains data. | Add an `onBeforeRouteLeave` guard and window `beforeunload` listener in `apply.vue` that triggers when `draft.hasDraftData` is true. |

---

## 12. Verdict on Readiness to Begin Portals

**READINESS VERDICT: APPROVED WITH PREREQUISITES**

The public website foundation is structurally sound, architecturally compliant, and demonstrably connected to PostgreSQL through FastAPI. The private `lms` schema, least-privilege role boundaries, and atomic audit logging provide a clean base for user authentication and role-based portal development.

### Prerequisites to Complete Before Writing Portal Code:
1. Fix the single Ruff linting error in `backend/run_server.py:9`.
2. Update `tests/e2e/public/development-connection.spec.ts` to reflect the current page structure.
3. Formalize the authentication strategy decision (e.g., Supabase Auth vs. standalone OAuth2/JWT in FastAPI) in an Architecture Decision Record (`docs/architecture/decisions/0002-auth-strategy.md`).
4. Apply P3 (dynamic query for homepage spotlight) to ensure 100% server-owned operational data.
