<script setup lang="ts">
import { ref } from 'vue'
import { useAsyncState } from '@vueuse/core'
import type { DataTableColumns } from 'naive-ui'
import { useMessage, useDialog } from 'naive-ui'
import { fetchSourceTypes, createSourceType, deleteSourceType } from '../api'
import type { SourceType } from '../types'

const message = useMessage()
const dialog = useDialog()

const newTypeName = ref('')
const adding = ref(false)

const { state: types, isLoading, execute: reload } = useAsyncState(
  fetchSourceTypes,
  [],
  { immediate: true, resetOnExecute: false }
)

const columns: DataTableColumns<SourceType> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '声源类型名称', key: 'name' },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render(row) {
      return (
        <a
          style="cursor: pointer; color: #d03050"
          onClick={() => confirmDelete(row)}
        >
          删除
        </a>
      )
    },
  },
]

async function handleAdd() {
  const name = newTypeName.value.trim()
  if (!name) {
    message.warning('请输入声源类型名称')
    return
  }
  adding.value = true
  try {
    await createSourceType({ name })
    message.success('添加成功')
    newTypeName.value = ''
    await reload()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    message.error(detail || '添加失败')
  } finally {
    adding.value = false
  }
}

function confirmDelete(row: SourceType) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除「${row.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteSourceType(row.id)
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
      <n-h2 style="margin: 0">声源类型字典管理</n-h2>
    </n-layout-header>

    <n-layout-content style="padding: 24px">
      <n-card title="类型列表">
        <template #header-extra>
          <n-space align="center">
            <n-input
              v-model:value="newTypeName"
              placeholder="输入新类型名称"
              style="width: 200px"
              @keyup.enter="handleAdd"
            />
            <n-button type="primary" :loading="adding" @click="handleAdd">
              添加
            </n-button>
          </n-space>
        </template>

        <n-data-table
          :columns="columns"
          :data="types"
          :loading="isLoading"
          :bordered="false"
          striped
        />
      </n-card>
    </n-layout-content>
  </n-layout>
</template>
