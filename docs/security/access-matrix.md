# Access matrix to implement

All entries below require authenticated, assigned roles and record-level checks.
They describe the intended product and are not implemented in this scaffold.

| Actor | Intended scope |
| --- | --- |
| Administrator | Authorized people, programs, classes, imports, records and reports |
| Teacher | Assigned classes/learners and authorized content/assessment workflows |
| Learner | Own permitted lessons, assignments, submissions, feedback, goals and portfolio |
| Parent/guardian | Appropriate released records for verified linked children |

Changing a selected role, program, class or child cannot grant access. Teachers need
appropriate membership; guardians need a verified link. Draft assessments, private
teacher reflections and unpublished reports require explicit visibility policies.

Enforce access in FastAPI on each operation and object. Select least-privilege
database roles and implement/test RLS for the real connection context. Owner or
bypass roles can defeat RLS; server database access does not automatically carry
Supabase Auth's user identity. Test both allowed and denied cases before exposing data.
