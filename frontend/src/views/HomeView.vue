<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useAsyncState } from '@vueuse/core'
import type { DataTableColumns } from 'naive-ui'
import { useMessage, useDialog } from 'naive-ui'
import {
  fetchSamplingPoints,
  createSamplingPoint,
  updateSamplingPoint,
  deleteSamplingPoint,
} from '../api'
import type { SamplingPoint, SamplingPointForm } from '../types'
import { emptyForm } from '../types'
import SamplingPointFormPanel from '../components/SamplingPointFormPanel.vue'

const message = useMessage()
const dialog = useDialog()

const showForm = ref(false)
const editingId = ref<number | null>(null)
const formModel = ref<SamplingPointForm>(emptyForm())

const isEditing = computed(() => editingId.value !== null)

const { state: points, isLoading, execute: reload } = useAsyncState(
  fetchSamplingPoints,
  [],
  { immediate: true, resetOnExecute: false }
)

const columns: DataTableColumns<SamplingPoint> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '地点', key: 'location', ellipsis: { tooltip: true } },
  { title: '声源类型', key: 'source_type', width: 100 },
  { title: '可听时间段', key: 'audible_time_period', ellipsis: { tooltip: true } },
  { title: '方向', key: 'direction', width: 80 },
  { title: '备注', key: 'notes', ellipsis: { tooltip: true } },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    render(row) {
      return [
        h(
          'a',
          {
            style: 'margin-right: 12px; cursor: pointer; color: #2080f0',
            onClick: () => openEdit(row),
          },
          '编辑'
        ),
        h(
          'a',
          {
            style: 'cursor: pointer; color: #d03050',
            onClick: () => confirmDelete(row),
          },
          '删除'
        ),
      ]
    },
  },
]

function openCreate() {
  editingId.value = null
  formModel.value = emptyForm()
  showForm.value = true
}

function openEdit(row: SamplingPoint) {
  editingId.value = row.id
  formModel.value = {
    location: row.location,
    source_type: row.source_type,
    audible_time_period: row.audible_time_period,
    direction: row.direction,
    notes: row.notes,
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
  formModel.value = emptyForm()
}

async function handleSubmit(payload: SamplingPointForm) {
  try {
    if (isEditing.value && editingId.value !== null) {
      await updateSamplingPoint(editingId.value, payload)
      message.success('更新成功')
    } else {
      await createSamplingPoint(payload)
      message.success('创建成功')
    }
    closeForm()
    await reload()
  } catch {
    message.error('操作失败，请检查表单或后端服务')
  }
}

function confirmDelete(row: SamplingPoint) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除「${row.location}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteSamplingPoint(row.id)
        message.success('已删除')
        await reload()
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <n-layout style="min-height: 100vh">
    <n-layout-header bordered style="padding: 16px 24px">
      <n-space align="center" justify="space-between" style="width: 100%">
        <n-h2 style="margin: 0">城市报时声采样点</n-h2>
        <n-button type="primary" @click="openCreate">新增采样点</n-button>
      </n-space>
    </n-layout-header>

    <n-layout-content style="padding: 24px">
      <n-card title="采样点列表">
        <n-data-table
          :columns="columns"
          :data="points"
          :loading="isLoading"
          :bordered="false"
          striped
        />
      </n-card>

      <n-drawer v-model:show="showForm" :width="420" placement="right">
        <n-drawer-content
          :title="isEditing ? '编辑采样点' : '新增采样点'"
          closable
        >
          <SamplingPointFormPanel
            :model="formModel"
            :loading="false"
            @submit="handleSubmit"
            @cancel="closeForm"
          />
        </n-drawer-content>
      </n-drawer>
    </n-layout-content>
  </n-layout>
</template>
