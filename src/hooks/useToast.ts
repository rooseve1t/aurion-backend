import { useUIStore } from '@/store/uiStore'

export const useToast = () => {
  const showToast = useUIStore((s) => s.showToast)
  return {
    success: (msg: string) => showToast(msg, 'success'),
    error: (msg: string) => showToast(msg, 'error'),
    info: (msg: string) => showToast(msg, 'info'),
    warning: (msg: string) => showToast(msg, 'warning'),
  }
}
