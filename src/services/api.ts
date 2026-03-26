import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const AUTH_UPDATED_EVENT = 'aurion-auth-updated'
const AUTH_CLEARED_EVENT = 'aurion-auth-cleared'

function normalizeApiBase(rawBase?: string): string {
  const trimmed = rawBase?.trim().replace(/\/+$/, '')
  if (!trimmed) return '/api/v1'
  if (trimmed.endsWith('/api/v1')) return trimmed
  if (trimmed.endsWith('/api')) return `${trimmed}/v1`
  return `${trimmed}/api/v1`
}

const BASE_URL = normalizeApiBase(import.meta.env.VITE_API_URL)
const FALLBACK_BASE_URL = '/api/v1'

function clearAuthTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(AUTH_CLEARED_EVENT))
  }
}

function notifyAuthTokensUpdated(accessToken: string, refreshToken: string) {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(AUTH_UPDATED_EVENT, {
      detail: { accessToken, refreshToken },
    }))
  }
}

function isHardAuthFailure(error: AxiosError): boolean {
  const status = error.response?.status ?? 0
  if (![400, 401].includes(status)) return false

  const detail = String(
    (error.response?.data as { detail?: unknown } | undefined)?.detail ?? ''
  ).toLowerCase()

  return (
    detail.includes('invalid refresh') ||
    detail.includes('refresh token') ||
    detail.includes('expired') ||
    detail.includes('signature')
  )
}

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: вставляем JWT ───────────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: обновляем токен при 401 ────────────────────────────
let isRefreshing = false
let queue: Array<{
  original: InternalAxiosRequestConfig & { _retry?: boolean; _fallbackUsed?: boolean }
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
}> = []

function shouldSkipRefresh(url?: string): boolean {
  return Boolean(
    url && (
      url.includes('/auth/token') ||
      url.includes('/auth/register') ||
      url.includes('/auth/2fa/verify')
    )
  )
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean; _fallbackUsed?: boolean }
    const refresh = localStorage.getItem('refresh_token')

    // Network fallback to same-origin proxy (/api/v1) when primary base is unreachable.
    if (
      !error.response &&
      original &&
      BASE_URL !== FALLBACK_BASE_URL &&
      !original._fallbackUsed &&
      typeof original.url === 'string' &&
      original.url.startsWith('/')
    ) {
      original._fallbackUsed = true
      original.baseURL = FALLBACK_BASE_URL
      return api(original)
    }

    if (
      error.response?.status !== 401 ||
      original._retry ||
      shouldSkipRefresh(original?.url) ||
      !refresh
    ) {
      return Promise.reject(error)
    }
    original._retry = true

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push({ original, resolve, reject })
      })
    }

    isRefreshing = true
    try {
      let data: { access_token: string; refresh_token: string }
      try {
        const response = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh })
        data = response.data
      } catch (refreshError) {
        if (
          axios.isAxiosError(refreshError) &&
          !refreshError.response &&
          BASE_URL !== FALLBACK_BASE_URL
        ) {
          const fallbackResponse = await axios.post(`${FALLBACK_BASE_URL}/auth/refresh`, { refresh_token: refresh })
          data = fallbackResponse.data
          original.baseURL = FALLBACK_BASE_URL
        } else {
          throw refreshError
        }
      }
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      notifyAuthTokensUpdated(data.access_token, data.refresh_token)
      queue.forEach((item) => {
        item.original.headers = item.original.headers ?? {}
        item.original.headers.Authorization = `Bearer ${data.access_token}`
        item.resolve(api(item.original))
      })
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${data.access_token}`
      return api(original)
    } catch (refreshError) {
      queue.forEach((item) => item.reject(refreshError))
      if (axios.isAxiosError(refreshError) && isHardAuthFailure(refreshError)) {
        clearAuthTokens()
      }
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
      queue = []
    }
  }
)

export { AUTH_CLEARED_EVENT, AUTH_UPDATED_EVENT }
