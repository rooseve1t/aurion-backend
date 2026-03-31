import axios from 'axios'
import type { FeedCard, FeedPage } from '@/types/feed'

// Отдельный axios-инстанс для v2 API
const apiV2 = axios.create({
  baseURL: '/api/v2',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

apiV2.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const PAGE_SIZE = 20

export async function getFeed(page = 0): Promise<FeedPage> {
  const { data } = await apiV2.get<{ items: FeedCard[]; total: number }>('/feed', {
    params: { page, limit: PAGE_SIZE },
  })
  return {
    items: data.items,
    page,
    hasMore: data.items.length === PAGE_SIZE,
  }
}

export async function confirmCard(id: string): Promise<void> {
  await apiV2.post(`/feed/${id}/confirm`)
}

export async function dismissCard(id: string): Promise<void> {
  await apiV2.post(`/feed/${id}/dismiss`)
}

export function connectFeedWebSocket(onCard: (card: FeedCard) => void): () => void {
  const token = localStorage.getItem('access_token')
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/api/v2/feed/ws${token ? `?token=${token}` : ''}`

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectDelay = 2000
  let closed = false

  function connect() {
    if (closed) return
    ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'feed_card' && data.card) {
          onCard(data.card as FeedCard)
        }
      } catch {
        // игнорируем невалидные сообщения
      }
    }

    ws.onclose = () => {
      if (closed) return
      reconnectTimer = setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)
        connect()
      }, reconnectDelay)
    }

    ws.onerror = () => ws?.close()
  }

  connect()

  return () => {
    closed = true
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
  }
}

// Утилиты для property-тестов
export function paginateFeed(cards: FeedCard[], page: number, pageSize = PAGE_SIZE): FeedCard[] {
  const start = page * pageSize
  return cards.slice(start, start + pageSize)
}

export function sortFeedCards(cards: FeedCard[]): FeedCard[] {
  return [...cards].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
}
