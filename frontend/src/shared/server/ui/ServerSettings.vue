<script setup lang="ts">
import ResponsiveOverlay from '@/shared/responsive-overlay/ui/ResponsiveOverlay.vue'
import { useServerUrl } from '@/shared/server/composables/useServerUrl'

const { draftUrl, open, openSettings, cancelSettings, saveServerUrl } = useServerUrl()
</script>

<template>
  <UButton
    icon="i-lucide-settings"
    color="primary"
    variant="ghost"
    size="xl"
    class="cursor-pointer w-10"
    aria-label="Server settings"
    @click="openSettings()"
  />

  <ResponsiveOverlay
    v-model:open="open"
    title="Server settings"
    description="Enter your Frappe server URL"
  >
    <template #body>
      <UFormField label="Server URL" name="serverUrl" required class="w-full">
        <UInput
          v-model="draftUrl"
          placeholder="https://example.com"
          autocomplete="url"
          @keydown.enter.prevent="saveServerUrl()"
          required
          class="w-full py-2"
        />
      </UFormField>
    </template>

    <template #footer>
      <div class="flex gap-2">
        <UButton
          label="Cancel"
          color="neutral"
          variant="outline"
          class="flex-1 justify-center"
          size="xl"
          @click="cancelSettings()"
        />
        <UButton
          label="Save"
          color="primary"
          class="flex-1 justify-center"
          :disabled="!draftUrl.trim()"
          size="xl"
          @click="saveServerUrl()"
        />
      </div>
    </template>
  </ResponsiveOverlay>
</template>
