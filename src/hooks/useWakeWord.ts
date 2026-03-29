/**
 * Wake-word детектор — слушает «JARVIS» / «Джарвис» без отправки аудио на сервер.
 * Использует Web Speech API (SpeechRecognition).
 */
import { useEffect, useRef, useCallback } from 'react'

export type WakeWordState = 'idle' | 'listening' | 'processing'

interface UseWakeWordOptions {
  onActivated: () => void
  enabled?: boolean
}

const WAKE_WORDS = ['jarvis', 'джарвис', 'джарвис,', 'jarvis,']

export function useWakeWord({ onActivated, enabled = true }: UseWakeWordOptions) {
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const activeRef = useRef(false)

  const start = useCallback(() => {
    type SpeechRecognitionCtor = new () => SpeechRecognition
    const w = window as Window & {
      SpeechRecognition?: SpeechRecognitionCtor
      webkitSpeechRecognition?: SpeechRecognitionCtor
    }
    const SpeechRecognitionImpl = w.SpeechRecognition || w.webkitSpeechRecognition

    if (!SpeechRecognitionImpl) {
      console.warn('[useWakeWord] Web Speech API не поддерживается в этом браузере')
      return
    }

    const recognition = new SpeechRecognitionImpl()
    recognition.lang = 'ru-RU'
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 3

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        for (let j = 0; j < result.length; j++) {
          const transcript = result[j].transcript.toLowerCase().trim()
          if (WAKE_WORDS.some((w) => transcript.includes(w))) {
            onActivated()
            return
          }
        }
      }
    }

    recognition.onend = () => {
      // Перезапускаем если ещё активны
      if (activeRef.current) {
        try { recognition.start() } catch { /* уже запущен */ }
      }
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === 'not-allowed') {
        console.warn('[useWakeWord] Доступ к микрофону запрещён')
        activeRef.current = false
      }
    }

    recognitionRef.current = recognition
    activeRef.current = true
    try { recognition.start() } catch { /* уже запущен */ }
  }, [onActivated])

  const stop = useCallback(() => {
    activeRef.current = false
    recognitionRef.current?.stop()
    recognitionRef.current = null
  }, [])

  useEffect(() => {
    if (enabled) {
      start()
    } else {
      stop()
    }
    return stop
  }, [enabled, start, stop])
}
