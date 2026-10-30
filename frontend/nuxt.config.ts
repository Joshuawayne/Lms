export default defineNuxtConfig({
  compatibilityDate: '2026-10-27',
  telemetry: false,
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@pinia/nuxt', '@nuxt/eslint'],
  css: ['~/assets/styles/main.css'],
  ui: { fonts: false },
  typescript: { strict: true },

  /*
   * Component registration is explicit so templates and the registry agree.
   * Without these entries Nuxt prefixes `components/ui/WaveDivider.vue` as
   * `UiWaveDivider` and ignores `features/**` entirely, which left the decorative
   * shapes and the program card unresolved in templates.
   */
  components: [
    { path: '~/components/ui', pathPrefix: false },
    { path: '~/features', pattern: '**/components/*.vue', pathPrefix: false },
    { path: '~/components', pathPrefix: false },
  ],

  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
      /*
       * Editorial choice only: which published program the homepage spotlights.
       * Its title, dates, eligibility and application availability always come
       * from the API record, never from this setting. Override with
       * NUXT_PUBLIC_FEATURED_PROGRAM_SLUG; leave empty to hide the spotlight.
       */
      featuredProgramSlug: 'coding-robotics-camp-nov-2026',
    },
  },
})
