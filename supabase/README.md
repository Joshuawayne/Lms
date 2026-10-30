# Database workspace

Supabase provides PostgreSQL for this project. Keep ordered SQL migrations in
`migrations/` as the single schema-change history. SQL executed manually through
Supabase must also be preserved as a reviewed, reproducible migration.

## Schema isolation

All application tables and types live in the private `lms` schema. This schema
is **not** exposed through the Supabase PostgREST / Data API. The `anon` and
`authenticated` roles have no grants on `lms` objects.

Access from the FastAPI backend goes through the `lms_api` role, which has
least-privilege grants and is subject to row-level security policies.

## Runtime role setup

The migration creates an `lms_api` role (`NOINHERIT NOLOGIN`). A **login role**
must be created per environment and granted `lms_api`:

```sql
CREATE ROLE lms_fastapi LOGIN PASSWORD '...' IN ROLE lms_api;
```

The FastAPI application issues `SET ROLE lms_api` after connecting. This ensures
the connection operates under the restricted grants and RLS policies defined in
the migration, not under the login role's own privileges.

**Do not use the migration owner, `postgres`, or any superuser role as the
FastAPI runtime connection.**

## Migrations

| Migration | Purpose |
| --- | --- |
| `20261028000001_programs_and_applications.sql` | Private `lms` schema, `lms_api` role, programs catalogue, enrolment applications, audit events, grants and RLS policies. |

Apply migrations through the Supabase dashboard SQL editor, the Supabase CLI,
or `psql` connected as the migration owner. Do not create parallel Alembic or
ORM auto-create histories.

## Development seed data

`seed-development.sql` inserts example programs as **draft** with applications
disabled. It is not a migration and must not be applied in production.

Always apply the seed script using a **maintenance or migration owner connection**,
not the restricted FastAPI runtime connection (`lms_api` / `lms_fastapi`):

```powershell
# Run as migration owner (has INSERT privileges on lms.programs):
psql "$LMS_MIGRATION_DATABASE_URL" -f supabase/seed-development.sql
```

> **Note on Application Windows:**
> Publishing seed programs (`SET status = 'published', applications_enabled = true`)
> does **not** override their future application windows (`applications_open_at` is in
> November 2026). Attempting public submissions prior to `applications_open_at` will
> be rejected by database RLS and the application repository.

To test the public application submission flow in development while keeping the
seed file safe and reproducible, explicitly shift the window on a single program:

```sql
UPDATE lms.programs
SET status = 'published',
    applications_enabled = true,
    applications_open_at = now() - interval '1 hour',
    applications_close_at = now() + interval '30 days'
WHERE slug = 'saturday-coding-club-jan-2027';
```

To restore the program to default seed state after testing:

```sql
UPDATE lms.programs
SET status = 'draft',
    applications_enabled = false,
    applications_open_at = '2026-11-15 06:00:00+03',
    applications_close_at = '2027-01-05 23:59:59+03'
WHERE slug = 'saturday-coding-club-jan-2027';
```

## Verification

After applying the migration, verify:

1. **Schema isolation**: `SELECT * FROM lms.programs;` works as the migration
   owner but fails as `anon` or `authenticated`.
2. **RLS enforcement**: Connect as `lms_api` and confirm that only published
   programs are visible, and draft/archived programs return no rows.
3. **Column-level grants and receipt scoping**: `lms_api` can select only non-personal receipt fields
   (`id`, `idempotency_key`, `request_fingerprint`, `program_id`, `status`, `submitted_at`, `reference`)
   on `enrolment_applications`, scoped strictly by the current request's `idempotency_key`. Direct queries for personal contact details are rejected by PostgreSQL column-level security.
4. **Submission availability & audit RLS**: `lms_api` can insert an application only if the program
   is published, applications are enabled, and the submission timestamp is within the open/close window.
   Audit event insertion requires `event_type = 'submitted'` and `actor_id IS NULL`.
5. **No mutation**: `lms_api` cannot execute `UPDATE` or `DELETE` on applications or audit events.
6. **Trigger**: Update a program row and confirm `updated_at` changes automatically.

These checks require a live Supabase connection. The backend readiness endpoint
returns HTTP 503 until credentials and TLS verification are configured.

## Open decisions

Add constraints, indexes, transactions, role grants and RLS tests alongside the
schema. `seed.sql` is reserved for reference data shared across environments.
Backups, restoration and retention policies need definition and verification.

The scaffold does not initialize a Supabase project, run SQL or select Supabase
Auth, Storage or Edge Functions. Configure only the PostgreSQL connection in the
backend.
