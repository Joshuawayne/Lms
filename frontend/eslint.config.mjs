import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  {
    ignores: [
      '.output',
      '.output/**',
      '**/.output/**',
      '.nuxt',
      '.nuxt/**',
      '**/.nuxt/**',
      'dist',
      'dist/**',
      '**/dist/**',
      'node_modules',
      'node_modules/**',
      '**/node_modules/**',
      'app/api/generated/**',
      '**/app/api/generated/**',
      '*.log',
      '**/*.log',
    ],
  },
)
