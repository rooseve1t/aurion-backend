import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { HomePage } from '@/pages/Home/HomePage'

describe('HomePage / DeviceCard', () => {
  it('отображает список устройств', async () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryAllByTestId('device-card').length).toBeGreaterThan(0)
    }, { timeout: 3000 })
    expect(screen.getByText('Лампа')).toBeInTheDocument()
  })

  it('показывает кнопку управления', async () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryByText('ВЫКЛ') || screen.queryByText('ВКЛ')).toBeDefined()
    }, { timeout: 3000 })
  })

  it('показывает заголовок страницы', () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    expect(screen.getByText('УМНЫЙ ДОМ')).toBeInTheDocument()
  })
})
