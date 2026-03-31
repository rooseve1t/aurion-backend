import axios from 'axios'

const apiV2 = axios.create({
  baseURL: '/api/v2',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

apiV2.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`
  return config
})

export interface HealthMetrics {
  heartRate?: number
  steps?: number
  sleepHours?: number
  activityMinutes?: number
  source: string
  recordedAt: string
}

export interface HealthPattern {
  metric: string
  period: 'week' | 'month' | 'quarter'
  trend: 'up' | 'down' | 'stable'
  dataPoints: { date: string; value: number }[]
}

export interface HealthRecommendation {
  id: string
  title: string
  body: string
  priority: 'low' | 'medium' | 'high'
}

export async function getLiveMetrics(): Promise<HealthMetrics> {
  const { data } = await apiV2.get<HealthMetrics>('/health/metrics')
  return data
}

export async function getPatterns(period: 'week' | 'month' | 'quarter' = 'week'): Promise<HealthPattern[]> {
  const { data } = await apiV2.get<HealthPattern[]>('/health/patterns', { params: { period } })
  return data
}

export async function getRecommendations(): Promise<HealthRecommendation[]> {
  const { data } = await apiV2.get<HealthRecommendation[]>('/health/recommendations')
  return data
}

export async function postManualMetrics(metrics: Omit<HealthMetrics, 'source' | 'recordedAt'>): Promise<void> {
  await apiV2.post('/health/metrics', metrics)
}
