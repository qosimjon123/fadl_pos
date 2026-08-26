<script setup lang="ts">
import { useAppLocale } from '@/shared/locale/composables/useAppLocale'

const { t } = useAppLocale()
</script>

<template>
  <UMain>
    <div class="flex items-center justify-center p-4">
      <UCard>
        <template #header>{{ t('signIn') }}</template>
        <p class="text-muted">{{ t('loginPlaceholder') }}</p>
      </UCard>
    </div>
  </UMain>
</template>
