import { useEffect, useRef } from 'react'
import { Send, Wifi, WifiOff } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useSystemStore } from '@/store/systemStore'
import { useChatStore } from '@/store/chatStore'
import { StatBar } from '@/components/StatBar/StatBar'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import { formatDate } from '@/utils'
import styles from './DashboardPage.module.css'

export function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const stats = useSystemStore((s) => s.stats)
  const { messages, isConnected, isTyping, sendMessage, loadHistory, connect, disconnect } = useChatStore()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    connect()
    loadHistory()
    return () => disconnect()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return
    sendMessage(input.trim())
    setInput('')
  }

  return (
    <div className={styles.page}>
      <StatBar stats={stats} />

      <div className={styles.body}>
        {/* ─── Left: System status ─── */}
        <aside className={styles.left}>
          <div className={styles.panel}>
            <div className={styles.panelTitle}>СТАТУС СИСТЕМЫ</div>
            <div className={styles.orbArea}>
              <CoreOrb size={80} active={isConnected} />
              <div className={styles.statusInfo}>
                <span className={styles.greeting}>
                  AURION ONLINE
                </span>
                <span className={styles.tier}>
                  {stats?.subscription_tier?.toUpperCase() || 'FREE'}
                </span>
              </div>
            </div>
          </div>

          <div className={styles.panel}>
            <div className={styles.panelTitle}>ПОКАЗАТЕЛИ</div>
            <div className={styles.metricList}>
              <Metric label="АПТАЙМ"     value={`${stats?.uptime_hours || 0}ч`} />
              <Metric label="УСТРОЙСТВА" value={String(stats?.devices_online || 0)} />
              <Metric label="ЗАПИСЕЙ"    value={String(stats?.memory_entries || 0)} />
              <Metric label="ЗАДАЧ"      value={String(stats?.active_tasks || 0)} />
            </div>
          </div>

          <div className={styles.panel}>
            <div className={styles.panelTitle}>КВАНТОВЫЙ МОДУЛЬ</div>
            <div className={`${styles.qStatus} ${stats?.quantum_status === 'online' ? styles.qOnline : ''}`}>
              ● {stats?.quantum_status?.toUpperCase() || 'OFFLINE'}
            </div>
          </div>
        </aside>

        {/* ─── Center: Chat ─── */}
        <main className={styles.chat}>
          <div className={styles.chatHeader}>
            <span>ЧАТ С AURION</span>
            <span className={`${styles.wsStatus} ${isConnected ? styles.wsOn : ''}`}>
              {isConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
              {isConnected ? 'ПОДКЛЮЧЁН' : 'ОТКЛ'}
            </span>
          </div>

          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={styles.emptyChat}>
                <CoreOrb size={48} />
                <p>Привет, {user?.username}. Чем могу помочь?</p>
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`${styles.message} ${msg.role === 'user' ? styles.userMsg : styles.assistantMsg}`}
              >
                <div className={styles.msgBubble}>{msg.content}</div>
                <div className={styles.msgTime}>{formatDate(msg.timestamp)}</div>
              </div>
            ))}
            {isTyping && (
              <div className={`${styles.message} ${styles.assistantMsg}`}>
                <div className={styles.msgBubble}>
                  <span className={styles.typingDot} />
                  <span className={styles.typingDot} />
                  <span className={styles.typingDot} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className={styles.inputRow} onSubmit={handleSend}>
            <input
              className="input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Введите сообщение..."
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn btn-cyan" disabled={!input.trim()}>
              <Send size={14} />
            </button>
          </form>
        </main>

        {/* ─── Right: Activity ─── */}
        <aside className={styles.right}>
          <div className={styles.panel}>
            <div className={styles.panelTitle}>БЫСТРЫЕ КОМАНДЫ</div>
            <div className={styles.quickCmds}>
              {['Что нового?', 'Статус устройств', 'Оптимизировать дом', 'Показать задачи'].map((cmd) => (
                <button key={cmd} className="btn btn-ghost"
                  style={{ width: '100%', justifyContent: 'flex-start', fontSize: '11px' }}
                  onClick={() => sendMessage(cmd)}>
                  &gt; {cmd}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.panel}>
            <div className={styles.panelTitle}>СТАТИСТИКА</div>
            <div className={styles.statGrid}>
              <StatCell label="Сообщений" value={messages.length} />
              <StatCell label="Память" value={stats?.memory_entries || 0} />
              <StatCell label="Дом" value={stats?.devices_online || 0} />
              <StatCell label="Задачи" value={stats?.active_tasks || 0} />
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0',
      borderBottom: '1px solid var(--border)', fontSize: '12px' }}>
      <span style={{ color: 'var(--text-muted)', letterSpacing: '0.5px' }}>{label}</span>
      <span style={{ color: 'var(--cyan)' }}>{value}</span>
    </div>
  )
}

function StatCell({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ textAlign: 'center', padding: '8px' }}>
      <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--cyan)' }}>{value}</div>
      <div style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '1px' }}>{label}</div>
    </div>
  )
}
