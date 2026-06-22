<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useAsyncState } from '@vueuse/core'
import type { DataTableColumns, UploadFileInfo } from 'naive-ui'
import { useMessage, useDialog } from 'naive-ui'
import {
  fetchSamplingPoints,
  createSamplingPoint,
  updateSamplingPoint,
  deleteSamplingPoint,
  exportSamplingPoints,
  importSamplingPoints,
} from '../api'
import type { SamplingPoint, SamplingPointForm, ImportResult } from '../types'
import { emptyForm } from '../types'
import SamplingPointFormPanel from '../components/SamplingPointFormPanel.vue'

const message = useMessage()
const dialog = useDialog()

const showForm = ref(false)
const editingId = ref<number | null>(null)
const formModel = ref<SamplingPointForm>(emptyForm())

const showImportModal = ref(false)
const importLoading = ref(false)
const importFile = ref<UploadFileInfo | null>(null)
const importResult = ref<ImportResult | null>(null)

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

async function handleExport() {
  try {
    await exportSamplingPoints()
    message.success('导出成功')
  } catch {
    message.error('导出失败，请稍后重试')
  }
}

function openImportModal() {
  importFile.value = null
  importResult.value = null
  showImportModal.value = true
}

function closeImportModal() {
  showImportModal.value = false
}

function handleFileChange(options: { file: UploadFileInfo; fileList: UploadFileInfo[] }) {
  importFile.value = options.file
  importResult.value = null
}

async function handleImport() {
  if (!importFile.value?.file) {
    message.warning('请先选择要导入的 CSV 文件')
    return
  }
  importLoading.value = true
  try {
    const result = await importSamplingPoints(importFile.value.file)
    importResult.value = result
    if (result.success_count > 0) {
      await reload()
    }
    if (result.failed_count === 0) {
      message.success(`导入完成：成功 ${result.success_count} 条，跳过 ${result.skip_count} 条`)
    } else {
      message.warning(`导入完成：成功 ${result.success_count} 条，跳过 ${result.skip_count} 条，失败 ${result.failed_count} 条`)
    }
  } catch (err: any) {
    message.error(err?.response?.data?.detail || '导入失败，请检查文件格式')
  } finally {
    importLoading.value = false
  }
}
</script>

<template>
  <n-layout style="min-height: 100vh">
    <n-layout-header bordered style="padding: 16px 24px">
      <n-space align="center" justify="space-between" style="width: 100%">
        <n-h2 style="margin: 0">城市报时声采样点</n-h2>
        <n-space>
          <n-button @click="handleExport">导出</n-button>
          <n-button @click="openImportModal">导入</n-button>
          <n-button type="primary" @click="openCreate">新增采样点</n-button>
        </n-space>
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

      <n-modal v-model:show="showImportModal" preset="dialog" title="导入采样点" :mask-closable="false" :close-on-esc="true">
        <n-space vertical :size="16" style="margin-top: 12px">
          <n-upload
            :show-file-list="true"
            :max="1"
            accept=".csv"
            :custom-request="() => {}"
            @change="handleFileChange"
          >
            <n-button>选择 CSV 文件</n-button>
            <template #tip>
              <n-text depth="3">仅支持 CSV 格式，需包含列：地点、声源类型、可听时间段、方向、备注</n-text>
            </template>
          </n-upload>

          <div v-if="importResult" style="padding: 12px; background: #f5f7fa; border-radius: 6px">
            <n-text strong>导入结果：</n-text>
            <n-space vertical :size="6" style="margin-top: 8px">
              <n-text>总计：{{ importResult.total_count }} 条</n-text>
              <n-text type="success">成功：{{ importResult.success_count }} 条</n-text>
              <n-text type="warning">跳过（地点重复）：{{ importResult.skip_count }} 条</n-text>
              <n-text type="error">失败：{{ importResult.failed_count }} 条</n-text>
              <div v-if="importResult.errors.length > 0" style="margin-top: 8px">
                <n-text type="error" style="font-size: 13px">错误详情：</n-text>
                <ul style="margin: 6px 0 0 18px; padding: 0">
                  <li v-for="(err, idx) in importResult.errors" :key="idx" style="font-size: 12px; color: #d03050">
                    {{ err }}
                  </li>
                </ul>
              </div>
            </n-space>
          </div>
        </n-space>

        <template #action>
          <n-space justify="end">
            <n-button @click="closeImportModal">关闭</n-button>
            <n-button type="primary" :loading="importLoading" @click="handleImport">开始导入</n-button>
          </n-space>
        </template>
      </n-modal>
    </n-layout-content>
  </n-layout>
</template>
