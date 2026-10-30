<!--
  Application submission page — /programs/:slug/apply

  Builds the form from the SubmitApplicationRequest schema.
  Uses the applicationDraft Pinia store for memory-only state management.

  Submission flow:
  1. Validates all required fields before enabling submit.
  2. Builds payload with monotonic attempt ID and fresh idempotency key.
  3. POSTs to /programs/:slug/applications.
  4. On 200/201: records receipt scoped to program and shows confirmation.
  5. On 409: shows conflict message (idempotency key reused with different payload).
  6. On network error: preserves draft and attempt for safe retry with original key.
-->
<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import type { components } from '~/api/generated/types'
import { getPathwayInfo } from '~/features/programs/composables/pathwayInfo'
import { useApplicationAvailability } from '~/features/programs/composables/useApplicationAvailability'
import { useApplicationDraftStore } from '~/stores/applicationDraft'
import { readApiProblem } from '~/api/errors'

definePageMeta({ layout: 'public' })

const route = useRoute()
const { $api } = useNuxtApp()
const slug = computed(() => route.params.slug as string)
const draft = useApplicationDraftStore()

/* ── Fetch program to verify it exists and applications are open ───── */
const { data: program, status: programStatus, error: programError } = useAsyncData(
  `program-apply-${slug.value}`,
  () => $api<components['schemas']['ProgramDetailResponse']>(`/programs/${slug.value}`),
)

const pathway = computed(() => program.value ? getPathwayInfo(program.value.pathway) : null)
const availability = computed(() => useApplicationAvailability(program.value))

/** Scoped receipt for THIS specific program only — avoids showing A's receipt on B */
const currentReceipt = computed(() => {
  const pId = program.value?.id
  const pSlug = program.value?.slug || slug.value
  if (draft.receipt) {
    if (pId && draft.receipt.program_id === pId) return draft.receipt
    if (pSlug && draft.receipt.program_id === pSlug) return draft.receipt
  }
  if (pId && draft.receiptsByProgramId[pId]) return draft.receiptsByProgramId[pId]
  if (pSlug && draft.receiptsBySlug[pSlug]) return draft.receiptsBySlug[pSlug]
  return draft.receiptForProgram(pId) || draft.receiptForProgram(pSlug) || null
})

/** Check if there is an uncertain attempt for this program to offer safe retry */
const pendingAttempt = computed(() => draft.uncertainAttemptForProgram(slug.value))

useHead({
  title: computed(() => program.value ? `Apply — ${program.value.title} — Jjenga Code` : 'Apply — Jjenga Code'),
})

/* ── Form validation ────────────────────────────────────────────────── */
const validationErrors = computed(() => {
  const errors: Record<string, string> = {}
  if (!draft.guardianName.trim()) errors.guardianName = 'Your full name is required.'
  if (!draft.guardianEmail.trim()) {
    errors.guardianEmail = 'Your email address is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(draft.guardianEmail.trim())) {
    errors.guardianEmail = 'Please enter a valid email address.'
  }
  if (!draft.learnerName.trim()) errors.learnerName = 'The learner\'s name is required.'
  if (draft.learnerAgeYears === null || draft.learnerAgeYears < 1) {
    errors.learnerAge = 'The learner\'s age is required.'
  } else {
    if (program.value?.min_age_years && draft.learnerAgeYears < program.value.min_age_years) {
      errors.learnerAge = `Minimum age for this program is ${program.value.min_age_years} years.`
    }
    if (program.value?.max_age_years && draft.learnerAgeYears > program.value.max_age_years) {
      errors.learnerAge = `Maximum age for this program is ${program.value.max_age_years} years.`
    }
  }
  if (!draft.declarationAccepted) errors.declaration = 'You must accept the declaration to apply.'
  return errors
})

const isValid = computed(() => Object.keys(validationErrors.value).length === 0)
const showErrors = ref(false)

/* ── Relationship options ───────────────────────────────────────────── */
const relationshipOptions = [
  { value: 'parent', label: 'Parent' },
  { value: 'guardian', label: 'Guardian' },
  { value: 'grandparent', label: 'Grandparent' },
  { value: 'sibling', label: 'Sibling' },
  { value: 'other', label: 'Other' },
] as const

/* ── Submission ─────────────────────────────────────────────────────── */
async function handleSubmit() {
  showErrors.value = true
  if (!isValid.value) {
    nextTick(() => {
      const summary = document.getElementById('error-summary')
      summary?.focus()
    })
    return
  }

  /* Clear any previous receipt for this program */
  draft.clearProgramReceipt(slug.value)
  draft.receipt = null

  const { attemptId, payload } = draft.beginSubmission(slug.value)

  try {
    const receipt = await $api<components['schemas']['ApplicationReceiptResponse']>(
      `/programs/${slug.value}/applications`,
      { method: 'POST', body: payload },
    )
    draft.recordReceipt(receipt, slug.value, attemptId)
  } catch (err: unknown) {
    const problem = readApiProblem(err)
    if (problem?.status === 409) {
      draft.submissionError = 'This application has already been submitted with different information. Please review your details and try again.'
    } else if (problem?.status === 422) {
      draft.submissionError = problem.detail || 'Some fields are invalid. Please check your entries.'
    } else if (problem?.status === 404) {
      draft.submissionError = 'This program is no longer accepting applications.'
    } else {
      /* Network error or lost response — preserve attempt snapshot for safe retry */
      draft.recordUncertainAttempt({
        programTarget: slug.value,
        payload,
        attemptId,
        timestamp: Date.now(),
      })
      draft.submissionError = 'Something went wrong. Your application has been saved and you can safely retry.'
    }
  } finally {
    draft.submitting = false
  }
}

/* ── Replay uncertain attempt ───────────────────────────────────────── */
async function handleRetry() {
  const pending = draft.uncertainAttemptForProgram(slug.value)
  if (!pending) {
    return handleSubmit()
  }

  draft.submitting = true
  draft.submissionError = null

  try {
    const receipt = await $api<components['schemas']['ApplicationReceiptResponse']>(
      `/programs/${slug.value}/applications`,
      { method: 'POST', body: pending.payload },
    )
    draft.recordReceipt(receipt, slug.value, pending.attemptId)
  } catch (err: unknown) {
    const problem = readApiProblem(err)
    if (problem?.status === 409) {
      draft.submissionError = 'This application has already been submitted with different information. Please review your details and try again.'
    } else if (problem?.status === 422) {
      draft.submissionError = problem.detail || 'Some fields are invalid. Please check your entries.'
    } else if (problem?.status === 404) {
      draft.submissionError = 'This program is no longer accepting applications.'
    } else {
      draft.submissionError = 'Something went wrong. Your application has been saved and you can safely retry.'
    }
  } finally {
    draft.submitting = false
  }
}

/* ── Reset to start a new application ───────────────────────────────── */
function startNewApplication() {
  draft.resetAll()
  showErrors.value = false
}
</script>

<template>
  <div>
    <!-- ── Header ───────────────────────────────────────────────────── -->
    <section class="bg-navy-900 text-white relative overflow-hidden">
      <div class="relative max-w-7xl mx-auto px-5 lg:px-8 py-12 md:py-16">
        <nav aria-label="Breadcrumb" class="mb-4">
          <ol class="flex items-center gap-2 text-sm text-navy-400">
            <li><NuxtLink to="/programs" class="hover:text-yellow-400 transition-colors">Programs</NuxtLink></li>
            <li><UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5" /></li>
            <li v-if="program">
              <NuxtLink :to="`/programs/${program.slug}`" class="hover:text-yellow-400 transition-colors">{{ program.title }}</NuxtLink>
            </li>
            <li v-if="program"><UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5" /></li>
            <li class="text-navy-200">Apply</li>
          </ol>
        </nav>
        <h1 class="text-2xl md:text-3xl font-heading font-bold">
          <template v-if="program">Apply for {{ program.title }}</template>
          <template v-else>Apply</template>
        </h1>
        <p v-if="pathway" class="mt-2 text-sm text-navy-300">
          {{ pathway.label }} Pathway
        </p>
      </div>
      <WaveDivider color="var(--color-navy-50)" />
    </section>

    <section class="section-gap bg-navy-50">
      <div class="max-w-3xl mx-auto px-5 lg:px-8">
        <!-- Loading -->
        <div v-if="programStatus === 'pending'" class="text-center py-16">
          <div class="animate-spin w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto mb-4" />
          <p class="text-navy-500">Loading program details…</p>
        </div>

        <!-- Program not found -->
        <div v-else-if="programError" class="text-center py-16">
          <UIcon name="i-lucide-alert-triangle" class="w-12 h-12 text-pink-500 mx-auto mb-4" />
          <h2 class="font-heading font-bold text-navy-800 text-xl mb-2">Program not found</h2>
          <p class="text-navy-500 mb-6">This program may have been removed or the link may be incorrect.</p>
          <NuxtLink to="/programs">
            <UButton class="bg-purple-600 hover:bg-purple-700 text-white rounded-full px-6">Browse programs</UButton>
          </NuxtLink>
        </div>

        <!-- ═══ Confirmation screen ═══════════════════════════════════ -->
        <!-- Placed BEFORE availability check so that applicants who confirmed can always see their receipt, even if applications close! -->
        <div v-else-if="currentReceipt" class="py-8">
          <div class="rounded-2xl bg-white border-2 border-green-200 p-8 text-center" data-aos="fade-up">
            <div class="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <UIcon name="i-lucide-check-circle" class="w-10 h-10 text-green-600" />
            </div>
            <h2 class="text-2xl font-heading font-bold text-navy-800 mb-2">Submitted for review</h2>
            <p class="text-navy-500 mb-6">Your application has been received and will be reviewed by our team.</p>

            <div class="bg-navy-50 rounded-xl p-4 inline-block mb-6">
              <p class="text-xs text-navy-400 uppercase tracking-wider mb-1">Reference</p>
              <p class="text-lg font-mono font-bold text-navy-800">{{ currentReceipt.reference }}</p>
            </div>

            <p v-if="currentReceipt.is_retry" class="text-sm text-yellow-600 mb-4">
              This is a replay of a previously submitted application.
            </p>

            <p class="text-sm text-navy-500 mb-8">
              Keep your reference number for your records. We'll be in touch with next steps.
            </p>

            <div class="flex flex-wrap justify-center gap-4">
              <NuxtLink :to="`/programs/${slug}`">
                <UButton variant="outline" class="rounded-full px-6 border-navy-200 text-navy-600">
                  View program
                </UButton>
              </NuxtLink>
              <UButton class="bg-purple-600 hover:bg-purple-700 text-white rounded-full px-6" @click="startNewApplication">
                Apply to another program
              </UButton>
            </div>
          </div>
        </div>

        <!-- Applications not open (Only shown if no receipt exists and no uncertain attempt can be replayed) -->
        <div v-else-if="program && !availability.canApply && !pendingAttempt" class="text-center py-16">
          <UIcon name="i-lucide-clock" class="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h2 class="font-heading font-bold text-navy-800 text-xl mb-2">{{ availability.label }}</h2>
          <p class="text-navy-500 mb-6">
            <template v-if="availability.status === 'not_yet'">Check back when the application window opens.</template>
            <template v-else>You can browse other available programs.</template>
          </p>
          <NuxtLink :to="`/programs/${program.slug}`">
            <UButton class="bg-purple-600 hover:bg-purple-700 text-white rounded-full px-6">View program details</UButton>
          </NuxtLink>
        </div>

        <!-- ═══ Application form (or retry banner) ═════════════════════ -->
        <div v-else-if="program" class="py-8">
          <!-- Pending attempt retry banner -->
          <div v-if="pendingAttempt" class="rounded-xl bg-yellow-50 border border-yellow-300 p-5 mb-8 flex items-start justify-between gap-4" data-aos="fade-up">
            <div class="flex items-start gap-3">
              <UIcon name="i-lucide-refresh-cw" class="w-5 h-5 text-yellow-600 mt-0.5 shrink-0" />
              <div class="text-sm text-yellow-900">
                <p class="font-semibold">Unconfirmed submission saved</p>
                <p class="mt-1 text-yellow-800">A previous submission attempt encountered a network disruption. You can safely retry it now using the original submission key.</p>
              </div>
            </div>
            <UButton
              size="sm"
              :loading="draft.submitting"
              class="bg-yellow-500 hover:bg-yellow-600 text-navy-900 font-semibold rounded-full px-4 shrink-0"
              @click="handleRetry"
            >
              Retry now
            </UButton>
          </div>

          <!-- Draft notice -->
          <div v-else class="rounded-xl bg-yellow-50 border border-yellow-200 p-4 mb-8 flex items-start gap-3" data-aos="fade-up">
            <UIcon name="i-lucide-info" class="w-5 h-5 text-yellow-600 mt-0.5 shrink-0" />
            <div class="text-sm text-yellow-800">
              <p class="font-medium">Your application is saved in this tab only.</p>
              <p class="mt-1 text-yellow-700">Refreshing or closing the tab will clear your entered information. No account is needed to apply.</p>
            </div>
          </div>

          <form class="space-y-8" novalidate @submit.prevent="handleSubmit">
            <!-- Accessible Error Summary -->
            <div
              v-if="showErrors && !isValid"
              id="error-summary"
              class="rounded-xl bg-pink-50 border-2 border-pink-300 p-5 focus:outline-none focus:ring-2 focus:ring-pink-500"
              role="alert"
              tabindex="-1"
              aria-labelledby="error-summary-title"
            >
              <div class="flex items-center gap-2 mb-2">
                <UIcon name="i-lucide-alert-circle" class="w-5 h-5 text-pink-600" />
                <p id="error-summary-title" class="text-sm font-bold text-pink-900">Please correct the following before submitting:</p>
              </div>
              <ul class="text-sm text-pink-800 list-disc list-inside space-y-1">
                <li v-for="(msg, field) in validationErrors" :key="field">
                  <a :href="`#${field}`" class="underline hover:text-pink-950 font-medium">{{ msg }}</a>
                </li>
              </ul>
            </div>

            <!-- Submission error -->
            <div v-if="draft.submissionError" class="rounded-xl bg-pink-50 border border-pink-200 p-4" role="alert">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-alert-triangle" class="w-5 h-5 text-pink-600" />
                <p class="text-sm text-pink-800">{{ draft.submissionError }}</p>
              </div>
            </div>

            <!-- Guardian section -->
            <fieldset class="rounded-2xl bg-white border border-navy-100 p-6 space-y-5" data-aos="fade-up">
              <legend class="text-lg font-heading font-bold text-navy-800 px-1">Your details</legend>

              <div>
                <label for="guardianName" class="block text-sm font-medium text-navy-700 mb-1.5">Full name *</label>
                <input
                  id="guardianName"
                  v-model="draft.guardianName"
                  type="text"
                  autocomplete="name"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                  :class="showErrors && validationErrors.guardianName ? 'border-pink-400 ring-1 ring-pink-300' : ''"
                  :aria-invalid="showErrors && !!validationErrors.guardianName"
                  :aria-describedby="showErrors && validationErrors.guardianName ? 'guardianName-error' : undefined"
                  placeholder="e.g. Jane Wanjiku"
                >
                <p v-if="showErrors && validationErrors.guardianName" id="guardianName-error" class="text-xs text-pink-600 mt-1">
                  {{ validationErrors.guardianName }}
                </p>
              </div>

              <div>
                <label for="guardianEmail" class="block text-sm font-medium text-navy-700 mb-1.5">Email address *</label>
                <input
                  id="guardianEmail"
                  v-model="draft.guardianEmail"
                  type="email"
                  autocomplete="email"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                  :class="showErrors && validationErrors.guardianEmail ? 'border-pink-400 ring-1 ring-pink-300' : ''"
                  :aria-invalid="showErrors && !!validationErrors.guardianEmail"
                  :aria-describedby="showErrors && validationErrors.guardianEmail ? 'guardianEmail-error' : undefined"
                  placeholder="e.g. jane@example.com"
                >
                <p v-if="showErrors && validationErrors.guardianEmail" id="guardianEmail-error" class="text-xs text-pink-600 mt-1">
                  {{ validationErrors.guardianEmail }}
                </p>
              </div>

              <div>
                <label for="guardianPhone" class="block text-sm font-medium text-navy-700 mb-1.5">Phone number <span class="text-navy-400">(optional)</span></label>
                <input
                  id="guardianPhone"
                  v-model="draft.guardianPhone"
                  type="tel"
                  autocomplete="tel"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                  placeholder="e.g. +254 7XX XXX XXX"
                >
              </div>

              <div>
                <label for="guardianRelationship" class="block text-sm font-medium text-navy-700 mb-1.5">Relationship to learner *</label>
                <select
                  id="guardianRelationship"
                  v-model="draft.guardianRelationship"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                >
                  <option v-for="opt in relationshipOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </fieldset>

            <!-- Learner section -->
            <fieldset class="rounded-2xl bg-white border border-navy-100 p-6 space-y-5" data-aos="fade-up">
              <legend class="text-lg font-heading font-bold text-navy-800 px-1">Learner details</legend>

              <div>
                <label for="learnerName" class="block text-sm font-medium text-navy-700 mb-1.5">Learner's full name *</label>
                <input
                  id="learnerName"
                  v-model="draft.learnerName"
                  type="text"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                  :class="showErrors && validationErrors.learnerName ? 'border-pink-400 ring-1 ring-pink-300' : ''"
                  :aria-invalid="showErrors && !!validationErrors.learnerName"
                  :aria-describedby="showErrors && validationErrors.learnerName ? 'learnerName-error' : undefined"
                  placeholder="e.g. Alex Omondi"
                >
                <p v-if="showErrors && validationErrors.learnerName" id="learnerName-error" class="text-xs text-pink-600 mt-1">
                  {{ validationErrors.learnerName }}
                </p>
              </div>

              <div>
                <label for="learnerAge" class="block text-sm font-medium text-navy-700 mb-1.5">
                  Age (years) *
                  <span v-if="program.min_age_years && program.max_age_years" class="text-navy-400 font-normal">
                    — {{ program.min_age_years }}–{{ program.max_age_years }} for this program
                  </span>
                </label>
                <input
                  id="learnerAge"
                  v-model.number="draft.learnerAgeYears"
                  type="number"
                  min="1"
                  :max="program.max_age_years ?? undefined"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
                  :class="showErrors && validationErrors.learnerAge ? 'border-pink-400 ring-1 ring-pink-300' : ''"
                  :aria-invalid="showErrors && !!validationErrors.learnerAge"
                  :aria-describedby="showErrors && validationErrors.learnerAge ? 'learnerAge-error' : undefined"
                >
                <p v-if="showErrors && validationErrors.learnerAge" id="learnerAge-error" class="text-xs text-pink-600 mt-1">
                  {{ validationErrors.learnerAge }}
                </p>
              </div>

              <div>
                <label for="notes" class="block text-sm font-medium text-navy-700 mb-1.5">
                  Additional notes <span class="text-navy-400">(optional)</span>
                </label>
                <textarea
                  id="notes"
                  v-model="draft.notes"
                  rows="3"
                  class="w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-800 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition resize-y"
                  placeholder="Any relevant information: experience level, accessibility needs, dietary requirements for camps, etc."
                />
              </div>
            </fieldset>

            <!-- Declaration -->
            <div class="rounded-2xl bg-white border border-navy-100 p-6" data-aos="fade-up">
              <label class="flex items-start gap-3 cursor-pointer">
                <input
                  id="declaration"
                  v-model="draft.declarationAccepted"
                  type="checkbox"
                  class="mt-1 h-5 w-5 rounded border-navy-300 text-purple-600 focus:ring-purple-500"
                  :aria-invalid="showErrors && !!validationErrors.declaration"
                  :aria-describedby="showErrors && validationErrors.declaration ? 'declaration-error' : undefined"
                >
                <span class="text-sm text-navy-700 leading-relaxed">
                  I confirm that the information provided is accurate and I consent to Jjenga Code
                  processing this application. I understand my child's participation is subject to
                  review and placement availability. *
                </span>
              </label>
              <p v-if="showErrors && validationErrors.declaration" id="declaration-error" class="text-xs text-pink-600 mt-2 ml-8">
                {{ validationErrors.declaration }}
              </p>
            </div>

            <!-- Submit button -->
            <div class="flex flex-col sm:flex-row items-center gap-4">
              <UButton
                type="submit"
                size="lg"
                :loading="draft.submitting"
                :disabled="draft.submitting"
                class="bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full px-10 py-3 text-base w-full sm:w-auto"
              >
                {{ draft.submitting ? 'Submitting…' : 'Submit application' }}
              </UButton>
              <NuxtLink :to="`/programs/${slug}`" class="text-sm text-navy-500 hover:text-purple-600 transition-colors">
                Back to program details
              </NuxtLink>
            </div>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>
