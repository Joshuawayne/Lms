<!--
  Program discovery page — /programs

  Lists published programs with pathway filtering and pagination.
  Consumes GET /api/v1/programs through the existing API client.
  Handles loading, empty, error and filtered-empty states.
  Provides two-way synchronization between URL query parameters and reactive filter state.
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { components } from '~/api/generated/types'
import { PATHWAY_FILTER_OPTIONS } from '~/features/programs/composables/pathwayInfo'

definePageMeta({ layout: 'public' })

useHead({
  title: 'Programs — Jjenga Code',
  meta: [
    { name: 'description', content: 'Browse Jjenga Code\'s coding and robotics programs for young people. Filter by school term, Saturday club or holiday pathway.' },
  ],
})

type Pathway = components['schemas']['Pathway']

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()

/* ── reactive query state ───────────────────────────────────────────── */
const selectedPathway = ref<Pathway | null>(
  (route.query.pathway as Pathway | undefined) ?? null,
)
const currentPage = ref(Number(route.query.page) || 1)
const pageSize = 9

/* ── fetch programs ─────────────────────────────────────────────────── */
const { data: response, status, error, refresh } = useAsyncData(
  () => {
    const params: Record<string, string | number> = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (selectedPathway.value) {
      params.pathway = selectedPathway.value
    }
    return $api<components['schemas']['ProgramListResponse']>('/programs', { params })
  },
  { watch: [selectedPathway, currentPage] },
)

/* ── sync state when URL changes (e.g. browser back/forward or direct links) ── */
watch(
  () => route.query,
  (newQuery) => {
    const qPathway = (newQuery.pathway as Pathway | undefined) ?? null
    const qPage = Number(newQuery.page) || 1
    if (selectedPathway.value !== qPathway) {
      selectedPathway.value = qPathway
    }
    if (currentPage.value !== qPage) {
      currentPage.value = qPage
    }
  },
)

/* ── sync URL when local filter state changes ────────────────────────── */
watch([selectedPathway, currentPage], ([pw, page]) => {
  const currentQPathway = (route.query.pathway as Pathway | undefined) ?? null
  const currentQPage = Number(route.query.page) || 1
  if (pw !== currentQPathway || page !== currentQPage) {
    const query: Record<string, string> = {}
    if (pw) query.pathway = pw
    if (page > 1) query.page = String(page)
    router.replace({ query })
  }
})

function setPathway(pw: Pathway | null) {
  selectedPathway.value = pw
  currentPage.value = 1
}

function setPage(page: number) {
  currentPage.value = page
  /* Scroll to top of listing on page change */
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div>
    <!-- ── header ───────────────────────────────────────────────────── -->
    <section class="bg-navy-900 text-white relative overflow-hidden">
      <BlobShape class="absolute -top-16 right-10 opacity-10" size="300px" color="var(--color-purple-400)" />
      <div class="relative max-w-7xl mx-auto px-5 lg:px-8 py-16 md:py-20">
        <h1 class="text-3xl md:text-4xl font-heading font-extrabold mb-3" data-aos="fade-up">
          Our programs
        </h1>
        <p class="text-navy-300 text-lg max-w-xl" data-aos="fade-up" data-aos-delay="100">
          Find the right coding and robotics program for your child.
        </p>
      </div>
      <WaveDivider color="var(--color-navy-50)" />
    </section>

    <!-- ── catalogue ────────────────────────────────────────────────── -->
    <section class="section-gap bg-navy-50">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <!-- Pathway filter tabs -->
        <div class="flex flex-wrap gap-2 mb-10" data-aos="fade-up" role="tablist" aria-label="Filter programs by pathway">
          <button
            v-for="option in PATHWAY_FILTER_OPTIONS"
            :key="String(option.value)"
            role="tab"
            :aria-selected="selectedPathway === option.value"
            class="px-5 py-2 rounded-full text-sm font-medium transition-all duration-200"
            :class="selectedPathway === option.value
              ? 'bg-purple-600 text-white shadow-md'
              : 'bg-white text-navy-600 hover:bg-purple-50 border border-navy-200'"
            @click="setPathway(option.value)"
          >
            {{ option.label }}
          </button>
        </div>

        <!-- Loading skeleton -->
        <div v-if="status === 'pending'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="n in 6"
            :key="n"
            class="rounded-2xl bg-white border border-navy-100 p-6 animate-pulse space-y-4"
          >
            <div class="h-4 bg-navy-100 rounded w-1/3" />
            <div class="h-6 bg-navy-100 rounded w-3/4" />
            <div class="h-16 bg-navy-100 rounded" />
            <div class="h-8 bg-navy-100 rounded w-1/2" />
          </div>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="text-center py-16" data-aos="fade-up">
          <UIcon name="i-lucide-alert-triangle" class="w-12 h-12 text-pink-500 mx-auto mb-4" />
          <h2 class="font-heading font-bold text-navy-800 text-xl mb-2">Unable to load programs</h2>
          <p class="text-navy-500 mb-6">Something went wrong while fetching the catalogue.</p>
          <UButton class="bg-purple-600 hover:bg-purple-700 text-white rounded-full px-6" @click="() => refresh()">
            Try again
          </UButton>
        </div>

        <!-- Empty state (no programs at all) -->
        <div v-else-if="response && response.items.length === 0 && !selectedPathway" class="text-center py-16" data-aos="fade-up">
          <UIcon name="i-lucide-calendar" class="w-12 h-12 text-navy-300 mx-auto mb-4" />
          <h2 class="font-heading font-bold text-navy-800 text-xl mb-2">No programs available yet</h2>
          <p class="text-navy-500 max-w-md mx-auto">
            We're preparing new cohorts. Check back soon or contact us to register your interest.
          </p>
        </div>

        <!-- Filtered empty state (no matches for this pathway) -->
        <div v-else-if="response && response.items.length === 0 && selectedPathway" class="text-center py-16" data-aos="fade-up">
          <UIcon name="i-lucide-search" class="w-12 h-12 text-navy-300 mx-auto mb-4" />
          <h2 class="font-heading font-bold text-navy-800 text-xl mb-2">No programs in this pathway</h2>
          <p class="text-navy-500 mb-6">There are currently no published programs matching your selection.</p>
          <UButton variant="outline" class="rounded-full px-6 border-navy-200 text-navy-600" @click="setPathway(null)">
            Show all programs
          </UButton>
        </div>

        <!-- Program grid -->
        <div v-else-if="response && response.items.length > 0">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <ProgramCard
              v-for="prog in response.items"
              :key="prog.id"
              :program="prog"
            />
          </div>

          <!-- Pagination -->
          <div v-if="response.total_pages > 1" class="flex justify-center items-center gap-2" data-aos="fade-up">
            <UButton
              variant="outline"
              size="sm"
              :disabled="currentPage <= 1"
              class="rounded-full"
              @click="setPage(currentPage - 1)"
            >
              Previous
            </UButton>

            <span class="text-sm text-navy-500 px-3">
              Page {{ currentPage }} of {{ response.total_pages }}
            </span>

            <UButton
              variant="outline"
              size="sm"
              :disabled="currentPage >= response.total_pages"
              class="rounded-full"
              @click="setPage(currentPage + 1)"
            >
              Next
            </UButton>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
