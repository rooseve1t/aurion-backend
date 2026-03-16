import { create } from 'zustand'
import type { Device } from '@/types'
import { smarthomeService } from '@/services/smarthome'
import toast from 'react-hot-toast'

interface DevicesState {
  devices: Device[]
  loading: boolean
  fetch: () => Promise<void>
  control: (id: number, cmd: Record<string, unknown>) => Promise<void>
  optimize: () => Promise<void>
}

export const useDevicesStore = create<DevicesState>()((set, get) => ({
  devices: [],
  loading: false,

  fetch: async () => {
    set({ loading: true })
    try {
      const devices = await smarthomeService.getDevices()
      set({ devices })
    } finally {
      set({ loading: false })
    }
  },

  control: async (id, cmd) => {
    await smarthomeService.control(id, cmd)
    await get().fetch()
    toast.success('Команда отправлена')
  },

  optimize: async () => {
    const result = await smarthomeService.optimize()
    toast.success('Оптимизация завершена')
    return result
  },
}))
