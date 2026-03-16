import { api } from './api'
import type { SystemStats } from '@/types'

export const systemService = {
  async getStats(): Promise<SystemStats> {
    const { data } = await api.get<SystemStats>('/system/stats')
    return data
  },
}
