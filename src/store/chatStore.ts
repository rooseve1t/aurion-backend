import { create } from 'zustand'
import type { ChatMessage } from '@/types'
import { memoryService } from '@/services/memory'
import { voiceSocket } from '@/services/voice'

interface ChatState {
  messages: ChatMessage[]
  isConnected: boolean
  isTyping: boolean
  addMessage: (m: ChatMessage) => void
  sendMessage: (text: string) => void
  loadHistory: () => Promise<void>
  setConnected: (v: boolean) => void
  setTyping: (v: boolean) => void
  connect: () => void
  disconnect: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isConnected: false,
  isTyping: false,

  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  setConnected: (v) => set({ isConnected: v }),
  setTyping: (v) => set({ isTyping: v }),

  sendMessage: (text) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    get().addMessage(userMsg)
    set({ isTyping: true })
    voiceSocket.send(text)
    // Save to memory
    memoryService.create(text, 5, ['chat']).catch(() => {})
  },

  loadHistory: async () => {
    try {
      const entries = await memoryService.search('', 30)
      const msgs: ChatMessage[] = entries.map((e) => ({
        id: String(e.id),
        role: 'user' as const,
        content: e.content,
        timestamp: e.created_at,
      }))
      set({ messages: msgs })
    } catch {/* empty session */ }
  },

  connect: () => {
    voiceSocket.connect(
      (msg) => {
        get().addMessage(msg)
        set({ isTyping: false })
      },
      (status) => {
        set({ isConnected: status === 'connected' })
      }
    )
  },

  disconnect: () => voiceSocket.disconnect(),
}))
