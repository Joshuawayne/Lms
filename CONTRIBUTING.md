# Development rules

Read `docs/product/system-algorithm.md` and `docs/engineering/solid-and-dependencies.md`
before implementing a workflow. Add meaningful tests for the rules and failure
paths being introduced. Update contracts and documentation in the same change.

Use `uv sync --project backend --frozen`, `npm ci`, and `npm ci --prefix frontend`
for reproducible installation.
Run `scripts/check.ps1` before submitting work. Keep secrets, actual learner records,
media evidence, dependency folders and build outputs out of version control.

No module is complete merely because its folder exists. Keep public functions,
request/response models and domain records explicitly typed. Explain non-obvious
decisions and invariants in comments. Review the algorithm and authorization scope
alongside code style.
