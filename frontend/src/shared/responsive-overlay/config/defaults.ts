const softOverlay = 'bg-elevated/55 backdrop-blur-sm'

export const modalOverlayDefaults = {
  close: true,
  dismissible: false,
  modal: true,
  ui: { overlay: softOverlay },
} as const

export const drawerOverlayDefaults = {
  close: false,
  dismissible: true,
  modal: true,
  handle: true,
  ui: { overlay: softOverlay },
} as const
