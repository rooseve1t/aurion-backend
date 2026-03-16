import { create } from 'zustand'
import type { SystemStats } from '@/types'
import { systemService } from '@/services/system'

interface SystemState {
  stats: SystemStats | null
  isLoading: boolean
  fetch: () => Promise<void>
}

const DEFAULT_STATS: SystemStats = {
  devices_online: 0,
  memory_entries: 0,
  active_tasks: 0,
  quantum_status: 'offline',
  subscription_tier: 'Free',
  uptime_hours: 0,
}

export const useSystemStore = create<SystemState>((set) => ({
  stats: null,
  isLoading: false,

  fetch: async () => {
    set({ isLoading: true })
    try {
      const stats = await systemService.getStats()
      set({ stats, isLoading: false })
    } catch {
      set({ stats: DEFAULT_STATS, isLoading: false })
    }
  },
}))
