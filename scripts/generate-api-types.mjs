import { writeFile, mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import openapiTS, { astToString } from 'openapi-typescript'

export async function generateApiTypes() {
  const ast = await openapiTS(new URL('../contracts/api/v1/openapi.json', import.meta.url))
  return '// Generated from contracts/api/v1/openapi.json. Run npm run contracts:generate.\n'
    + astToString(ast)
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const directory = new URL('../frontend/app/api/generated/', import.meta.url)
  await mkdir(directory, { recursive: true })
  await writeFile(new URL('types.ts', directory), await generateApiTypes(), 'utf8')
  console.log('Generated frontend/app/api/generated/types.ts')
}
