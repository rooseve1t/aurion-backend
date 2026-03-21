import { api } from './api'
import type { Reminder } from '@/types'

interface ReminderPayload {
  title: string
  note: string
  due_at?: string | null
  priority: Reminder['priority']
}

export const remindersService = {
  async list(): Promise<Reminder[]> {
    const { data } = await api.get<Reminder[]>('/reminders')
    return data
  },

  async create(payload: ReminderPayload): Promise<Reminder> {
    const { data } = await api.post<Reminder>('/reminders', payload)
    return data
  },

  async update(id: number, payload: Partial<ReminderPayload> & { status?: Reminder['status'] }): Promise<Reminder> {
    const { data } = await api.patch<Reminder>(`/reminders/${id}`, payload)
    return data
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/reminders/${id}`)
  },
}
