/**
 * RealtimeDashboard — HUD-дашборд с данными в реальном времени через WebSocket.
 * Виджеты: статус системы, активность агентов, радар угроз, финансовый тикер.
 */
import React, { useEffect, useState, useCallback } from 'react'
import { wsService } from '@/services/ws'

// ─── Типы данных ──────────────────────────────────────────────────────────────

interface SystemStatus {
  database: string
  redis: string
  jarvis: string
  cpu?: number
  memory?: number
}

interface AgentStatus {
  name: string
  role: string
  status: 'standby' | 'working' | 'error'
  last_action?: string
}

interface ThreatItem {
  id: string
  level: 'low' | 'medium' | 'high' | 'critical'
  message: string
  timestamp: string
}

interface QuoteItem {
  symbol: string
  price: number | null
  change_pct: number
  stale?: boolean
}

interface DashboardState {
  system: SystemStatus
  agents: AgentStatus[]
  threats: ThreatItem[]
  quotes: QuoteItem[]
  lastUpdate: string
}

const INITIAL: DashboardState = {
  system: { database: 'unknown', redis: 'unknown', jarvis: 'online' },
  agents: [],
  threats: [],
  quotes: [],
  lastUpdate: '',
}

// ─── Вспомогательные компоненты ───────────────────────────────────────────────

const StatusDot: React.FC<{ status: string }> = ({ status }) => {
  const color =
    status === 'connected' || status === 'online' || status === 'standby'
      ? 'var(--hud-accent-green)'
      : status === 'working'
      ? 'var(--hud-accent)'
      : status === 'error' || status === 'degraded'
      ? 'var(--hud-accent-red)'
      : 'var(--hud-text-muted)'

  return (
    <span
      style={{
        display: 'inline-block',
        width: 8,
        height: 8,
        borderRadius: '50%',
        background: color,
        boxShadow: `0 0 6px ${color}`,
        marginRight: 6,
        flexShrink: 0,
      }}
    />
  )
}

const ThreatBadge: React.FC<{ level: ThreatItem['level'] }> = ({ level }) => {
  const colors: Record<string, string> = {
    low: '#00ff88',
    medium: '#ffd700',
    high: '#ff8800',
    critical: '#ff4444',
  }
  const c = colors[level] || '#aaa'
  return (
    <span
      style={{
        fontSize: '0.65rem',
        padding: '1px 6px',
        borderRadius: 3,
        border: `1px solid ${c}`,
        color: c,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}
    >
      {level}
    </span>
  )
}

// ─── Основной компонент ───────────────────────────────────────────────────────

export const RealtimeDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardState>(INITIAL)

  const handleWsMessage = useCallback((msg: { type?: string; payload?: unknown }) => {
    const payload = msg.payload as Record<string, unknown> | undefined
    if (!payload) return

    setData((prev) => {
      const next = { ...prev, lastUpdate: new Date().toLocaleTimeString('ru-RU') }

      switch (msg.type) {
        case 'system_status':
          next.system = payload as SystemStatus
          break
        case 'agent_status':
          next.agents = Array.isArray(payload) ? (payload as AgentStatus[]) : prev.agents
          break
        case 'threat_alert':
          next.threats = [payload as ThreatItem, ...prev.threats].slice(0, 5)
          break
        case 'quote_update':
          next.quotes = Array.isArray(payload) ? (payload as QuoteItem[]) : prev.quotes
          break
        case 'health':
          if (typeof payload === 'object' && payload !== null) {
            const services = (payload as { services?: Record<string, string> }).services || {}
            next.system = {
              database: services.database || 'unknown',
              redis: services.redis || 'unknown',
              jarvis: 'online',
            }
          }
          break
      }
      return next
    })
  }, [])

  useEffect(() => {
    const unsub = wsService.onMessage(handleWsMessage as Parameters<typeof wsService.onMessage>[0])
    return unsub
  }, [handleWsMessage])

  const panelStyle: React.CSSProperties = {
    background: 'var(--glass-bg)',
    border: 'var(--glass-border)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    borderRadius: 8,
    padding: '12px 16px',
  }

  const titleStyle: React.CSSProperties = {
    fontSize: '0.7rem',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
    color: 'var(--hud-accent)',
    textShadow: 'var(--text-glow-cyan)',
    marginBottom: 10,
    fontFamily: 'var(--font-hud)',
  }

  const rowStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '0.8rem',
    padding: '3px 0',
    color: 'var(--hud-text)',
  }

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 12,
        padding: 16,
        fontFamily: 'var(--font-ui)',
      }}
    >
      {/* ─── Статус системы ─────────────────────────────────────────────── */}
      <div style={panelStyle}>
        <div style={titleStyle}>Статус системы</div>
        {[
          { label: 'База данных', value: data.system.database },
          { label: 'Redis', value: data.system.redis },
          { label: 'JARVIS', value: data.system.jarvis },
        ].map(({ label, value }) => (
          <div key={label} style={rowStyle}>
            <span style={{ color: 'var(--hud-text-dim)' }}>{label}</span>
            <span style={{ display: 'flex', alignItems: 'center' }}>
              <StatusDot status={value} />
              <span style={{ fontSize: '0.75rem' }}>{value}</span>
            </span>
          </div>
        ))}
        {data.lastUpdate && (
          <div style={{ fontSize: '0.65rem', color: 'var(--hud-text-muted)', marginTop: 8 }}>
            Обновлено: {data.lastUpdate}
          </div>
        )}
      </div>

      {/* ─── Агенты ─────────────────────────────────────────────────────── */}
      <div style={panelStyle}>
        <div style={titleStyle}>Агенты</div>
        {data.agents.length === 0 ? (
          <div style={{ fontSize: '0.75rem', color: 'var(--hud-text-muted)' }}>
            Нет активных агентов
          </div>
        ) : (
          data.agents.map((agent) => (
            <div key={agent.name} style={rowStyle}>
              <span style={{ display: 'flex', alignItems: 'center' }}>
                <StatusDot status={agent.status} />
                <span style={{ color: 'var(--hud-text-dim)', fontSize: '0.75rem' }}>
                  {agent.role}
                </span>
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--hud-text-muted)', maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {agent.last_action || agent.status}
              </span>
            </div>
          ))
        )}
      </div>

      {/* ─── Радар угроз ────────────────────────────────────────────────── */}
      <div style={panelStyle}>
        <div style={titleStyle}>Угрозы</div>
        {data.threats.length === 0 ? (
          <div style={{ fontSize: '0.75rem', color: 'var(--hud-accent-green)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <StatusDot status="online" />
            Угроз не обнаружено
          </div>
        ) : (
          data.threats.map((t) => (
            <div key={t.id} style={{ ...rowStyle, flexDirection: 'column', alignItems: 'flex-start', gap: 2, borderBottom: '1px solid rgba(0,212,255,0.08)', paddingBottom: 6, marginBottom: 4 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <ThreatBadge level={t.level} />
                <span style={{ fontSize: '0.65rem', color: 'var(--hud-text-muted)' }}>{t.timestamp}</span>
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--hud-text)' }}>{t.message}</span>
            </div>
          ))
        )}
      </div>

      {/* ─── Финансовый тикер ───────────────────────────────────────────── */}
      <div style={panelStyle}>
        <div style={titleStyle}>Котировки</div>
        {data.quotes.length === 0 ? (
          <div style={{ fontSize: '0.75rem', color: 'var(--hud-text-muted)' }}>
            Нет данных
          </div>
        ) : (
          data.quotes.map((q) => {
            const up = (q.change_pct ?? 0) >= 0
            const changeColor = up ? 'var(--hud-accent-green)' : 'var(--hud-accent-red)'
            return (
              <div key={q.symbol} style={rowStyle}>
                <span style={{ fontFamily: 'var(--font-hud)', fontSize: '0.8rem' }}>{q.symbol}</span>
                <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span>{q.price != null ? q.price.toFixed(2) : '—'}</span>
                  <span style={{ color: changeColor, fontSize: '0.75rem' }}>
                    {up ? '▲' : '▼'} {Math.abs(q.change_pct ?? 0).toFixed(2)}%
                  </span>
                  {q.stale && <span style={{ fontSize: '0.6rem', color: 'var(--hud-accent-yellow)' }}>⚠</span>}
                </span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
