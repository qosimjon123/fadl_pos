import { ref } from 'vue'
import { createSharedComposable, useLocalStorage } from '@vueuse/core'

import { DEFAULT_SERVER_URL, SERVER_URL_STORAGE_KEY } from '@/shared/server/config/storage'

const _useServerUrl = () => {
  const serverUrl = useLocalStorage(SERVER_URL_STORAGE_KEY, DEFAULT_SERVER_URL)
  const draftUrl = ref(serverUrl.value)
  const open = ref(false)

  function openSettings() {
    draftUrl.value = serverUrl.value
    open.value = true
  }

  function cancelSettings() {
    open.value = false
  }

  function saveServerUrl() {
    const value = draftUrl.value.trim()
    if (!value) return

    serverUrl.value = value
    open.value = false
  }

  return { serverUrl, draftUrl, open, openSettings, cancelSettings, saveServerUrl }
}

export const useServerUrl = createSharedComposable(_useServerUrl)
