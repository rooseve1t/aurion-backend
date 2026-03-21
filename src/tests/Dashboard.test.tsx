import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// Mock WebSocket
vi.stubGlobal('WebSocket', class {
  onopen: (() => void) | null = null
  onclose: (() => void) | null = null
  onmessage: (() => void) | null = null
  onerror: (() => void) | null = null
  readyState = 1
  send = vi.fn()
  close = vi.fn()
  constructor() { setTimeout(() => this.onopen?.(), 0) }
})

describe('DashboardPage', () => {
  it('отображает заголовок чата', async () => {
    const { DashboardPage } = await import('@/pages/Dashboard/DashboardPage')
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    expect(screen.getByText('ЧАТ С AURION')).toBeInTheDocument()
  })

  it('показывает поле ввода', async () => {
    const { DashboardPage } = await import('@/pages/Dashboard/DashboardPage')
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    expect(screen.getByPlaceholderText('Введите сообщение...')).toBeInTheDocument()
  })
})
