<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useAsyncState } from '@vueuse/core'
import type { DataTableColumns } from 'naive-ui'
import { useMessage, useDialog } from 'naive-ui'
import {
  fetchSamplingRecords,
  createSamplingRecord,
  updateSamplingRecord,
  deleteSamplingRecord,
  fetchSamplingPoints,
} from '../api'
import type { SamplingRecord, SamplingRecordForm, SamplingPoint } from '../types'
import { emptyRecordForm } from '../types'
import SamplingRecordFormPanel from '../components/SamplingRecordFormPanel.vue'

const message = useMessage()
const dialog = useDialog()

const showForm = ref(false)
const formSubmitting = ref(false)
const editingId = ref<number | null>(null)
const formModel = ref<SamplingRecordForm>(emptyRecordForm())
const selectedPointId = ref<number | null>(null)

const isEditing = computed(() => editingId.value !== null)

const { state: samplingPoints } = useAsyncState(fetchSamplingPoints, [], {
  immediate: true,
  resetOnExecute: false,
})

const {
  state: records,
  isLoading,
  execute: reloadRecords,
} = useAsyncState(
  () => fetchSamplingRecords(selectedPointId.value ?? undefined),
  [],
  { immediate: true, resetOnExecute: false }
)

const pointMap = computed(() => {
  const m = new Map<number, string>()
  samplingPoints.value.forEach((p: SamplingPoint) => {
    m.set(p.id, p.location)
  })
  return m
})

const pointOptions = computed(() => [
  { label: '全部采样点', value: null },
  ...samplingPoints.value.map((p: SamplingPoint) => ({
    label: `${p.id} - ${p.location}`,
    value: p.id,
  })),
])

const columns: DataTableColumns<SamplingRecord> = [
  { title: 'ID', key: 'id', width: 60 },
  {
    title: '采样点',
    key: 'point_id',
    width: 140,
    ellipsis: { tooltip: true },
    render(row) {
      return pointMap.value.get(row.point_id) ?? `#${row.point_id}`
    },
  },
  { title: '采样日期', key: 'sampling_date', width: 100 },
  { title: '报时时间', key: 'actual_chime_time', width: 90 },
  { title: '噪声等级', key: 'noise_level', width: 90 },
  { title: '采样员', key: 'sampler_name', width: 80 },
  { title: '说明', key: 'description', ellipsis: { tooltip: true } },
  {
    title: '操作',
    key: 'actions',
    width: 130,
    fixed: 'right',
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

function handlePointChange(value: number | null) {
  selectedPointId.value = value
  reloadRecords()
}

function openCreate() {
  editingId.value = null
  formModel.value = {
    ...emptyRecordForm(),
    point_id: selectedPointId.value,
  }
  showForm.value = true
}

function openEdit(row: SamplingRecord) {
  editingId.value = row.id
  formModel.value = {
    point_id: row.point_id,
    sampling_date: row.sampling_date,
    actual_chime_time: row.actual_chime_time,
    noise_level: row.noise_level,
    sampler_name: row.sampler_name,
    description: row.description,
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
  formModel.value = emptyRecordForm()
  formSubmitting.value = false
}

async function handleSubmit(payload: SamplingRecordForm) {
  formSubmitting.value = true
  try {
    if (isEditing.value && editingId.value !== null) {
      await updateSamplingRecord(editingId.value, payload)
      message.success('更新成功')
    } else {
      await createSamplingRecord(payload)
      message.success('创建成功')
    }
    closeForm()
    await reloadRecords()
  } catch {
    message.error('操作失败，请检查表单或后端服务')
    formSubmitting.value = false
  }
}

function confirmDelete(row: SamplingRecord) {
  const location = pointMap.value.get(row.point_id) ?? `#${row.point_id}`
  dialog.warning({
    title: '确认删除',
    content: `确定删除「${location}」在 ${row.sampling_date} 的采样记录吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteSamplingRecord(row.id)
        message.success('已删除')
        await reloadRecords()
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
        <n-h2 style="margin: 0">现场采样记录</n-h2>
        <n-button type="primary" @click="openCreate">新增采样记录</n-button>
      </n-space>
    </n-layout-header>

    <n-layout-content style="padding: 24px">
      <n-card title="采样记录列表">
        <n-space style="margin-bottom: 16px" justify="space-between" wrap>
          <n-select
            :value="selectedPointId"
            :options="pointOptions"
            placeholder="选择采样点筛选"
            clearable
            @update:value="handlePointChange"
            style="width: 260px"
          />
          <n-text depth="3" style="font-size: 12px">
            表格内容过多时可横向滚动查看 →
          </n-text>
        </n-space>

        <n-data-table
          :columns="columns"
          :data="records"
          :loading="isLoading"
          :bordered="false"
          striped
          :scroll-x="880"
        />
      </n-card>

      <n-drawer v-model:show="showForm" :width="420" placement="right">
        <n-drawer-content
          :title="isEditing ? '编辑采样记录' : '新增采样记录'"
          closable
        >
          <SamplingRecordFormPanel
            :model="formModel"
            :loading="formSubmitting"
            :sampling-points="samplingPoints"
            @submit="handleSubmit"
            @cancel="closeForm"
          />
        </n-drawer-content>
      </n-drawer>
    </n-layout-content>
  </n-layout>
</template>
