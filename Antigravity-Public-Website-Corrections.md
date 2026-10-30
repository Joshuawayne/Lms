# Correct the Jjenga Code public milestone

Continue the existing project at `C:\LearningManagementSystem`. Read the attached independent review and regression evidence. Implement the corrections below and complete their verification before starting portals.

Preserve Nuxt/Vue, Nuxt UI/Reka UI, Tailwind, Pinia, FastAPI, Supabase PostgreSQL, existing business rules, API integrations and the approved poster identity. Follow the existing layered structure, SOLID, clean code and useful purpose comments/docstrings. Correct the existing foundation without replacing it with a new scaffold.

Do not produce another audit-only response. Fix the identified defects, preserve evidence of checks and report actual remaining blockers. Reuse existing private environment configuration without printing secrets.

## 1. Repair application identity and recovery

- Scope drafts, attempts, idempotency keys and receipts to the correct selected program.
- A receipt for Program A must never confirm Program B.
- Include the target program in client submission identity. The same normalized submission to the same program reuses its key; changing the program or effective payload gets a new key.
- Preserve an uncertain submission snapshot and its key after a lost response. Do not silently turn it into a different application.
- Separate new-submission availability from showing/replaying an earlier successful or uncertain attempt. Closing applications must not hide a matching confirmed receipt or prevent a safe replay.
- Guard response handling against navigation, new attempts and in-flight edits. A late response must not clear a newer draft or confirm another program.
- Keep draft personal data memory-only and isolated between SSR requests. Clear the appropriate personal draft only after its own confirmed response.
- Make starting another application, browser navigation and confirmation behaviour coherent.

Port the supplied review probes into appropriate project tests. Add meaningful coverage for lost responses, changed programs, late responses, closed-window retries and clean subsequent applications. The review harness uses local review paths and helper stubs; it is evidence, not a replacement for your project configuration or real browser tests.

## 2. Enforce receipt isolation in PostgreSQL

- Replace the application's receipt SELECT policy `USING (true)` with the agreed request-key isolation.
- Missing scope must fail closed. Normal lookup, insert-returning, concurrent replay and post-closure replay must still work for the correct key.
- Establish and clear the scope at the transaction boundary; keep it safe across connection reuse.
- Preserve column-level denial of personal-data reads, runtime least privilege, availability checks and atomic application/audit persistence.
- Retain the corrected autocommit connection setup. Do not recreate the earlier outer-transaction/savepoint problem.
- Commit successful application/audit writes before returning confirmation.
- Inspect migration history. If the original migration has already been applied, add an ordered corrective migration rather than editing its applied history. Update documentation to match actual enforcement.

Verify missing/wrong/correct key scope, denied personal columns, denied mutations, safe replay/conflict, exactly one audit event, concurrency and rollback using native PostgreSQL with independent connections. Report any hosted Supabase gap separately.

## 3. Make database tests isolated and repeatable

- Remove automatic fallback from test targets to the ordinary runtime database URL.
- Require an explicitly isolated test target and an appropriate maintenance setup connection.
- Verify the chosen environment before fixture writes. Do not run tests against production.
- Clean up committed fixtures even after failures. A test run must not leave published synthetic programs in the public catalogue.
- Investigate the reported 44 total/38 published programs: identify their source and environment. Inventory them before cleanup. Remove only confirmed test-owned records through an appropriate maintenance operation; do not delete uncertain business records or test by resetting the whole database.
- Fix the audit denial test to use valid audit enum values and real fixtures, then assert the intended authorization failure rather than any database error.
- Test unavailable-program RLS directly when claiming database enforcement.
- Exercise rollback through the production repository with a controlled audit failure, prove that the application insert occurred before that failure, and independently assert that neither record committed.

## 4. Remove operational hardcoding and unsupported claims

- Load the homepage's approved featured program from the existing API. Render its title, dates, eligibility and application availability from the returned record. Handle unavailable/unpublished/missing records honestly.
- Do not leave permanent "applications are currently open" text in templates.
- A configured editorial choice of featured program is acceptable; duplicating its changing operational facts is not.
- Remove or replace guessed Saturday hours, universal holiday duration, provisional global ages and conflicting form limits.
- Retain approved static pathway explanations, brand copy and contact channels.
- Do not invent fees, remaining seats, deadlines, staff credentials, equipment availability, transport, venue safety certification or admissions criteria.
- Remove unsupported equipment/laptop and venue-vetting assurances until verified. If a fact is genuinely required but unavailable, record the missing information and continue independent work.
- Keep learner development language encouraging curiosity, agency, practice and evidence. No fabricated urgency, character ranking or guaranteed outcomes.
- Keep database/security/testing implementation claims out of parent-facing marketing copy. Explain the parent benefit plainly.

Do not invent new database fields or unsupported program facts merely to make the design look complete. If the existing model cannot represent required verified schedule/venue information structurally, document that concrete gap and the smallest compatible contract/migration change before implementing it.

## 5. Correct catalogue and error behaviour

- Validate route query values and keep the catalogue synchronized with pathway/page query changes, including same-page navigation and history.
- Preserve filters across pagination and use deterministic backend ordering with a unique final tie-breaker.
- Distinguish a genuinely missing program from a network/backend outage. Provide appropriate recovery and HTTP behaviour.
- Align form limits and integer/optional-field validation with the backend contract and program eligibility. Do not choose an age policy on the owner's behalf.
- Reject unexpected request properties as required by our strict API contract; regenerate OpenAPI/types through the existing workflow when necessary.
- Add accessible field/error associations, a useful linked/focused summary and clear submission errors.
- Implement the agreed configurable public submission rate/body protections at the appropriate deployment boundary. Document their scope for the actual worker/deployment model; do not present CORS as abuse prevention.

## 6. Finish the approved visual implementation

Use the supplied Jenga Code posters as the primary art direction and the actual retro SVG logo.

The exact palette must be applied to rendered brand roles:

- Navy `#160D35`
- Purple `#8C2ACA`
- Yellow `#F9C41D`
- Pink `#F6479A`
- Muted rose `#9F555E`
- White `#FFFFFF`

Correct the mismatch where exact brand tokens are declared but buttons and major surfaces keep the old palette. Supporting accessible shades are allowed; distinguish and document them deliberately. Check computed colours in the browser.

Preserve Sora headings, DM Sans body text, expressive composition, meaningful photography, original shapes and restrained texture. Resolve the actual Nuxt component names for the decorative shapes and confirm that they render without component warnings.

Connect image error recovery; a never-used SVG helper is not a fallback. Provide suitable responsive image sizing. Inspect each photograph and replace inaccurate alt text, photographer handles and invented source-page URLs with verified information. Keep stock photography explicitly illustrative. CDN images are allowed; do not wait for original learner photographs.

Correct Lenis/AOS lifecycle handling, anchor navigation, back/forward restoration and reduced motion. Content must remain readable when animation initialization fails. Preserve native touch and keyboard behaviour. Do not reset every navigation to the top indiscriminately.

Verify mobile menu behaviour for same-page anchor links, keyboard access, focus, contrast, image cropping and horizontal overflow across the whole public site.

## 7. Complete verification and handover

Run the actual project checks: formatting, linting, static typing, import boundaries, backend tests, native database tests, OpenAPI/generated-type checks, frontend tests and a production build. Fix the reported Ruff formatting differences. Retain any real Windows event-loop compatibility work and include its source in the handover.

Run real browser scenarios for:

1. Catalogue filtering/pagination and navigation.
2. Program discovery/details from actual backend records.
3. Form validation and failures.
4. Browser submission through FastAPI into the intended database.
5. Independent committed application/audit assertions.
6. Lost-response retry with no duplicate rows/events.
7. Changed-program and changed-payload behaviour.
8. Matching receipt display and replay after closure.
9. Rejection of stale responses and confirmation leakage.
10. Starting a clean subsequent application.

Separate mocked/unit/rendering evidence, native database evidence, direct HTTP evidence and browser-to-database evidence. Never substitute one for another.

Confirm whether the application is using local PostgreSQL, local Supabase, a tunnel or hosted Supabase. If hosted Supabase is not configured, say so and report exactly what remains blocked. Do not fabricate connectivity or silently substitute another database.

Update README, `docs/design/public-website.md`, image provenance, API/database notes and verification instructions. Preserve the agreed future portal requirements without claiming those features exist.

Provide a complete sanitized handover ZIP including relevant source, all lockfiles, non-secret configuration, contract scripts, migrations, tests, the served SVG assets, documentation and actual verification outputs. Exclude secrets, real personal data, dependency directories and generated build caches. Include actual desktop/tablet/mobile screenshots as requested for review.

Finish with a concise implemented/fixed/verified/blocked report. Do not claim the public milestone is complete while any submission-integrity requirement is failing or while end-to-end database evidence is missing. Do not begin portal implementation in this task.
