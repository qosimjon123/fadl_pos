import { extendLocale } from '@nuxt/ui/composables'
import { ru, tg } from '@nuxt/ui/locale'

const ruLocale = extendLocale(ru, { name: 'РУС' })
const tgLocale = extendLocale(tg, { name: 'ТҶ' })

export const localeByCode = { ru: ruLocale, tg: tgLocale }
export const appLocales = [ruLocale, tgLocale]

export type AppLocaleCode = keyof typeof localeByCode

export const appMessages = {
  ru: {
    signIn: 'Вход',
    loginPlaceholder: 'Форма входа будет здесь',
  },
  tg: {
    signIn: 'Ворид',
    loginPlaceholder: 'Шакли ворид дар ин ҷо хоҳад буд',
  },
} as const
