const softOverlay = 'bg-elevated/55 backdrop-blur-sm'

export const modalOverlayDefaults = {
  close: {
    color: 'primary',
    variant: 'outline',
    class: 'rounded-full',
  },
  dismissible: false,
  modal: true,
  ui: {
    overlay: softOverlay,
    footer: 'justify-end',
  },
} as const

export const drawerDefaults = {
  overlay: `${softOverlay} fixed inset-0 z-40`,
  content:
    'responsive-drawer-content fixed inset-x-0 bottom-0 z-50 flex max-h-[90dvh] flex-col rounded-t-lg bg-default px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-3 shadow-lg outline-none',
  handle: 'mx-auto mb-3 h-1.5 w-12 shrink-0 rounded-full bg-accented',
  title: 'text-lg font-semibold text-highlighted',
  description: 'mt-1 text-sm text-muted',
  body: 'flex-1 overflow-y-auto py-2',
  footer: 'mt-4 shrink-0',
} as const
