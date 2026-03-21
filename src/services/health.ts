import { api } from './api'
import type { HealthConnection, HealthData } from '@/types'

export const healthService = {
  async getData(): Promise<HealthData> {
    const { data } = await api.get<HealthData>('/health/data')
    return data
  },

  async connectGoogle(): Promise<HealthConnection> {
    const { data } = await api.post<HealthConnection>('/health/connect/google')
    return data
  },

  async connectFitbit(): Promise<HealthConnection> {
    const { data } = await api.post<HealthConnection>('/health/connect/fitbit')
    return data
  },
}
