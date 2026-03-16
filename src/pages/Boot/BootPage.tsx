import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import styles from './BootPage.module.css'

const STEPS = [
  'ИНИЦИАЛИЗАЦИЯ ЯДРА...',
  'ЗАГРУЗКА НЕЙРОСЕТЕЙ...',
  'СИНХРОНИЗАЦИЯ ПАМЯТИ...',
  'ПРОВЕРКА БЕЗОПАСНОСТИ...',
  'АКТИВАЦИЯ АГЕНТОВ...',
  'СИСТЕМА ГОТОВА.',
]

export function BootPage() {
  const [step, setStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => {
        const next = s + 1
        setProgress(Math.round((next / STEPS.length) * 100))
        if (next >= STEPS.length) {
          clearInterval(interval)
          setTimeout(() => {
            const token = localStorage.getItem('access_token')
            navigate(token ? '/dashboard' : '/auth/login')
          }, 800)
        }
        return next
      })
    }, 400)
    return () => clearInterval(interval)
  }, [navigate])

  return (
    <div className={styles.page}>
      <div className={styles.scan} />
      <div className={styles.center}>
        <CoreOrb size={120} active={step < STEPS.length} />
        <div className={styles.title}>AURION OS</div>
        <div className={styles.version}>ВЕРСИЯ 1.0.0 — SECURE BOOT</div>
        <div className={styles.log}>
          {STEPS.slice(0, step + 1).map((s, i) => (
            <div
              key={i}
              className={`${styles.logLine} ${i === step ? styles.current : styles.done}`}
            >
              <span className={styles.prompt}>&gt;</span> {s}
            </div>
          ))}
        </div>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        <div className={styles.progressText}>{progress}%</div>
      </div>
    </div>
  )
}
