import type { ChatMessage } from '@/types'

type WSHandler = (msg: ChatMessage) => void
type StatusHandler = (s: 'connected' | 'disconnected' | 'error') => void

class VoiceSocket {
  private ws: WebSocket | null = null
  private onMsg: WSHandler | null = null
  private onStatus: StatusHandler | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  connect(onMessage: WSHandler, onStatus: StatusHandler): void {
    this.onMsg = onMessage
    this.onStatus = onStatus
    const token = localStorage.getItem('access_token')
    const wsBase = import.meta.env.VITE_WS_URL || `ws://${window.location.host}`
    this.ws = new WebSocket(`${wsBase}/api/v1/voice/ws?token=${token}`)

    this.ws.onopen = () => onStatus('connected')
    this.ws.onclose = () => {
      onStatus('disconnected')
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
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }
}

export const voiceSocket = new VoiceSocket()
