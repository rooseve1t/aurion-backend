import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from './mocks/testUtils'
import MemoryPage from '@/pages/Memory'

describe('MemoryPage', () => {
  it('рендерит страницу памяти', () => {
    render(<MemoryPage />)
    expect(screen.getByTestId('memory-page')).toBeInTheDocument()
  })

  it('отображает заголовок ВЕКТОРНАЯ ПАМЯТЬ', () => {
    render(<MemoryPage />)
    expect(screen.getByText('ВЕКТОРНАЯ ПАМЯТЬ')).toBeInTheDocument()
  })

  it('показывает список записей после загрузки', async () => {
    render(<MemoryPage />)
    await waitFor(() => {
      expect(screen.getByTestId('memory-list')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('отображает записи из мок-данных', async () => {
    render(<MemoryPage />)
    await waitFor(() => {
      expect(screen.getByText(/Встреча в пятницу/)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('кнопка добавления записи', () => {
    render(<MemoryPage />)
    expect(screen.getByText('Добавить')).toBeInTheDocument()
  })

  it('поле поиска присутствует', () => {
    render(<MemoryPage />)
    expect(screen.getByPlaceholderText('Поиск по памяти...')).toBeInTheDocument()
  })
})
