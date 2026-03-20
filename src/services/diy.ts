import { api } from './api'

export const diyService = {
  async instructions() {
    const { data } = await api.get('/diy/instructions')
    return data as {
      quickstart: string[]
      mqtt_host: string
      example_topics: string[]
      sample_payload: Record<string, unknown>
    }
  },

  async listSketches() {
    const { data } = await api.get('/diy/sketches')
    return data as Array<{ id: number; name: string; device_type: string; board: string; protocol: string; created_at: string }>
  },

  async uploadSketch(payload: { name: string; device_type: string; board: string; sketch_code: string; protocol: string }) {
    const { data } = await api.post('/diy/sketches', payload)
    return data as { id: number; status: string }
  },
}
