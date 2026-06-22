import axios from 'axios'
import type { SamplingPoint, SamplingPointForm } from './types'

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
