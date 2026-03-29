import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'

// Базовый компонент печатания
interface TypingTextProps {
  text: string
  speed?: number
  delay?: number
  onComplete?: () => void
  showCursor?: boolean
  className?: string
  variant?: 'default' | 'glow' | 'neon' | 'matrix'
}

export function TypingText({ 
  text, 
  speed = 50, 
  delay = 0, 
  onComplete, 
  showCursor = true,
  className = '',
  variant = 'default'
}: TypingTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showCursorState, setShowCursorState] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsTyping(true)
      setDisplayedText('')
      
      let index = 0
      const typeInterval = setInterval(() => {
        if (index < text.length) {
          setDisplayedText(prev => prev + text[index])
          index++
        } else {
          clearInterval(typeInterval)
          setIsTyping(false)
          onComplete?.()
        }
      }, speed)

      return () => clearInterval(typeInterval)
    }, delay)

    return () => clearTimeout(timer)
  }, [text, speed, delay, onComplete])

  // Cursor blink effect
  useEffect(() => {
    if (!showCursor || !isTyping) return
    
    const cursorInterval = setInterval(() => {
      setShowCursorState(prev => !prev)
    }, 500)

    return () => clearInterval(cursorInterval)
  }, [showCursor, isTyping])

  const variantClasses = {
    default: 'aurion-typing-default',
    glow: 'aurion-typing-glow',
    neon: 'aurion-typing-neon',
    matrix: 'aurion-typing-matrix'
  }

  return (
    <span className={`${variantClasses[variant]} ${className}`}>
      {displayedText}
      {showCursor && isTyping && (
        <span className={`aurion-typing-cursor ${showCursorState ? 'opacity-100' : 'opacity-0'}`}>|</span>
      )}
    </span>
  )
}

// Эффект печатания с удалением (delete & retype)
interface TypingLoopProps {
  texts: string[]
  speed?: number
  deleteSpeed?: number
  pauseDuration?: number
  className?: string
}

export function TypingLoop({ 
  texts, 
  speed = 100, 
  deleteSpeed = 50, 
  pauseDuration = 2000,
  className = ''
}: TypingLoopProps) {
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
  const [displayedText, setDisplayedText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    const currentText = texts[currentTextIndex]
    
    if (isPaused) {
      const pauseTimer = setTimeout(() => {
        setIsPaused(false)
        setIsDeleting(true)
      }, pauseDuration)
      return () => clearTimeout(pauseTimer)
    }

    if (isDeleting) {
      if (displayedText.length > 0) {
        const deleteTimer = setTimeout(() => {
          setDisplayedText(prev => prev.slice(0, -1))
        }, deleteSpeed)
        return () => clearTimeout(deleteTimer)
      } else {
        setIsDeleting(false)
        setCurrentTextIndex((prev) => (prev + 1) % texts.length)
      }
    } else {
      if (displayedText.length < currentText.length) {
        const typeTimer = setTimeout(() => {
          setDisplayedText(prev => prev + currentText[displayedText.length])
        }, speed)
        return () => clearTimeout(typeTimer)
      } else {
        setIsPaused(true)
      }
    }
  }, [displayedText, isDeleting, isPaused, currentTextIndex, texts, speed, deleteSpeed, pauseDuration])

  return (
    <span className={className}>
      {displayedText}
      <span className="aurion-typing-cursor opacity-100">|</span>
    </span>
  )
}

// Индикатор печатания (typing indicator)
interface TypingIndicatorProps {
  users?: string[]
  showText?: boolean
  variant?: 'dots' | 'pulse' | 'wave' | 'bounce'
  size?: 'sm' | 'md' | 'lg'
  color?: string
}

export function TypingIndicator({ 
  users = [], 
  showText = true, 
  variant = 'dots',
  size = 'md',
  color = 'var(--aurion-cyan)'
}: TypingIndicatorProps) {
  const [dots, setDots] = useState([false, false, false])
  const [waveOffset, setWaveOffset] = useState(0)

  useEffect(() => {
    if (variant === 'dots') {
      const interval = setInterval(() => {
        setDots(prev => {
          const next = [...prev]
          const activeIndex = prev.findIndex(d => d)
          if (activeIndex === -1) {
            next[0] = true
          } else if (activeIndex === prev.length - 1) {
            next[activeIndex] = false
          } else {
            next[activeIndex] = false
            next[activeIndex + 1] = true
          }
          return next
        })
      }, 200)
      return () => clearInterval(interval)
    } else if (variant === 'wave') {
      const interval = setInterval(() => {
        setWaveOffset(prev => (prev + 1) % 3)
      }, 150)
      return () => clearInterval(interval)
    }
  }, [variant])

  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-3 h-3'
  }

  const renderDots = () => {
    switch (variant) {
      case 'dots':
        return (
          <div className="flex gap-1">
            {dots.map((active, i) => (
              <div
                key={i}
                className={`${sizeClasses[size]} rounded-full transition-all duration-200 ${
                  active ? 'opacity-100 scale-100' : 'opacity-30 scale-75'
                }`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        )
      
      case 'pulse':
        return (
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`${sizeClasses[size]} rounded-full aurion-pulse`}
                style={{ 
                  backgroundColor: color,
                  animationDelay: `${i * 0.2}s`
                }}
              />
            ))}
          </div>
        )
      
      case 'wave':
        return (
          <div className="flex gap-1 items-end">
            {[0, 1, 2].map((i) => {
              const offset = (i + waveOffset) % 3
              const height = offset === 0 ? '100%' : offset === 1 ? '60%' : '30%'
              return (
                <div
                  key={i}
                  className={`${sizeClasses[size]} rounded-full transition-all duration-150`}
                  style={{ 
                    backgroundColor: color,
                    height: size === 'sm' ? (offset === 0 ? '6px' : offset === 1 ? '4px' : '2px') :
                           size === 'md' ? (offset === 0 ? '8px' : offset === 1 ? '5px' : '3px') :
                           (offset === 0 ? '12px' : offset === 1 ? '7px' : '4px')
                  }}
                />
              )
            })}
          </div>
        )
      
      case 'bounce':
        return (
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`${sizeClasses[size]} rounded-full aurion-bounce`}
                style={{ 
                  backgroundColor: color,
                  animationDelay: `${i * 0.1}s`
                }}
              />
            ))}
          </div>
        )
      
      default:
        return null
    }
  }

  const getUserText = () => {
    if (users.length === 0) return 'Кто-то печатает'
    if (users.length === 1) return `${users[0]} печатает`
    if (users.length === 2) return `${users[0]} и ${users[1]} печатают`
    return `${users.length} человека печатают`
  }

  return (
    <div className="flex items-center gap-2">
      {renderDots()}
      {showText && (
        <span className="aurion-mono text-xs text-[var(--aurion-text-muted)]">
          {getUserText()}
        </span>
      )}
    </div>
  )
}

// Сообщение с эффектом печатания
interface TypingMessageProps {
  message: string
  isOwn?: boolean
  sender?: string
  avatar?: React.ReactNode
  timestamp?: string
  typingSpeed?: number
  onComplete?: () => void
  showTypingIndicator?: boolean
}

export function TypingMessage({ 
  message, 
  isOwn = false, 
  sender, 
  avatar, 
  timestamp,
  typingSpeed = 30,
  onComplete,
  showTypingIndicator = true
}: TypingMessageProps) {
  const [isTyping, setIsTyping] = useState(true)
  const [showIndicator, setShowIndicator] = useState(true)

  const handleTypingComplete = () => {
    setIsTyping(false)
    setShowIndicator(false)
    onComplete?.()
  }

  return (
    <div className={`flex gap-3 mb-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
      {avatar && (
        <div className="flex-shrink-0">
          {avatar}
        </div>
      )}
      
      <div className={`flex-1 max-w-[70%] ${isOwn ? 'text-right' : ''}`}>
        {sender && !isOwn && (
          <p className="aurion-mono text-xs text-[var(--aurion-text-muted)] mb-1">
            {sender}
          </p>
        )}
        
        <div className={`aurion-card p-3 ${isOwn ? 'aurion-card-reverse' : ''} relative`}>
          {showIndicator && isTyping && (
            <div className="absolute bottom-2 left-3">
              <TypingIndicator variant="dots" size="sm" showText={false} />
            </div>
          )}
          
          <p className="text-sm leading-relaxed">
            <TypingText 
              text={message} 
              speed={typingSpeed}
              onComplete={handleTypingComplete}
              showCursor={isTyping}
              variant="neon"
            />
          </p>
        </div>
        
        {timestamp && (
          <p className="aurion-mono text-[10px] text-[var(--aurion-text-muted)] mt-1">
            {timestamp}
          </p>
        )}
      </div>
    </div>
  )
}

// Чат с эффектами печатания
interface TypingChatProps {
  messages: Array<{
    id: string
    text: string
    isOwn: boolean
    sender?: string
    timestamp?: string
  }>
  onSendMessage?: (message: string) => void
  isTyping?: boolean
  typingUsers?: string[]
  className?: string
}

export function TypingChat({ 
  messages, 
  onSendMessage, 
  isTyping = false, 
  typingUsers = [],
  className = ''
}: TypingChatProps) {
  const [inputValue, setInputValue] = useState('')
  const [isSending, setIsSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim() || isSending) return
    
    setIsSending(true)
    await onSendMessage?.(inputValue)
    setInputValue('')
    setIsSending(false)
  }

  return (
    <div className={`aurion-card flex flex-col h-full ${className}`}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <TypingMessage
            key={message.id}
            message={message.text}
            isOwn={message.isOwn}
            sender={message.sender}
            avatar={
              message.isOwn ? (
                <div className="w-8 h-8 rounded-full bg-[var(--aurion-cyan)]/20 border border-[var(--aurion-cyan)]/50 flex items-center justify-center">
                  <User size={16} className="text-[var(--aurion-cyan)]" />
                </div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-[var(--aurion-purple)]/20 border border-[var(--aurion-purple)]/50 flex items-center justify-center">
                  <Bot size={16} className="text-[var(--aurion-purple)]" />
                </div>
              )
            }
            timestamp={message.timestamp}
            typingSpeed={20}
          />
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-[var(--aurion-purple)]/20 border border-[var(--aurion-purple)]/50 flex items-center justify-center">
              <Bot size={16} className="text-[var(--aurion-purple)]" />
            </div>
            <div className="aurion-card p-3 max-w-[70%]">
              <TypingIndicator 
                users={typingUsers} 
                variant="wave" 
                size="sm"
                color="var(--aurion-purple)"
              />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[var(--aurion-text-dim)]/15">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Введите сообщение..."
            className="aurion-input flex-1"
            disabled={isSending}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isSending}
            className="aurion-btn aurion-btn-primary px-4 py-2"
          >
            {isSending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

// Печатание с матричным эффектом
interface MatrixTypingProps {
  text: string
  speed?: number
  className?: string
}

export function MatrixTyping({ text, speed = 100, className = '' }: MatrixTypingProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [matrixChars, setMatrixChars] = useState('')

  useEffect(() => {
    let index = 0
    const matrixInterval = setInterval(() => {
      if (index < text.length) {
        // Add random matrix characters
        const randomChar = String.fromCharCode(33 + Math.floor(Math.random() * 94))
        setMatrixChars(prev => prev + randomChar)
        
        setTimeout(() => {
          setDisplayedText(prev => prev + text[index])
          setMatrixChars(prev => prev.slice(0, -1))
        }, speed / 2)
        
        index++
      } else {
        clearInterval(matrixInterval)
      }
    }, speed)

    return () => clearInterval(matrixInterval)
  }, [text, speed])

  return (
    <span className={`aurion-typing-matrix ${className}`}>
      {displayedText}
      <span className="text-[var(--aurion-green-dim)] opacity-50">{matrixChars}</span>
      <span className="aurion-typing-cursor text-[var(--aurion-green-dim)]">_</span>
    </span>
  )
}

// Печатание с искрами (sparkle effect)
interface SparkleTypingProps {
  text: string
  speed?: number
  className?: string
}

export function SparkleTyping({ text, speed = 80, className = '' }: SparkleTypingProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [sparkles, setSparkles] = useState<Array<{id: number, x: number}>>([])

  useEffect(() => {
    let index = 0
    const typeInterval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(prev => prev + text[index])
        
        // Add sparkle effect
        setSparkles(prev => [...prev, {
          id: Date.now() + Math.random(),
          x: index
        }])
        
        // Remove sparkle after animation
        setTimeout(() => {
          setSparkles(prev => prev.slice(1))
        }, 1000)
        
        index++
      } else {
        clearInterval(typeInterval)
      }
    }, speed)

    return () => clearInterval(typeInterval)
  }, [text, speed])

  return (
    <span className={`relative inline-block ${className}`}>
      {displayedText.split('').map((char, i) => (
        <span key={i} className="relative">
          {char}
          {sparkles.some(s => s.x === i) && (
            <Sparkles 
              size={12} 
              className="absolute -top-2 -right-2 text-[var(--aurion-cyan)] aurion-pulse" 
            />
          )}
        </span>
      ))}
      <span className="aurion-typing-cursor text-[var(--aurion-cyan)]">|</span>
    </span>
  )
}

