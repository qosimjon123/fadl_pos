<script setup lang="ts">
import type {
  DrawerContentProps,
  DrawerHandleProps,
  DrawerOverlayProps,
  DrawerRootProps,
} from 'reka-ui'
import {
  DrawerContent,
  DrawerDescription,
  DrawerHandle,
  DrawerOverlay,
  DrawerPortal,
  DrawerRoot,
  DrawerTitle,
} from 'reka-ui'

import { drawerDefaults, modalOverlayDefaults } from '@/shared/responsive-overlay/config/defaults'
import { useResponsiveOverlay } from '@/shared/responsive-overlay/composables/useResponsiveOverlay'

export type ResponsiveDrawerProps = {
  root?: Omit<DrawerRootProps, 'open'>
  overlay?: DrawerOverlayProps
  content?: DrawerContentProps
  handle?: DrawerHandleProps
}

const open = defineModel<boolean>('open', { required: true })

defineProps<{
  title?: string
  description?: string
  modalProps?: Record<string, unknown>
  drawerProps?: ResponsiveDrawerProps
}>()

const { isDesktop } = useResponsiveOverlay()
</script>

<template>
  <UModal
    v-if="isDesktop"
    v-model:open="open"
    v-bind="{ ...modalOverlayDefaults, ...modalProps, title, description }"
  >
    <template v-if="$slots.body" #body="slotProps">
      <slot name="body" v-bind="slotProps" />
    </template>
    <template v-if="$slots.footer" #footer="slotProps">
      <slot name="footer" v-bind="slotProps" />
    </template>
  </UModal>

  <DrawerRoot v-else v-model:open="open" v-bind="drawerProps?.root">
    <DrawerPortal>
      <DrawerOverlay :class="drawerDefaults.overlay" v-bind="drawerProps?.overlay" />

      <DrawerContent :class="drawerDefaults.content" v-bind="drawerProps?.content">
        <DrawerHandle :class="drawerDefaults.handle" v-bind="drawerProps?.handle" />

        <DrawerTitle v-if="title" :class="drawerDefaults.title">
          {{ title }}
        </DrawerTitle>

        <DrawerDescription v-if="description" :class="drawerDefaults.description">
          {{ description }}
        </DrawerDescription>

        <div v-if="$slots.body" :class="drawerDefaults.body">
          <slot name="body" />
        </div>

        <div v-if="$slots.footer" :class="drawerDefaults.footer">
          <slot name="footer" />
        </div>
      </DrawerContent>
    </DrawerPortal>
  </DrawerRoot>
</template>

<style>
.responsive-drawer-content {
  --bleed: 48px;
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + var(--bleed));
  margin-bottom: calc(-1 * var(--bleed));
  transform: translateY(var(--drawer-swipe-movement-y, 0px));
  transition: transform 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.responsive-drawer-content[data-state='open'] {
  animation: responsive-drawer-in 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.responsive-drawer-content[data-state='closed'] {
  animation: responsive-drawer-out 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.responsive-drawer-content[data-swiping] {
  transition-duration: 0ms;
}

@keyframes responsive-drawer-in {
  from {
    translate: 0 calc(100% - var(--bleed));
  }
}

@keyframes responsive-drawer-out {
  to {
    translate: 0 calc(100% - var(--bleed));
  }
}
</style>
