/** 报时声采样点类型定义 */

export interface SamplingPoint {
  id: number
  location: string
  source_type: string
  audible_time_period: string
  direction: string
  notes: string
}

export interface SamplingPointForm {
  location: string
  source_type: string
  audible_time_period: string
  direction: string
  notes: string
}

/** 空表单默认值 */
export function emptyForm(): SamplingPointForm {
  return {
    location: '',
    source_type: '',
    audible_time_period: '',
    direction: '',
    notes: '',
  }
}

/** 现场采样记录类型定义 */
export interface SamplingRecord {
  id: number
  point_id: number
  sampling_date: string
  actual_chime_time: string
  noise_level: string
  sampler_name: string
  description: string
}

export interface SamplingRecordForm {
  point_id: number | null
  sampling_date: string
  actual_chime_time: string
  noise_level: string
  sampler_name: string
  description: string
}

/** 空采样记录表单默认值 */
export function emptyRecordForm(): SamplingRecordForm {
  return {
    point_id: null,
    sampling_date: '',
    actual_chime_time: '',
    noise_level: '',
    sampler_name: '',
    description: '',
  }
}
