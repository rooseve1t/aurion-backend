import { api } from './api'
import type { Tariff, Subscription, Payment } from '@/types'

export const paymentsService = {
  async listTariffs(): Promise<Tariff[]> {
    const { data } = await api.get<Tariff[]>('/payments/tariffs')
    return data
  },

  async subscribe(tariffId: string | number, saveMethod = true): Promise<{
    subscription_id: string; payment_id: string; confirmation_url: string
    tariff_name: string; amount: number
  }> {
    const { data } = await api.post('/payments/subscribe', {
      tariff_id: String(tariffId), save_payment_method: saveMethod,
    })
    return data
  },

  async listSubscriptions(): Promise<Subscription[]> {
    const { data } = await api.get<Subscription[]>('/payments/subscriptions')
    return data
  },

  async currentSubscription(): Promise<Subscription & { tariff?: Tariff; days_left?: number }> {
    const { data } = await api.get('/payments/subscriptions/current')
    return data
  },

  async cancelSubscription(id: string | number): Promise<Subscription> {
    const { data } = await api.post<{ subscription: Subscription }>(`/payments/subscriptions/${id}/cancel`)
    return data.subscription
  },

  async listPayments(): Promise<{ payments: Payment[]; total: number }> {
    const { data } = await api.get('/payments/payments')
    return data
  },
}
