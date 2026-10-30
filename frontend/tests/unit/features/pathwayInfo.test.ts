/**
 * Unit tests for pathwayInfo helpers.
 */
import { describe, expect, it } from 'vitest'
import {
  getPathwayInfo,
  PATHWAY_FILTER_OPTIONS,
} from '../../../app/features/programs/composables/pathwayInfo'

describe('pathwayInfo helper', () => {
  it('returns label, icon, and color for school_term pathway', () => {
    const info = getPathwayInfo('school_term')
    expect(info.label).toBe('School-Term Program')
    expect(info.short).toBe('School Term')
    expect(info.icon).toBe('i-lucide-book-open')
    expect(info.color).toContain('purple')
  })

  it('returns label, icon, and color for saturday_club pathway', () => {
    const info = getPathwayInfo('saturday_club')
    expect(info.label).toBe('Saturday Coding Club')
    expect(info.short).toBe('Saturday Club')
    expect(info.icon).toBe('i-lucide-calendar-days')
    expect(info.color).toContain('yellow')
  })

  it('returns label, icon, and color for holiday pathway', () => {
    const info = getPathwayInfo('holiday')
    expect(info.label).toBe('Holiday Program')
    expect(info.short).toBe('Holiday')
    expect(info.icon).toBe('i-lucide-sun')
    expect(info.color).toContain('pink')
  })

  it('includes all filter options including "All programs"', () => {
    expect(PATHWAY_FILTER_OPTIONS).toHaveLength(4)
    expect(PATHWAY_FILTER_OPTIONS[0]).toEqual({ value: null, label: 'All programs' })
    expect(PATHWAY_FILTER_OPTIONS.map((o) => o.value)).toEqual([
      null,
      'school_term',
      'saturday_club',
      'holiday',
    ])
  })
})
