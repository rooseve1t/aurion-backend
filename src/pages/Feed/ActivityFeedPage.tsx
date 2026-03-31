import React, { useCallback, useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { FeedCard as FeedCardData } from '@/types/feed'
import {
  connectFeedWebSocket,
  confirmCard,
  dismissCard,
  getFeed,
} from '@/services/feedService'

const TYPE_ACCENT: Record<string, string> = {
  observation: '#00d4ff',
  suggestion:  '#00ff88',
  alert:       '#ff4444',
  insight:     '#8b5cf6',
}

const DOMAIN_LABEL: Record<string, string> = {
  health:   'Здоровье',
  finance:  'Финансы',
  security: 'Безопасность',
  calendar: 'Календарь',
}

const TYPE_LABEL: Record<string, string> = {
  observation: 'Наблюдение',
  suggestion:  'Предложение',
  alert:       'Предупреждение',
  insight:     'Инсайт',
}

interface CardProps {
  card: FeedCardData
  onConfirm: (id: string) => void
  onDismiss: (id: string) => void
}

const FeedCard: React.FC<CardProps> = ({ card, onConfirm, onDismiss }) => {
  const accent = TYPE_ACCENT[card.type] ?? '#00d4ff'
  const isConfirmed = Boolean(card.confirmedAt)
  const isDismissed = Boolean(card.dismissedAt)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      style={{
        background: 'rgba(13,13,24,0.85)',
        border: `1px solid ${accent}33`,
        borderLeft: `3px solid ${accent}`,
        borderRadius: 8,
        padding: '14px 16px',
        marginBottom: 10,
        backdropFilter: 'blur(12px)',
        boxShadow: `0 2px 16px rgba(0,0,0,0.5), 0 0 8px ${accent}22`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <span style={{
          fontSize: 10,
          fontFamily: 'var(--font-hud)',
          letterSpacing: '0.1em',
          textTransform: 'uppercase' as const,
          color: accent,
          textShadow: `0 0 6px ${accent}`,
        }}>
          {TYPE_LABEL[card.type]}
        </span>
        <span style={{ color: 'rgba(224,244,255,0.3)', fontSize: 10 }}>·</span>
        <span style={{ color: 'rgba(224,244,255,0.4)', fontSize: 10, fontFamily: 'var(--font-hud)' }}>
          {DOMAIN_LABEL[card.domain]}
        </span>
        <span style={{ marginLeft: 'auto', color: 'rgba(224,244,255,0.3)', fontSize: 10 }}>
          {new Date(card.createdAt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      <div style={{ color: '#e0f4ff', fontSize: 14, fontWeight: 500, marginBottom: 4 }}>
        {card.title}
      </div>
      <div style={{ color: 'rgba(224,244,255,0.6)', fontSize: 13, lineHeight: 1.5 }}>
        {card.body}
      </div>

      {card.requiresConfirmation && !isConfirmed && !isDismissed && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button
            onClick={() => onConfirm(card.id)}
            className="neon-btn"
            style={{ borderColor: '#00ff88', color: '#00ff88' }}
          >
            Подтвердить
          </button>
          <button
            onClick={() => onDismiss(card.id)}
            className="neon-btn"
            style={{ borderColor: '#ff4444', color: '#ff4444' }}
          >
            Отклонить
          </button>
        </div>
      )}

      {isConfirmed && (
        <div style={{ marginTop: 8, color: '#00ff88', fontSize: 11, fontFamily: 'var(--font-hud)' }}>
          ✓ Подтверждено
        </div>
      )}
      {isDismissed && (
        <div style={{ marginTop: 8, color: 'rgba(224,244,255,0.3)', fontSize: 11, fontFamily: 'var(--font-hud)' }}>
          — Отклонено
        </div>
      )}
    </motion.div>
  )
}

export const ActivityFeedPage: React.FC = () => {
  const [cards, setCards] = useState<FeedCardData[]>([])
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [loading, setLoading] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const loaderRef = useRef<HTMLDivElement>(null)
  const loadingRef = useRef(false)

  const loadPage = useCallback(async (p: number) => {
    if (loadingRef.current) return
    loadingRef.current = true
    setLoading(true)
    try {
      const result = await getFeed(p)
      setCards((prev) => (p === 0 ? result.items : [...prev, ...result.items]))
      setHasMore(result.hasMore)
      setPage(p)
    } catch {
      // не блокируем UI при ошибке
    } finally {
      loadingRef.current = false
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadPage(0)
  }, [loadPage])

  useEffect(() => {
    if (!loaderRef.current) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingRef.current) {
          loadPage(page + 1)
        }
      },
      { threshold: 0.1 }
    )
    observer.observe(loaderRef.current)
    return () => observer.disconnect()
  }, [hasMore, page, loadPage])

  useEffect(() => {
    const disconnect = connectFeedWebSocket((card) => {
      setCards((prev) => [card, ...prev])
      setWsConnected(true)
    })
    return disconnect
  }, [])

  const handleConfirm = async (id: string) => {
    try {
      await confirmCard(id)
      setCards((prev) =>
        prev.map((c) => (c.id === id ? { ...c, confirmedAt: new Date().toISOString() } : c))
      )
    } catch { /* ignore */ }
  }

  const handleDismiss = async (id: string) => {
    try {
      await dismissCard(id)
      setCards((prev) =>
        prev.map((c) => (c.id === id ? { ...c, dismissedAt: new Date().toISOString() } : c))
      )
    } catch { /* ignore */ }
  }

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1 style={{
            margin: 0,
            fontSize: 20,
            fontFamily: 'var(--font-hud)',
            color: '#00d4ff',
            textShadow: '0 0 8px rgba(0,212,255,0.6)',
            letterSpacing: '0.05em',
          }}>
            ACTIVITY FEED
          </h1>
          <div
            title={wsConnected ? 'WebSocket подключён' : 'WebSocket отключён'}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: wsConnected ? '#00ff88' : '#ff4444',
              boxShadow: wsConnected
                ? '0 0 6px rgba(0,255,136,0.8)'
                : '0 0 6px rgba(255,68,68,0.8)',
              transition: '300ms ease',
            }}
          />
        </div>
        <p style={{ margin: '4px 0 0', color: 'rgba(224,244,255,0.4)', fontSize: 12, fontFamily: 'var(--font-hud)' }}>
          Лента активности JARVIS
        </p>
      </motion.div>

      <AnimatePresence initial={false}>
        {cards.map((card) => (
          <FeedCard
            key={card.id}
            card={card}
            onConfirm={handleConfirm}
            onDismiss={handleDismiss}
          />
        ))}
      </AnimatePresence>

      {!loading && cards.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          style={{
            textAlign: 'center',
            padding: '60px 0',
            color: 'rgba(224,244,255,0.3)',
            fontFamily: 'var(--font-hud)',
            fontSize: 13,
          }}
        >
          <div style={{ fontSize: 32, marginBottom: 12 }}>◈</div>
          <div>Лента пуста. JARVIS наблюдает...</div>
        </motion.div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
            style={{ color: '#00d4ff', fontFamily: 'var(--font-hud)', fontSize: 12 }}
          >
            ЗАГРУЗКА...
          </motion.div>
        </div>
      )}

      <div ref={loaderRef} style={{ height: 1 }} />

      {!hasMore && cards.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '16px 0',
          color: 'rgba(224,244,255,0.2)',
          fontFamily: 'var(--font-hud)',
          fontSize: 11,
          letterSpacing: '0.1em',
        }}>
          — КОНЕЦ ЛЕНТЫ —
        </div>
      )}
    </div>
  )
}
