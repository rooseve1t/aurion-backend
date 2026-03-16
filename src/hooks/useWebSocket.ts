import { useEffect } from 'react'
import { wsService } from '@/services/ws'
import { useChatStore } from '@/store/chatStore'
import type { WsMessage } from '@/types'
import toast from 'react-hot-toast'

export function useWebSocket() {
  const { addMessage, setTyping, setWsConnected } = useChatStore()

  useEffect(() => {
    const unsub = wsService.onMessage((msg: WsMessage) => {
      if (msg.type === 'chat_response' && msg.content) {
        addMessage('assistant', msg.content)
        setTyping(false)
      }
      if (msg.type === 'agent_task_update') {
        const status = msg.status === 'completed' ? '✅' : msg.status === 'failed' ? '❌' : '⏳'
        toast(`${status} Задача #${msg.task_id}: ${msg.status}`, { duration: 4000 })
      }
      if (msg.type === 'error') {
        setTyping(false)
        toast.error(msg.content ?? 'Ошибка WebSocket')
      }
    })

    setWsConnected(wsService.isConnected)
    const timer = setInterval(() => setWsConnected(wsService.isConnected), 3000)

    return () => {
      unsub()
      clearInterval(timer)
    }
  }, [addMessage, setTyping, setWsConnected])
}
