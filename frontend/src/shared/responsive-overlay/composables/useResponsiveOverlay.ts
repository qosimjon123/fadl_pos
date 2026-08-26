import { createSharedComposable, useMediaQuery } from '@vueuse/core'

const _useResponsiveOverlay = () => {
  const isDesktop = useMediaQuery('(min-width: 768px)')
  return { isDesktop }
}

export const useResponsiveOverlay = createSharedComposable(_useResponsiveOverlay)
