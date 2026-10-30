<script setup lang="ts">
import type { components } from '~/api/generated/types'
import { readApiProblem } from '~/api/errors'

type Liveness = components['schemas']['LivenessResponse']

useHead({ title: 'Jjenga Code — development setup' })

const api = useApi()
const { data, error, status, execute } = useAsyncData(
  'backend-liveness',
  () => api<Liveness>('/health/live'),
  { server: false, immediate: false },
)
const problem = computed(() => readApiProblem(error.value))
</script>

<template>
  <section class="mx-auto max-w-2xl space-y-6">
    <UBadge color="neutral" variant="soft">Development setup</UBadge>
    <h1 class="text-3xl font-semibold">Jjenga Code LMS</h1>
    <p class="text-muted">The frontend workspace is ready for development.</p>

    <UCard>
      <div class="space-y-4">
        <h2 class="text-lg font-medium">Backend connection</h2>
        <p class="text-muted">Start FastAPI, then check that the frontend can reach it.</p>
        <UButton :loading="status === 'pending'" @click="execute()">
          Check backend
        </UButton>
        <p role="status" aria-live="polite">
          <span v-if="status === 'success'">Connected to {{ data?.service }}.</span>
          <span v-else-if="status === 'error'">
            {{ problem?.detail ?? 'Backend unavailable. Check that FastAPI is running on port 8000.' }}
          </span>
          <span v-else-if="status === 'pending'">Checking connection…</span>
          <span v-else>Connection has not been checked yet.</span>
        </p>
      </div>
    </UCard>

    <p class="text-sm text-muted">
      This confirms API connectivity. Database readiness is checked separately.
    </p>
  </section>
</template>
