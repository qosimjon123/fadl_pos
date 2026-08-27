import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

const SESSION_EXC = new Set(['AuthenticationError', 'SessionExpired'])

const DEFAULT_SKIP_URLS = ['/api/method/login', '/api/method/logout']

function shortExcType(raw: string | undefined): string | undefined {
  if (!raw) return undefined
  const trimmed = raw.trim()
  return trimmed.includes('.') ? trimmed.split('.').pop() : trimmed
}

function responseBody(error: AxiosError): Record<string, unknown> | undefined {
  const data = error.response?.data
  return typeof data === 'object' && data !== null ? (data as Record<string, unknown>) : undefined
}

/** Mirrors Frappe desk session checks — 401, session_expired flag, auth exception types. */
export function isSessionTerminated(error: AxiosError): boolean {
  const body = responseBody(error)

  if (body?.session_expired === true) return true

  const excType = shortExcType(typeof body?.exc_type === 'string' ? body.exc_type : undefined)
  if (excType && SESSION_EXC.has(excType)) return true

  return error.response?.status === 401
}

export function isAuthEndpoint(config: InternalAxiosRequestConfig, extraSkipUrls: string[] = []): boolean {
  const url = config.url ?? ''
  const skipUrls = [...DEFAULT_SKIP_URLS, ...extraSkipUrls]
  return skipUrls.some((skip) => url.includes(skip))
}
