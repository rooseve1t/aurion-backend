import { useEffect, useRef, useState } from 'react'
import { Send, Wifi, WifiOff, Trash2 } from 'lucide-react'
import { StatBar } from '@/components/StatBar'
import { CoreOrb } from '@/components/CoreOrb'
import { useChatStore } from '@/store/chatStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { formatDate } from '@/utils'

export default function DashboardPage() {
  const { messages, isTyping, wsConnected, sendMessage, loadHistory, clear } = useChatStore()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  useWebSocket()

  useEffect(() => { loadHistory() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, isTyping])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text) return
    sendMessage(text)
    setInput('')
  }

  return (
    <div className="flex flex-col h-full">
      <StatBar />

      <div className="flex-1 flex overflow-hidden">
        {/* Left panel */}
        <aside className="hidden lg:flex flex-col w-52 border-r border-cyan/10 p-3 gap-4 bg-card/20">
          <div className="text-[10px] text-cyan/40 tracking-widest font-bold">СИСТЕМА</div>
          <div className="flex justify-center">
            <CoreOrb size={72} />
          </div>
          <div className="space-y-2">
            {[
              { label: 'Сессия', value: 'АКТИВНА', color: 'text-emerald' },
              { label: 'Модель', value: 'CLAUDE-4', color: 'text-cyan' },
              { label: 'Контекст', value: `${messages.length} msg`, color: 'text-purple' },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-[10px]">
                <span className="text-white/30">{item.label}</span>
                <span className={item.color}>{item.value}</span>
              </div>
            ))}
          </div>
        </aside>

        {/* Chat center */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-cyan/10">
            <div className="flex items-center gap-2">
              {wsConnected
                ? <Wifi size={14} className="text-emerald" />
                : <WifiOff size={14} className="text-danger" />}
              <span className="text-[10px] text-white/40 tracking-wider">
                {wsConnected ? 'КАНАЛ АКТИВЕН' : 'ПЕРЕПОДКЛЮЧЕНИЕ...'}
              </span>
            </div>
            <button onClick={clear} className="text-white/20 hover:text-white/60 transition-colors">
              <Trash2 size={14} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-white/20">
                <CoreOrb size={60} pulse={false} />
                <p className="text-xs tracking-widest">НАЧНИТЕ ДИАЛОГ</p>
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div className={`
                  max-w-[75%] rounded px-4 py-2.5 text-sm leading-relaxed
                  ${msg.role === 'user'
                    ? 'bg-cyan/10 border border-cyan/25 text-white'
                    : 'bg-card border border-white/10 text-white/85'}
                `}>
                  {msg.role === 'assistant' && (
                    <div className="text-[9px] text-cyan/50 mb-1 tracking-widest">AURION</div>
                  )}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  <div className="text-[9px] text-white/20 mt-1">{formatDate(msg.timestamp)}</div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-card border border-cyan/20 rounded px-4 py-2.5">
                  <div className="text-[9px] text-cyan/50 mb-1 tracking-widest">AURION</div>
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <span key={i} className="w-1 h-1 bg-cyan rounded-full animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="flex gap-2 p-4 border-t border-cyan/10">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Введите сообщение..."
              className="flex-1 bg-surface border border-cyan/20 rounded px-4 py-2.5 text-sm text-white placeholder-white/25 focus:outline-none focus:border-cyan/50 transition-all"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="px-4 py-2.5 bg-cyan/10 hover:bg-cyan/20 border border-cyan/40 text-cyan rounded transition-all disabled:opacity-30"
            >
              <Send size={16} />
            </button>
          </form>
        </div>

        {/* Right panel — Activity */}
        <aside className="hidden xl:flex flex-col w-52 border-l border-cyan/10 p-3 gap-3 bg-card/20">
          <div className="text-[10px] text-cyan/40 tracking-widest font-bold">АКТИВНОСТЬ</div>
          <div className="space-y-2 flex-1 overflow-y-auto">
            {messages.slice(-5).reverse().map((m) => (
              <div key={m.id} className="text-[10px] text-white/30 border-l-2 border-cyan/20 pl-2 py-0.5">
                <span className={m.role === 'user' ? 'text-cyan/60' : 'text-purple/60'}>
                  {m.role === 'user' ? 'ВЫ' : 'AI'}
                </span>
                {' '}{m.content.slice(0, 40)}{m.content.length > 40 ? '...' : ''}
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  )
}
