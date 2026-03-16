import { describe, it, expect, vi, beforeAll, afterEach, afterAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { server } from './server'
import { HomePage } from '@/pages/Home/HomePage'

describe('HomePage / DeviceCard', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())

  it('отображает список устройств', async () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryAllByTestId('device-card').length).toBeGreaterThan(0)
    }, { timeout: 3000 })
    expect(screen.getByText('Лампа')).toBeDefined()
  })

  it('показывает кнопку управления', async () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.queryByText('ВЫКЛ') || screen.queryByText('ВКЛ')).toBeDefined()
    }, { timeout: 3000 })
  })

  it('показывает заголовок страницы', () => {
    render(<MemoryRouter><HomePage /></MemoryRouter>)
    expect(screen.getByText('УМНЫЙ ДОМ')).toBeDefined()
  })
})
