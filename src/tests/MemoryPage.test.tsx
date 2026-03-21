import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { MemoryPage } from '@/pages/Memory/MemoryPage'

describe('MemoryPage', () => {
  it('загружает и отображает записи памяти', async () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    await waitFor(() => {
      const cards = screen.queryAllByTestId('memory-card')
      expect(cards.length).toBeGreaterThan(0)
    }, { timeout: 3000 })
    expect(screen.getByText('Тестовая запись в памяти')).toBeInTheDocument()
  })

  it('показывает поле поиска', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByPlaceholderText('Семантический поиск...')).toBeInTheDocument()
  })

  it('показывает кнопку добавления', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByText('ДОБАВИТЬ')).toBeInTheDocument()
  })
})
