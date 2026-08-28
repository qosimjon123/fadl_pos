<script setup lang="ts">
import Locale from '@/shared/locale/ui/Locale.vue'
import Connection from '@/shared/server/ui/Connection.vue'
import ServerSettings from '@/shared/server/ui/ServerSettings.vue'
import Theme from '@/shared/theme/ui/Theme.vue'
</script>

<template>
  <UHeader title="Fadl POS" to="/login" :toggle="false">
    <template #right>
      <div class="flex items-center gap-1">
        <Connection />
        <Locale />
        <ServerSettings />
        <Theme />
      </div>
    </template>
  </UHeader>
</template>
