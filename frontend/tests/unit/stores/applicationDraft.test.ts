/**
 * Unit tests for applicationDraft Pinia store.
 */
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { useApplicationDraftStore } from '../../../app/stores/applicationDraft'

describe('useApplicationDraftStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('starts with blank default state', () => {
    const store = useApplicationDraftStore()
    expect(store.guardianName).toBe('')
    expect(store.guardianEmail).toBe('')
    expect(store.guardianRelationship).toBe('parent')
    expect(store.learnerName).toBe('')
    expect(store.learnerAgeYears).toBeNull()
    expect(store.declarationAccepted).toBe(false)
    expect(store.hasReceipt).toBe(false)
    expect(store.submitting).toBe(false)
  })

  it('builds payload and generates an idempotency key', () => {
    const store = useApplicationDraftStore()
    store.guardianName = 'Grace Hopper'
    store.guardianEmail = 'grace@example.com'
    store.learnerName = 'Ada Lovelace'
    store.learnerAgeYears = 12
    store.declarationAccepted = true

    const payload = store.buildPayload()
    expect(payload.idempotency_key).toBeDefined()
    expect(payload.idempotency_key.length).toBeGreaterThan(10)
    expect(payload.guardian_name).toBe('Grace Hopper')
    expect(payload.guardian_email).toBe('grace@example.com')
    expect(payload.learner_name).toBe('Ada Lovelace')
    expect(payload.learner_age_years).toBe(12)
    expect(payload.declaration_version).toBe(1)
  })

  it('generates a fresh idempotency key for each new submission build', () => {
    const store = useApplicationDraftStore()
    store.guardianName = 'Grace Hopper'
    store.guardianEmail = 'grace@example.com'
    store.learnerName = 'Ada Lovelace'
    store.learnerAgeYears = 12
    store.declarationAccepted = true

    const first = store.buildPayload('program-a')
    const second = store.buildPayload('program-b')

    expect(first.idempotency_key).not.toBe(second.idempotency_key)
  })

  it('preserves idempotency key when retrying an uncertain attempt', () => {
    const store = useApplicationDraftStore()
    store.guardianName = 'Grace Hopper'
    store.guardianEmail = 'grace@example.com'
    store.learnerName = 'Ada Lovelace'
    store.learnerAgeYears = 12
    store.declarationAccepted = true

    const { attemptId, payload } = store.beginSubmission('coding-camp')
    store.recordUncertainAttempt({
      programTarget: 'coding-camp',
      payload,
      attemptId,
      timestamp: Date.now(),
    })

    const pending = store.uncertainAttemptForProgram('coding-camp')
    expect(pending).not.toBeNull()
    expect(pending?.payload.idempotency_key).toBe(payload.idempotency_key)
  })

  it('records receipt and clears personal fields', () => {
    const store = useApplicationDraftStore()
    store.guardianName = 'Grace Hopper'
    store.guardianEmail = 'grace@example.com'
    store.learnerName = 'Ada Lovelace'

    store.recordReceipt({
      id: 'app-uuid',
      reference: 'JJ-2026-XYZ',
      status: 'submitted',
      is_retry: false,
      submitted_at: '2026-10-28T10:00:00Z',
      program_id: 'prog-uuid',
    })

    expect(store.hasReceipt).toBe(true)
    expect(store.receipt?.reference).toBe('JJ-2026-XYZ')
    expect(store.guardianName).toBe('')
    expect(store.guardianEmail).toBe('')
    expect(store.learnerName).toBe('')
  })

  it('resets all state on resetAll without warnings', () => {
    const store = useApplicationDraftStore()
    store.guardianName = 'Grace Hopper'
    store.submissionError = 'Something went wrong'
    store.receipt = {
      id: 'app-uuid',
      reference: 'JJ-2026-XYZ',
      status: 'submitted',
      is_retry: false,
      submitted_at: '2026-10-28T10:00:00Z',
      program_id: 'prog-uuid',
    }

    store.resetAll()
    expect(store.guardianName).toBe('')
    expect(store.submissionError).toBeNull()
    expect(store.receipt).toBeNull()
    expect(store.hasReceipt).toBe(false)
  })
})
