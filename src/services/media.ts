import { api } from './api'
import type { MediaItem } from '@/types'

interface MediaCreatePayload {
  title: string
  media_type: MediaItem['media_type']
  mood: MediaItem['mood']
  duration_minutes: number
  description: string
}

export const mediaService = {
  async list(): Promise<MediaItem[]> {
    const { data } = await api.get<MediaItem[]>('/media/items')
    return data
  },

  async create(payload: MediaCreatePayload): Promise<MediaItem> {
    const { data } = await api.post<MediaItem>('/media/items', payload)
    return data
  },

  async updateStatus(id: number, status: MediaItem['status']): Promise<MediaItem> {
    const { data } = await api.patch<MediaItem>(`/media/items/${id}`, { status })
    return data
  },
}
