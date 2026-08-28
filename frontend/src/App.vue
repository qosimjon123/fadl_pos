<script setup lang="ts">
import { watchEffect } from 'vue'

import { useAppLocale } from '@/shared/locale/composables/useAppLocale'
import { useConnection } from '@/shared/server/composables/useConnection'

const { locale } = useAppLocale()
useConnection()

watchEffect(() => {
  document.documentElement.lang = locale.value.code
  document.documentElement.dir = locale.value.dir
})
</script>

<template>
  <UApp :locale="locale">
    <RouterView />
  </UApp>
</template>
