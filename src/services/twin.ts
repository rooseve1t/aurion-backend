import { api } from './api'
import type { TwinPrediction, TwinProfile } from '@/types'

export const twinService = {
  async getProfile(): Promise<TwinProfile> {
    const { data } = await api.get<TwinProfile>('/twin/profile')
    return data
  },

  async getPredictions(): Promise<TwinPrediction[]> {
    const { data } = await api.get<TwinPrediction[]>('/twin/predictions')
    return data
  },
}
