export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBaseUrl,
    timeout: 10000,
    retry: 0,
    credentials: 'omit',
    headers: { Accept: 'application/json, application/problem+json' },
  })

  return { provide: { api } }
})
