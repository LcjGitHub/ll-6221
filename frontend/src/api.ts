import axios from 'axios'
import type {
  ImportResult,
  SamplingPoint,
  SamplingPointForm,
  SamplingRecord,
  SamplingRecordForm,
  SourceType,
  SourceTypeForm,
  Statistics,
} from './types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/** 获取全部采样点 */
export async function fetchSamplingPoints(): Promise<SamplingPoint[]> {
  const { data } = await api.get<SamplingPoint[]>('/sampling-points')
  return data
}

/** 创建采样点 */
export async function createSamplingPoint(
  payload: SamplingPointForm
): Promise<SamplingPoint> {
  const { data } = await api.post<SamplingPoint>('/sampling-points', payload)
  return data
}

/** 更新采样点 */
export async function updateSamplingPoint(
  id: number,
  payload: SamplingPointForm
): Promise<SamplingPoint> {
  const { data } = await api.put<SamplingPoint>(`/sampling-points/${id}`, payload)
  return data
}

/** 删除采样点 */
export async function deleteSamplingPoint(id: number): Promise<void> {
  await api.delete(`/sampling-points/${id}`)
}

/** 获取采样记录列表，可按采样点筛选 */
export async function fetchSamplingRecords(
  pointId?: number
): Promise<SamplingRecord[]> {
  const params = pointId != null ? { point_id: pointId } : {}
  const { data } = await api.get<SamplingRecord[]>('/sampling-records', { params })
  return data
}

/** 获取单条采样记录 */
export async function fetchSamplingRecord(id: number): Promise<SamplingRecord> {
  const { data } = await api.get<SamplingRecord>(`/sampling-records/${id}`)
  return data
}

/** 创建采样记录 */
export async function createSamplingRecord(
  payload: SamplingRecordForm
): Promise<SamplingRecord> {
  const body = {
    ...payload,
    point_id: payload.point_id ?? 0,
    sampling_date: payload.sampling_date ?? '',
    actual_chime_time: payload.actual_chime_time ?? '',
  }
  const { data } = await api.post<SamplingRecord>('/sampling-records', body)
  return data
}

/** 更新采样记录 */
export async function updateSamplingRecord(
  id: number,
  payload: SamplingRecordForm
): Promise<SamplingRecord> {
  const body = {
    ...payload,
    point_id: payload.point_id ?? 0,
    sampling_date: payload.sampling_date ?? '',
    actual_chime_time: payload.actual_chime_time ?? '',
  }
  const { data } = await api.put<SamplingRecord>(`/sampling-records/${id}`, body)
  return data
}

/** 删除采样记录 */
export async function deleteSamplingRecord(id: number): Promise<void> {
  await api.delete(`/sampling-records/${id}`)
}

/** 获取统计汇总数据 */
export async function fetchStatistics(): Promise<Statistics> {
  const { data } = await api.get<Statistics>('/statistics')
  return data
}

/** 导出采样点 CSV 文件 */
export async function exportSamplingPoints(): Promise<void> {
  const response = await api.get('/sampling-points/export', {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = 'sampling_points.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/** 导入采样点 CSV 文件 */
export async function importSamplingPoints(file: File): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<ImportResult>('/sampling-points/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

/** 获取全部声源类型 */
export async function fetchSourceTypes(): Promise<SourceType[]> {
  const { data } = await api.get<SourceType[]>('/source-types')
  return data
}

/** 新增声源类型 */
export async function createSourceType(
  payload: SourceTypeForm
): Promise<SourceType> {
  const { data } = await api.post<SourceType>('/source-types', payload)
  return data
}

/** 删除声源类型 */
export async function deleteSourceType(id: number): Promise<void> {
  await api.delete(`/source-types/${id}`)
}
