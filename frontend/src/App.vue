<script setup lang="ts">
import HomeView from './views/HomeView.vue'
</script>

<template>
  <n-config-provider>
    <n-message-provider>
      <n-dialog-provider>
        <HomeView />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
body {
  margin: 0;
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: #f5f7fa;
}
</style>
