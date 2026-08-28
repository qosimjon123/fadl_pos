<script setup lang="ts">
import { useConnection } from '@/shared/server/composables/useConnection'

defineOptions({ name: 'ServerConnection' })
const connected = useConnection()
</script>

<template>
  <UButton
    icon="i-lucide-wifi"
    :color="connected ? 'primary' : 'error'"
    variant="ghost"
    size="xl"
    class="cursor-default pointer-events-none"
    aria-label="Server connection status"
  />
</template>
