import axios from 'axios'
import type {
  SamplingPoint,
  SamplingPointForm,
  SamplingRecord,
  SamplingRecordForm,
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
