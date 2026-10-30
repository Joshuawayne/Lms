/**
 * Maps API pathway enum values to human-readable labels, short descriptions
 * and icon names for consistent display across program cards and filters.
 */
import type { components } from '~/api/generated/types'

type Pathway = components['schemas']['Pathway']

export interface PathwayInfo {
  label: string
  short: string
  icon: string
  color: string
}

const PATHWAY_MAP: Record<Pathway, PathwayInfo> = {
  school_term: {
    label: 'School-Term Program',
    short: 'School Term',
    icon: 'i-lucide-book-open',
    color: 'var(--color-purple-500)',
  },
  saturday_club: {
    label: 'Saturday Coding Club',
    short: 'Saturday Club',
    icon: 'i-lucide-calendar-days',
    color: 'var(--color-yellow-500)',
  },
  holiday: {
    label: 'Holiday Program',
    short: 'Holiday',
    icon: 'i-lucide-sun',
    color: 'var(--color-pink-500)',
  },
}

export function getPathwayInfo(pathway: Pathway): PathwayInfo {
  return PATHWAY_MAP[pathway]
}

/** All pathway options for filter UI, with an "all" entry prepended. */
export const PATHWAY_FILTER_OPTIONS: Array<{ value: Pathway | null; label: string }> = [
  { value: null, label: 'All programs' },
  { value: 'school_term', label: 'School Term' },
  { value: 'saturday_club', label: 'Saturday Club' },
  { value: 'holiday', label: 'Holiday' },
]
