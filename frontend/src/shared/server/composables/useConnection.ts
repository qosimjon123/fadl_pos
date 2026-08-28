import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import { ping } from '@/shared/server/api/ping'
import { connected } from '@/shared/server/store/connection'
import { useServerUrl } from './useServerUrl'

export function useConnection() {
  const { serverUrl } = useServerUrl()
  const { isSuccess } = useQuery({
    queryKey: computed(() => ['ping', serverUrl.value]),
    queryFn: ping,
    refetchInterval: (query) => (query.state.status === 'error' ? 10000 : false),
  })
  return computed(() => connected.value || isSuccess.value)
}
