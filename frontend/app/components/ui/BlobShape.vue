<!--
  Decorative blob SVG for background visual accents.
  Uses the design token border-radius for organic shapes.
  Props: size (CSS dimension), color.
-->
<script setup lang="ts">
withDefaults(defineProps<{
  size?: string
  color?: string
}>(), {
  size: '200px',
  color: 'var(--color-yellow-300)',
})
</script>

<template>
  <div
    class="shape-float opacity-30"
    aria-hidden="true"
    :style="{
      width: size,
      height: size,
      backgroundColor: color,
      borderRadius: 'var(--radius-blob)',
      filter: 'blur(2px)',
    }"
  />
</template>
