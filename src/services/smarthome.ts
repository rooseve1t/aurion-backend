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

  async control(deviceId: number, command: string, params: Record<string, unknown> = {}): Promise<void> {
    await api.post('/smarthome/control', { device_id: deviceId, command, params })
  },

  async optimize(): Promise<{ savings_kwh: number; actions: string[] }> {
    const { data } = await api.post('/smarthome/optimize')
    return data
  },

  async deleteDevice(id: number): Promise<void> {
    await api.delete(`/smarthome/devices/${id}`)
  },
}
