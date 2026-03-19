import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

function normalizeApiBase(rawBase?: string): string {
  const trimmed = rawBase?.trim().replace(/\/+$/, '')
  if (!trimmed) return '/api/v1'
  if (trimmed.endsWith('/api/v1')) return trimmed
  if (trimmed.endsWith('/api')) return `${trimmed}/v1`
  return `${trimmed}/api/v1`
}

const BASE_URL = normalizeApiBase(import.meta.env.VITE_API_URL)

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
let queue: Array<(token: string) => void> = []

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
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const refresh = localStorage.getItem('refresh_token')

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
      return new Promise((resolve) => {
        queue.push((token) => {
          original.headers = original.headers ?? {}
          original.headers.Authorization = `Bearer ${token}`
          resolve(api(original))
        })
      })
    }

    isRefreshing = true
    try {
      const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
        refresh_token: refresh,
      })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      queue.forEach((cb) => cb(data.access_token))
      queue = []
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${data.access_token}`
      return api(original)
    } catch {
      localStorage.clear()
      window.location.href = '/auth/login'
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  }
)
