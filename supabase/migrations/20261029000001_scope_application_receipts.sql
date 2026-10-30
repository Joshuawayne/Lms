-- Migration: scope enrolment-application receipt reads to the current request key
-- Created:  2026-10-29
-- Corrects: 20261028000001_programs_and_applications.sql
--
-- WHY THIS EXISTS
--   The original migration (already applied to the local development database)
--   created the receipt SELECT policy as USING (true).  That let the runtime
--   role read the receipt columns of EVERY application, contradicting the
--   documented request-key isolation.  The applied migration is left untouched
--   so history stays truthful; this migration supersedes the policy.
--
-- HOW RECEIPT ISOLATION WORKS
--   The backend opens a transaction, sets a transaction-local setting
--   (set_config('lms.request_key', <uuid>, true)) and only then reads or inserts.
--   The SELECT policy compares each row's idempotency_key with that setting.
--     * Setting absent, empty or not a UUID  -> lms.current_request_key() is NULL
--       -> the comparison is NULL -> NO rows are visible (fail closed).
--     * Setting present -> only the receipt row with that exact key is visible,
--       which also covers INSERT ... RETURNING and the concurrent-replay lookup.
--   Because the setting is transaction-local (is_local = true) PostgreSQL clears
--   it automatically at COMMIT or ROLLBACK, so a pooled/reused connection can
--   never carry one request's scope into the next request.
--
-- WHAT THIS DOES NOT DO
--   The scope is defence in depth against application bugs and accidental
--   enumeration.  It is not a boundary against a fully compromised backend,
--   which can set the setting itself.  Column-level denial of personal data
--   (guardian/learner columns) is unchanged and remains the primary control.

BEGIN;

CREATE OR REPLACE FUNCTION lms.current_request_key()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
    SELECT CASE
        WHEN current_setting('lms.request_key', true)
             ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN current_setting('lms.request_key', true)::uuid
        ELSE NULL
    END
$$;

COMMENT ON FUNCTION lms.current_request_key() IS
    'Transaction-local receipt scope. NULL (fail closed) when unset or malformed.';

REVOKE ALL ON FUNCTION lms.current_request_key() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION lms.current_request_key() TO lms_api;

DROP POLICY IF EXISTS applications_api_select ON lms.enrolment_applications;

CREATE POLICY applications_api_select ON lms.enrolment_applications
    FOR SELECT TO lms_api
    USING (idempotency_key = lms.current_request_key());

COMMIT;
