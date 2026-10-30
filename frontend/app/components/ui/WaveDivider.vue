<!--
  Decorative wave SVG divider for section transitions.
  Used between homepage sections to create organic visual flow.
  Props: flip (inverts vertically), color (fill).
-->
<script setup lang="ts">
withDefaults(defineProps<{
  flip?: boolean
  color?: string
}>(), {
  flip: false,
  color: 'var(--color-navy-900)',
})
</script>

<template>
  <div
    class="w-full overflow-hidden leading-none"
    :class="flip ? 'rotate-180' : ''"
    aria-hidden="true"
  >
    <svg
      viewBox="0 0 1440 120"
      preserveAspectRatio="none"
      class="block w-full h-16 md:h-24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        :fill="color"
        d="M0,64 C240,120 480,0 720,64 C960,128 1200,16 1440,80 L1440,120 L0,120 Z"
      />
    </svg>
  </div>
</template>
