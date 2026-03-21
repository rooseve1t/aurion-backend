import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthPage } from '@/pages/Auth/AuthPage'

describe('AuthPage', () => {
  const renderAuth = () =>
    render(
      <MemoryRouter initialEntries={['/auth/login']}>
        <Routes>
          <Route path="/auth/login" element={<AuthPage />} />
          <Route path="/auth/register" element={<AuthPage />} />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    )

  it('показывает форму входа', () => {
    renderAuth()
    expect(screen.getByText('ВОЙТИ')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('user@aurionai.ru или ceo.martin')).toBeInTheDocument()
  })

  it('переключается на регистрацию', async () => {
    renderAuth()
    await userEvent.click(screen.getByText('СОЗДАТЬ АККАУНТ'))
    await waitFor(() => {
      expect(screen.getByText('ЗАРЕГИСТРИРОВАТЬСЯ')).toBeInTheDocument()
    })
  })

  it('заполняет и отправляет форму входа', async () => {
    renderAuth()
    await userEvent.type(screen.getByPlaceholderText('user@aurionai.ru или ceo.martin'), 'test@test.com')
    await userEvent.type(screen.getByPlaceholderText('••••••••'), 'password123')
    await userEvent.click(screen.getByText('ВОЙТИ'))
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
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
