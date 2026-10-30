<!--
  Decorative star SVG accent for hero and feature sections.
  A four-pointed star rendered inline. Colour and size are customisable.
-->
<script setup lang="ts">
withDefaults(defineProps<{
  size?: string
  color?: string
}>(), {
  size: '32',
  color: 'var(--color-yellow-400)',
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    class="inline-block"
  >
    <path
      d="M16 0 L20 12 L32 16 L20 20 L16 32 L12 20 L0 16 L12 12 Z"
      :fill="color"
    />
  </svg>
</template>
