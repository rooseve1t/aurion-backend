import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from './mocks/testUtils'
import PaymentsPage from '@/pages/Payments'

const mockCurrent = {
  id: 1, tariff_id: 2, status: 'active' as const,
  start_date: new Date().toISOString(),
  end_date: new Date(Date.now() + 20 * 86400000).toISOString(),
  auto_renew: true, cancelled_at: null,
  created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
  tariff: {
    id: 2, name: 'Basic', price: 990, duration_days: 30, is_active: true,
    features: { voice: true, memory_limit: 1000, devices_limit: 20, osint: false, quantum: false, finance: true, agents: false, evolution: false },
  },
  days_left: 20,
}

vi.mock('@/store/subscriptionStore', () => ({
  useSubscriptionStore: () => ({
    tariffs: [
      { id: 1, name: 'Free',  price: 0,    duration_days: 30, is_active: true, features: { voice: true, memory_limit: 100, devices_limit: 5, osint: false, quantum: false, finance: false, agents: false, evolution: false } },
      { id: 2, name: 'Basic', price: 990,  duration_days: 30, is_active: true, features: { voice: true, memory_limit: 1000, devices_limit: 20, osint: false, quantum: false, finance: true, agents: false, evolution: false } },
      { id: 3, name: 'Pro',   price: 2990, duration_days: 30, is_active: true, features: { voice: true, memory_limit: -1, devices_limit: -1, osint: true, quantum: true, finance: true, agents: true, evolution: false } },
    ],
    current: mockCurrent,
    history: [],
    fetchTariffs:  vi.fn(),
    fetchCurrent:  vi.fn(),
    fetchHistory:  vi.fn(),
    subscribe:     vi.fn().mockResolvedValue('https://yookassa.ru/checkout/test'),
    cancel:        vi.fn(),
  }),
}))

describe('PaymentsPage', () => {
  it('рендерит страницу подписок', () => {
    render(<PaymentsPage />)
    expect(screen.getByText('ПОДПИСКА И ПЛАТЕЖИ')).toBeInTheDocument()
  })

  it('отображает все три тарифные карточки', () => {
    render(<PaymentsPage />)
    const cards = screen.getAllByTestId('subscription-card')
    expect(cards.length).toBe(3)
  })

  it('показывает Free, Basic, Pro', () => {
    render(<PaymentsPage />)
    expect(screen.getByText('FREE')).toBeInTheDocument()
    expect(screen.getByText('BASIC')).toBeInTheDocument()
    expect(screen.getByText('PRO')).toBeInTheDocument()
  })

  it('активный тариф имеет метку АКТИВЕН', () => {
    render(<PaymentsPage />)
    expect(screen.getByText('АКТИВЕН')).toBeInTheDocument()
  })

  it('переключение на вкладку История', () => {
    render(<PaymentsPage />)
    fireEvent.click(screen.getByText('История'))
    expect(screen.getByText('История платежей пуста')).toBeInTheDocument()
  })
})
