/**
 * Application draft store — memory-only Pinia store for the application form.
 *
 * Holds guardian/learner fields, manages idempotency key lifecycle, and tracks
 * submission state and confirmed receipts scoped by program.
 *
 * Draft is intentionally memory-only (never in localStorage/sessionStorage)
 * to protect personal data and isolate requests.
 *
 * Idempotency key rules:
 *   - The submission identity includes the target program AND normalized payload fields.
 *   - Each new submission attempt generated through buildPayload receives a fresh key.
 *   - An uncertain submission snapshot and key are preserved after a lost response/network error.
 *   - Confirmed receipts are scoped to program_id so a receipt for Program A never confirms Program B.
 *   - Form fields are cleared only upon confirmed receipt for that submission.
 */
import { defineStore } from 'pinia'
import type { components } from '~/api/generated/types'

type SubmitRequest = components['schemas']['SubmitApplicationRequest']
type ReceiptResponse = components['schemas']['ApplicationReceiptResponse']
type GuardianRelationship = components['schemas']['GuardianRelationship']

/** Global monotonic counter across all store instances and resets. */
let globalAttemptSequence = 0

/** Generates a random idempotency key (UUID v4). */
export function generateKey(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.trunc(Math.random() * 16)
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export interface UncertainAttempt {
  programTarget: string
  payload: SubmitRequest
  attemptId: number
  timestamp: number
}

export interface ApplicationDraftState {
  /* Form fields */
  guardianName: string
  guardianEmail: string
  guardianPhone: string
  guardianRelationship: GuardianRelationship
  learnerName: string
  learnerAgeYears: number | null
  notes: string
  declarationAccepted: boolean

  /* Submission tracking */
  targetProgram: string
  idempotencyKey: string
  submitting: boolean
  submissionError: string | null
  currentAttemptId: number

  /* Preserved uncertain attempt after network failure for safe replay */
  uncertainAttempt: UncertainAttempt | null

  /* Receipts scoped by program_id and slug */
  receiptsByProgramId: Record<string, ReceiptResponse>
  receiptsBySlug: Record<string, ReceiptResponse>
  receipt: ReceiptResponse | null
}

export const useApplicationDraftStore = defineStore('applicationDraft', {
  state: (): ApplicationDraftState => ({
    guardianName: '',
    guardianEmail: '',
    guardianPhone: '',
    guardianRelationship: 'parent',
    learnerName: '',
    learnerAgeYears: null,
    notes: '',
    declarationAccepted: false,

    targetProgram: '',
    idempotencyKey: generateKey(),
    submitting: false,
    submissionError: null,
    currentAttemptId: 0,
    uncertainAttempt: null,

    receiptsByProgramId: {},
    receiptsBySlug: {},
    receipt: null,
  }),

  getters: {
    /** Whether the form has any entered personal data. */
    hasDraftData(): boolean {
      return !!(
        this.guardianName.trim()
        || this.guardianEmail.trim()
        || this.guardianPhone.trim()
        || this.learnerName.trim()
        || this.notes.trim()
      )
    },

    /** True when any confirmed receipt exists in this session. */
    hasReceipt(): boolean {
      return this.receipt !== null
    },

    /** Latest confirmed receipt. */
    latestReceipt(): ReceiptResponse | null {
      return this.receipt
    },

    /** Check whether a confirmed receipt exists for a specific program ID or slug. */
    receiptForProgram: (state) => (programIdOrSlug?: string | null): ReceiptResponse | null => {
      if (!programIdOrSlug) return null
      return state.receiptsByProgramId[programIdOrSlug] || state.receiptsBySlug[programIdOrSlug] || null
    },

    /** True if a confirmed receipt exists specifically for this program. */
    hasReceiptForProgram: (state) => (programIdOrSlug?: string | null): boolean => {
      if (!programIdOrSlug) return false
      return !!(state.receiptsByProgramId[programIdOrSlug] || state.receiptsBySlug[programIdOrSlug])
    },

    /** Check if there is a pending uncertain attempt for this program that can be safely retried. */
    uncertainAttemptForProgram: (state) => (programTarget: string): UncertainAttempt | null => {
      if (state.uncertainAttempt && state.uncertainAttempt.programTarget === programTarget) {
        return state.uncertainAttempt
      }
      return null
    },
  },

  actions: {
    /**
     * Builds the request payload for a specific target program.
     * Generates a fresh idempotency key for every new submission payload
     * so that submissions to different programs or distinct attempts never collide.
     * Retries of an uncertain submission reuse the saved snapshot instead.
     */
    buildPayload(targetProgramIdentifier: string = ''): SubmitRequest {
      const target = targetProgramIdentifier.trim()
      if (target) {
        this.targetProgram = target
      }

      this.idempotencyKey = generateKey()

      const fields: Omit<SubmitRequest, 'idempotency_key'> = {
        guardian_name: this.guardianName.trim(),
        guardian_email: this.guardianEmail.trim().toLowerCase(),
        guardian_phone: this.guardianPhone.trim() || null,
        guardian_relationship: this.guardianRelationship,
        learner_name: this.learnerName.trim(),
        learner_age_years: this.learnerAgeYears!,
        notes: this.notes.trim() || null,
        declaration_accepted: this.declarationAccepted,
        declaration_version: 1,
      }

      return { idempotency_key: this.idempotencyKey, ...fields }
    },

    /**
     * Begins a submission attempt with a monotonic attempt ID to guard
     * against out-of-order or late responses overwriting newer user state.
     */
    beginSubmission(targetProgram: string): { attemptId: number; payload: SubmitRequest } {
      globalAttemptSequence += 1
      this.currentAttemptId = globalAttemptSequence
      const attemptId = this.currentAttemptId
      this.submitting = true
      this.submissionError = null
      const payload = this.buildPayload(targetProgram)
      return { attemptId, payload }
    },

    /**
     * Records a successful receipt scoped to the program.
     * Guards against late or stale responses from previous attempts.
     */
    recordReceipt(receipt: ReceiptResponse, programSlug?: string, attemptId?: number) {
      if (attemptId !== undefined && attemptId !== this.currentAttemptId) {
        // Stale response from an earlier attempt; ignore to prevent draft corruption
        return
      }

      this.receipt = receipt
      if (receipt.program_id) {
        this.receiptsByProgramId[receipt.program_id] = receipt
      }
      if (programSlug) {
        this.receiptsBySlug[programSlug] = receipt
      }

      // Clear uncertain attempt since it was resolved
      this.uncertainAttempt = null
      this.submitting = false
      this.submissionError = null

      // Clear personal fields now that submission is safely confirmed
      this.clearPersonalDetails()
    },

    /**
     * Saves an uncertain attempt after network error or lost response
     * so it can be replayed safely without losing the idempotency key or fields.
     */
    recordUncertainAttempt(attempt: UncertainAttempt) {
      if (attempt.attemptId === this.currentAttemptId) {
        this.uncertainAttempt = attempt
        this.submitting = false
      }
    },

    /** Clears form fields but preserves receipts and historical keys. */
    clearPersonalDetails() {
      this.guardianName = ''
      this.guardianEmail = ''
      this.guardianPhone = ''
      this.guardianRelationship = 'parent'
      this.learnerName = ''
      this.learnerAgeYears = null
      this.notes = ''
      this.declarationAccepted = false
      this.targetProgram = ''
      this.idempotencyKey = generateKey()
      this.submissionError = null
    },

    /** Clear a specific program's receipt to allow a fresh application. */
    clearProgramReceipt(programIdOrSlug: string) {
      const { [programIdOrSlug]: _removedId, ...remainingById } = this.receiptsByProgramId
      this.receiptsByProgramId = remainingById
      const { [programIdOrSlug]: _removedSlug, ...remainingBySlug } = this.receiptsBySlug
      this.receiptsBySlug = remainingBySlug
      if (this.receipt?.program_id === programIdOrSlug) {
        this.receipt = null
      }
    },

    /** Fully resets the store, clearing all drafts and receipts. */
    resetAll() {
      this.clearPersonalDetails()
      this.receiptsByProgramId = {}
      this.receiptsBySlug = {}
      this.receipt = null
      this.uncertainAttempt = null
      this.currentAttemptId = 0
    },
  },
})
