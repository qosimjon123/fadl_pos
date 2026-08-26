<script setup lang="ts">
import Locale from '@/shared/locale/ui/Locale.vue'
import Theme from '@/shared/theme/ui/Theme.vue'
</script>

<template>
  <UHeader title="Fadl POS" to="/login">
    <template #right>
      <div class="flex items-center gap-1">
        <Locale />
        <Theme />
      </div>
    </template>
  </UHeader>
</template>
