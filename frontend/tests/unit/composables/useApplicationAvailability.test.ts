/**
 * Unit tests for useApplicationAvailability composable.
 */
import { describe, expect, it } from 'vitest'
import { useApplicationAvailability } from '../../../app/features/programs/composables/useApplicationAvailability'

type ProgramInput = NonNullable<Parameters<typeof useApplicationAvailability>[0]>

function makeProgram(overrides: Partial<ProgramInput> = {}): ProgramInput {
  return {
    id: 'test-id',
    slug: 'test-slug',
    title: 'Test Program',
    summary: 'Test summary',
    status: 'published',
    pathway: 'school_term',
    delivery: 'in_person',
    display_order: 1,
    min_age_years: 7,
    max_age_years: 12,
    max_enrolments: 20,
    starts_on: null,
    ends_on: null,
    applications_enabled: true,
    applications_open_at: null,
    applications_close_at: null,
    ...overrides,
  }
}

describe('useApplicationAvailability', () => {
  it('returns unavailable when program is null or undefined', () => {
    expect(useApplicationAvailability(null)).toEqual({
      canApply: false,
      label: 'Unavailable',
      status: 'closed',
    })
    expect(useApplicationAvailability(undefined)).toEqual({
      canApply: false,
      label: 'Unavailable',
      status: 'closed',
    })
  })

  it('returns disabled when applications_enabled is false', () => {
    const program = makeProgram({
      applications_enabled: false,
      applications_open_at: null,
      applications_close_at: null,
    })

    const result = useApplicationAvailability(program)
    expect(result.canApply).toBe(false)
    expect(result.status).toBe('disabled')
    expect(result.label).toBe('Applications not available')
  })

  it('returns not_yet when applications_open_at is in the future', () => {
    const futureDate = new Date(Date.now() + 86400000).toISOString()
    const program = makeProgram({
      applications_enabled: true,
      applications_open_at: futureDate,
      applications_close_at: null,
    })

    const result = useApplicationAvailability(program)
    expect(result.canApply).toBe(false)
    expect(result.status).toBe('not_yet')
    expect(result.label).toContain('Applications open')
  })

  it('returns closed when applications_close_at has passed', () => {
    const pastDate = new Date(Date.now() - 86400000).toISOString()
    const program = makeProgram({
      applications_enabled: true,
      applications_open_at: new Date(Date.now() - 172800000).toISOString(),
      applications_close_at: pastDate,
    })

    const result = useApplicationAvailability(program)
    expect(result.canApply).toBe(false)
    expect(result.status).toBe('closed')
    expect(result.label).toBe('Applications have closed')
  })

  it('returns open when enabled and within date window', () => {
    const program = makeProgram({
      applications_enabled: true,
      applications_open_at: new Date(Date.now() - 86400000).toISOString(),
      applications_close_at: new Date(Date.now() + 86400000).toISOString(),
    })

    const result = useApplicationAvailability(program)
    expect(result.canApply).toBe(true)
    expect(result.status).toBe('open')
    expect(result.label).toBe('Applications open')
  })
})
