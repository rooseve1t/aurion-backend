/**
 * Визуальный индикатор состояния голосового ввода JARVIS.
 * Синий = ожидание wake-word, Зелёный = активное прослушивание, Жёлтый = обработка.
 */
import React, { useEffect, useRef } from 'react'

export type VoiceState = 'idle' | 'listening' | 'processing'

interface VoiceIndicatorProps {
  state: VoiceState
  /** Автовозврат в idle через N мс (по умолчанию 10 000) */
  autoResetMs?: number
  onReset?: () => void
}

const STATE_CONFIG: Record<VoiceState, { color: string; label: string; glow: string }> = {
  idle:       { color: '#00d4ff', label: 'Ожидание',   glow: 'rgba(0,212,255,0.3)' },
  listening:  { color: '#00ff88', label: 'Слушаю',     glow: 'rgba(0,255,136,0.4)' },
  processing: { color: '#ffd700', label: 'Обработка',  glow: 'rgba(255,215,0,0.4)' },
}

export const VoiceIndicator: React.FC<VoiceIndicatorProps> = ({
  state,
  autoResetMs = 10_000,
  onReset,
}) => {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const { color, label, glow } = STATE_CONFIG[state]

  // Автовозврат в idle если нет команды
  useEffect(() => {
    if (state === 'listening') {
      timerRef.current = setTimeout(() => {
        onReset?.()
      }, autoResetMs)
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [state, autoResetMs, onReset])

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 14px',
        borderRadius: '20px',
        background: 'rgba(0,0,0,0.4)',
        border: `1px solid ${color}44`,
        backdropFilter: 'blur(8px)',
        userSelect: 'none',
      }}
      title={`JARVIS: ${label}`}
    >
      {/* Пульсирующий кружок */}
      <span
        style={{
          display: 'inline-block',
          width: 10,
          height: 10,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 8px ${glow}, 0 0 16px ${glow}`,
          animation: state !== 'idle' ? 'jarvis-pulse 1s ease-in-out infinite' : 'none',
        }}
      />
      <span style={{ color, fontSize: '0.75rem', fontWeight: 500, letterSpacing: '0.05em' }}>
        {label}
      </span>

      <style>{`
        @keyframes jarvis-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50%       { opacity: 0.5; transform: scale(1.3); }
        }
      `}</style>
    </div>
  )
}
