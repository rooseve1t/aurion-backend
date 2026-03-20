import { useEffect, useState } from 'react'
import { Shield } from 'lucide-react'
import { guardianService } from '@/services/guardian'
import { useToast } from '@/hooks/useToast'
import styles from './GuardianPage.module.css'

export function GuardianPage() {
  const toast = useToast()
  const [hosts, setHosts] = useState('192.168.1.1, 192.168.1.100')
  const [loading, setLoading] = useState(false)
  const [scan, setScan] = useState<Awaited<ReturnType<typeof guardianService.scan>> | null>(null)
  const [audit, setAudit] = useState<Awaited<ReturnType<typeof guardianService.routerAudit>> | null>(null)

  useEffect(() => {
    guardianService.routerAudit().then(setAudit).catch(() => undefined)
  }, [])

  const runScan = async () => {
    setLoading(true)
    try {
      const parsed = hosts
        .split(',')
        .map((v) => v.trim())
        .filter(Boolean)
      const data = await guardianService.scan(parsed)
      setScan(data)
      toast.success('Сканирование завершено')
    } catch {
      toast.error('Не удалось выполнить скан')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Shield size={20} color="var(--cyan)" />
        <span className={styles.title}>GUARDIAN — БЕЗОПАСНОСТЬ</span>
      </div>
      <div className={styles.info}>
        <p>Проверка локальной сети, базовый аудит роутера и рекомендации по усилению защиты.</p>
        <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
          <label className="label">HOSTS (через запятую)</label>
          <input className="input" value={hosts} onChange={(e) => setHosts(e.target.value)} />
          <button className="btn btn-cyan" onClick={runScan} disabled={loading}>
            {loading ? 'СКАНИРУЕМ...' : 'ЗАПУСТИТЬ СКАН'}
          </button>
        </div>

        {audit && (
          <div style={{ marginTop: 14, display: 'grid', gap: 6 }}>
            {audit.checks.map((check) => (
              <div key={check.item}>
                <strong>{check.item}:</strong> {check.message}
              </div>
            ))}
          </div>
        )}

        {scan && (
          <div style={{ marginTop: 14, display: 'grid', gap: 8 }}>
            {scan.report.map((row) => (
              <div key={row.host}>
                <strong>{row.host}</strong> • score {row.score} • ports: {row.open_ports.join(', ') || 'none'}
              </div>
            ))}
            {scan.recommendations.map((tip) => (
              <div key={tip}>{tip}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
