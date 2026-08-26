<script setup lang="ts">
import { appLocales } from '@/shared/locale/config/locales'
import { useAppLocale } from '@/shared/locale/composables/useAppLocale'

const { localeCode } = useAppLocale()
</script>

<template>
  <ULocaleSelect
    v-model="localeCode"
    :locales="[...appLocales]"
    variant="ghost"
    size="xl"
    class="cursor-pointer"
  />
</template>
