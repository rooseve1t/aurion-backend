import React, { useEffect, useRef, useState } from 'react'
import ReactDOM from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useHUDStore } from '@/store/hudStore'
import type { HUDSnapshot } from '@/types'

// Helper: color based on value and thresholds
function getMetricColor(value: number, warnAt: number, critAt: number): string {
  if (value >= critAt) return '#ef4444' // red
  if (value >= warnAt) return '#f59e0b' // amber
  return '#22c55e' // green
}

function StressColor(index: number): string {
  if (index >= 70) return '#ef4444'
  if (index >= 40) return '#f59e0b'
  return '#22c55e'
}

function ThreatColor(level: string): string {
  switch (level) {
    case 'critical': return '#ef4444'
    case 'high': return '#f97316'
    case 'medium': return '#f59e0b'
    default: return '#22c55e'
  }
}

interface MetricPillProps {
  label: string
  value: string
  color: string
  pulse?: boolean
}

function MetricPill({ label, value, color, pulse }: MetricPillProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
      <span style={{ fontSize: '9px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </span>
      <motion.span
        animate={pulse ? { opacity: [1, 0.4, 1] } : {}}
        transition={pulse ? { duration: 1, repeat: Infinity } : {}}
        style={{
          fontSize: '11px',
          fontWeight: 700,
          color,
          fontFamily: 'monospace',
          letterSpacing: '0.05em',
        }}
      >
        {value}
      </motion.span>
    </div>
  )
}

const API_BASE = (import.meta as { env: Record<string, string> }).env.VITE_API_URL || ''

async function fetchHUDSnapshot(): Promise<HUDSnapshot | null> {
  try {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token')
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    const res = await fetch(`${API_BASE}/api/v1/system/hud-snapshot`, { headers })
    if (!res.ok) return null
    return await res.json() as HUDSnapshot
  } catch {
    return null
  }
}

interface ExpandedMetricProps {
  label: string
  value: string
  progress: number
  color: string
}

function ExpandedMetric({ label, value, progress, color }: ExpandedMetricProps) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <span style={{ fontSize: '9px', color: '#94a3b8', textTransform: 'uppercase' }}>{label}</span>
        <span style={{ fontSize: '10px', color, fontWeight: 700, fontFamily: 'monospace' }}>{value}</span>
      </div>
      <div style={{ height: '3px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
        <motion.div
          animate={{ width: `${Math.min(progress, 100)}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ height: '100%', background: color, borderRadius: '2px' }}
        />
      </div>
    </div>
  )
}

export function JarvisHUDOverlay() {
  const {
    isVisible,
    isExpanded,
    snapshot,
    setSnapshot,
    setExpanded,
    setEmergency,
  } = useHUDStore()
  const [showEmergencyFlash, setShowEmergencyFlash] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Poll HUD data every 15 seconds
  useEffect(() => {
    const poll = async () => {
      const data = await fetchHUDSnapshot()
      if (data) setSnapshot(data)
    }
    void poll()
    intervalRef.current = setInterval(() => { void poll() }, 15000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [setSnapshot])

  // Listen for emergency/HUD update events via window.postMessage
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) as Record<string, unknown> : event.data as Record<string, unknown>
        if (data?.type === 'emergency_protocol_triggered') {
          setEmergency(true, typeof data.message === 'string' ? data.message : 'АВАРИЙНЫЙ ПРОТОКОЛ АКТИВИРОВАН')
          setShowEmergencyFlash(true)
          setTimeout(() => {
            setShowEmergencyFlash(false)
          }, 5000)
        }
        if (data?.type === 'system_hud_update' && data.snapshot) {
          setSnapshot(data.snapshot as HUDSnapshot)
        }
      } catch {
        // ignore malformed messages
      }
    }
    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [setSnapshot, setEmergency])

  if (!isVisible) return null

  const snap = snapshot

  const hudContent = (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      style={{
        position: 'fixed',
        bottom: 0,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 9999,
        fontFamily: '"Courier New", monospace',
        userSelect: 'none',
      }}
    >
      {/* Emergency Flash */}
      <AnimatePresence>
        {showEmergencyFlash && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [1, 0.3, 1, 0.3, 1] }}
            exit={{ opacity: 0 }}
            transition={{ duration: 5, times: [0, 0.2, 0.4, 0.6, 1] }}
            style={{
              position: 'absolute',
              top: '-40px',
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'rgba(239, 68, 68, 0.9)',
              color: 'white',
              padding: '6px 16px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 700,
              letterSpacing: '0.15em',
              whiteSpace: 'nowrap',
              border: '1px solid #ef4444',
              backdropFilter: 'blur(8px)',
            }}
          >
            АВАРИЙНЫЙ ПРОТОКОЛ АКТИВИРОВАН
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main HUD Bar */}
      <motion.div
        layout
        animate={{
          height: isExpanded ? 180 : 42,
          width: isExpanded ? 720 : 580,
          borderRadius: isExpanded ? '12px 12px 0 0' : '8px 8px 0 0',
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        style={{
          background: 'rgba(2, 8, 23, 0.92)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderBottom: 'none',
          backdropFilter: 'blur(12px)',
          overflow: 'hidden',
          boxShadow: '0 -4px 24px rgba(34, 197, 94, 0.1)',
        }}
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
      >
        {/* Top accent line */}
        <div style={{
          height: '2px',
          background: 'linear-gradient(90deg, transparent, rgba(34, 197, 94, 0.6), rgba(6, 182, 212, 0.6), transparent)',
        }} />

        {/* Collapsed view - always visible */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '24px',
          padding: '8px 20px',
          height: '40px',
        }}>
          {/* JARVIS label */}
          <span style={{ fontSize: '10px', color: '#22c55e', fontWeight: 700, letterSpacing: '0.15em' }}>
            J.A.R.V.I.S
          </span>

          <div style={{ width: '1px', height: '20px', background: 'rgba(34, 197, 94, 0.3)' }} />

          {snap ? (
            <>
              <MetricPill label="CPU" value={`${snap.cpu_percent}%`} color={getMetricColor(snap.cpu_percent, 70, 90)} pulse={snap.cpu_percent > 90} />
              <MetricPill label="RAM" value={`${snap.memory_percent}%`} color={getMetricColor(snap.memory_percent, 75, 90)} pulse={snap.memory_percent > 90} />
              <MetricPill label="АГЕНТЫ" value={String(snap.active_agents)} color="#06b6d4" />
              <MetricPill label="ЗАДАЧИ" value={String(snap.pending_tasks)} color="#8b5cf6" />
              <MetricPill label="УГРОЗА" value={snap.threat_level.toUpperCase()} color={ThreatColor(snap.threat_level)} pulse={snap.threat_level === 'critical'} />
              <MetricPill label="СТРЕСС" value={`${snap.stress_index}%`} color={StressColor(snap.stress_index)} pulse={snap.stress_index >= 70} />
            </>
          ) : (
            <span style={{ fontSize: '10px', color: '#64748b' }}>ИНИЦИАЛИЗАЦИЯ...</span>
          )}

          <div style={{ width: '1px', height: '20px', background: 'rgba(34, 197, 94, 0.3)' }} />

          {/* Autonomy level */}
          {snap && (
            <span style={{ fontSize: '9px', color: '#94a3b8', letterSpacing: '0.1em' }}>
              {snap.autonomy_level.toUpperCase()}
            </span>
          )}
        </div>

        {/* Expanded view */}
        <AnimatePresence>
          {isExpanded && snap && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ padding: '12px 20px' }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                <ExpandedMetric
                  label="Процессор"
                  value={`${snap.cpu_percent}%`}
                  progress={snap.cpu_percent}
                  color={getMetricColor(snap.cpu_percent, 70, 90)}
                />
                <ExpandedMetric
                  label="Память"
                  value={`${snap.memory_used_gb} GB`}
                  progress={snap.memory_percent}
                  color={getMetricColor(snap.memory_percent, 75, 90)}
                />
                <ExpandedMetric
                  label="Стресс"
                  value={`${snap.stress_index}%`}
                  progress={snap.stress_index}
                  color={StressColor(snap.stress_index)}
                />
                <ExpandedMetric
                  label="Миссии"
                  value={String(snap.active_missions)}
                  progress={Math.min(snap.active_missions * 20, 100)}
                  color="#8b5cf6"
                />
              </div>

              <div style={{
                marginTop: '10px',
                paddingTop: '8px',
                borderTop: '1px solid rgba(34, 197, 94, 0.15)',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '9px',
                color: '#64748b',
              }}>
                <span>Агентов активно: {snap.active_agents}</span>
                <span>Задач в очереди: {snap.pending_tasks}</span>
                <span>Автономность: {snap.autonomy_level}</span>
                <span>Угроза: {snap.threat_level}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  )

  // Use portal to render into document.body; fall back gracefully if unavailable
  const portalTarget = typeof document !== 'undefined' ? document.body : null
  if (!portalTarget) return null

  return ReactDOM.createPortal(hudContent, portalTarget)
}

export default JarvisHUDOverlay
