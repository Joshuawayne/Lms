-- Development-only seed data for manual local testing.
--
-- IMPORTANT: This file is NOT a migration. Do not apply it in production.
-- Run it manually against a development database using a migration or maintenance
-- connection (such as LMS_MIGRATION_DATABASE_URL or connected as the migration owner):
--
--   psql "$LMS_MIGRATION_DATABASE_URL" -f supabase/seed-development.sql
--
-- DO NOT use the restricted FastAPI runtime connection (LMS_DATABASE_URL / lms_api).
-- The lms_api role has least-privilege SELECT-only grants on lms.programs and will
-- be denied INSERT privileges on the programs table.
--
-- All programs are inserted as DRAFT with applications_enabled = false.
--
-- Application Window Notice:
--   Publishing and enabling seed programs (status = 'published', applications_enabled = true)
--   does NOT override their scheduled application windows. The default seeds specify
--   future opening dates (e.g. 2026-11-01 and 2026-11-15). Any public submission attempt
--   prior to applications_open_at will be rejected by database RLS and the application repository.
--
-- Development-only open window testing:
--   To test the public application submission flow locally while keeping default seeds
--   safe (unpublished and disabled), explicitly shift the window on a single program:
--
--   UPDATE lms.programs
--   SET status = 'published',
--       applications_enabled = true,
--       applications_open_at = now() - interval '1 hour',
--       applications_close_at = now() + interval '30 days'
--   WHERE slug = 'saturday-coding-club-jan-2027';
--
--   To restore the program to default seed state after testing:
--
--   UPDATE lms.programs
--   SET status = 'draft',
--       applications_enabled = false,
--       applications_open_at = '2026-11-15 06:00:00+03',
--       applications_close_at = '2027-01-05 23:59:59+03'
--   WHERE slug = 'saturday-coding-club-jan-2027';
--
-- Date verification (2026–2027 calendar):
--   December 2026: 15=Tue  16=Wed  17=Thu  18=Fri  19=Sat (Tuesday–Saturday camp).
--   January 2027:  1=Fri   2=Sat   3=Sun   ... 8=Fri 9=Sat 10=Sun
--   April 2027:    1=Thu   2=Fri   3=Sat   ... 10=Sat 11=Sun 12=Mon
--   Saturday Club dates below use 2027-01-09 (Sat) through 2027-04-10 (Sat).

INSERT INTO lms.programs (
    pathway, title, slug, summary, description, delivery, status,
    applications_enabled,
    applications_open_at, applications_close_at,
    starts_on, ends_on, min_age_years, max_age_years, display_order
) VALUES
(
    'school_term',
    'Coding & Robotics — Term 1 2027',
    'coding-robotics-term1-2027',
    'Weekly coding and robotics sessions during the school term. Learners build projects, solve real problems and present their work.',
    'Our school-term program runs every week during the term. Learners work through structured projects in coding and robotics, develop problem-solving skills and finish the term with a portfolio of completed work. Sessions combine guided instruction, collaborative building and individual challenges.',
    'in_person',
    'draft',
    false,
    '2026-11-01 06:00:00+03',
    '2026-12-15 23:59:59+03',
    '2027-01-13',
    '2027-04-04',
    7, 16, 1
),
(
    'saturday_club',
    'Saturday Coding Club — Jan 2027',
    'saturday-coding-club-jan-2027',
    'Every Saturday morning. Drop in, build something, meet other young makers.',
    'The Saturday Coding Club meets every Saturday morning for two hours of hands-on building. Learners choose from guided challenges or continue their own projects. New learners are welcome any Saturday. Topics rotate across web development, games, electronics and robotics.',
    'in_person',
    'draft',
    false,
    '2026-11-15 06:00:00+03',
    '2027-01-05 23:59:59+03',
    '2027-01-09',
    '2027-04-10',
    8, 17, 1
),
(
    'holiday',
    'December Holiday Coding Camp 2026',
    'holiday-coding-camp-dec-2026',
    'An intensive week of coding, robotics and creative projects during the December holiday.',
    'Our holiday camp runs for five full days. Learners tackle a theme-based project from concept to finished product. Past themes have included smart homes, games and community solutions. Each day combines new skills, collaborative building and creative presentation. Recordings and notes are shared with participants after the camp.',
    'in_person',
    'draft',
    false,
    '2026-11-01 06:00:00+03',
    '2026-12-08 23:59:59+03',
    '2026-12-15',
    '2026-12-19',
    7, 16, 1
)
ON CONFLICT (slug) DO NOTHING;
