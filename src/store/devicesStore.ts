import { create } from 'zustand'
import type { Device } from '@/types'
import { smarthomeService } from '@/services/smarthome'
import { useUIStore } from './uiStore'

interface DevicesState {
  devices: Device[]
  loading: boolean
  fetch: () => Promise<void>
  control: (id: number, command: string, params?: Record<string, unknown>) => Promise<void>
  optimize: () => Promise<{ savings_kwh: number; actions: string[] }>
}

export const useDevicesStore = create<DevicesState>()((set, get) => ({
  devices: [],
  loading: false,

  fetch: async () => {
    set({ loading: true })
    try {
      const devices = await smarthomeService.listDevices()
      set({ devices })
    } finally {
      set({ loading: false })
    }
  },

  control: async (id, command, params = {}) => {
    await smarthomeService.control(id, command, params)
    await get().fetch()
    useUIStore.getState().showToast('Команда отправлена', 'success')
  },

  optimize: async () => {
    const result = await smarthomeService.optimize()
    useUIStore.getState().showToast('Оптимизация завершена', 'success')
    return result
  },
}))
