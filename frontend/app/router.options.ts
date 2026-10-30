/**
 * Router scroll behaviour for the public website.
 *
 * - Back/forward: restore the saved position once the page has rendered.
 * - Hash links (`/#faq`): scroll to the target; the sticky header offset comes from the
 *   `scroll-padding-top` set in main.css, so no pixel constants live here.
 * - Same-page query changes (catalogue filters, pagination): keep the position; the
 *   page decides whether to move focus or scroll.
 * - Any other navigation: start at the top.
 * Reduced motion never smooth-scrolls.
 */
import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig>{
  scrollBehavior(to, from, savedPosition) {
    const nuxtApp = useNuxtApp()
    const behavior = import.meta.client
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'instant'
      : 'smooth'

    if (savedPosition) {
      return new Promise((resolve) => {
        nuxtApp.hooks.hookOnce('page:finish', () => {
          setTimeout(() => resolve(savedPosition), 60)
        })
      })
    }

    if (to.hash) {
      if (to.path === from.path) return { el: to.hash, behavior }
      return new Promise((resolve) => {
        nuxtApp.hooks.hookOnce('page:finish', () => {
          setTimeout(() => resolve({ el: to.hash, behavior: 'instant' }), 60)
        })
      })
    }

    if (to.path === from.path) return false
    return { left: 0, top: 0, behavior: 'instant' }
  },
}

