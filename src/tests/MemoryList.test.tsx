import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { MemoryPage } from '@/pages/Memory/MemoryPage'

describe('MemoryPage', () => {
  it('отображает заголовок ВЕКТОРНАЯ ПАМЯТЬ', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByText('ВЕКТОРНАЯ ПАМЯТЬ')).toBeInTheDocument()
  })

  it('показывает список записей после загрузки', async () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getAllByTestId('memory-card').length).toBeGreaterThan(0)
    }, { timeout: 3000 })
  })

  it('отображает записи из мок-данных', async () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByText(/Тестовая запись в памяти/)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('кнопка добавления записи', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByText('ДОБАВИТЬ')).toBeInTheDocument()
  })

  it('поле поиска присутствует', () => {
    render(<MemoryRouter><MemoryPage /></MemoryRouter>)
    expect(screen.getByPlaceholderText('Семантический поиск...')).toBeInTheDocument()
  })
})
