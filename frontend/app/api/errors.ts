export interface ApiProblem {
  title: string
  status: number
  detail?: string
  request_id?: string
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Read a problem response while allowing ordinary network failures to fall back safely. */
export function readApiProblem(error: unknown): ApiProblem | undefined {
  if (!isRecord(error) || !isRecord(error.data)) return undefined

  const data = error.data
  if (
    typeof data.title !== 'string'
    || typeof data.status !== 'number'
    || !Number.isInteger(data.status)
    || data.status < 400
    || data.status > 599
  ) return undefined

  return {
    title: data.title,
    status: data.status,
    detail: typeof data.detail === 'string' ? data.detail : undefined,
    request_id: typeof data.request_id === 'string' ? data.request_id : undefined,
  }
}
