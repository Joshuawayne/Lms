<!--
  Program summary card for the catalogue listing.
  Shows pathway badge, title, summary, age range, dates and application status.
  Links to the program detail page using the slug.
-->
<script setup lang="ts">
import type { components } from '~/api/generated/types'
import { getPathwayInfo } from '~/features/programs/composables/pathwayInfo'
import { useApplicationAvailability } from '~/features/programs/composables/useApplicationAvailability'

const props = defineProps<{
  program: components['schemas']['ProgramSummaryResponse']
}>()

const pathway = computed(() => getPathwayInfo(props.program.pathway))
const availability = computed(() => useApplicationAvailability(props.program))

function formatDate(iso: string | null): string {
  if (!iso) return 'TBA'
  return new Date(iso).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <NuxtLink
    :to="`/programs/${program.slug}`"
    class="group block rounded-2xl border border-navy-100 bg-white overflow-hidden hover:shadow-lg hover:shadow-purple-100/50 hover:-translate-y-1 transition-all duration-300"
  >
    <!-- Coloured top bar for pathway identity -->
    <div class="h-2" :style="{ backgroundColor: pathway.color }" />

    <div class="p-6 space-y-4">
      <!-- Pathway badge -->
      <div class="flex items-center gap-2">
        <UIcon :name="pathway.icon" class="w-4 h-4" :style="{ color: pathway.color }" />
        <span class="text-xs font-semibold uppercase tracking-wider" :style="{ color: pathway.color }">
          {{ pathway.short }}
        </span>
      </div>

      <!-- Title -->
      <h3 class="text-lg font-heading font-bold text-navy-800 group-hover:text-purple-600 transition-colors line-clamp-2">
        {{ program.title }}
      </h3>

      <!-- Summary -->
      <p class="text-sm text-navy-500 leading-relaxed line-clamp-3">
        {{ program.summary }}
      </p>

      <!-- Meta details -->
      <div class="flex flex-wrap gap-3 text-xs text-navy-400">
        <span v-if="program.min_age_years || program.max_age_years" class="flex items-center gap-1">
          <UIcon name="i-lucide-users" class="w-3.5 h-3.5" />
          Ages {{ program.min_age_years ?? '?' }}–{{ program.max_age_years ?? '?' }}
        </span>
        <span v-if="program.starts_on" class="flex items-center gap-1">
          <UIcon name="i-lucide-calendar" class="w-3.5 h-3.5" />
          {{ formatDate(program.starts_on) }}
        </span>
        <span class="flex items-center gap-1">
          <UIcon name="i-lucide-map-pin" class="w-3.5 h-3.5" />
          {{ program.delivery === 'in_person' ? 'In Person' : program.delivery === 'online' ? 'Online' : 'Hybrid' }}
        </span>
      </div>

      <!-- Availability indicator -->
      <div class="pt-2 border-t border-navy-50">
        <span
          class="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full"
          :class="{
            'bg-green-50 text-green-700': availability.status === 'open',
            'bg-yellow-50 text-yellow-700': availability.status === 'not_yet',
            'bg-navy-50 text-navy-400': availability.status === 'closed' || availability.status === 'disabled',
          }"
        >
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="{
              'bg-green-500': availability.status === 'open',
              'bg-yellow-500': availability.status === 'not_yet',
              'bg-navy-300': availability.status === 'closed' || availability.status === 'disabled',
            }"
          />
          {{ availability.label }}
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
