/**
 * FullscreenHUD — обёртка для полноэкранного режима JARVIS.
 * В fullscreen скрывает браузерные элементы, показывает полный HUD.
 * Корректно работает от 1280×720.
 */
import React from 'react'
import { useFullscreen } from '@/hooks/useFullscreen'
import { JarvisAvatar } from './JarvisAvatar'
import { RealtimeDashboard } from './RealtimeDashboard'
import { VoiceIndicator } from './VoiceIndicator'
import type { AvatarState } from './JarvisAvatar'
import type { VoiceState } from './VoiceIndicator'

interface FullscreenHUDProps {
  avatarState?: AvatarState
  voiceState?: VoiceState
  onVoiceReset?: () => void
  children?: React.ReactNode
}

export const FullscreenHUD: React.FC<FullscreenHUDProps> = ({
  avatarState = 'idle',
  voiceState = 'idle',
  onVoiceReset,
  children,
}) => {
  const { isFullscreen, toggle } = useFullscreen()

  return (
    <div
      style={{
        position: 'relative',
        background: 'var(--hud-bg)',
        color: 'var(--hud-text)',
        minHeight: '100vh',
        minWidth: 1280,
        fontFamily: 'var(--font-ui)',
        overflow: 'hidden',
      }}
    >
      {/* Фоновые частицы */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse at 20% 50%, rgba(0,128,255,0.06) 0%, transparent 60%),' +
            'radial-gradient(ellipse at 80% 20%, rgba(0,212,255,0.04) 0%, transparent 50%)',
          pointerEvents: 'none',
        }}
      />

      {/* Верхняя панель */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          borderBottom: '1px solid rgba(0,212,255,0.15)',
          position: 'relative',
          zIndex: 10,
        }}
      >
        {/* Логотип */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <JarvisAvatar state={avatarState} size={48} />
          <div>
            <div
              style={{
                fontSize: '1.1rem',
                fontWeight: 700,
                color: 'var(--hud-accent)',
                textShadow: 'var(--text-glow-cyan)',
                letterSpacing: '0.15em',
                fontFamily: 'var(--font-hud)',
              }}
            >
              AURION OS
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--hud-text-muted)', letterSpacing: '0.1em' }}>
              JARVIS v2.0 · {new Date().toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}
            </div>
          </div>
        </div>

        {/* Центр — индикатор голоса */}
        <VoiceIndicator state={voiceState} onReset={onVoiceReset} />

        {/* Правая часть — кнопка fullscreen */}
        <button
          onClick={toggle}
          title={isFullscreen ? 'Выйти из полноэкранного режима (F11)' : 'Полноэкранный режим (F11)'}
          style={{
            background: 'rgba(0,212,255,0.08)',
            border: '1px solid rgba(0,212,255,0.3)',
            color: 'var(--hud-accent)',
            borderRadius: 4,
            padding: '6px 12px',
            cursor: 'pointer',
            fontSize: '0.75rem',
            letterSpacing: '0.05em',
            fontFamily: 'var(--font-hud)',
            transition: '150ms ease',
          }}
        >
          {isFullscreen ? '⊡ ВЫХОД' : '⊞ HUD'}
        </button>
      </div>

      {/* Основной контент */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {children ?? <RealtimeDashboard />}
      </div>

      {/* CSS для fullscreen — скрываем браузерные элементы */}
      <style>{`
        :fullscreen .hud-root,
        :-webkit-full-screen .hud-root {
          background: var(--hud-bg);
        }
        @media (max-width: 1279px) {
          .fullscreen-hud-inner {
            transform: scale(0.85);
            transform-origin: top left;
          }
        }
      `}</style>
    </div>
  )
}
