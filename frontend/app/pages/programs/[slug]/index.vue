<!--
  Program detail page — /programs/:slug

  Fetches a single program by slug using GET /api/v1/programs/:slug.
  Displays full description, dates, eligibility and a prominent CTA
  to apply when the application window is open.
  Distinguishes HTTP 404 (Program not found) from HTTP 503 / network errors.
-->
<script setup lang="ts">
import { computed } from 'vue'
import type { components } from '~/api/generated/types'
import { getPathwayInfo } from '~/features/programs/composables/pathwayInfo'
import { useApplicationAvailability } from '~/features/programs/composables/useApplicationAvailability'
import { readApiProblem } from '~/api/errors'

definePageMeta({ layout: 'public' })

const route = useRoute()
const { $api } = useNuxtApp()
const slug = computed(() => route.params.slug as string)

const { data: program, status, error, refresh } = useAsyncData(
  `program-${slug.value}`,
  () => $api<components['schemas']['ProgramDetailResponse']>(`/programs/${slug.value}`),
)

const pathway = computed(() => (program.value ? getPathwayInfo(program.value.pathway) : null))
const availability = computed(() => useApplicationAvailability(program.value))

const apiProblem = computed(() => (error.value ? readApiProblem(error.value) : null))
const isNotFound = computed(() => {
  if (!error.value) return false
  return apiProblem.value?.status === 404 || (error.value as { statusCode?: number })?.statusCode === 404
})

useHead({
  title: computed(() => (program.value ? `${program.value.title} — Jjenga Code` : 'Program — Jjenga Code')),
  meta: [
    { name: 'description', content: computed(() => program.value?.summary ?? 'Program details at Jjenga Code.') },
  ],
})

function formatDate(iso: string | null): string {
  if (!iso) return 'To be announced'
  return new Date(iso).toLocaleDateString('en-KE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <div>
    <!-- ── Loading skeleton ─────────────────────────────────────────── -->
    <template v-if="status === 'pending'">
      <section class="bg-navy-900 text-white">
        <div class="max-w-7xl mx-auto px-5 lg:px-8 py-16">
          <div class="animate-pulse space-y-4 max-w-2xl">
            <div class="h-4 bg-navy-700 rounded w-1/4" />
            <div class="h-10 bg-navy-700 rounded w-3/4" />
            <div class="h-5 bg-navy-700 rounded w-full" />
          </div>
        </div>
        <WaveDivider color="white" />
      </section>
    </template>

    <!-- ── 404 Not Found ────────────────────────────────────────────── -->
    <template v-else-if="error && isNotFound">
      <section class="bg-navy-900 text-white">
        <div class="max-w-7xl mx-auto px-5 lg:px-8 py-16">
          <h1 class="text-3xl font-heading font-bold mb-3">Program not found</h1>
          <p class="text-navy-300 mb-6">This program may no longer be published or the link may be incorrect.</p>
          <NuxtLink to="/programs">
            <UButton class="bg-yellow-400 hover:bg-yellow-300 text-navy-900 rounded-full px-6">
              Browse all programs
            </UButton>
          </NuxtLink>
        </div>
        <WaveDivider color="white" />
      </section>
    </template>

    <!-- ── 503 / Network Error with Retry ───────────────────────────── -->
    <template v-else-if="error">
      <section class="bg-navy-900 text-white">
        <div class="max-w-7xl mx-auto px-5 lg:px-8 py-16">
          <h1 class="text-3xl font-heading font-bold mb-3">Service temporarily unavailable</h1>
          <p class="text-navy-300 mb-6">Unable to connect to the catalogue service. Please check your connection and retry.</p>
          <div class="flex items-center gap-4">
            <UButton class="bg-yellow-400 hover:bg-yellow-300 text-navy-900 rounded-full px-6" @click="() => refresh()">
              Retry loading
            </UButton>
            <NuxtLink to="/programs" class="text-sm text-navy-300 hover:text-white underline">
              Browse other programs
            </NuxtLink>
          </div>
        </div>
        <WaveDivider color="white" />
      </section>
    </template>

    <!-- ── Program content ──────────────────────────────────────────── -->
    <template v-else-if="program">
      <!-- Header -->
      <section class="bg-navy-900 text-white relative overflow-hidden">
        <BlobShape class="absolute -top-16 right-10 opacity-10" size="350px" :color="pathway?.color ?? 'var(--color-purple-400)'" />
        <div class="relative max-w-7xl mx-auto px-5 lg:px-8 py-16 md:py-20">
          <!-- Breadcrumb -->
          <nav aria-label="Breadcrumb" class="mb-6" data-aos="fade-up">
            <ol class="flex items-center gap-2 text-sm text-navy-400">
              <li><NuxtLink to="/programs" class="hover:text-yellow-400 transition-colors">Programs</NuxtLink></li>
              <li><UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5" /></li>
              <li class="text-navy-200">{{ program.title }}</li>
            </ol>
          </nav>

          <!-- Pathway badge -->
          <div class="flex items-center gap-2 mb-4" data-aos="fade-up">
            <UIcon :name="pathway?.icon ?? 'i-lucide-book-open'" class="w-4 h-4 text-yellow-400" />
            <span class="text-sm font-semibold text-yellow-400 uppercase tracking-wider">{{ pathway?.label }}</span>
          </div>

          <h1 class="text-3xl md:text-4xl lg:text-5xl font-heading font-extrabold mb-4" data-aos="fade-up" data-aos-delay="100">
            {{ program.title }}
          </h1>
          <p class="text-lg text-navy-300 max-w-2xl" data-aos="fade-up" data-aos-delay="200">
            {{ program.summary }}
          </p>
        </div>
        <WaveDivider color="white" />
      </section>

      <!-- Details body -->
      <section class="section-gap bg-white">
        <div class="max-w-7xl mx-auto px-5 lg:px-8">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <!-- Main content (2 cols) -->
            <div class="lg:col-span-2 space-y-8">
              <div>
                <h2 class="text-2xl font-heading font-bold text-navy-800 mb-4">About this program</h2>
                <div class="prose max-w-none text-navy-600 leading-relaxed whitespace-pre-line">
                  {{ program.description }}
                </div>
              </div>

              <!-- Pathway description callout -->
              <div v-if="pathway" class="rounded-2xl p-6 border border-navy-100 bg-navy-50" data-aos="fade-up">
                <div class="flex items-center gap-3 mb-2">
                  <UIcon :name="pathway.icon" class="w-5 h-5 text-purple-600" />
                  <h3 class="font-heading font-bold text-navy-800">{{ pathway.label }} Pathway</h3>
                </div>
                <p class="text-sm text-navy-600 leading-relaxed">{{ program.summary }}</p>
              </div>
            </div>

            <!-- Sidebar / Action card (1 col) -->
            <div>
              <div class="sticky top-28 rounded-2xl border border-navy-100 p-6 shadow-sm bg-navy-50 space-y-6" data-aos="fade-up">
                <!-- Status badge -->
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold text-navy-400 uppercase tracking-wider">Status</span>
                  <span
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold"
                    :class="{
                      'bg-green-50 text-green-700': availability.status === 'open',
                      'bg-yellow-50 text-yellow-700': availability.status === 'not_yet',
                      'bg-navy-100 text-navy-500': availability.status === 'closed' || availability.status === 'disabled',
                    }"
                  >
                    <span
                      class="w-2 h-2 rounded-full"
                      :class="{
                        'bg-green-500': availability.status === 'open',
                        'bg-yellow-500': availability.status === 'not_yet',
                        'bg-navy-400': availability.status === 'closed' || availability.status === 'disabled',
                      }"
                    />
                    {{ availability.label }}
                  </span>
                </div>

                <!-- Key details list -->
                <dl class="space-y-4 text-sm divide-y divide-navy-100">
                  <div class="pt-3 flex justify-between">
                    <dt class="text-navy-500">Age range</dt>
                    <dd class="font-medium text-navy-800">
                      <template v-if="program.min_age_years && program.max_age_years">
                        {{ program.min_age_years }}–{{ program.max_age_years }} years
                      </template>
                      <template v-else-if="program.min_age_years">From {{ program.min_age_years }} years</template>
                      <template v-else-if="program.max_age_years">Up to {{ program.max_age_years }} years</template>
                      <template v-else>All ages welcome</template>
                    </dd>
                  </div>

                  <div class="pt-3 flex justify-between">
                    <dt class="text-navy-500">Applications open</dt>
                    <dd class="font-medium text-navy-800">{{ formatDate(program.applications_open_at) }}</dd>
                  </div>

                  <div class="pt-3 flex justify-between">
                    <dt class="text-navy-500">Applications close</dt>
                    <dd class="font-medium text-navy-800">{{ formatDate(program.applications_close_at) }}</dd>
                  </div>
                </dl>

                <!-- CTA -->
                <div>
                  <NuxtLink v-if="availability.canApply" :to="`/programs/${program.slug}/apply`" class="block">
                    <UButton size="lg" block class="bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-full py-3 shadow-md">
                      Apply now
                    </UButton>
                  </NuxtLink>
                  <UButton
                    v-else
                    size="lg"
                    block
                    disabled
                    class="bg-navy-200 text-navy-400 rounded-full py-3 cursor-not-allowed"
                  >
                    {{ availability.label }}
                  </UButton>
                </div>

                <p class="text-xs text-navy-600 text-center">
                  Applications are reviewed on a rolling basis. No payment is required to apply.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
