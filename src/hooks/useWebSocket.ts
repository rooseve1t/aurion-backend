import { useEffect } from 'react'
import { useChatStore } from '@/store/chatStore'

export function useWebSocket() {
  const connect = useChatStore((s) => s.connect)
  const disconnect = useChatStore((s) => s.disconnect)

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])
}
