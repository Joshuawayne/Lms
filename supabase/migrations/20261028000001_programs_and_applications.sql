-- Migration: programs and enrolment applications
-- Created:  2026-10-28
-- Applied:  not yet — requires Supabase connection
--
-- Establishes a private lms schema containing the public-facing program
-- catalogue, the enrolment-application workflow and lightweight submission
-- auditing.  No schema is created automatically at application startup; this
-- migration must be applied through the Supabase dashboard or CLI and
-- committed here as the sole schema-change history.
--
-- ┌──────────────────────────────────────────────────────────────────────────┐
-- │ DESIGN NOTES                                                           │
-- ├──────────────────────────────────────────────────────────────────────────┤
-- │ Schema isolation                                                       │
-- │   All objects live in the private 'lms' schema, which is NOT exposed   │
-- │   through the Supabase PostgREST / Data API.  The 'anon' and          │
-- │   'authenticated' roles receive no grants on 'lms' objects.            │
-- │                                                                        │
-- │ Role separation & least privilege                                      │
-- │   A dedicated 'lms_api' role is created with NOINHERIT NOLOGIN.       │
-- │   The FastAPI connection authenticates as a login role that has been   │
-- │   granted 'lms_api', then issues SET ROLE lms_api at session start.   │
-- │   lms_api does NOT own the tables and cannot bypass RLS.              │
-- │                                                                        │
-- │   lms_api column-level grants:                                         │
-- │     • programs: SELECT on all catalogue columns                        │
-- │     • enrolment_applications: INSERT on submission columns;            │
-- │       SELECT ONLY on receipt/idempotency columns (id, idempotency_key, │
-- │       request_fingerprint, program_id, status, submitted_at, reference)│
-- │       Personal data (guardian contact, learner details, notes) cannot  │
-- │       be read by lms_api outside insert-returning paths.               │
-- │     • application_audit_events: INSERT only (submitted events).        │
-- │   Administrator review permissions remain strictly separate.           │
-- │                                                                        │
-- │ Application availability enforcement                                   │
-- │   A program accepts applications when ALL of:                          │
-- │     • status = 'published'                                             │
-- │     • applications_enabled = true                                      │
-- │     • now() >= applications_open_at  (null = no earliest boundary)     │
-- │     • now() <  applications_close_at (null = no latest boundary)       │
-- │   Availability is enforced at two tiers:                               │
-- │     1. Backend use-case pre-checks for helpful validation errors.      │
-- │     2. Database RLS and conditional INSERT ... SELECT statements       │
-- │        ensuring race-free, atomic enforcement upon submission.         │
-- │                                                                        │
-- │ Idempotency & replay safety                                            │
-- │   The client generates a UUID idempotency_key before submitting.       │
-- │   The backend computes a SHA-256 fingerprint of the normalised         │
-- │   payload and stores it alongside the key.                             │
-- │     • Same key + same fingerprint → return original receipt            │
-- │     • Same key + different fingerprint → HTTP 409 conflict             │
-- │     • Concurrent inserts → ON CONFLICT ensures one row + one audit;   │
-- │       the losing thread verifies fingerprint matching.                 │
-- │   A retry after a lost successful response returns the original        │
-- │   receipt even if applications have since closed.                      │
-- │                                                                        │
-- │ Atomic auditing                                                        │
-- │   The application insert and its submission audit event MUST be in     │
-- │   one transaction.  Audit event is created only for new applications.  │
-- │                                                                        │
-- │ Applications ≠ enrolments                                              │
-- │   enrolment_applications is intentionally separate from a future       │
-- │   enrolments table.  Administrator approval is required before any     │
-- │   enrolment, learner identity or guardian relationship is established. │
-- │                                                                        │
-- │ Personal data protection                                               │
-- │   Guardian names, email, phone and learner names are personal data.    │
-- │   Excluded from application logs and replay query grants.              │
-- │                                                                        │
-- │ Age policy (Provisional)                                               │
-- │   The database constraint (1–99) is a data-validity guard.  Each      │
-- │   program's min_age_years / max_age_years defines eligibility.        │
-- │   The "typically 7–17" statement is provisional pending project owner  │
-- │   confirmation.                                                        │
-- │                                                                        │
-- │ Field limits & trimming                                                │
-- │   guardian_name:    1–200 characters (non-whitespace)                  │
-- │   guardian_email:   5–254 characters                                   │
-- │   guardian_phone:   5–30 characters (optional)                         │
-- │   learner_name:     1–200 characters (non-whitespace)                  │
-- │   learner_age:      1–99 (data validity)                               │
-- │   notes:            0–1000 characters (optional)                       │
-- │   program title:    1–200 characters (non-whitespace)                  │
-- │   program slug:     1–100 lowercase alphanumeric + hyphens             │
-- │   program summary:  1–500 characters (non-whitespace)                  │
-- │   program desc:     1–5000 characters (non-whitespace)                 │
-- │   reference:        1–50 characters, unique (non-whitespace)           │
-- │   fingerprint:      64 lowercase hex characters                        │
-- │   declaration_ver:  positive integer (>= 1)                            │
-- └──────────────────────────────────────────────────────────────────────────┘

BEGIN;

-- ─── schema ────────────────────────────────────────────────────────────────

CREATE SCHEMA IF NOT EXISTS lms;

-- Prevent the Supabase-managed anon and authenticated roles from accessing
-- anything in the lms schema.  All access goes through lms_api.
REVOKE ALL ON SCHEMA lms FROM PUBLIC;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        EXECUTE 'REVOKE ALL ON SCHEMA lms FROM anon';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        EXECUTE 'REVOKE ALL ON SCHEMA lms FROM authenticated';
    END IF;
END
$$;

-- ─── runtime role ──────────────────────────────────────────────────────────
-- The FastAPI application connects through a login role that has been
-- granted lms_api, then issues SET ROLE lms_api.  This role does not own
-- the tables and cannot bypass RLS.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'lms_api') THEN
        CREATE ROLE lms_api NOINHERIT NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA lms TO lms_api;

-- ─── enum types ────────────────────────────────────────────────────────────

CREATE TYPE lms.program_pathway AS ENUM (
    'school_term',
    'saturday_club',
    'holiday'
);

CREATE TYPE lms.program_status AS ENUM (
    'draft',
    'published',
    'archived'
);

CREATE TYPE lms.program_delivery AS ENUM (
    'in_person',
    'online',
    'hybrid'
);

CREATE TYPE lms.application_status AS ENUM (
    'submitted',
    'under_review',
    'approved',
    'rejected',
    'withdrawn'
);

CREATE TYPE lms.guardian_relationship AS ENUM (
    'parent',
    'guardian',
    'grandparent',
    'sibling',
    'other'
);

CREATE TYPE lms.application_audit_event_type AS ENUM (
    'submitted',
    'status_changed',
    'reviewed',
    'withdrawn'
);

-- ─── updated_at trigger function ───────────────────────────────────────────

CREATE OR REPLACE FUNCTION lms.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─── programs ──────────────────────────────────────────────────────────────

CREATE TABLE lms.programs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pathway          lms.program_pathway  NOT NULL,
    title            TEXT             NOT NULL
                         CHECK (char_length(btrim(title)) BETWEEN 1 AND 200),
    slug             TEXT             NOT NULL
                         CHECK (slug ~ '^[a-z0-9]([a-z0-9-]{0,98}[a-z0-9])?$'),
    summary          TEXT             NOT NULL
                         CHECK (char_length(btrim(summary)) BETWEEN 1 AND 500),
    description      TEXT             NOT NULL
                         CHECK (char_length(btrim(description)) BETWEEN 1 AND 5000),
    delivery         lms.program_delivery NOT NULL,
    status           lms.program_status   NOT NULL DEFAULT 'draft',

    applications_enabled   BOOLEAN NOT NULL DEFAULT false,
    applications_open_at   TIMESTAMPTZ,
    applications_close_at  TIMESTAMPTZ,

    starts_on        DATE,
    ends_on          DATE,

    max_enrolments   SMALLINT CHECK (max_enrolments > 0),
    min_age_years    SMALLINT CHECK (min_age_years > 0),
    max_age_years    SMALLINT CHECK (max_age_years > 0),

    display_order    SMALLINT NOT NULL DEFAULT 0,

    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT programs_slug_unique UNIQUE (slug),

    CONSTRAINT programs_date_range_valid CHECK (
        starts_on IS NULL OR ends_on IS NULL OR ends_on >= starts_on
    ),
    CONSTRAINT programs_age_range_valid CHECK (
        min_age_years IS NULL OR max_age_years IS NULL
        OR max_age_years >= min_age_years
    ),
    CONSTRAINT programs_application_window_valid CHECK (
        applications_open_at IS NULL OR applications_close_at IS NULL
        OR applications_close_at > applications_open_at
    )
);

CREATE INDEX programs_pathway_status_idx
    ON lms.programs (pathway, status);
CREATE INDEX programs_status_display_order_idx
    ON lms.programs (status, display_order);

CREATE TRIGGER programs_set_updated_at
    BEFORE UPDATE ON lms.programs
    FOR EACH ROW
    EXECUTE FUNCTION lms.set_updated_at();

-- ─── enrolment applications ────────────────────────────────────────────────

CREATE TABLE lms.enrolment_applications (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    idempotency_key  UUID    NOT NULL,

    request_fingerprint TEXT NOT NULL
                         CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),

    program_id       UUID    NOT NULL REFERENCES lms.programs (id),

    guardian_name    TEXT    NOT NULL
                         CHECK (char_length(btrim(guardian_name)) BETWEEN 1 AND 200),
    guardian_email   TEXT    NOT NULL
                         CHECK (char_length(btrim(guardian_email)) BETWEEN 5 AND 254),
    guardian_phone   TEXT
                         CHECK (guardian_phone IS NULL
                                OR char_length(btrim(guardian_phone)) BETWEEN 5 AND 30),
    guardian_relationship lms.guardian_relationship NOT NULL,

    learner_name     TEXT    NOT NULL
                         CHECK (char_length(btrim(learner_name)) BETWEEN 1 AND 200),
    learner_age_years SMALLINT NOT NULL
                         CHECK (learner_age_years BETWEEN 1 AND 99),

    notes            TEXT
                         CHECK (notes IS NULL
                                OR char_length(notes) <= 1000),

    declaration_accepted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    declaration_version     SMALLINT    NOT NULL DEFAULT 1
                         CHECK (declaration_version > 0),

    status           lms.application_status NOT NULL DEFAULT 'submitted',
    submitted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at      TIMESTAMPTZ,

    reference        TEXT    NOT NULL
                         CHECK (char_length(btrim(reference)) BETWEEN 1 AND 50),

    CONSTRAINT applications_idempotency_key_unique UNIQUE (idempotency_key),
    CONSTRAINT applications_reference_unique UNIQUE (reference)
);

CREATE INDEX enrolment_applications_program_idx
    ON lms.enrolment_applications (program_id, status);
CREATE INDEX enrolment_applications_email_idx
    ON lms.enrolment_applications (guardian_email);
CREATE INDEX enrolment_applications_submitted_at_idx
    ON lms.enrolment_applications (submitted_at DESC);

-- ─── application audit events ──────────────────────────────────────────────

CREATE TABLE lms.application_audit_events (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id   UUID    NOT NULL
                         REFERENCES lms.enrolment_applications (id),
    event_type       lms.application_audit_event_type NOT NULL,
    actor_id         UUID,
    detail           JSONB,
    occurred_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX application_audit_events_application_idx
    ON lms.application_audit_events (application_id, occurred_at);

-- ─── grants for lms_api ────────────────────────────────────────────────────
-- Principle of least privilege:
--   • Programs: read-only for public listings.
--   • Applications: INSERT on submission columns; SELECT ONLY on receipt/idempotency columns.
--     Personal data columns are NOT selectable by lms_api.
--   • Audit events: INSERT on submission events only.
--   • Administrator reviews require separate future grants.

GRANT SELECT ON lms.programs TO lms_api;

GRANT INSERT (
    idempotency_key,
    request_fingerprint,
    program_id,
    guardian_name,
    guardian_email,
    guardian_phone,
    guardian_relationship,
    learner_name,
    learner_age_years,
    notes,
    declaration_version,
    reference
) ON lms.enrolment_applications TO lms_api;

GRANT SELECT (
    id,
    idempotency_key,
    request_fingerprint,
    program_id,
    status,
    submitted_at,
    reference
) ON lms.enrolment_applications TO lms_api;

GRANT INSERT (
    application_id,
    event_type,
    actor_id,
    detail
) ON lms.application_audit_events TO lms_api;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA lms TO lms_api;

-- ─── row-level security ────────────────────────────────────────────────────

ALTER TABLE lms.programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE lms.enrolment_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE lms.application_audit_events ENABLE ROW LEVEL SECURITY;

-- Programs: lms_api can read only published programs.
CREATE POLICY programs_api_read ON lms.programs
    FOR SELECT TO lms_api
    USING (status = 'published');

-- Applications: lms_api can look up receipt records by idempotency key.
CREATE POLICY applications_api_select ON lms.enrolment_applications
    FOR SELECT TO lms_api
    USING (true);

-- Applications: lms_api can insert new applications only when:
--   1. Initial status is 'submitted'
--   2. Not reviewed (reviewed_at IS NULL)
--   3. The program is published, enabled, and currently in its application window
CREATE POLICY applications_api_insert ON lms.enrolment_applications
    FOR INSERT TO lms_api
    WITH CHECK (
        status = 'submitted'
        AND reviewed_at IS NULL
        AND EXISTS (
            SELECT 1 FROM lms.programs p
            WHERE p.id = program_id
              AND p.status = 'published'
              AND p.applications_enabled = true
              AND (p.applications_open_at IS NULL OR now() >= p.applications_open_at)
              AND (p.applications_close_at IS NULL OR now() < p.applications_close_at)
        )
    );

-- Audit events: lms_api can insert only 'submitted' events without an authenticated actor.
CREATE POLICY audit_api_insert ON lms.application_audit_events
    FOR INSERT TO lms_api
    WITH CHECK (
        event_type = 'submitted'
        AND actor_id IS NULL
    );

COMMIT;
