import { create } from 'zustand'
import type { Tariff, Subscription, Payment } from '@/types'
import { paymentsService } from '@/services/payments'
import toast from 'react-hot-toast'

interface SubState {
  tariffs: Tariff[]
  current: (Subscription & { tariff?: Tariff; days_left?: number }) | null
  history: Payment[]
  loading: boolean
  fetchTariffs: () => Promise<void>
  fetchCurrent: () => Promise<void>
  fetchHistory: () => Promise<void>
  subscribe: (tariffId: number) => Promise<string>
  cancel: (subId: number) => Promise<void>
}

export const useSubscriptionStore = create<SubState>()((set) => ({
  tariffs: [],
  current: null,
  history: [],
  loading: false,

  fetchTariffs: async () => {
    const tariffs = await paymentsService.getTariffs()
    set({ tariffs })
  },

  fetchCurrent: async () => {
    try {
      const current = await paymentsService.getCurrentSubscription()
      set({ current })
    } catch {
      set({ current: null })
    }
  },

  fetchHistory: async () => {
    const { payments } = await paymentsService.getPayments()
    set({ history: payments })
  },

  subscribe: async (tariffId) => {
    const result = await paymentsService.subscribe(tariffId)
    toast.success('Перенаправляем на страницу оплаты...')
    return result.confirmation_url
  },

  cancel: async (subId) => {
    await paymentsService.cancel(subId)
    toast.success('Подписка отменена')
    const current = await paymentsService.getCurrentSubscription().catch(() => null)
    set({ current })
  },
}))
