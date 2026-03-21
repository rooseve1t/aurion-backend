import { api } from './api'
import type { SocialPost } from '@/types'

export const socialService = {
  async list(): Promise<SocialPost[]> {
    const { data } = await api.get<SocialPost[]>('/social/feed')
    return data
  },

  async create(content: string, mood: SocialPost['mood']): Promise<SocialPost> {
    const { data } = await api.post<SocialPost>('/social/feed', { content, mood })
    return data
  },
}
