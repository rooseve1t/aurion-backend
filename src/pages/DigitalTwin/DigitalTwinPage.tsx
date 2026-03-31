import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  getLiveMetrics,
  getPatterns,
  getRecommendations,
  postManualMetrics,
  type HealthMetrics,
  type HealthPattern,
  type HealthRecommendation,
} from '@/services/healthService'

const PERIOD_LABELS = { week: 'Неделя', month: 'Месяц', quarter: 'Квартал' } as const
type Period = keyof typeof PERIOD_LABELS

const TREND_ICON = { up: '↑', down: '↓', stable: '→' }
const TREND_COLOR = { up: '#00ff88', down: '#ff4444', stable: '#00d4ff' }

const METRIC_LABELS: Record<string, string> = {
  heartRate: 'Пульс',
  steps: 'Шаги',
  sleepHours: 'Сон (ч)',
  activityMinutes: 'Активность (мин)',
}

const SparkLine: React.FC<{ points: { date: string; value: number }[] }> = ({ points }) => {
  if (points.length < 2) return null
  const vals = points.map((p) => p.value)
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const range = max - min || 1
  const w = 120
  const h = 32
  const coords = points.map((p, i) => {
    const x = (i / (points.length - 1)) * w
    const y = h - ((p.value - min) / range) * h
    return `${x},${y}`
  })
  return (
    <svg width={w} height={h} style={{ display: 'block' }}>
      <polyline
        points={coords.join(' ')}
        fill="none"
        stroke="#00d4ff"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        opacity={0.8}
      />
    </svg>
  )
}

const ManualForm: React.FC<{ onSaved: () => void }> = ({ onSaved }) => {
  const [form, setForm] = useState({ heartRate: '', steps: '', sleepHours: '', activityMinutes: '' })
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await postManualMetrics({
        heartRate: form.heartRate ? Number(form.heartRate) : undefined,
        steps: form.steps ? Number(form.steps) : undefined,
        sleepHours: form.sleepHours ? Number(form.sleepHours) : undefined,
        activityMinutes: form.activityMinutes ? Number(form.activityMinutes) : undefined,
      })
      onSaved()
    } catch { /* ignore */ } finally {
      setSaving(false)
    }
  }

  const inputStyle: React.CSSProperties = {
    background: 'rgba(0,212,255,0.05)',
    border: '1px solid rgba(0,212,255,0.2)',
    borderRadius: 4,
    color: '#e0f4ff',
    padding: '6px 10px',
    fontSize: 13,
    width: '100%',
    outline: 'none',
    fontFamily: 'var(--font-ui)',
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 12 }}>
      {(['heartRate', 'steps', 'sleepHours', 'activityMinutes'] as const).map((key) => (
        <div key={key}>
          <label style={{ fontSize: 11, color: 'rgba(224,244,255,0.4)', fontFamily: 'var(--font-hud)', display: 'block', marginBottom: 4 }}>
            {METRIC_LABELS[key]}
          </label>
          <input
            type="number"
            min={0}
            value={form[key]}
            onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
            style={inputStyle}
            placeholder="—"
          />
        </div>
      ))}
      <div style={{ gridColumn: '1 / -1' }}>
        <button
          type="submit"
          disabled={saving}
          className="neon-btn"
          style={{ borderColor: '#00d4ff', color: '#00d4ff', width: '100%' }}
        >
          {saving ? 'Сохранение...' : 'Сохранить'}
        </button>
      </div>
    </form>
  )
}

export const DigitalTwinPage: React.FC = () => {
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null)
  const [patterns, setPatterns] = useState<HealthPattern[]>([])
  const [recommendations, setRecommendations] = useState<HealthRecommendation[]>([])
  const [period, setPeriod] = useState<Period>('week')
  const [showManual, setShowManual] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    setLoading(true)
    try {
      const [m, p, r] = await Promise.allSettled([
        getLiveMetrics(),
        getPatterns(period),
        getRecommendations(),
      ])
      if (m.status === 'fulfilled') setMetrics(m.value)
      else setShowManual(true)
      if (p.status === 'fulfilled') setPatterns(p.value)
      if (r.status === 'fulfilled') setRecommendations(r.value)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [period])

  const card = (children: React.ReactNode, key?: string) => (
    <div key={key} style={{
      background: 'rgba(13,13,24,0.85)',
      border: '1px solid rgba(0,212,255,0.15)',
      borderRadius: 8,
      padding: '16px',
      backdropFilter: 'blur(12px)',
    }}>
      {children}
    </div>
  )

  const sectionTitle = (text: string) => (
    <div style={{
      fontSize: 11,
      fontFamily: 'var(--font-hud)',
      letterSpacing: '0.12em',
      textTransform: 'uppercase' as const,
      color: '#00d4ff',
      textShadow: '0 0 6px rgba(0,212,255,0.6)',
      marginBottom: 12,
    }}>
      {text}
    </div>
  )

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a0f',
      color: '#e0f4ff',
      fontFamily: 'var(--font-ui)',
      padding: '24px 16px',
      maxWidth: 720,
      margin: '0 auto',
    }}>
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        style={{ marginBottom: 24 }}
      >
        <h1 style={{
          margin: 0,
          fontSize: 20,
          fontFamily: 'var(--font-hud)',
          color: '#00d4ff',
          textShadow: '0 0 8px rgba(0,212,255,0.6)',
          letterSpacing: '0.05em',
        }}>
          DIGITAL TWIN
        </h1>
        <p style={{ margin: '4px 0 0', color: 'rgba(224,244,255,0.4)', fontSize: 12, fontFamily: 'var(--font-hud)' }}>
          Цифровой двойник здоровья
        </p>
      </motion.div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'rgba(224,244,255,0.3)', fontFamily: 'var(--font-hud)', fontSize: 12 }}>
          ЗАГРУЗКА...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {card(
            <>
              {sectionTitle('Уровень 1 — Живые показатели')}
              {metrics ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                  {(['heartRate', 'steps', 'sleepHours', 'activityMinutes'] as const).map((key) => (
                    metrics[key] !== undefined && (
                      <div key={key} style={{ background: 'rgba(0,212,255,0.05)', borderRadius: 6, padding: '10px 12px' }}>
                        <div style={{ fontSize: 11, color: 'rgba(224,244,255,0.4)', fontFamily: 'var(--font-hud)', marginBottom: 4 }}>
                          {METRIC_LABELS[key]}
                        </div>
                        <div style={{ fontSize: 22, fontWeight: 600, color: '#00d4ff' }}>
                          {metrics[key]}
                        </div>
                      </div>
                    )
                  ))}
                </div>
              ) : (
                <div style={{ color: 'rgba(224,244,255,0.4)', fontSize: 13, marginBottom: 8 }}>
                  Устройство не подключено. Введите данные вручную.
                </div>
              )}
              <button
                onClick={() => setShowManual((v) => !v)}
                className="neon-btn"
                style={{ borderColor: 'rgba(0,212,255,0.4)', color: 'rgba(0,212,255,0.7)', marginTop: 10, fontSize: 11 }}
              >
                {showManual ? 'Скрыть форму' : 'Ввести вручную'}
              </button>
              {showManual && <ManualForm onSaved={() => { setShowManual(false); loadData() }} />}
            </>
          )}

          {card(
            <>
              {sectionTitle('Уровень 2 — Паттерны')}
              <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                {(Object.keys(PERIOD_LABELS) as Period[]).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPeriod(p)}
                    className="neon-btn"
                    style={{
                      borderColor: period === p ? '#00d4ff' : 'rgba(0,212,255,0.2)',
                      color: period === p ? '#00d4ff' : 'rgba(224,244,255,0.4)',
                      fontSize: 11,
                    }}
                  >
                    {PERIOD_LABELS[p]}
                  </button>
                ))}
              </div>
              {patterns.length === 0 ? (
                <div style={{ color: 'rgba(224,244,255,0.3)', fontSize: 13 }}>Недостаточно данных</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {patterns.map((pat) => (
                    <div key={pat.metric} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ minWidth: 120, fontSize: 13, color: 'rgba(224,244,255,0.7)' }}>
                        {METRIC_LABELS[pat.metric] ?? pat.metric}
                      </div>
                      <SparkLine points={pat.dataPoints} />
                      <span style={{ fontSize: 16, color: TREND_COLOR[pat.trend] }}>
                        {TREND_ICON[pat.trend]}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {card(
            <>
              {sectionTitle('Уровень 3 — Рекомендации JARVIS')}
              {recommendations.length === 0 ? (
                <div style={{ color: 'rgba(224,244,255,0.3)', fontSize: 13 }}>
                  Накапливаю данные для анализа...
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {recommendations.map((rec) => (
                    <div key={rec.id} style={{
                      background: 'rgba(0,212,255,0.04)',
                      border: '1px solid rgba(0,212,255,0.1)',
                      borderRadius: 6,
                      padding: '10px 12px',
                    }}>
                      <div style={{ fontSize: 13, fontWeight: 500, color: '#e0f4ff', marginBottom: 4 }}>
                        {rec.title}
                      </div>
                      <div style={{ fontSize: 12, color: 'rgba(224,244,255,0.55)', lineHeight: 1.5 }}>
                        {rec.body}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

        </div>
      )}
    </div>
  )
}
