import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'

const serverUrl = vi.hoisted(() => ({ value: 'http://test.local' }))

vi.mock('@/shared/server/composables/useServerUrl', () => ({
  useServerUrl: () => ({ serverUrl }),
}))

import {
  configureFrappeClient,
  getFrappeApp,
  readAuthHeaderFromStorage,
  resetFrappeApp,
} from '../index'
import { AUTH_TOKEN_STORAGE_KEY } from '@/shared/server/config/storage'

function failingAdapter(status: number, data: Record<string, unknown>, _url: string) {
  return async (config: InternalAxiosRequestConfig) => {
    const error = new AxiosError('Request failed', AxiosError.ERR_BAD_REQUEST, config, {}, {
      status,
      data,
      statusText: 'Error',
      headers: {},
      config,
    })
    error.config = config
    throw error
  }
}

function successAdapter(data: unknown = { ok: true }) {
  return async (config: InternalAxiosRequestConfig): Promise<AxiosResponse> => ({
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  })
}

describe('frappe api client', () => {
  beforeEach(() => {
    serverUrl.value = 'http://test.local'
    localStorage.clear()
    resetFrappeApp()
    configureFrappeClient({})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns null when server URL is empty', () => {
    serverUrl.value = ''
    expect(getFrappeApp()).toBeNull()
  })

  it('reuses cached FrappeApp for the same server URL', () => {
    const first = getFrappeApp()
    const second = getFrappeApp()
    expect(first).not.toBeNull()
    expect(second).toBe(first)
  })

  it('recreates FrappeApp when server URL changes', () => {
    const first = getFrappeApp()
    serverUrl.value = 'http://other.local'
    const second = getFrappeApp()
    expect(second).not.toBeNull()
    expect(second).not.toBe(first)
  })

  it('sets Authorization from getAuthHeader on each request', async () => {
    configureFrappeClient({
      getAuthHeader: () => 'Basic abc123',
    })

    const app = getFrappeApp()!
    let capturedAuth: string | undefined

    app.axios.defaults.adapter = async (config) => {
      capturedAuth = config.headers?.Authorization as string | undefined
      return (await successAdapter()(config)) as AxiosResponse
    }

    await app.axios.get('/api/method/ping')

    expect(capturedAuth).toBe('Basic abc123')
  })

  it('removes Authorization when token is absent', async () => {
    configureFrappeClient({
      getAuthHeader: () => undefined,
    })

    const app = getFrappeApp()!
    let capturedAuth: string | undefined = 'stale'

    app.axios.defaults.adapter = async (config) => {
      capturedAuth = config.headers?.Authorization as string | undefined
      return (await successAdapter()(config)) as AxiosResponse
    }

    await app.axios.get('/api/method/ping')

    expect(capturedAuth).toBeUndefined()
  })

  it('reads Basic token from localStorage helper', () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, 'Basic stored-token')
    expect(readAuthHeaderFromStorage()).toBe('Basic stored-token')
  })

  it('calls onSessionTerminated once for parallel 401 responses', async () => {
    const onSessionTerminated = vi.fn<() => Promise<void>>().mockResolvedValue(undefined)
    configureFrappeClient({ onSessionTerminated })

    const app = getFrappeApp()!
    app.axios.defaults.adapter = failingAdapter(401, {}, '/api/method/foo')

    await expect(
      Promise.allSettled([app.axios.get('/api/method/foo'), app.axios.get('/api/method/bar')]),
    ).resolves.toBeDefined()

    expect(onSessionTerminated).toHaveBeenCalledTimes(1)
  })

  it('does not call onSessionTerminated for plain 403', async () => {
    const onSessionTerminated = vi.fn<() => void>()
    configureFrappeClient({ onSessionTerminated })

    const app = getFrappeApp()!
    app.axios.defaults.adapter = failingAdapter(403, { _server_messages: 'Not permitted' }, '/api/method/foo')

    await expect(app.axios.get('/api/method/foo')).rejects.toBeInstanceOf(AxiosError)
    expect(onSessionTerminated).not.toHaveBeenCalled()
  })

  it('skips session cleanup for login endpoint', async () => {
    const onSessionTerminated = vi.fn<() => void>()
    configureFrappeClient({ onSessionTerminated })

    const app = getFrappeApp()!
    app.axios.defaults.adapter = failingAdapter(401, {}, '/api/method/login')

    await expect(app.axios.post('/api/method/login')).rejects.toBeInstanceOf(AxiosError)
    expect(onSessionTerminated).not.toHaveBeenCalled()
  })

  it('preserves original axios rejection after session cleanup', async () => {
    configureFrappeClient({
      onSessionTerminated: vi.fn<() => Promise<void>>().mockResolvedValue(undefined),
    })

    const app = getFrappeApp()!
    app.axios.defaults.adapter = failingAdapter(401, { message: 'Unauthorized' }, '/api/method/foo')

    await expect(app.axios.get('/api/method/foo')).rejects.toMatchObject({
      response: { status: 401, data: { message: 'Unauthorized' } },
    })
  })

  it('allows future session cleanup after a successful response', async () => {
    const onSessionTerminated = vi.fn<() => Promise<void>>().mockResolvedValue(undefined)
    configureFrappeClient({ onSessionTerminated })

    const app = getFrappeApp()!
    app.axios.defaults.adapter = failingAdapter(401, {}, '/api/method/foo')

    await expect(app.axios.get('/api/method/foo')).rejects.toBeInstanceOf(AxiosError)
    expect(onSessionTerminated).toHaveBeenCalledTimes(1)

    app.axios.defaults.adapter = successAdapter()
    await app.axios.get('/api/method/recover')

    app.axios.defaults.adapter = failingAdapter(401, {}, '/api/method/foo')
    await expect(app.axios.get('/api/method/foo')).rejects.toBeInstanceOf(AxiosError)
    expect(onSessionTerminated).toHaveBeenCalledTimes(2)
  })
})
