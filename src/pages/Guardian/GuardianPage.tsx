import { Shield } from 'lucide-react'
import { Link } from 'react-router-dom'
import styles from './GuardianPage.module.css'

export function GuardianPage() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Shield size={20} color="var(--cyan)" />
        <span className={styles.title}>GUARDIAN — БЕЗОПАСНОСТЬ</span>
      </div>
      <div className={styles.info}>
        <p>Управление безопасностью: <Link to="/profile" className={styles.link}>Профиль → 2FA</Link>.</p>
        <p style={{ marginTop: 8 }}>Аудит-лог, управление сессиями — в разработке.</p>
        <span className={styles.wip}>В РАЗРАБОТКЕ</span>
      </div>
    </div>
  )
}
