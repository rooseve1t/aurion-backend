import { useEffect, useState } from 'react'
import { Activity, HeartPulse, Link2 } from 'lucide-react'
import { healthService } from '@/services/health'
import { useToast } from '@/hooks/useToast'
import { formatDate } from '@/utils'
import type { HealthData } from '@/types'
import styles from './Workspace.module.css'

export function HealthPage() {
  const [data, setData] = useState<HealthData | null>(null)
  const [loading, setLoading] = useState(false)
  const [connecting, setConnecting] = useState<string | null>(null)
  const toast = useToast()

  const load = async () => {
    setLoading(true)
    try {
      setData(await healthService.getData())
    } catch {
      toast.error('Не удалось загрузить health-профиль')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const connect = async (provider: 'google' | 'fitbit') => {
    setConnecting(provider)
    try {
      if (provider === 'google') {
        await healthService.connectGoogle()
      } else {
        await healthService.connectFitbit()
      }
      await load()
      toast.success(`Профиль ${provider === 'google' ? 'Google Fit' : 'Fitbit'} синхронизирован`)
    } catch {
      toast.error('Не удалось синхронизировать подключение')
    } finally {
      setConnecting(null)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleBlock}>
          <HeartPulse size={20} color="var(--cyan)" />
          <div>
            <div className={styles.title}>HEALTH HUB</div>
            <div className={styles.subtitle}>Пульс привычек, восстановление и интеграции здоровья</div>
          </div>
        </div>
        <div className={styles.actions}>
          <button className="btn btn-ghost" onClick={() => connect('google')} disabled={connecting !== null}>
            <Link2 size={14} />
            {connecting === 'google' ? 'СИНХРОН...' : 'GOOGLE FIT'}
          </button>
          <button className="btn btn-cyan" onClick={() => connect('fitbit')} disabled={connecting !== null}>
            <Activity size={14} />
            {connecting === 'fitbit' ? 'СИНХРОН...' : 'FITBIT'}
          </button>
        </div>
      </div>

      <div className={styles.grid}>
        <MetricCard label="Шаги" value={String(data?.summary.steps ?? 0)} />
        <MetricCard label="Сон" value={`${data?.summary.sleep_hours ?? 0} ч`} />
        <MetricCard label="Recovery" value={`${data?.summary.recovery ?? 0}%`} />
        <MetricCard label="Вода" value={`${data?.summary.hydration_liters ?? 0} л`} />
      </div>

      <div className={styles.grid}>
        <section className={styles.card}>
          <div className={styles.sectionTitle}>Подключения</div>
          <div className={styles.list}>
            {data?.connections.map((connection) => (
              <div key={connection.id} className={styles.item}>
                <div className={styles.itemRow}>
                  <div className={styles.itemTitle}>{connection.provider}</div>
                  <div className={styles.badge}>{connection.status}</div>
                </div>
                <div className={styles.itemMeta}>
                  Последняя синхронизация: {connection.last_sync_at ? formatDate(connection.last_sync_at) : 'ещё не было'}
                </div>
                <div className={styles.badgeRow}>
                  <span className={styles.badge}>{connection.metrics.steps} steps</span>
                  <span className={styles.badge}>{connection.metrics.sleep_hours} h sleep</span>
                  <span className={styles.badge}>{connection.metrics.recovery}% recovery</span>
                </div>
              </div>
            ))}
            {!loading && !data?.connections.length && <div className={styles.empty}>Пока нет подключений</div>}
          </div>
        </section>

        <section className={styles.card}>
          <div className={styles.sectionTitle}>Динамика 7 дней</div>
          <div className={styles.timeline}>
            {data?.timeline.map((row) => (
              <div key={row.date} className={styles.timelineRow}>
                <span className={styles.itemMeta}>{row.date}</span>
                <div className={styles.bar}>
                  <div className={styles.barFill} style={{ width: `${Math.min(100, row.steps / 130)}%` }} />
                </div>
                <span className={styles.itemMeta}>{row.steps} шагов</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Инсайты Aurion</div>
        <div className={styles.list}>
          {data?.insights.map((item) => (
            <div key={item} className={styles.itemMeta}>{item}</div>
          ))}
          {!loading && !data && <div className={styles.empty}>Данные появятся после первой синхронизации</div>}
        </div>
      </section>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.card}>
      <div className={styles.sectionTitle}>{label}</div>
      <div className={styles.metricValue}>{value}</div>
      <div className={styles.metricLabel}>Обновляется в живом профиле здоровья</div>
    </div>
  )
}
