/** Independent regression probes for the interrupted snapshot, using its real store and pages. */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { computed, createSSRApp, defineComponent, h, ref } from 'vue'
import { renderToString } from '@vue/server-renderer'
import { useApplicationDraftStore } from '../progress-20261030/frontend/app/stores/applicationDraft'
import ApplicationPage from '../progress-20261030/frontend/app/pages/programs/[slug]/apply.vue'
import Homepage from '../progress-20261030/frontend/app/pages/index.vue'

const idA = '11111111-1111-4111-8111-111111111111'
const idB = '22222222-2222-4222-8222-222222222222'

function program(id: string, enabled = true) {
  return { id, slug: id === idA ? 'program-a' : 'program-b', title: id === idA ? 'Program A' : 'Program B',
    pathway: 'holiday', applications_enabled: enabled, applications_open_at: null,
    applications_close_at: null, min_age_years: 7, max_age_years: 17 }
}

function receipt() {
  return { id: '33333333-3333-4333-8333-333333333333', reference: 'SYNTHETIC-REFERENCE-A',
    program_id: idA, status: 'submitted' as const, submitted_at: '2026-10-30T00:00:00Z', is_retry: false }
}

function fill(store: ReturnType<typeof useApplicationDraftStore>) {
  store.guardianName = 'Synthetic Guardian'
  store.guardianEmail = 'synthetic@example.com'
  store.learnerName = 'Synthetic Learner'
  store.learnerAgeYears = 10
  store.declarationAccepted = true
}

async function render(component: object, pinia: ReturnType<typeof createPinia>, selected = program(idB)) {
  vi.stubGlobal('ref', ref)
  vi.stubGlobal('computed', computed)
  vi.stubGlobal('definePageMeta', () => {})
  vi.stubGlobal('useHead', () => {})
  vi.stubGlobal('useRoute', () => ({ params: { slug: selected.slug } }))
  vi.stubGlobal('useNuxtApp', () => ({ $api: vi.fn() }))
  vi.stubGlobal('useAsyncData', () => ({ data: ref(selected), status: ref('success'), error: ref(null) }))
  const app = createSSRApp(component)
  app.use(pinia)
  for (const name of ['UButton', 'NuxtLink']) {
    app.component(name, defineComponent({ setup: (_, { slots }) => () => h('span', slots.default?.()) }))
  }
  for (const name of ['UIcon', 'WaveDivider', 'BlobShape', 'StarAccent']) {
    app.component(name, defineComponent({ setup: () => () => h('span') }))
  }
  return renderToString(app)
}

describe('Interrupted source snapshot: required behaviour', () => {
  let pinia: ReturnType<typeof createPinia>
  beforeEach(() => {
    vi.unstubAllGlobals()
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('actually clears a previous confirmation when the page attempts to clear it', () => {
    const store = useApplicationDraftStore()
    store.recordReceipt(receipt(), 'program-a')
    // This is the current page's line 84, executed before its try/catch and HTTP call.
    ;(store as any).receipt = null
    expect(store.receipt).toBeNull()
  })

  it('renders the homepage using the actual current photograph registry', async () => {
    await expect(render(Homepage, pinia)).resolves.toBeTypeOf('string')
  })

  it('does not show Program A’s confirmation on Program B', async () => {
    useApplicationDraftStore().recordReceipt(receipt(), 'program-a')
    const html = await render(ApplicationPage, pinia, program(idB))
    expect(html).toContain('Apply for Program B')
    expect(html).not.toContain('SYNTHETIC-REFERENCE-A')
  })

  it('keeps a confirmed receipt visible after its program is disabled', async () => {
    useApplicationDraftStore().recordReceipt(receipt(), 'program-a')
    const html = await render(ApplicationPage, pinia, program(idA, false))
    expect(html).toContain('SYNTHETIC-REFERENCE-A')
  })

  it('changes keys when the unchanged form targets another program through the current page flow', () => {
    const store = useApplicationDraftStore()
    fill(store)
    const first = { url: '/programs/program-a/applications', body: store.buildPayload() }
    const second = { url: '/programs/program-b/applications', body: store.buildPayload() }
    expect(first.url).not.toBe(second.url)
    expect(first.body.idempotency_key).not.toBe(second.body.idempotency_key)
  })

  it('does not accept a stale response after reset followed by a new attempt', () => {
    const store = useApplicationDraftStore()
    fill(store)
    const old = store.beginSubmission('program-a')
    store.resetAll()
    fill(store)
    store.guardianName = 'New draft to preserve'
    store.beginSubmission('program-b')
    store.recordReceipt(receipt(), 'program-a', old.attemptId)
    expect(store.guardianName).toBe('New draft to preserve')
    expect(store.latestReceipt).toBeNull()
  })
})
