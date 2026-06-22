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
