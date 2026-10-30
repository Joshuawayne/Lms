/** Disposable SQL probe of both uploaded migrations; not native multi-session or hosted verification. */
import { readFileSync } from 'node:fs'
import { PGlite } from '/workspace/scratch/b007f44caea1/review-tools-20261030/node_modules/@electric-sql/pglite/dist/index.js'

const db = new PGlite()
try {
  for (const file of ['20261028000001_programs_and_applications.sql', '20261029000001_scope_application_receipts.sql']) {
    await db.exec(readFileSync(new URL('../progress-20261030/supabase/migrations/' + file, import.meta.url), 'utf8'))
  }
  await db.exec(`INSERT INTO lms.programs(id,pathway,title,slug,summary,description,delivery,status,applications_enabled)
    VALUES ('11111111-1111-4111-8111-111111111111','holiday','Synthetic','synthetic','Synthetic','Synthetic','online','published',true);
    INSERT INTO lms.enrolment_applications(idempotency_key,request_fingerprint,program_id,guardian_name,guardian_email,guardian_relationship,learner_name,learner_age_years,reference)
    VALUES ('22222222-2222-4222-8222-222222222222',repeat('a',64),'11111111-1111-4111-8111-111111111111','Synthetic','synthetic@example.com','parent','Synthetic',10,'SYNTHETIC-A'),
    ('33333333-3333-4333-8333-333333333333',repeat('b',64),'11111111-1111-4111-8111-111111111111','Synthetic','synthetic@example.com','parent','Synthetic',10,'SYNTHETIC-B');
    SET ROLE lms_api;`)
  const count = async () => (await db.query('SELECT reference FROM lms.enrolment_applications')).rows.length
  console.log(JSON.stringify({check:'missing_scope',visible:await count(),expected:0}))
  for (const [label, key, expected] of [
    ['correct_scope','22222222-2222-4222-8222-222222222222',1],
    ['wrong_scope','44444444-4444-4444-8444-444444444444',0],
    ['malformed_scope','not-a-uuid',0],
  ]) {
    await db.exec('BEGIN')
    await db.query("SELECT set_config('lms.request_key',$1,true)",[key])
    const visible = await count()
    console.log(JSON.stringify({check:label,visible,expected}))
    if(visible!==expected) throw new Error('Receipt policy mismatch')
    await db.exec('COMMIT')
  }
  console.log(JSON.stringify({check:'scope_after_commit',visible:await count(),expected:0}))
  try {
    await db.query('SELECT guardian_email FROM lms.enrolment_applications')
    throw new Error('Personal columns unexpectedly readable')
  } catch (error) {
    if(error.code!=='42501') throw error
    console.log(JSON.stringify({check:'personal_columns',sqlstate:error.code,expected:'42501'}))
  }
  console.log('LIMIT: PGlite SQL inspection only; native concurrency and hosted Supabase not tested.')
} finally { await db.close() }
