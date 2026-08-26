<script setup lang="ts">
import { computed } from 'vue'

import { drawerOverlayDefaults, modalOverlayDefaults } from '@/shared/responsive-overlay/config/defaults'
import { useResponsiveOverlay } from '@/shared/responsive-overlay/composables/useResponsiveOverlay'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  title?: string
  description?: string
  modalProps?: Record<string, unknown>
  drawerProps?: Record<string, unknown>
}>()

defineEmits<{
  'close:prevent': []
}>()

const { isDesktop } = useResponsiveOverlay()

const modalBind = computed(() => ({
  ...modalOverlayDefaults,
  ...props.modalProps,
  title: props.title,
  description: props.description,
  ui: {
    ...modalOverlayDefaults.ui,
    ...(props.modalProps?.ui as Record<string, string> | undefined),
  },
}))

const drawerBind = computed(() => ({
  ...drawerOverlayDefaults,
  ...props.drawerProps,
  title: props.title,
  description: props.description,
  ui: {
    ...drawerOverlayDefaults.ui,
    ...(props.drawerProps?.ui as Record<string, string> | undefined),
  },
}))
</script>

<template>
  <UModal
    v-if="isDesktop"
    v-model:open="open"
    v-bind="modalBind"
    @close:prevent="$emit('close:prevent')"
    :ui="{ footer: 'justify-end' }"
    :close="{
      color: 'primary',
      variant: 'outline',
      class: 'rounded-full'
    }"
  >
    <template v-if="$slots.body" #body="slotProps">
      <slot name="body" v-bind="slotProps" />
    </template>
    <template v-if="$slots.footer" #footer="slotProps"">
      <slot name="footer" v-bind="slotProps" />
    </template>
  </UModal>

  <UDrawer
    v-else
    v-model:open="open"
    v-bind="drawerBind"
    @close:prevent="$emit('close:prevent')"
  >
    <template v-if="$slots.body" #body>
      <slot name="body" />
    </template>
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </UDrawer>
</template>
