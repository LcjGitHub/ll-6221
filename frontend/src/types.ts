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
  sampling_date: string | null
  actual_chime_time: string | null
  noise_level: string
  sampler_name: string
  description: string
}

/** 空采样记录表单默认值 */
export function emptyRecordForm(): SamplingRecordForm {
  return {
    point_id: null,
    sampling_date: null,
    actual_chime_time: null,
    noise_level: '',
    sampler_name: '',
    description: '',
  }
}

/** 统计汇总数据类型 */
export interface Statistics {
  total_points: number
  source_type_counts: Record<string, number>
  direction_counts: Record<string, number>
}

/** 采样点导入结果 */
export interface ImportResult {
  total_count: number
  success_count: number
  skip_count: number
  failed_count: number
  errors: string[]
}

/** 声源类型字典 */
export interface SourceType {
  id: number
  name: string
}

export interface SourceTypeForm {
  name: string
}
