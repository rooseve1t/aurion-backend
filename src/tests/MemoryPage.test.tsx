import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { server } from './server'
import { MemoryPage } from '@/pages/Memory/MemoryPage'

describe('MemoryPage', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())

  it('загружает и отображает записи памяти', async () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    await waitFor(() => {
      const cards = screen.queryAllByTestId('memory-card')
      expect(cards.length).toBeGreaterThan(0)
    }, { timeout: 3000 })
    expect(screen.getByText('Тестовая запись в памяти')).toBeDefined()
  })

  it('показывает поле поиска', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByPlaceholderText('Семантический поиск...')).toBeDefined()
  })

  it('показывает кнопку добавления', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByText('ДОБАВИТЬ')).toBeDefined()
  })
})
