/**
 * Хук для управления полноэкранным HUD-режимом.
 * Горячая клавиша F11 или кнопка — переключение.
 */
import { useState, useEffect, useCallback } from 'react'

export function useFullscreen() {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const enter = useCallback(async () => {
    try {
      await document.documentElement.requestFullscreen()
    } catch {
      // Браузер не поддерживает или запрос отклонён
    }
  }, [])

  const exit = useCallback(async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen()
      }
    } catch { /* игнорируем */ }
  }, [])

  const toggle = useCallback(() => {
    if (document.fullscreenElement) {
      exit()
    } else {
      enter()
    }
  }, [enter, exit])

  // Слушаем изменения fullscreen
  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', handler)
    return () => document.removeEventListener('fullscreenchange', handler)
  }, [])

  // Горячая клавиша F11
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'F11') {
        e.preventDefault()
        toggle()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [toggle])

  return { isFullscreen, toggle, enter, exit }
}
