import { api } from './api'
import type { User, TokenPair } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<TokenPair> {
    const form = new URLSearchParams({ username: email, password })
    const { data } = await api.post<TokenPair>('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },

  async register(email: string, username: string, password: string): Promise<User> {
    const { data } = await api.post<User>('/auth/register', { email, username, password })
    return data
  },

  async verify2fa(code: string): Promise<TokenPair> {
    const { data } = await api.post<TokenPair>('/auth/2fa/verify', { code })
    return data
  },

  async setup2fa(): Promise<{ qr_code: string; secret: string; otpauth_url: string }> {
    const { data } = await api.post('/auth/2fa/enable')
    return data
  },

  async confirmEnable2fa(code: string): Promise<void> {
    await api.post('/auth/2fa/verify-enable', { code })
  },

  async disable2fa(code: string): Promise<void> {
    await api.post('/auth/2fa/disable', { code })
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>('/auth/me')
    return data
  },

  async logout(refreshToken: string): Promise<void> {
    await api.post('/auth/logout', { refresh_token: refreshToken })
  },
}
