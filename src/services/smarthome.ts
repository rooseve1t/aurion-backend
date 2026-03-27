import { api } from './api'
import type { Device } from '@/types'

export const smarthomeService = {
  async listDevices(): Promise<Device[]> {
    const { data } = await api.get<Device[]>('/smarthome/devices')
    return data
  },

  async addDevice(payload: {
    name: string; device_type: string; room: string; protocol: string
  }): Promise<Device> {
    const { data } = await api.post<Device>('/smarthome/devices', payload)
    return data
  },

  async control(deviceId: string | number, command: string, params: Record<string, unknown> = {}): Promise<void> {
    await api.post(`/smarthome/devices/${deviceId}/control`, {
      command,
      parameters: params,
    })
  },

  async optimize(): Promise<{ savings_kwh: number; actions: string[] }> {
    const { data } = await api.post('/smarthome/energy/optimize', {})
    return {
      savings_kwh: Number(data?.estimated_savings ?? 0),
      actions: Array.isArray(data?.optimization_plan?.commands)
        ? data.optimization_plan.commands.map((item: { command?: string; device_id?: string }) =>
          `${item.command || 'update'}:${item.device_id || 'unknown'}`
        )
        : [],
    }
  },

  async deleteDevice(id: string | number): Promise<void> {
    await api.delete(`/smarthome/devices/${id}`)
  },
}
