import { create } from 'zustand'
import type { Tariff, Subscription, Payment } from '@/types'
import { paymentsService } from '@/services/payments'
import { useUIStore } from './uiStore'

interface CurrentSubscription extends Subscription {
  tariff?: Tariff
  days_left?: number
}

interface SubState {
  tariffs: Tariff[]
  current: CurrentSubscription | null
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
    const tariffs = await paymentsService.listTariffs()
    set({ tariffs })
  },

  fetchCurrent: async () => {
    try {
      const current = await paymentsService.currentSubscription()
      set({ current })
    } catch {
      set({ current: null })
    }
  },

  fetchHistory: async () => {
    const { payments } = await paymentsService.listPayments()
    set({ history: payments })
  },

  subscribe: async (tariffId) => {
    const result = await paymentsService.subscribe(tariffId)
    useUIStore.getState().showToast('Подписка активирована', 'success')
    return result.confirmation_url
  },

  cancel: async (subId) => {
    await paymentsService.cancelSubscription(subId)
    useUIStore.getState().showToast('Подписка отменена', 'success')
    const current = await paymentsService.currentSubscription().catch(() => null)
    set({ current })
  },
}))
