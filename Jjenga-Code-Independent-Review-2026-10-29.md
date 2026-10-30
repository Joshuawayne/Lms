# Jjenga Code: independent review of the Antigravity audit package

Date: 29 October 2026. Scope: inspect the supplied public website implementation, verify meaningful claims, and identify corrections before portal development. No supplied application source was changed.

## Verdict

**The public milestone is not ready for sign-off.** There is a useful, functioning foundation, but the original audit's "qualified pass" misses reproducible application-state defects, an unimplemented database isolation requirement, unsafe database test isolation, unsupported public claims and material design-compliance gaps.

This is a review of the uploaded snapshot, not direct access to `C:\LearningManagementSystem`. Hosted Supabase connectivity, the Windows runtime and a complete production/browser deployment were not independently verified.

The uploaded standalone report is byte-for-byte identical to the report inside the ZIP. It retains the earlier verdict, incorrect image inventory and deferred-feature classifications; the requested amendments were not included.

## Independently executed checks

Existing compatible dependencies were reused in an isolated review workspace. Native database environment variables were explicitly removed before running backend tests. The uploaded lockfiles were absent, so this is not a fresh frozen installation of the user's exact Windows environment.

| Check | Result | What this establishes |
| --- | --- | --- |
| Existing backend tests | **39 passed, 7 skipped** | Unit/API tests pass. All seven native PostgreSQL tests were skipped without credentials. |
| Existing frontend tests, Vitest 5.0.5 | **19 passed, 4 suites** | Current unit coverage passes; it does not cover the reproduced defects below. |
| Independent frontend regression probes | **3 failed** | The actual uploaded application page/store violate three agreed receipt/idempotency requirements. |
| Ruff lint, supplied backend | **Passed** | The supplied files pass lint. The separately reported `backend/run_server.py` was not included. |
| Ruff formatting | **Failed: 4 files** | `main.py`, application `ports.py`, `in_memory.py` and `postgres.py` would be reformatted. |
| Mypy with explicit backend config | **Passed: 130 source files** | Static Python typing passes. |
| Import-linter | **2 contracts kept, 0 broken** | The configured dependency boundaries pass. |
| Generated FastAPI OpenAPI vs supplied JSON | **Exact equality** | Runtime-generated OpenAPI matches the supplied committed contract. Generated TypeScript synchronization was not independently established. |
| Disposable PGlite execution of supplied migration | **Isolation defect reproduced** | `lms_api` can read both synthetic receipts without a request-key scope. Personal-column reads are correctly denied. |
| Existing negative audit-event test scenario in PGlite | **Wrong failure reproduced** | `under_review` produces SQLSTATE `22P02`, an invalid enum error; this is not evidence that the intended audit authorization rule was tested. |
| Full browser / production / hosted Supabase verification | **Not established** | Missing package/config/evidence inputs and local runtime limitations prevent a defensible completion claim. |

The independent frontend probes use the actual uploaded Vue SFC and Pinia store with fixture program data, Nuxt helper stubs and simple UI component stubs. They are isolated rendering/state tests, not browser-to-database tests. PGlite checks exercise the supplied PostgreSQL SQL/policies in a disposable environment; they do not establish native multi-session concurrency, durable HTTP persistence or a hosted Supabase connection.

## What is correctly implemented in the snapshot

- Three pathway enum values are separate from delivery modes.
- Published catalogue queries are real PostgreSQL repository queries, with bounded API pagination and parameterized values.
- The composition root does not silently replace an unavailable production database with in-memory data. Missing repositories return a service-unavailable problem.
- Application insertion and its submission audit event share a repository transaction.
- **The previous connection/savepoint concern is addressed in source:** the runtime factory now connects with `autocommit=True` before `SET ROLE`, and repository transaction contexts control write commits. This is a source-level finding; hosted persistence remains unverified.
- Personal application columns are excluded from the runtime role's SELECT grant. The disposable SQL check confirms denial of `guardian_email` reads.
- The use case compares backend fingerprints and returns an existing receipt before checking whether applications have closed, while the program remains published and resolvable.
- The closure and concurrency test files now contain substantive scenarios rather than the earlier placeholders. Their presence does not establish that they passed in the intended database environment.
- The draft state is memory-only, and receipt recording clears entered personal fields.

## Findings requiring correction

### F01 — P1: a receipt for one program confirms a different program

Sources: `frontend/app/stores/applicationDraft.ts:83`, `:121`; `frontend/app/pages/programs/[slug]/apply.vue:178`.

`hasReceipt` checks only whether the global store contains any receipt. The application page does not compare `receipt.program_id` with the loaded program. After submitting Program A, visiting Program B's application page can show "Apply for Program B" followed by A's reference and "Submitted for review."

**Reproduced:** an independent render of the uploaded page with Program B and Program A's stored receipt displayed `SYNTHETIC-RECEIPT-A` as confirmation.

Correction: associate confirmations with the program and submission attempt they actually acknowledge. Preserve useful receipts without allowing one to confirm another application.

### F02 — P1: changing only the target program reuses an idempotency key

Sources: `frontend/app/stores/applicationDraft.ts:95`; `frontend/app/pages/programs/[slug]/apply.vue:89`.

The store's payload identity includes applicant fields but excludes the target program. The program appears only in the HTTP URL. If the response for Program A is lost and a parent switches to Program B with unchanged personal details, the store reuses the key. The backend fingerprint correctly includes `program_id`, so the second submission conflicts rather than becoming a new application.

**Reproduced:** request snapshots for A and B received the same key.

Correction: include target program identity in client submission identity. Unchanged retries of the same submission must still reuse their original key.

### F03 — P1: closed-program handling hides receipts and blocks safe retries

Source: `frontend/app/pages/programs/[slug]/apply.vue:165`, `:178`.

The availability branch appears before the confirmation branch. When applications become disabled/closed, a previously confirmed receipt disappears from the page. The same gate prevents a pending uncertain submission from being retried through the form after closure, despite backend replay support.

**Reproduced:** rendering a closed Program A with its matching confirmed receipt hid the reference. Blocking the lost-response retry is established by the same template gate; the complete browser/network scenario remains unexecuted.

Correction: separate permission to create a new application from the ability to show or safely retry an already attempted submission.

### F04 — P1: the database does not enforce request-key receipt isolation

Sources: `supabase/migrations/20261028000001_programs_and_applications.sql:359`; `backend/app/modules/programs/infrastructure/postgres.py:179`; `supabase/README.md`, verification item 3.

The SELECT policy is `USING (true)`. The repository filters its normal query by key, but the database role itself may select every receipt row. No transaction-local request-key scope is established. This contradicts the README's claim of strict database receipt scoping.

**Reproduced:** after applying the exact migration, `SET ROLE lms_api; SELECT reference FROM lms.enrolment_applications` returned both synthetic applicants' references. Reading personal columns still failed with SQLSTATE `42501`.

This is a database defense requirement failure. The reviewed public HTTP routes do not expose a receipt-enumeration endpoint, so this finding is not proof of a browser-accessible disclosure.

Correction: enforce the approved request-key scope at the database boundary, including fail-closed behaviour when scope is absent, and set/reset it transactionally in both lookup and insertion/replay paths. Preserve atomic commit behaviour and column-level restrictions. Use a new migration if the original migration has already been applied.

### F05 — P1: database tests can contaminate the runtime catalogue

Source: `backend/tests/integration/database/test_postgres_database.py:36`, `:68`, `:136`, `:263`, `:312`, `:376`, `:437`.

Test connections fall back to `LMS_DATABASE_URL`; maintenance connections can fall back to the same target. Tests commit fixture programs with autocommit and contain no fixture cleanup. A full run creates eight program rows, seven of them published, plus application/audit records.

If configured against a development runtime database, repeated runs leave synthetic programmes visible in its public catalogue. This is a plausible explanation for the reported 44 records, not proof of their actual origin; no live program inventory or provenance script was supplied.

Correction: require an explicitly isolated test database and appropriate maintenance connection, reject unintended runtime/production targets, and clean up committed fixtures in failure-safe teardown. Do not automatically delete any existing records whose ownership is uncertain.

### F06 — P1: operational facts and unsupported promises are published as constants

Sources: `frontend/app/pages/index.vue:66`, `:76`, `:158`, `:175`, `:313`, `:346`, `:564`, `:598`; `frontend/app/pages/programs/[slug]/apply.vue:330`.

Examples include:

- Saturday hours fixed to 9am–12pm.
- A five-day/full-day format generalized to holiday programs.
- A camp CTA permanently claiming "Applications are currently open for ages 7–17."
- An equipment promise covering all kits and lab laptops on advance request.
- A claim that every venue meets vetted child-safety standards.
- Admissions criteria involving class group balance and mentor ratios.
- A reassurance that schedules and availability are always connected to the database, immediately contradicted by the hardcoded spotlight.
- An HTML maximum age of 25 alongside program-specific validation and a database data-validity range of 1–99.

The posters establish a particular camp's dates/hours/venue and contact channels. They do not establish a universal age policy, Saturday hours, equipment provision or venue vetting. These statements may ultimately be true, but approval/evidence was not supplied. Do not call them false solely because evidence is absent; remove or qualify them until verified.

The form uses `novalidate`, so `max="25"` is a contradictory HTML constraint, not proof that every manually entered age over 25 is currently rejected. The original audit overstates that specific behaviour.

Correction: source current program facts and availability from approved backend records; retain approved static brand/pathway explanations. Do not replace missing facts with guesses or invent database columns and schedules without a documented decision.

### F07 — P2: catalogue query state is synchronized in only one direction

Source: `frontend/app/pages/programs/index.vue:28`, `:49`.

Filter/page refs read `route.query` once. Watchers write their values back to the URL, but there is no corresponding reaction to later query changes. Following another pathway link while the catalogue component is reused, or navigating through query history, can leave the displayed selection/request out of step with the URL.

Correction: make validated URL query state authoritative or implement consistent two-way synchronization. Verify same-page pathway links, direct URLs, pagination and browser history. Backend ordering should add a unique final tie-breaker after `display_order` and `created_at` (`postgres.py:118`).

### F08 — P2: exact palette tokens exist, but the UI mainly uses the old palette

Sources: `frontend/app/assets/styles/tokens.css:17`, `:34`, `:43`; `frontend/app/layouts/public.vue:58`, `:112`; public page utility classes.

Exact `--color-brand-*` tokens are declared but not consumed by the reviewed components. Common classes still resolve to old values: `bg-purple-600` is `#553280`, `bg-navy-900` is `#0A1122`, and `bg-navy-950` is `#060B15`. Their presence is not equivalent to applying our approved palette.

Correction: bind actual main surfaces, headlines, buttons and accents to approved brand roles, with deliberate accessible tints/shades. Keep a documented distinction between the base colours and supporting shades. Verify rendered computed colours, not only token declarations.

### F09 — P2: decorative components are referenced under names Nuxt does not register

Sources: `frontend/app/components/ui/WaveDivider.vue`, `BlobShape.vue`, `StarAccent.vue`; `frontend/app/layouts/public.vue:113`; program templates; `frontend/nuxt.config.ts`.

Templates use `<WaveDivider>` and `<BlobShape>` without imports or path-prefix configuration. Preparing the supplied configuration generated `UiWaveDivider`, `UiBlobShape` and `UiStarAccent`; it did not register the unprefixed names. This undermines the claim that these shapes are working on the rendered pages.

Correction: use the registered names, explicit imports or deliberate component-discovery configuration. Verify absence of unresolved-component warnings.

### F10 — P2: motion behaviour does not meet the full agreed contract

Sources: `frontend/app/plugins/lenis.client.ts:45`, `:51`; `aos.client.ts:25`; `frontend/app/assets/styles/main.css:16`, `:35`.

- Lenis resets scroll to zero after every navigation, without distinguishing anchors or back/forward restoration.
- Its `destroy()` function is provided but is not attached to the claimed teardown hook.
- AOS schedules route timers without registering cleanup.
- AOS styles are imported unconditionally; the stylesheet only forces content visible for reduced-motion users, not for ordinary users when animation initialization fails. Verify and correct progressive enhancement.
- Initial preference checks and some CSS reduced-motion support exist, but the report does not establish the full keyboard/anchor/history/failure scenarios.

Correction: implement the agreed public-site motion lifecycle and preserve native navigation behaviour. Do not add a new animation stack.

### F11 — P2: image fallback and provenance claims exceed the implementation

Sources: `frontend/app/utils/images.ts:31`, `:103`; `frontend/app/pages/index.vue` image tags; `docs/product/image-manifest.md`; audit section 8.2.

`getPlaceholderSvg()` is defined but never imported/called by the reviewed components; image tags have no error handler. A fallback generator's existence is not a working fallback. Images also use one fixed CDN width without `srcset`/`sizes`.

The audit image inventory does not match the source registry. Several source-page URLs appear to have been assembled by appending CDN timestamp identifiers rather than supplying verified original photo-page identifiers. Verify the links; this review did not independently fetch all six.

For the robot photo, the actual source is [Alex Knight's white robot near a brown wall](https://unsplash.com/photos/white-robot-near-brown-wall-2EJCSULRwC8), with the `agk42` profile shown on that page. The earlier audit's breadboard description and the registry's `agkdesign` handle are inaccurate.

Correction: inspect the actual images, record verified provenance, use accurate alt text, and connect error recovery. Keep stock imagery explicitly illustrative.

### F12 — P2: validation, error states and public abuse controls are incomplete

Sources: `frontend/app/pages/programs/[slug]/apply.vue:43`, `:99`, `:155`, `:225`; program details page `:57`; `backend/app/modules/programs/api/schemas.py:106`; `backend/app/bootstrap.py`.

- Field validation does not cover all backend length/phone/integer constraints.
- Error text is visually adjacent but lacks field associations such as `aria-describedby`/`aria-invalid`; the summary does not focus/link to invalid fields.
- Any detail-fetch error is presented as "Program not found," including service/network failures.
- `SubmitApplicationRequest` silently ignores extra fields rather than rejecting them. An independent schema check accepted a payload containing `status` and `reviewed_at` and discarded those fields. This does not approve an application, but it contradicts the strict request-contract requirement.
- No application-level submission rate limit or request-body size enforcement is present. External deployment protection was not supplied, so its existence is unverified.
- Receipt recording is unconditional after an awaited response and has no attempt/program freshness guard; fields remain editable in flight. A late response can affect a newer draft. This path needs a targeted browser/async test; it was not among the three executed probes.

Correction: align validation with the approved contract, implement accessible errors, distinguish unavailable from missing records, protect attempt freshness and supply the agreed public submission controls at the appropriate deployment boundary.

### F13 — P2: parts of the native test suite can pass for the wrong reason

Source: `backend/tests/integration/database/test_postgres_database.py:228`, `:437`.

The negative audit test inserts `under_review`, which is not an `application_audit_event_type`; it catches any `psycopg.Error`. The reproduced failure is invalid enum `22P02`, not the intended authorization denial. Tests of unavailable submissions call a repository query that filters records before insertion, so they do not independently establish the RLS rejection path.

The improved rollback test manually writes SQL rather than causing the production repository's audit step to fail. Its broad error assertion can also accept failure of the first insert. Add assertions that establish which step failed and verify production repository rollback through an independent connection.

Correction: valid fixture entities/enum values, specific SQLSTATEs, direct RLS checks where policy enforcement is being claimed, production-repository failure injection and isolated fixture cleanup.

### F14 — evidence and documentation: the review package is incomplete

Absent from this ZIP: all lockfiles; `backend/run_server.py`; setup/contract scripts referenced by package commands; frontend TypeScript/test/lint configuration; `frontend/public` brand assets; `docs/design/public-website.md`; audit scratch scripts; raw claimed test logs; database inventory; screenshots.

Some SVGs exist under `docs/brand`, but that does not establish their presence at the frontend's served `/brand/...` paths in the user's project.

These are **package omissions**, not proof that every file is absent from the Windows project. They prevent a reproducible review of the claims that depend on them. The README still describes the original startup scaffold and connectivity page.

A development render was attempted with existing local dependencies. Nuxt generated component registrations, but full rendering was blocked by missing local AOS/Lenis dependencies and worker IPC permissions. Those local limitations are not attributed to the user's Windows application. A production build was not independently run.

Correction: provide the omitted non-secret inputs/evidence, update documentation, and replace the completion verdict with what is actually verified. Keep deferred portal features documented as deferred.

## Order of work

1. Correct receipt/program/attempt identity, closed-window recovery and request-key database isolation.
2. Isolate database tests; identify existing synthetic records without deleting uncertain business data.
3. Replace operational hardcoding and unsupported copy; validate catalogue URL behaviour.
4. Correct brand application, component registration, motion, images and accessible error states.
5. Run the complete existing checks plus meaningful regression/native database/browser scenarios; deliver the missing source/evidence package.
6. Begin the portal milestone after the public submission chain is genuinely verified against the intended Supabase environment. Select authentication deliberately; this review does not select a provider.

There is no reason to rewrite Nuxt, FastAPI or the existing layered foundation to make these corrections.

## Evidence files

The companion evidence ZIP contains the three failing regression probes and output, the disposable SQL probe and output, a verification transcript, generated component-name evidence, package integrity/omission evidence and reproduction notes. Synthetic details only; no environment files or applicant records.
