import { readFile } from 'node:fs/promises'
import { generateApiTypes } from './generate-api-types.mjs'

const current = await readFile(new URL('../frontend/app/api/generated/types.ts', import.meta.url), 'utf8')
if (current !== await generateApiTypes()) {
  console.error('Frontend API types are stale. Run npm run contracts:generate.')
  process.exitCode = 1
} else {
  console.log('Frontend API types match the OpenAPI contract.')
}
