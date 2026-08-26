import { computed } from 'vue'
import { createSharedComposable, useLocalStorage, usePreferredLanguages } from '@vueuse/core'

import { appMessages, localeByCode, type AppLocaleCode } from '@/shared/locale/config/locales'

function resolveDefaultLocale(): AppLocaleCode {
  const preferred = usePreferredLanguages().value
  const match = preferred.find((l) => l.startsWith('tg') || l.startsWith('ru'))
  if (match?.startsWith('tg')) return 'tg'
  return 'ru'
}

const _useAppLocale = () => {
  const localeCode = useLocalStorage<AppLocaleCode>('fadl-locale', resolveDefaultLocale())

  const locale = computed(() => localeByCode[localeCode.value] ?? localeByCode.ru)

  const t = (key: keyof typeof appMessages.ru) =>
    appMessages[localeCode.value]?.[key] ?? appMessages.ru[key]

  return { localeCode, locale, t }
}

export const useAppLocale = createSharedComposable(_useAppLocale)
