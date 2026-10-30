# Whole-system algorithm

Every implemented business use case must trace these steps:

1. Establish the authenticated actor, assigned role, selected program/class/child,
   and the relevant record context.
2. Authorize the operation and the specific records involved.
3. Validate input, references, current version, state and retry/concurrency conditions.
4. Execute the appropriate workflow through application use cases and domain rules.
5. Persist the outcome, version, evidence and required audit events atomically.
6. Refresh only the views/reports the recipient may see, respecting release rules.
7. Offer an explainable next action based on suitable evidence and reviewed feedback.

Suggestions support a workflow; they cannot grant permissions, rewrite assessment
evidence, publish reports, or silently change teacher decisions. Missing, interrupted
or unobserved work does not prove low ability or poor values.

Each use case must document actor, scope, inputs, validations, transitions, stored
outcome, publication rules and recovery/next action. Use accepted events or durable
job delivery for work that must survive a process restart; do not treat an in-process
background task as a durable queue.

Imports require a preview and explicit confirmation. Activity authoring preserves
drafts and published versions. Learner attempts preserve assigned versions and work
in progress. Teachers can request more evidence and override recommendations with
an explanation. Parents see only approved information for a verified linked child.

Implementation status: these business use cases are pending. The current scaffold
exposes infrastructure health endpoints and a browser connectivity check only.
