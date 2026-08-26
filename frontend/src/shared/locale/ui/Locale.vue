<script setup lang="ts">
import { computed, resolveComponent, type DefineComponent } from 'vue'

import { appLocales, localeByCode, type AppLocaleCode } from '@/shared/locale/config/locales'
import { useAppLocale } from '@/shared/locale/composables/useAppLocale'

const { localeCode } = useAppLocale()

const selectedLocale = computed<string>({
  get: () => localeCode.value,
  set: (value) => {
    if (value in localeByCode) localeCode.value = value as AppLocaleCode
  },
})

const LocaleSelect = resolveComponent('ULocaleSelect') as DefineComponent<{
  modelValue: string
  locales?: unknown[]
  variant?: string
  size?: string
  class?: unknown
}>
</script>

<template>
  <LocaleSelect
    v-model="selectedLocale"
    :locales="[...appLocales]"
    variant="ghost"
    size="xl"
    class="cursor-pointer"
  />
</template>
