import { describe, expect, it } from 'vitest'
import { readApiProblem } from '../../app/api/errors'

describe('API problem handling', () => {
  it('preserves useful problem fields and the server request ID', () => {
    expect(readApiProblem({ data: {
      title: 'Service Unavailable', status: 503, detail: 'Try again later.',
      request_id: 'request-123', private_field: 'discard-this',
    } })).toEqual({
      title: 'Service Unavailable', status: 503, detail: 'Try again later.',
      request_id: 'request-123',
    })
  })

  it('lets network failures use the interface fallback', () => {
    expect(readApiProblem(new Error('Network failure'))).toBeUndefined()
  })

  it('rejects malformed error bodies', () => {
    expect(readApiProblem({ data: { title: 'Failure', status: '503' } })).toBeUndefined()
    expect(readApiProblem({ data: { title: 'Not an error', status: 200 } })).toBeUndefined()
    expect(readApiProblem({ data: [] })).toBeUndefined()
  })

  it('ignores malformed optional fields', () => {
    expect(readApiProblem({ data: { title: 'Failure', status: 500, detail: {}, request_id: [] } }))
      .toEqual({ title: 'Failure', status: 500, detail: undefined, request_id: undefined })
  })
})
