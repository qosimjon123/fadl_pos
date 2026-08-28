<script setup lang="ts">
import { connected } from '@/shared/server/store/connection'

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
