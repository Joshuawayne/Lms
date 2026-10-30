<!--
  Responsive photograph with a working failure path.

  Renders a registry photograph with srcset/sizes and a fixed aspect ratio (no layout
  shift). If the image fails — including a failure that happened before hydration, which
  the @error handler alone would miss — it is replaced by the on-brand placeholder and the
  alt text still describes the intended photograph.
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { BrandImageKey } from '~/utils/images'
import { BRAND_IMAGES, getPlaceholderSvg, imageSrcset, imageUrl } from '~/utils/images'

const props = withDefaults(defineProps<{
  imageKey: BrandImageKey
  sizes: string
  /** Hero images load eagerly with high priority; everything else is lazy. */
  priority?: boolean
  /** CSS aspect-ratio, e.g. "4 / 3". Omit when the parent controls the height. */
  ratio?: string
}>(), { priority: false, ratio: undefined })

const image = computed(() => BRAND_IMAGES[props.imageKey])
const failed = ref(false)
const element = ref<HTMLImageElement | null>(null)

onMounted(() => {
  // Catch images that already failed before Vue attached the error listener.
  if (element.value?.complete && element.value.naturalWidth === 0) failed.value = true
})
</script>

<template>
  <img
    ref="element"
    :src="failed ? getPlaceholderSvg() : imageUrl(image, 960)"
    :srcset="failed ? undefined : imageSrcset(image)"
    :sizes="failed ? undefined : sizes"
    :alt="image.alt"
    :width="image.width"
    :height="image.height"
    :loading="priority ? 'eager' : 'lazy'"
    :fetchpriority="priority ? 'high' : 'auto'"
    decoding="async"
    :data-image-failed="failed ? 'true' : undefined"
    :style="{ objectPosition: image.focus, aspectRatio: ratio }"
    class="block h-full w-full object-cover"
    @error="failed = true"
  >
</template>
