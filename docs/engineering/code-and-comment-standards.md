# Code and comments

Use concrete names, focused functions and explicit public types. Keep database,
API and UI representations separate where their responsibilities differ. Name
states, errors and transitions instead of relying on unexplained strings or numbers.

Comments explain why, invariants, security assumptions or non-obvious decisions.
Docstrings describe contracts, inputs/outputs and important failures where useful.
Avoid comments that merely repeat the code. Keep documentation current with changes.

Run Ruff formatting/linting, mypy and import checks for Python, and ESLint and Nuxt
type checking for the frontend. Use generated API types rather than handwritten
copies of backend request/response models. Do not catch failures silently or expose
raw exceptions, secrets or sensitive records in user-facing errors.
