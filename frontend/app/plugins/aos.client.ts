/**
 * AOS (Animate On Scroll) — progressive enhancement for short reveal effects.
 *
 * Lifecycle rules (see docs/design/public-website.md, "Motion"):
 *   - Content is visible without AOS. Its stylesheet is NOT part of the global CSS; it is
 *     injected here only after AOS has initialised successfully, and removed again if
 *     initialisation fails or the visitor switches on reduced motion.
 *   - Initialisation waits for `app:mounted`, so classes AOS adds never race hydration.
 *   - Every timer is tracked and cleared on teardown (app unmount and HMR dispose).
 *   - Reduced motion is honoured at start-up and when the preference changes.
 */
import AOS from 'aos'
import aosStyles from 'aos/dist/aos.css?inline'

export default defineNuxtPlugin({
  name: 'aos',
  enforce: 'post',
  setup(nuxtApp) {
    if (import.meta.server) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    let styleElement: HTMLStyleElement | null = null
    let refreshTimer: number | undefined
    let active = false

    function reveal(): void {
      for (const element of document.querySelectorAll('[data-aos]')) {
        element.classList.remove('aos-init', 'aos-animate')
      }
    }

    function disable(): void {
      window.clearTimeout(refreshTimer)
      styleElement?.remove()
      styleElement = null
      document.documentElement.classList.remove('aos-enabled')
      reveal()
      active = false
    }

    function enable(): void {
      if (active || reducedMotion.matches) return
      try {
        styleElement = document.createElement('style')
        styleElement.dataset.aos = 'true'
        styleElement.textContent = aosStyles
        document.head.append(styleElement)
        AOS.init({ duration: 600, easing: 'ease-out-cubic', once: true, offset: 40 })
        document.documentElement.classList.add('aos-enabled')
        active = true
      }
      catch (error) {
        console.warn('AOS could not start; content stays visible.', error)
        disable()
      }
    }

    function onPreferenceChange(): void {
      if (reducedMotion.matches) disable()
      else enable()
    }

    function onPageFinish(): void {
      if (!active) return
      window.clearTimeout(refreshTimer)
      refreshTimer = window.setTimeout(() => AOS.refreshHard(), 150)
    }

    function teardown(): void {
      reducedMotion.removeEventListener('change', onPreferenceChange)
      disable()
    }

    reducedMotion.addEventListener('change', onPreferenceChange)
    nuxtApp.hook('app:mounted', enable)
    nuxtApp.hook('page:finish', onPageFinish)
    nuxtApp.vueApp.onUnmount(teardown)
    import.meta.hot?.dispose(teardown)
  },
})
