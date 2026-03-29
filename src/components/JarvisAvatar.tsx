/**
 * JarvisAvatar — анимированный аватар JARVIS.
 * Состояния: idle (медленная пульсация), speaking (звуковая волна), listening (быстрая пульсация).
 * Синхронизируется с аудиопотоком через Web Audio API AnalyserNode.
 */
import React, { useEffect, useRef, useCallback } from 'react'

export type AvatarState = 'idle' | 'speaking' | 'listening'

interface JarvisAvatarProps {
  state: AvatarState
  size?: number
  /** Аудиоэлемент для синхронизации с речью JARVIS */
  audioRef?: React.RefObject<HTMLAudioElement>
}

const COLORS = {
  idle:      '#00d4ff',
  speaking:  '#00ff88',
  listening: '#ffd700',
}

export const JarvisAvatar: React.FC<JarvisAvatarProps> = ({
  state,
  size = 120,
  audioRef,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animFrameRef = useRef<number>(0)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const dataRef = useRef<Uint8Array<ArrayBuffer>>(new Uint8Array(64) as Uint8Array<ArrayBuffer>)
  const phaseRef = useRef(0)

  // Подключаем Web Audio API к аудиоэлементу
  const connectAudio = useCallback(() => {
    if (!audioRef?.current) return
    try {
      const ctx = new AudioContext()
      const source = ctx.createMediaElementSource(audioRef.current)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 128
      source.connect(analyser)
      analyser.connect(ctx.destination)
      analyserRef.current = analyser
      dataRef.current = new Uint8Array(analyser.frequencyBinCount) as Uint8Array<ArrayBuffer>
    } catch {
      // Браузер не поддерживает или уже подключён
    }
  }, [audioRef])

  useEffect(() => {
    if (audioRef?.current) {
      audioRef.current.addEventListener('play', connectAudio, { once: true })
    }
    return () => {
      audioRef?.current?.removeEventListener('play', connectAudio)
    }
  }, [audioRef, connectAudio])

  // Основной цикл рендера
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const color = COLORS[state]
    const cx = size / 2
    const cy = size / 2
    const r = size * 0.35

    const draw = () => {
      ctx.clearRect(0, 0, size, size)
      phaseRef.current += state === 'idle' ? 0.02 : state === 'listening' ? 0.08 : 0.05

      // Получаем данные анализатора если есть
      if (analyserRef.current && state === 'speaking') {
        analyserRef.current.getByteFrequencyData(dataRef.current)
      }

      // ─── Внешнее кольцо (glow) ───────────────────────────────────────
      const glowRadius = r + 8 + Math.sin(phaseRef.current) * (state === 'idle' ? 3 : 8)
      const grad = ctx.createRadialGradient(cx, cy, r - 4, cx, cy, glowRadius + 12)
      grad.addColorStop(0, color + 'aa')
      grad.addColorStop(1, color + '00')
      ctx.beginPath()
      ctx.arc(cx, cy, glowRadius + 12, 0, Math.PI * 2)
      ctx.fillStyle = grad
      ctx.fill()

      // ─── Основной круг ────────────────────────────────────────────────
      ctx.beginPath()
      ctx.arc(cx, cy, r, 0, Math.PI * 2)
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.shadowColor = color
      ctx.shadowBlur = 12
      ctx.stroke()
      ctx.shadowBlur = 0

      // ─── Звуковая волна (speaking) ────────────────────────────────────
      if (state === 'speaking') {
        const bars = dataRef.current.length
        ctx.beginPath()
        for (let i = 0; i <= bars; i++) {
          const angle = (i / bars) * Math.PI * 2 - Math.PI / 2
          const amp = (dataRef.current[i % bars] / 255) * r * 0.5 + 2
          const rx = cx + Math.cos(angle) * (r + amp)
          const ry = cy + Math.sin(angle) * (r + amp)
          i === 0 ? ctx.moveTo(rx, ry) : ctx.lineTo(rx, ry)
        }
        ctx.closePath()
        ctx.strokeStyle = color + 'cc'
        ctx.lineWidth = 1.5
        ctx.shadowColor = color
        ctx.shadowBlur = 8
        ctx.stroke()
        ctx.shadowBlur = 0
      }

      // ─── Пульсирующие кольца (idle / listening) ───────────────────────
      if (state !== 'speaking') {
        const rings = state === 'listening' ? 3 : 2
        for (let i = 0; i < rings; i++) {
          const t = ((phaseRef.current * 0.5 + i / rings) % 1)
          const ringR = r + t * r * 0.8
          const alpha = (1 - t) * 0.5
          ctx.beginPath()
          ctx.arc(cx, cy, ringR, 0, Math.PI * 2)
          ctx.strokeStyle = color + Math.round(alpha * 255).toString(16).padStart(2, '0')
          ctx.lineWidth = 1
          ctx.stroke()
        }
      }

      // ─── Центральная точка ────────────────────────────────────────────
      ctx.beginPath()
      ctx.arc(cx, cy, 4, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.shadowColor = color
      ctx.shadowBlur = 10
      ctx.fill()
      ctx.shadowBlur = 0

      animFrameRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(animFrameRef.current)
  }, [state, size])

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      style={{ display: 'block' }}
      aria-label={`JARVIS: ${state}`}
    />
  )
}
