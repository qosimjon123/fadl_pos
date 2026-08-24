<template>
  <UFooter>
    <template #left>
      <p class="text-muted text-sm">© {{ year }} Fadl POS</p>
    </template>
  </UFooter>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>
