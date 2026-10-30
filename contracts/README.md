# Shared contracts

`api/v1/openapi.json` is generated from FastAPI schemas. The matching frontend types
are generated into `frontend/app/api/generated/types.ts`. Generate both through
`npm run contracts:generate` and verify through `npm run contracts:check`.

`activities/v1/blocks` is reserved for authored, versioned activity configuration
schemas. These need deliberate design and will be used by editor/player validation
and the backend. No activity schemas or H5P compatibility are implemented yet.

Keep valid/error examples beside the contracts as resource workflows are introduced.
