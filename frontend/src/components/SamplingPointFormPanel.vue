<script setup lang="ts">
import { reactive, watch, ref } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import type { SamplingPointForm } from '../types'

const props = defineProps<{
  model: SamplingPointForm
  loading: boolean
}>()

const emit = defineEmits<{
  submit: [payload: SamplingPointForm]
  cancel: []
}>()

const formRef = ref<FormInst | null>(null)
const form = reactive<SamplingPointForm>({ ...props.model })

watch(
  () => props.model,
  (value) => {
    Object.assign(form, value)
  },
  { deep: true }
)

const rules: FormRules = {
  location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
  source_type: [{ required: true, message: '请输入声源类型', trigger: 'blur' }],
  audible_time_period: [
    { required: true, message: '请输入可听时间段', trigger: 'blur' },
  ],
  direction: [{ required: true, message: '请输入方向', trigger: 'blur' }],
}

const sourceTypeOptions = [
  { label: '古钟', value: '古钟' },
  { label: '电子钟', value: '电子钟' },
  { label: '鼓声', value: '鼓声' },
  { label: '其他', value: '其他' },
]

const directionOptions = [
  { label: '东', value: '东' },
  { label: '南', value: '南' },
  { label: '西', value: '西' },
  { label: '北', value: '北' },
  { label: '东南', value: '东南' },
  { label: '西南', value: '西南' },
  { label: '东北', value: '东北' },
  { label: '西北', value: '西北' },
]

async function handleSubmit() {
  await formRef.value?.validate()
  emit('submit', { ...form })
}
</script>

<template>
  <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
    <n-form-item label="地点" path="location">
      <n-input v-model:value="form.location" placeholder="如：北京钟楼" />
    </n-form-item>

    <n-form-item label="声源类型" path="source_type">
      <n-select
        v-model:value="form.source_type"
        :options="sourceTypeOptions"
        placeholder="选择声源类型"
        filterable
        tag
      />
    </n-form-item>

    <n-form-item label="可听时间段" path="audible_time_period">
      <n-input
        v-model:value="form.audible_time_period"
        placeholder="如：06:00-07:00, 12:00-13:00"
      />
    </n-form-item>

    <n-form-item label="方向" path="direction">
      <n-select
        v-model:value="form.direction"
        :options="directionOptions"
        placeholder="选择方向"
        filterable
        tag
      />
    </n-form-item>

    <n-form-item label="备注" path="notes">
      <n-input
        v-model:value="form.notes"
        type="textarea"
        placeholder="可选备注"
        :autosize="{ minRows: 3, maxRows: 6 }"
      />
    </n-form-item>

    <n-space>
      <n-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </n-button>
      <n-button @click="emit('cancel')">取消</n-button>
    </n-space>
  </n-form>
</template>
