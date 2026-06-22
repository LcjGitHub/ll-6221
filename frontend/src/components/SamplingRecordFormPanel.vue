<script setup lang="ts">
import { reactive, watch, ref, computed } from 'vue'
import type { FormInst, FormRules, SelectOption } from 'naive-ui'
import type { SamplingRecordForm } from '../types'
import type { SamplingPoint } from '../types'

const props = defineProps<{
  model: SamplingRecordForm
  loading: boolean
  samplingPoints: SamplingPoint[]
}>()

const emit = defineEmits<{
  submit: [payload: SamplingRecordForm]
  cancel: []
}>()

const formRef = ref<FormInst | null>(null)
const form = reactive<SamplingRecordForm>({ ...props.model })

watch(
  () => props.model,
  (value) => {
    Object.assign(form, value)
  },
  { deep: true }
)

const pointOptions = computed<SelectOption[]>(() =>
  props.samplingPoints.map((p) => ({
    label: `${p.id} - ${p.location}`,
    value: p.id,
  }))
)

const noiseLevelOptions: SelectOption[] = [
  { label: '安静（<40dB）', value: '安静' },
  { label: '较安静（40-50dB）', value: '较安静' },
  { label: '一般（50-60dB）', value: '一般' },
  { label: '较吵（60-70dB）', value: '较吵' },
  { label: '嘈杂（>70dB）', value: '嘈杂' },
]

const rules: FormRules = {
  point_id: [
    {
      required: true,
      type: 'number',
      message: '请选择关联采样点',
      trigger: 'change',
    },
  ],
  sampling_date: [{ required: true, message: '请选择采样日期', trigger: 'blur' }],
  actual_chime_time: [
    { required: true, message: '请输入实际听到报时的时间', trigger: 'blur' },
  ],
  noise_level: [{ required: true, message: '请选择环境噪声等级', trigger: 'change' }],
  sampler_name: [{ required: true, message: '请输入采样员姓名', trigger: 'blur' }],
}

async function handleSubmit() {
  await formRef.value?.validate()
  emit('submit', { ...form })
}
</script>

<template>
  <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
    <n-form-item label="关联采样点" path="point_id">
      <n-select
        v-model:value="form.point_id"
        :options="pointOptions"
        placeholder="选择采样点"
        filterable
        :loading="samplingPoints.length === 0"
      />
    </n-form-item>

    <n-form-item label="采样日期" path="sampling_date">
      <n-date-picker
        v-model:value="form.sampling_date"
        type="date"
        placeholder="选择日期"
        value-format="yyyy-MM-dd"
        style="width: 100%"
      />
    </n-form-item>

    <n-form-item label="实际听到报时的时间" path="actual_chime_time">
      <n-time-picker
        v-model:value="form.actual_chime_time"
        placeholder="选择时间"
        format="HH:mm"
        value-format="HH:mm"
        style="width: 100%"
      />
    </n-form-item>

    <n-form-item label="环境噪声等级" path="noise_level">
      <n-select
        v-model:value="form.noise_level"
        :options="noiseLevelOptions"
        placeholder="选择噪声等级"
        filterable
      />
    </n-form-item>

    <n-form-item label="采样员姓名" path="sampler_name">
      <n-input v-model:value="form.sampler_name" placeholder="请输入采样员姓名" />
    </n-form-item>

    <n-form-item label="说明文字" path="description">
      <n-input
        v-model:value="form.description"
        type="textarea"
        placeholder="可填写说明或备注信息"
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
