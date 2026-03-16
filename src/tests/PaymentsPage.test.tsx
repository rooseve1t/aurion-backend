import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { server } from './server'
import { PaymentsPage } from '@/pages/Payments/PaymentsPage'

describe('PaymentsPage', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())

  it('загружает тарифы', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryAllByTestId('tariff-card').length).toBe(3)
    }, { timeout: 3000 })
    expect(screen.getByText('FREE')).toBeDefined()
    expect(screen.getByText('BASIC')).toBeDefined()
    expect(screen.getByText('PRO')).toBeDefined()
  })

  it('переключает на историю платежей', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    const histBtn = screen.getByText('ИСТОРИЯ')
    await userEvent.click(histBtn)
    await waitFor(() => {
      expect(screen.getByText('Нет истории платежей')).toBeDefined()
    }, { timeout: 3000 })
  })

  it('показывает активную подписку', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryByTestId('subscription-banner')).toBeDefined()
    }, { timeout: 3000 })
  })
})
