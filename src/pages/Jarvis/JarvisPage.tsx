import { useState, useRef, useEffect } from 'react'
import './JarvisPage.css'

// Страница JARVIS ассистента
export function JarvisPage() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Автопрокрутка к новым сообщениям
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Отправка сообщения
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Имитация ответа JARVIS (здесь должен быть реальный API вызов)
    setTimeout(() => {
      const jarvisResponse = {
        role: 'assistant',
        content: `Я получил ваше сообщение: "${userMessage.content}". Это демо-ответ. В реальной версии здесь будет ответ от AI.`
      }
      setMessages(prev => [...prev, jarvisResponse])
      setIsLoading(false)
    }, 1000)
  }

  // Голосовой ввод
  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Здесь должен быть код для работы с микрофоном
  }

  return (
    <div className="jarvis-page">
      <h1 className="page-title">🤖 JARVIS</h1>
      <p className="page-subtitle">Ваш персональный AI-ассистент</p>

      {/* Область сообщений */}
      <div className="chat-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="jarvis-avatar">🤖</div>
            <p>Привет! Я JARVIS, ваш персональный ассистент.</p>
            <p>Чем могу помочь?</p>
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
