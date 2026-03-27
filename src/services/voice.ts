import { api } from './api'
import { browserVoice } from './browserVoice'
import type { ChatMessage, VoicePersona, WsMessage } from '@/types'

type WSHandler = (msg: ChatMessage) => void
type StatusHandler = (s: 'connected' | 'disconnected' | 'error') => void

interface VoicePreviewResponse {
  text: string
  emotion: string
  voice_persona: VoicePersona
  tts: {
    provider: string
    audio_b64?: string
    mime_type?: string
    emotion?: string
    persona?: string
    note?: string
  }
}

function normalizeWsBase(rawBase?: string): string {
  const trimmed = rawBase?.trim().replace(/\/+$/, '')
  if (trimmed) return trimmed

  const apiBase = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, '')
  if (apiBase?.startsWith('https://')) return apiBase.replace(/^https:\/\//, 'wss://').replace(/\/api(?:\/v1)?$/, '')
  if (apiBase?.startsWith('http://')) return apiBase.replace(/^http:\/\//, 'ws://').replace(/\/api(?:\/v1)?$/, '')

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${wsProtocol}//${window.location.host}`
}

class VoiceSocket {
  private ws: WebSocket | null = null
  private onMsg: WSHandler | null = null
  private onStatus: StatusHandler | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private manualClose = false
  private audioPlayer: HTMLAudioElement | null = null

  private playTts(tts: WsMessage['tts'] | VoicePreviewResponse['tts'] | undefined, text: string, persona: VoicePersona = 'calm'): void {
    const ttsAudioB64 = tts?.audio_b64
    const ttsMimeType = tts?.mime_type || 'audio/ogg'

    if (ttsAudioB64) {
      const src = `data:${ttsMimeType};base64,${ttsAudioB64}`
      if (!this.audioPlayer) this.audioPlayer = new Audio()
      this.audioPlayer.pause()
      this.audioPlayer.src = src
      this.audioPlayer.play().catch(() => {
        browserVoice.speakFallback(text, persona)
      })
      return
    }

    browserVoice.speakFallback(text, persona)
  }

  connect(onMessage: WSHandler, onStatus: StatusHandler): void {
    this.onMsg = onMessage
    this.onStatus = onStatus
    const token = localStorage.getItem('access_token')
    if (!token) {
      onStatus('error')
      return
    }
    this.manualClose = false
    const wsBase = normalizeWsBase(import.meta.env.VITE_WS_URL)
    this.ws = new WebSocket(`${wsBase}/api/v1/voice/ws?token=${token}`)

    this.ws.onopen = () => onStatus('connected')
    this.ws.onclose = () => {
      onStatus('disconnected')
      if (this.manualClose) return
      this.reconnectTimer = setTimeout(() => this.connect(onMessage, onStatus), 5000)
    }
    this.ws.onerror = () => onStatus('error')
    this.ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as WsMessage
        if (data.content) {
          const persona = data?.voice_persona || 'calm'
          this.playTts(data?.tts, data.content, persona)
          onMessage({
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date().toISOString(),
            emotion: data?.emotion,
            voice_persona: persona,
            tts_audio_b64: data?.tts?.audio_b64,
            tts_provider: data?.tts?.provider,
            tts_mime_type: data?.tts?.mime_type || 'audio/ogg',
          })
        }
      } catch {/* ignore */ }
    }
  }

  send(text: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'text', content: text }))
    }
  }

  disconnect(): void {
    this.manualClose = true
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
    this.audioPlayer = null
  }

  async preview(text: string, persona: VoicePersona): Promise<VoicePreviewResponse> {
    const { data } = await api.post<VoicePreviewResponse>('/voice/preview', { text, persona })
    this.playTts(data.tts, data.text, data.voice_persona)
    return data
  }
}

export const voiceSocket = new VoiceSocket()
