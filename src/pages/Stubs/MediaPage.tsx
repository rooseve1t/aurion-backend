import { Wrench } from 'lucide-react'
import styles from './Stub.module.css'

export function MediaPage() {
  return (
    <div className={styles.page}>
      <Wrench size={48} color="var(--border)" />
      <div className={styles.title}>Media</div>
      <div className={styles.text}>Этот модуль находится в разработке.</div>
      <span className={styles.badge}>СКОРО</span>
    </div>
  )
}
