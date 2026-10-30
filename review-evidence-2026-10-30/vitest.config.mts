/** Isolated review configuration; actual uploaded Vue components are compiled unchanged. */
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('.', import.meta.url))
export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '~': fileURLToPath(new URL('../progress-20261030/frontend/app', import.meta.url)) } },
  test: { root, include: ['interrupted-state.test.ts'], environment: 'node', fileParallelism: false },
})
