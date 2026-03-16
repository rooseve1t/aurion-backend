import { api } from './api'
import type { BankAccount, Transaction, FinanceAnalytics } from '@/types'

export const financeService = {
  async listAccounts(): Promise<BankAccount[]> {
    const { data } = await api.get<BankAccount[]>('/finance/accounts')
    return data
  },

  async listTransactions(accountId: number, limit = 50): Promise<Transaction[]> {
    const { data } = await api.get<Transaction[]>(`/finance/accounts/${accountId}/transactions`, {
      params: { limit },
    })
    return data
  },

  async getAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<FinanceAnalytics> {
    const { data } = await api.get('/finance/analytics', { params: { period } })
    return data
  },

  async getTips(): Promise<string[]> {
    const { data } = await api.get<string[]>('/finance/tips')
    return data
  },
}
