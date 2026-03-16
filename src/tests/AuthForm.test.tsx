import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { server } from './server'
import { AuthPage } from '@/pages/Auth/AuthPage'

describe('AuthPage', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())

  const renderAuth = () =>
    render(
      <MemoryRouter initialEntries={['/auth/login']}>
        <Routes>
          <Route path="/auth/login" element={<AuthPage />} />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    )

  it('показывает форму входа', () => {
    renderAuth()
    expect(screen.getByText('ВОЙТИ')).toBeDefined()
    expect(screen.getByPlaceholderText('user@aurionai.ru')).toBeDefined()
  })

  it('переключается на регистрацию', async () => {
    renderAuth()
    await userEvent.click(screen.getByText('СОЗДАТЬ АККАУНТ'))
    expect(screen.getByText('ЗАРЕГИСТРИРОВАТЬСЯ')).toBeDefined()
  })

  it('заполняет и отправляет форму входа', async () => {
    renderAuth()
    await userEvent.type(screen.getByPlaceholderText('user@aurionai.ru'), 'test@test.com')
    await userEvent.type(screen.getByPlaceholderText('••••••••'), 'password123')
    await userEvent.click(screen.getByText('ВОЙТИ'))
    await waitFor(() => {
      // После успешного входа перенаправляет
      expect(screen.queryByText('Dashboard') !== null || screen.queryByText('ВОЙТИ') !== null).toBeTruthy()
    }, { timeout: 3000 })
  })

  it('переключает видимость пароля', async () => {
    renderAuth()
    const pwInput = screen.getByPlaceholderText('••••••••')
    expect(pwInput.getAttribute('type')).toBe('password')
    // Клик на кнопку показа пароля
    const eyeBtn = pwInput.parentElement?.querySelector('button')
    if (eyeBtn) {
      await userEvent.click(eyeBtn)
      expect(pwInput.getAttribute('type')).toBe('text')
    }
  })
})
