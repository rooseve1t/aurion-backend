import type { ChatMessage } from '@/types'

type WSHandler = (msg: ChatMessage) => void
type StatusHandler = (s: 'connected' | 'disconnected' | 'error') => void

function normalizeWsBase(rawBase?: string): string {
  const trimmed = rawBase?.trim().replace(/\/+$/, '')
  if (trimmed) return trimmed

  const apiBase = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, '')
  if (apiBase?.startsWith('https://')) return apiBase.replace(/^https:\/\//, 'wss://').replace(/\/api(?:\/v1)?$/, '')
  if (apiBase?.startsWith('http://')) return apiBase.replace(/^http:\/\//, 'ws://').replace(/\/api(?:\/v1)?$/, '')

  return `ws://${window.location.host}`
}

class VoiceSocket {
  private ws: WebSocket | null = null
  private onMsg: WSHandler | null = null
  private onStatus: StatusHandler | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private manualClose = false

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
        const data = JSON.parse(e.data)
        if (data.content) {
          onMessage({
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date().toISOString(),
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
  }
}

export const voiceSocket = new VoiceSocket()
