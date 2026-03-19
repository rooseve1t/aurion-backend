import { create } from 'zustand'

export type ToastType = 'info' | 'success' | 'error' | 'warning'

export interface Toast {
  id: string
  type: ToastType
  message: string
}

interface UIState {
  activeModule: string
  sidebarOpen: boolean
  toasts: Toast[]
  setActiveModule: (m: string) => void
  setSidebarOpen: (value: boolean) => void
  toggleSidebar: () => void
  showToast: (message: string, type?: ToastType) => void
  dismissToast: (id: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  activeModule: 'dashboard',
  sidebarOpen: false,
  toasts: [],

  setActiveModule: (m) => set({ activeModule: m }),
  setSidebarOpen: (value) => set({ sidebarOpen: value }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  showToast: (message, type = 'info') => {
    const id = crypto.randomUUID()
    set((s) => ({ toasts: [...s.toasts, { id, type, message }] }))
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, 4000)
  },

  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

export const useUiStore = useUIStore
