<script setup lang="ts">
import { computed } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { fetchStatistics } from '../api'

const { state: statistics, isLoading } = useAsyncState(fetchStatistics, null, {
  immediate: true,
  resetOnExecute: false,
})

const sourceTypeEntries = computed(() => {
  if (!statistics.value) return []
  return Object.entries(statistics.value.source_type_counts).sort(
    (a, b) => b[1] - a[1]
  )
})

const directionEntries = computed(() => {
  if (!statistics.value) return []
  return Object.entries(statistics.value.direction_counts).sort(
    (a, b) => b[1] - a[1]
  )
})

const maxSourceTypeCount = computed(() => {
  if (sourceTypeEntries.value.length === 0) return 1
  return Math.max(...sourceTypeEntries.value.map(([, v]) => v))
})

const maxDirectionCount = computed(() => {
  if (directionEntries.value.length === 0) return 1
  return Math.max(...directionEntries.value.map(([, v]) => v))
})

const directionColors: Record<string, string> = {
  东: '#2080f0',
  南: '#18a058',
  西: '#f0a020',
  北: '#d03050',
  东南: '#63e2b7',
  东北: '#20c997',
  西南: '#e6a23c',
  西北: '#909399',
}

function getDirectionColor(dir: string): string {
  return directionColors[dir] || '#63e2b7'
}

const sourceTypeColors = [
  '#2080f0',
  '#18a058',
  '#f0a020',
  '#d03050',
  '#722ed1',
  '#13c2c2',
  '#eb2f96',
  '#fa8c16',
]

function getSourceTypeColor(index: number): string {
  return sourceTypeColors[index % sourceTypeColors.length]
}

function getDirectionCardStyle(direction: string): Record<string, string> {
  const color = getDirectionColor(direction)
  return {
    textAlign: 'center',
    background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
  }
}
</script>

<template>
  <n-layout style="min-height: 100vh">
    <n-layout-header bordered style="padding: 16px 24px">
      <n-space align="center" style="width: 100%">
        <n-h2 style="margin: 0">数据概览统计</n-h2>
      </n-space>
    </n-layout-header>

    <n-layout-content style="padding: 24px">
      <n-spin :show="isLoading" description="加载中...">
        <div v-if="statistics">
          <n-grid :cols="1" :x-gap="16" :y-gap="16">
            <n-gi>
              <n-card title="采样点总数" style="text-align: center">
                <n-statistic :value="statistics.total_points">
                  <template #suffix>
                    <span style="font-size: 16px; color: #999">个</span>
                  </template>
                </n-statistic>
              </n-card>
            </n-gi>

            <n-gi>
              <n-card title="各声源类型数量">
                <div v-if="sourceTypeEntries.length > 0">
                  <n-space vertical style="width: 100%">
                    <div
                      v-for="([type, count], index) in sourceTypeEntries"
                      :key="type"
                      style="margin-bottom: 8px"
                    >
                      <n-space justify="space-between" style="width: 100%; margin-bottom: 4px">
                        <span style="font-weight: 500">
                          <span
                            :style="{
                              display: 'inline-block',
                              width: '12px',
                              height: '12px',
                              borderRadius: '2px',
                              marginRight: '8px',
                              backgroundColor: getSourceTypeColor(index),
                            }"
                          ></span>
                          {{ type }}
                        </span>
                        <n-tag>{{ count }} 个</n-tag>
                      </n-space>
                      <div
                        style="
                          width: 100%;
                          height: 8px;
                          background: #f0f0f0;
                          border-radius: 4px;
                          overflow: hidden;
                        "
                      >
                        <div
                          :style="{
                            width: `${(count / maxSourceTypeCount) * 100}%`,
                            height: '100%',
                            backgroundColor: getSourceTypeColor(index),
                            transition: 'width 0.3s ease',
                          }"
                        ></div>
                      </div>
                    </div>
                  </n-space>
                </div>
                <n-empty v-else description="暂无数据" />
              </n-card>
            </n-gi>

            <n-gi>
              <n-card title="各方向数量">
                <div v-if="directionEntries.length > 0">
                  <n-grid :cols="4" :x-gap="12" :y-gap="12">
                    <n-gi
                      v-for="([direction, count]) in directionEntries"
                      :key="direction"
                    >
                      <n-card
                        :bordered="false"
                        :style="getDirectionCardStyle(direction)"
                      >
                        <div
                          :style="{
                            fontSize: '28px',
                            fontWeight: 'bold',
                            color: getDirectionColor(direction),
                            marginBottom: '4px',
                          }"
                        >
                          {{ count }}
                        </div>
                        <div style="color: #666; font-size: 14px">
                          {{ direction }}
                        </div>
                        <div
                          :style="{
                            width: '100%',
                            height: '4px',
                            background: '#f0f0f0',
                            borderRadius: '2px',
                            marginTop: '8px',
                            overflow: 'hidden',
                          }"
                        >
                          <div
                            :style="{
                              width: `${(count / maxDirectionCount) * 100}%`,
                              height: '100%',
                              backgroundColor: getDirectionColor(direction),
                              transition: 'width 0.3s ease',
                            }"
                          ></div>
                        </div>
                      </n-card>
                    </n-gi>
                  </n-grid>
                </div>
                <n-empty v-else description="暂无数据" />
              </n-card>
            </n-gi>
          </n-grid>
        </div>
        <n-empty v-else description="加载失败" />
      </n-spin>
    </n-layout-content>
  </n-layout>
</template>
