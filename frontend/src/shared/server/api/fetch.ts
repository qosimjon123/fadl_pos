import { useServerUrl } from '@/shared/server/composables/useServerUrl'
import { getToken } from '@/shared/server/store/token'

export function setupFrappeApi() {
  const { serverUrl } = useServerUrl()
  const base = globalThis.fetch

  globalThis.fetch = (input, init) => {
    if (typeof input !== 'string' || !input.startsWith('/api/')) return base(input, init)

    const headers = new Headers(init?.headers)
    const token = getToken()
    if (token) headers.set('Authorization', token)

    return base(new URL(input, serverUrl.value), { ...init, credentials: 'omit', headers })
  }
}
