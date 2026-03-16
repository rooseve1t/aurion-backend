import { X } from 'lucide-react'
import { useUIStore, type Toast } from '@/store/uiStore'
import styles from './Toast.module.css'

const iconColor: Record<Toast['type'], string> = {
  success: 'var(--green)',
  error:   'var(--red)',
  warning: 'var(--amber)',
  info:    'var(--cyan)',
}

export function ToastContainer() {
  const { toasts, dismissToast } = useUIStore()
  return (
    <div className={styles.container}>
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`${styles.toast} animate-slide-right`}
          style={{ borderLeftColor: iconColor[t.type] }}
        >
          <span className={styles.msg}>{t.message}</span>
          <button className={styles.close} onClick={() => dismissToast(t.id)}>
            <X size={12} />
          </button>
        </div>
      ))}
    </div>
  )
}
