import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import ui from '@nuxt/ui/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    ui({
      ui: {
        colors: {
          primary: 'fadl',
          secondary: 'blue',
          success: 'green',
          info: 'blue',
          warning: 'yellow',
          error: 'red',
          neutral: 'slate',
        },
        button: {
          slots: {
            base: 'disabled:opacity-100 disabled:blur-[1px] aria-disabled:opacity-40 aria-disabled:blur-[1px]',
          },
          variants: {
            size: {
              xs: {
                base: 'px-2 py-1 text-xs gap-1',
                leadingIcon: 'size-4',
                trailingIcon: 'size-4',
                leadingAvatarSize: '2xs',
              },
              sm: {
                base: 'px-2.5 py-1.5 text-xs gap-1.5',
                leadingIcon: 'size-4',
                trailingIcon: 'size-4',
                leadingAvatarSize: '2xs',
              },
              md: {
                base: 'px-6 py-4 text-sm gap-4',
                leadingIcon: 'size-5',
                trailingIcon: 'size-5',
                leadingAvatarSize: '2xs',
              },
              lg: {
                base: 'px-3.5 py-2.5 text-sm gap-2',
                leadingIcon: 'size-5',
                trailingIcon: 'size-5',
                leadingAvatarSize: '2xs',
              },
              xl: {
                base: 'px-4 py-3 text-base gap-2.5',
                leadingIcon: 'size-6',
                trailingIcon: 'size-6',
                leadingAvatarSize: '2xs',
              },
            },
          },
          compoundVariants: [
            { size: 'xs',  class: 'p-1' },
            { size: 'sm',  class: 'p-1.5' },
            { size: 'md',  class: 'p-4' },
            { size: 'lg',  class: 'p-2.5' },
            { size: 'xl',  class: 'p-3' },
          ],
        },
      },
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true, // слушать 0.0.0.0 — нужно для туннеля
    allowedHosts: true,
  },
})
