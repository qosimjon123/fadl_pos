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
    'responsive-drawer-content fixed inset-x-0 bottom-0 z-50 flex max-h-[95dvh] flex-col rounded-t-lg bg-default pb-[max(1rem,env(safe-area-inset-bottom))] shadow-lg outline-none',
  handleArea: 'shrink-0 px-4 pt-3',
  handle: 'mx-auto h-1.5 w-12 rounded-full bg-accented',
  sections: 'flex min-h-0 flex-1 flex-col divide-y divide-default',
  header: 'flex flex-col gap-1 p-4 sm:px-6',
  title: 'text-lg font-semibold text-highlighted',
  description: 'text-sm text-muted',
  body: 'flex-1 overflow-y-auto p-4 sm:p-6',
  footer: 'shrink-0 p-4 sm:px-6',
} as const
