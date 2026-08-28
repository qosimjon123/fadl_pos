import type { AxiosInstance, AxiosError } from 'axios'

import router from '@/router'
import { FRAPPE_SESSION_TERMINATED_EXC_TYPES } from '@/shared/server/config/storage'
import { connected } from '@/shared/server/store/connection'
import { getToken, resetToken } from '@/shared/server/store/token'

export function attachRawAuthorizationHeaderInterceptor(axios: AxiosInstance) {
  axios.interceptors.request.use((c) => {
    const token = getToken()
    if (token) c.headers.Authorization = token
    return c
  })
}

export function attachFrappeUnauthorizedInterceptor(axios: AxiosInstance) {
  axios.interceptors.response.use(
    (r) => {
      connected.value = true
      return r
    },
    async (e: AxiosError) => {
      connected.value = !e.response || e.response.status >= 500
      const data = e.response?.data as { exc_type?: string; errors?: { type: string }[] }
      const type = data?.exc_type ?? data?.errors?.[0]?.type
      if (type && FRAPPE_SESSION_TERMINATED_EXC_TYPES.has(type)) {
        resetToken()
        if (router.currentRoute.value.name !== 'login') await router.push({ name: 'login' })
      }
      return Promise.reject(e)
    },
  )
}
