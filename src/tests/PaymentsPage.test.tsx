import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { PaymentsPage } from '@/pages/Payments/PaymentsPage'

describe('PaymentsPage', () => {
  it('загружает тарифы', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    const cards = await screen.findAllByTestId('tariff-card')
    expect(cards.length).toBe(3)
    expect(screen.getByText('FREE')).toBeInTheDocument()
    expect(screen.getByText('BASIC')).toBeInTheDocument()
    expect(screen.getByText('PRO')).toBeInTheDocument()
  })

  it('переключает на историю платежей', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    const histBtn = screen.getByText('ИСТОРИЯ')
    await userEvent.click(histBtn)
    await waitFor(() => {
      expect(screen.getByText('Нет истории платежей')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('показывает активную подписку', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByTestId('subscription-banner')).toBeInTheDocument()
    }, { timeout: 3000 })
  })
})
