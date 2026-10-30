/**
 * Nuxt UI colour roles bound to the Jjenga Code palette.
 *
 * `purple` and `navy` resolve to the scales declared in assets/styles/tokens.css, whose
 * 500 (purple) and 900 (navy) steps are the exact poster colours. Nuxt UI uses the 500
 * step for solid primary surfaces, so UI components render in #8C2ACA.
 */
export default defineAppConfig({
  ui: {
    colors: {
      primary: 'purple',
      secondary: 'pink',
      warning: 'yellow',
      error: 'pink',
      neutral: 'navy',
    },
  },
})

