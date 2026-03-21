import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { PaymentsPage } from '@/pages/Payments/PaymentsPage'

describe('Subscription UI', () => {
  it('рендерит страницу подписки', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    expect(screen.getByText('ПОДПИСКА И ПЛАТЕЖИ')).toBeInTheDocument()
    expect(await screen.findAllByTestId('tariff-card')).toHaveLength(3)
  })

  it('показывает активный баннер и автопродление', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    expect(await screen.findByTestId('subscription-banner')).toBeInTheDocument()
    expect(screen.getByText('АВТОПРОДЛЕНИЕ')).toBeInTheDocument()
  })

  it('переключается на вкладку ИСТОРИЯ', async () => {
    render(<MemoryRouter><PaymentsPage /></MemoryRouter>)
    await userEvent.click(screen.getByText('ИСТОРИЯ'))
    expect(await screen.findByText('Нет истории платежей')).toBeInTheDocument()
  })
})
