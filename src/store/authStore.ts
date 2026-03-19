import { create } from 'zustand'
import type { User } from '@/types'
import { authService } from '@/services/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  needs2FA: boolean
  pending2FAToken: string | null
  isLoading: boolean
  error: string | null
  setTokens: (access: string, refresh: string) => void
  setUser: (u: User) => void
  setNeeds2FA: (v: boolean) => void
  login: (email: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  needs2FA: false,
  pending2FAToken: null,
  isLoading: false,
  error: null,

  setTokens: (access, refresh) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    set({ accessToken: access, refreshToken: refresh })
  },

  setUser: (u) => set({ user: u }),
  setNeeds2FA: (v) => set({ needs2FA: v, pending2FAToken: v ? get().pending2FAToken : null }),
  clearError: () => set({ error: null }),

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const tokens = await authService.login(email, password)
      get().setTokens(tokens.access_token, tokens.refresh_token)
      const user = await authService.getMe()
      set({ user, isLoading: false, needs2FA: false, pending2FAToken: null })
      return true
    } catch (e: unknown) {
      const responseData = (e as {
        response?: {
          data?: {
            detail?: string
            requires_2fa?: boolean
            otp_token?: string
          }
        }
      })?.response?.data
      const msg = responseData?.detail || 'Ошибка входа'
      if (responseData?.requires_2fa && responseData.otp_token) {
        set({
          isLoading: false,
          needs2FA: true,
          pending2FAToken: responseData.otp_token,
          error: null,
        })
        return false
      }
      set({ isLoading: false, error: msg })
      return false
    }
  },

  logout: async () => {
    const refresh = get().refreshToken
    try {
      if (refresh) await authService.logout(refresh)
    } finally {
      localStorage.clear()
      set({ user: null, accessToken: null, refreshToken: null, needs2FA: false, pending2FAToken: null })
    }
  },

  fetchMe: async () => {
    try {
      const user = await authService.getMe()
      set({ user })
    } catch {
      // token expired - handled by interceptor
    }
  },
}))
