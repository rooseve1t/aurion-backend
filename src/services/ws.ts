import type { WsMessage } from '@/types'

function normalizeWsBase(rawBase?: string): string {
  const trimmed = rawBase?.trim().replace(/\/+$/, '')
  if (trimmed) return trimmed.replace(/\/api(?:\/v1)?$/, '')

  const apiBase = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, '')
  if (apiBase?.startsWith('https://')) return apiBase.replace(/^https:\/\//, 'wss://').replace(/\/api(?:\/v1)?$/, '')
  if (apiBase?.startsWith('http://')) return apiBase.replace(/^http:\/\//, 'ws://').replace(/\/api(?:\/v1)?$/, '')

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${wsProtocol}//${window.location.host}`
}

const WS_BASE = normalizeWsBase(import.meta.env.VITE_WS_URL)

type MessageHandler = (msg: WsMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private handlers: MessageHandler[] = []
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectDelay = 2000

  connect(token: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) return
    this.ws = new WebSocket(`${WS_BASE}/api/v1/voice/ws?token=${token}`)

    this.ws.onopen = () => {
      console.log('[WS] Connected')
      this.reconnectDelay = 2000
    }

    this.ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data)
        this.handlers.forEach((h) => h(msg))
      } catch {}
    }

    this.ws.onclose = () => {
      console.log('[WS] Disconnected — reconnect in', this.reconnectDelay, 'ms')
      this.reconnectTimer = setTimeout(() => {
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000)
        this.connect(token)
      }, this.reconnectDelay)
    }

    this.ws.onerror = (e) => console.error('[WS] Error', e)
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }

  send(data: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  onMessage(handler: MessageHandler): () => void {
    this.handlers.push(handler)
    return () => { this.handlers = this.handlers.filter((h) => h !== handler) }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
