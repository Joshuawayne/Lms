/**
 * Lenis smooth scrolling — optional enhancement for pointer/wheel scrolling only.
 *
 * Behaviour contract:
 *   - Disabled for reduced motion (at start-up and when the preference changes).
 *   - Touch stays native (`syncTouch` is off) and keyboard scrolling is never intercepted.
 *   - Lenis does NOT handle anchors or route scroll position. Plain `#hash` links use the
 *     browser's own jump (header offset comes from `scroll-padding-top`); route changes,
 *     hash navigation and back/forward restoration are owned by app/router.options.ts.
 *   - It is created after `app:mounted`, driven by one requestAnimationFrame loop, and
 *     destroyed on app unmount and HMR dispose (loop cancelled, instance destroyed).
 */
import Lenis from 'lenis'

export default defineNuxtPlugin({
  name: 'lenis',
  enforce: 'post',
  setup(nuxtApp) {
    if (import.meta.server) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    let lenis: Lenis | null = null
    let frame: number | null = null

    function tick(time: number): void {
      lenis?.raf(time)
      frame = requestAnimationFrame(tick)
    }

    function start(): void {
      if (lenis || reducedMotion.matches) return
      try {
        lenis = new Lenis({
          autoRaf: false,
          anchors: false,
          syncTouch: false,
          duration: 1.05,
          easing: (t: number) => Math.min(1, 1.001 - 2 ** (-10 * t)),
        })
        frame = requestAnimationFrame(tick)
      }
      catch (error) {
        console.warn('Lenis could not start; native scrolling is used.', error)
        stop()
      }
    }

    function stop(): void {
      if (frame !== null) cancelAnimationFrame(frame)
      frame = null
      lenis?.destroy()
      lenis = null
    }

    function onPreferenceChange(): void {
      if (reducedMotion.matches) stop()
      else start()
    }

    function teardown(): void {
      reducedMotion.removeEventListener('change', onPreferenceChange)
      stop()
    }

    reducedMotion.addEventListener('change', onPreferenceChange)
    nuxtApp.hook('app:mounted', start)
    nuxtApp.vueApp.onUnmount(teardown)
    import.meta.hot?.dispose(teardown)

    return {
      provide: {
        lenis: {
          /** The live instance, or null when disabled (reduced motion or failed start). */
          instance: (): Lenis | null => lenis,
          destroy: teardown,
        },
      },
    }
  },
})
