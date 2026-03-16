import { api } from './api'
import type { MemoryEntry } from '@/types'

export const memoryService = {
  async search(query: string, limit = 20): Promise<MemoryEntry[]> {
    const { data } = await api.get<MemoryEntry[]>('/memory/search', {
      params: { query, limit },
    })
    return data
  },

  async create(content: string, importance = 5, tags: string[] = []): Promise<MemoryEntry> {
    const { data } = await api.post<MemoryEntry>('/memory/', { content, importance, tags })
    return data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/memory/${id}`)
  },

  async count(): Promise<number> {
    const { data } = await api.get<{ count: number }>('/memory/count')
    return data.count
  },
}
