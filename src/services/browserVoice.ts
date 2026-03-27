import type { VoicePersona } from '@/types'

type VoiceState = 'idle' | 'listening' | 'processing' | 'error'

interface BrowserVoiceCallbacks {
  onStateChange?: (state: VoiceState) => void
  onInterim?: (text: string) => void
  onFinal?: (text: string) => void
  onError?: (message: string) => void
}

interface SpeechRecognitionResultLike {
  readonly transcript: string
  readonly confidence: number
}

interface SpeechRecognitionAlternativeListLike {
  readonly 0: SpeechRecognitionResultLike
}

interface SpeechRecognitionEventLike extends Event {
  readonly resultIndex: number
  readonly results: ArrayLike<SpeechRecognitionAlternativeListLike & { isFinal?: boolean }>
}

interface SpeechRecognitionLike extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  onstart: ((this: SpeechRecognitionLike, ev: Event) => unknown) | null
  onend: ((this: SpeechRecognitionLike, ev: Event) => unknown) | null
  onerror: ((this: SpeechRecognitionLike, ev: Event & { error?: string }) => unknown) | null
  onresult: ((this: SpeechRecognitionLike, ev: SpeechRecognitionEventLike) => unknown) | null
  start(): void
  stop(): void
  abort(): void
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor
    webkitSpeechRecognition?: SpeechRecognitionConstructor
  }
}

const PERSONA_RATE: Record<VoicePersona, number> = {
  calm: 0.96,
  ironic: 1.02,
  sarcastic: 1.05,
  jarvis: 0.92,
}

const PERSONA_PITCH: Record<VoicePersona, number> = {
  calm: 0.98,
  ironic: 1.08,
  sarcastic: 0.94,
  jarvis: 0.82,
}

class BrowserVoiceService {
  private recognition: SpeechRecognitionLike | null = null

  isRecognitionSupported(): boolean {
    return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  }

  startRecognition(callbacks: BrowserVoiceCallbacks): boolean {
    const RecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!RecognitionCtor) {
      callbacks.onError?.('Распознавание речи не поддерживается этим браузером')
      callbacks.onStateChange?.('error')
      return false
    }

    this.stopRecognition()
    const recognition = new RecognitionCtor()
    let completedWithFinal = false
    this.recognition = recognition
    recognition.lang = 'ru-RU'
    recognition.continuous = false
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onstart = () => callbacks.onStateChange?.('listening')

    recognition.onresult = (event) => {
      let interim = ''
      let finalText = ''

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i]
        const transcript = result?.[0]?.transcript?.trim() || ''
        if (!transcript) continue
        if (result.isFinal) {
          finalText += `${transcript} `
        } else {
          interim += `${transcript} `
        }
      }

      callbacks.onInterim?.((finalText || interim).trim())

      const normalizedFinal = finalText.trim()
      if (normalizedFinal) {
        completedWithFinal = true
        callbacks.onStateChange?.('processing')
        callbacks.onFinal?.(normalizedFinal)
      }
    }

    recognition.onerror = (event) => {
      const errorCode = event.error || 'unknown'
      const message = errorCode === 'not-allowed'
        ? 'Браузер заблокировал доступ к микрофону'
        : errorCode === 'no-speech'
          ? 'Речь не распознана, попробуйте ещё раз'
          : 'Ошибка голосового ввода'
      callbacks.onError?.(message)
      callbacks.onStateChange?.('error')
    }

    recognition.onend = () => {
      if (this.recognition === recognition) {
        this.recognition = null
      }
      if (!completedWithFinal) {
        callbacks.onStateChange?.('idle')
      }
    }

    recognition.start()
    return true
  }

  stopRecognition(): void {
    if (!this.recognition) return
    this.recognition.stop()
    this.recognition = null
  }

  speakFallback(text: string, persona: VoicePersona = 'calm'): void {
    if (!('speechSynthesis' in window) || !text.trim()) return

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'ru-RU'
    utterance.rate = PERSONA_RATE[persona]
    utterance.pitch = PERSONA_PITCH[persona]
    utterance.volume = 1

    const voices = window.speechSynthesis.getVoices()
    const russianVoice = voices.find((voice) => voice.lang.toLowerCase().startsWith('ru'))
    if (russianVoice) {
      utterance.voice = russianVoice
    }

    window.speechSynthesis.speak(utterance)
  }
}

export const browserVoice = new BrowserVoiceService()
export type { VoiceState }
