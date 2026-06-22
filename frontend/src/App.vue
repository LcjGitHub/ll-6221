<script setup lang="ts">
import { ref } from 'vue'
import HomeView from './views/HomeView.vue'
import SamplingRecordView from './views/SamplingRecordView.vue'
import StatisticsView from './views/StatisticsView.vue'

type TabKey = 'overview' | 'points' | 'records'

const activeKey = ref<TabKey>('overview')
</script>

<template>
  <n-config-provider>
    <n-message-provider>
      <n-dialog-provider>
        <n-layout style="min-height: 100vh">
          <n-tabs
            v-model:value="activeKey"
            type="line"
            style="padding: 0 24px; border-bottom: 1px solid #e0e0e0"
          >
            <n-tab-pane name="overview" tab="数据概览">
              <StatisticsView />
            </n-tab-pane>
            <n-tab-pane name="points" tab="采样点管理">
              <HomeView />
            </n-tab-pane>
            <n-tab-pane name="records" tab="采样记录管理">
              <SamplingRecordView />
            </n-tab-pane>
          </n-tabs>
        </n-layout>
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
