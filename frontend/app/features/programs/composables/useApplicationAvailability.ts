/**
 * Determines the availability state of a program's application window.
 *
 * Returns a human-readable status and whether applications can currently
 * be submitted based on the program's enabled flag and open/close timestamps.
 */
import type { components } from '~/api/generated/types'

type ProgramSummary = components['schemas']['ProgramSummaryResponse']
type ProgramDetail = components['schemas']['ProgramDetailResponse']

export interface ApplicationAvailability {
  /** Whether the form should be shown and submissions accepted */
  canApply: boolean
  /** Human-readable status label */
  label: string
  /** CSS-friendly status key for styling */
  status: 'open' | 'closed' | 'not_yet' | 'disabled'
}

export function useApplicationAvailability(
  program: ProgramSummary | ProgramDetail | null | undefined,
): ApplicationAvailability {
  if (!program) {
    return { canApply: false, label: 'Unavailable', status: 'closed' }
  }

  if (!program.applications_enabled) {
    return { canApply: false, label: 'Applications not available', status: 'disabled' }
  }

  const now = new Date()

  if (program.applications_open_at) {
    const openDate = new Date(program.applications_open_at)
    if (now < openDate) {
      return {
        canApply: false,
        label: `Applications open ${openDate.toLocaleDateString('en-KE', { day: 'numeric', month: 'long', year: 'numeric' })}`,
        status: 'not_yet',
      }
    }
  }

  if (program.applications_close_at) {
    const closeDate = new Date(program.applications_close_at)
    if (now >= closeDate) {
      return { canApply: false, label: 'Applications have closed', status: 'closed' }
    }
  }

  return { canApply: true, label: 'Applications open', status: 'open' }
}
