import { AUTH_TOKEN_STORAGE_KEY } from '@/shared/server/config/storage'

export function getToken(): string | undefined {
  return localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim() || undefined
}

export function setToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token.trim())
}

export function resetToken(): void {
  localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
}
