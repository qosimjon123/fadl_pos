import { describe, expect, it } from 'vitest'
import { AxiosError, type InternalAxiosRequestConfig } from 'axios'

import { isAuthEndpoint, isSessionTerminated } from '../session'

function axiosError(
  status: number,
  data: Record<string, unknown>,
  url: string,
): AxiosError {
  const config = { url } as InternalAxiosRequestConfig
  const error = new AxiosError('Request failed', AxiosError.ERR_BAD_REQUEST, config, {}, {
    status,
    data,
    statusText: 'Error',
    headers: {},
    config,
  })
  error.config = config
  return error
}

describe('isSessionTerminated', () => {
  it('returns true for HTTP 401', () => {
    expect(isSessionTerminated(axiosError(401, {}, '/api/method/foo'))).toBe(true)
  })

  it('returns true when session_expired flag is set', () => {
    expect(
      isSessionTerminated(axiosError(403, { session_expired: true }, '/api/method/foo')),
    ).toBe(true)
  })

  it('returns true for AuthenticationError exc_type', () => {
    expect(
      isSessionTerminated(
        axiosError(403, { exc_type: 'frappe.exceptions.AuthenticationError' }, '/api/method/foo'),
      ),
    ).toBe(true)
  })

  it('returns false for plain 403 permission error', () => {
    expect(
      isSessionTerminated(
        axiosError(403, { _server_messages: 'Not permitted' }, '/api/method/foo'),
      ),
    ).toBe(false)
  })
})

describe('isAuthEndpoint', () => {
  it('skips default login and logout paths', () => {
    expect(isAuthEndpoint({ url: '/api/method/login' } as InternalAxiosRequestConfig)).toBe(true)
    expect(isAuthEndpoint({ url: '/api/method/logout' } as InternalAxiosRequestConfig)).toBe(true)
  })

  it('supports custom skip paths', () => {
    expect(
      isAuthEndpoint({ url: '/api/method/fadl_pos.api.login' } as InternalAxiosRequestConfig, [
        '/api/method/fadl_pos.api.login',
      ]),
    ).toBe(true)
  })
})
