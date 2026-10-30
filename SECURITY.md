# Security development status

This is a development scaffold. The public API exposes health endpoints only.
Identity providers, authenticated sessions, object-level authorization and private
file storage are future work. Do not add learner-facing data endpoints until the
access matrix and corresponding denial tests are implemented.

Keep PostgreSQL credentials in `backend/.env`. Production runtime roles must have
appropriate privileges and an intentional RLS strategy matching the actual database
execution context. Use CA and hostname verification for Supabase connections.

Report suspected vulnerabilities privately to the project owner. Include the
request ID and reproduction steps, avoiding credentials or children's information.
