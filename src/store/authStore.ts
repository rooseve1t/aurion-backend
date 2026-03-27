import { create } from 'zustand'
import type { User } from '@/types'
import { authService } from '@/services/auth'
import { AUTH_CLEARED_EVENT, AUTH_UPDATED_EVENT } from '@/services/api'

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
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent(AUTH_UPDATED_EVENT, {
        detail: { accessToken: access, refreshToken: refresh },
      }))
    }
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
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, accessToken: null, refreshToken: null, needs2FA: false, pending2FAToken: null })
    }
  },

  fetchMe: async () => {
    try {
      const user = await authService.getMe()
      set({ user })
    } catch (e: unknown) {
      const isNetworkError = !(e as { response?: unknown })?.response
      if (isNetworkError) {
        // Сетевая ошибка — не сбрасываем сессию, просто логируем
        console.warn('[AuthStore] Network error in fetchMe, keeping session')
        return
      }
      // 401 или другая HTTP ошибка — сбрасываем только если нет токена
      const accessToken = localStorage.getItem('access_token')
      if (!accessToken) {
        set({
          user: null,
          accessToken: null,
          refreshToken: localStorage.getItem('refresh_token'),
          needs2FA: false,
          pending2FAToken: null,
        })
      }
    }
  },
}))

if (typeof window !== 'undefined') {
  window.addEventListener(AUTH_CLEARED_EVENT, () => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      needs2FA: false,
      pending2FAToken: null,
      isLoading: false,
      error: null,
    })
  })

  window.addEventListener(AUTH_UPDATED_EVENT, ((event: Event) => {
    const detail = (event as CustomEvent<{ accessToken?: string; refreshToken?: string }>).detail
    if (!detail) return
    useAuthStore.setState((state) => ({
      ...state,
      accessToken: detail.accessToken ?? state.accessToken,
      refreshToken: detail.refreshToken ?? state.refreshToken,
    }))
  }) as EventListener)
}
