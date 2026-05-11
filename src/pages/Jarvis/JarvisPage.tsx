import { useState, useRef, useEffect, useCallback } from 'react'
import './JarvisPage.css'
import { JarvisHologram3D } from '@/components/Jarvis/Hologram3D'
import { voiceSocket } from '@/services/voice'
import { api } from '@/services/api'
import type { ChatMessage } from '@/types'

// Страница JARVIS ассистента
export function JarvisPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [emotion, setEmotion] = useState('neutral')
  const [evolution, setEvolution] = useState({ stage: 'seed', experience: 0, progress: 0 })
  const [metrics, setMetrics] = useState({ cpu_usage: 0, memory_usage: 0, disk_usage: 0 })
  const [traits, setTraits] = useState<Record<string, number>>({})
  const [showPersonality, setShowPersonality] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Обработка входящих сообщений от WebSocket
  const onMessage = useCallback((msg: any) => {
    if (msg.type === 'system_update') {
      setEvolution(msg.evolution)
      setMetrics(msg.status.system_metrics)
      return
    }

    const chatMsg = msg as ChatMessage
    if (chatMsg.content) {
      setMessages(prev => [...prev, chatMsg])
      setEmotion(chatMsg.emotion || 'neutral')
      setIsLoading(false)
    }
  }, [])

  const onStatus = useCallback((status: string) => {
    console.log('JARVIS Connection status:', status)
    if (status === 'error') setIsLoading(false)
  }, [])

  useEffect(() => {
    voiceSocket.connect(onMessage, onStatus)

    // Загрузка черт личности
    api.get('/jarvis/personality/traits').then(res => setTraits(res.data)).catch(console.error)

    // Подключаемся также к автономному WebSocket для метрик
    const token = localStorage.getItem('access_token')
    const user_id = 'sir' // В реальности брать из профиля
    const metricsWs = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/jarvis/autonomy/ws/${user_id}?token=${token}`)

    metricsWs.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'system_update') {
          setEvolution(data.evolution)
          setMetrics(data.status.system_metrics)
        }
      } catch (err) {
        console.error('Metrics WS error:', err)
      }
    }

    return () => {
      voiceSocket.disconnect()
      metricsWs.close()
    }
  }, [onMessage, onStatus])

  // Автопрокрутка к новым сообщениям
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Отправка сообщения
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setEmotion('processing')

    voiceSocket.send(input)
  }

  // Голосовой ввод
  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Здесь должен быть код для работы с микрофоном
  }

  const updateTrait = async (trait_id: string, value: number) => {
    try {
      await api.post('/jarvis/personality/traits/update', { trait_id, value })
      setTraits(prev => ({ ...prev, [trait_id]: value / 100 }))
    } catch (err) {
      console.error('Failed to update trait:', err)
    }
  }

  return (
    <div className="jarvis-page">
      <div className="jarvis-hero">
        <JarvisHologram3D
          emotion={emotion}
          height="350px"
        />
        <div className="jarvis-overlay">
          <h1 className="page-title">JARVIS</h1>
          <p className="page-subtitle">Aurion OS Intelligence Layer</p>

          <div className="jarvis-stats">
            <div className="stat-item">
              <span className="stat-label">STAGE</span>
              <span className="stat-value">{evolution.stage.toUpperCase()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">XP</span>
              <span className="stat-value">{evolution.experience}</span>
            </div>
            <div className="evolution-progress">
              <div className="progress-bar" style={{ width: `${evolution.progress}%` }}></div>
            </div>
          </div>

          <div className="system-metrics">
            <div className="metric-item">
              <span className="metric-label">CPU</span>
              <div className="metric-bar"><div className="fill" style={{ width: `${metrics.cpu_usage}%` }}></div></div>
            </div>
            <div className="metric-item">
              <span className="metric-label">RAM</span>
              <div className="metric-bar"><div className="fill" style={{ width: `${metrics.memory_usage}%` }}></div></div>
            </div>
          </div>

          <button
            className="personality-toggle"
            onClick={() => setShowPersonality(!showPersonality)}
          >
            {showPersonality ? 'HIDE SETTINGS' : 'PERSONALITY SETTINGS'}
          </button>
        </div>

        {showPersonality && (
          <div className="personality-panel">
            <h3 className="panel-title">CORE TRAITS</h3>
            {Object.entries(traits).map(([id, val]) => (
              <div key={id} className="trait-control">
                <div className="trait-info">
                  <span className="trait-name">{id.toUpperCase()}</span>
                  <span className="trait-value">{Math.round(val * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={val * 100}
                  onChange={(e) => updateTrait(id, parseInt(e.target.value))}
                  className="trait-slider"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Область сообщений */}
      <div className="chat-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Система активна, сэр. Ожидаю ваших указаний.</p>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content loading">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Панель ввода */}
      <div className="input-panel">
        <button 
          className={`voice-button ${isRecording ? 'recording' : ''}`}
          onClick={toggleRecording}
          title="Голосовой ввод"
        >
          🎤
        </button>
        
        <input
          type="text"
          className="message-input"
          placeholder="Введите сообщение..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        />
        
        <button 
          className="send-button"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          Отправить
        </button>
      </div>
    </div>
  )
}
