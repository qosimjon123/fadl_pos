import { FrappeApp } from 'frappe-js-sdk'
import type { AxiosError, AxiosInstance } from 'axios'

import { useServerUrl } from '@/shared/server/composables/useServerUrl'
import { AUTH_TOKEN_STORAGE_KEY } from '@/shared/server/config/storage'

import { isAuthEndpoint, isSessionTerminated } from './session'

export { isAuthEndpoint, isSessionTerminated } from './session'

export type FrappeClientConfig = {
  /** Returns full Authorization value, e.g. `Basic abc123`. */
  getAuthHeader?: () => string | undefined
  /** Clears local auth state and redirects to login — no server logout call here. */
  onSessionTerminated?: () => void | Promise<void>
  /** Custom login/logout paths that must not trigger session cleanup. */
  skipSessionCheckUrls?: string[]
}

const attached = new WeakSet<AxiosInstance>()

let config: FrappeClientConfig = {}
let frappeApp: FrappeApp | null = null
let sessionCleanup: Promise<void> | null = null

export function configureFrappeClient(next: FrappeClientConfig): void {
  config = next
}

export function readAuthHeaderFromStorage(): string | undefined {
  try {
    const value = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim()
    return value || undefined
  } catch {
    return undefined
  }
}

export function resetFrappeApp(): void {
  frappeApp = null
  sessionCleanup = null
}

async function runSessionTerminated(): Promise<void> {
  if (sessionCleanup) return sessionCleanup

  sessionCleanup = (async () => {
    try {
      await config.onSessionTerminated?.()
    } catch {
      /* keep rejection chain */
    }
  })()

  return sessionCleanup
}

function attachInterceptors(axios: AxiosInstance): void {
  if (attached.has(axios)) return
  attached.add(axios)

  axios.interceptors.request.use((req) => {
    const header = config.getAuthHeader?.()
    if (typeof header === 'string' && header.length > 0) {
      req.headers.Authorization = header
    } else {
      delete req.headers.Authorization
    }
    return req
  })

  axios.interceptors.response.use(
    (response) => {
      sessionCleanup = null
      return response
    },
    async (error: AxiosError) => {
      const reqConfig = error.config

      if (
        reqConfig &&
        !isAuthEndpoint(reqConfig, config.skipSessionCheckUrls) &&
        isSessionTerminated(error)
      ) {
        await runSessionTerminated()
      }

      return Promise.reject(error)
    },
  )
}

function createFrappeApp(url: string): FrappeApp {
  const app = new FrappeApp(url)
  attachInterceptors(app.axios)
  return app
}

export function getFrappeApp(): FrappeApp | null {
  const url = useServerUrl().serverUrl.value.trim()
  if (!url) return null

  if (!frappeApp || frappeApp.url !== url) {
    frappeApp = createFrappeApp(url)
  }

  return frappeApp
}

export function getFrappeCall() {
  return getFrappeApp()?.call() ?? null
}

export function getFrappeDb() {
  return getFrappeApp()?.db() ?? null
}

export function getFrappeFileUpload() {
  return getFrappeApp()?.file() ?? null
}
