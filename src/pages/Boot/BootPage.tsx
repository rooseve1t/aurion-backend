import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './BootPage.css'

// Шаги загрузки системы
const STEPS = [
  'Инициализация квантового ядра...',
  'Загрузка нейронных сетей...',
  'Синхронизация векторной памяти...',
  'Проверка протоколов безопасности...',
  'Активация автономных агентов...',
  'Установка защищенного канала...',
  'Система готова к работе.',
]

export function BootPage() {
  const [step, setStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const navigate = useNavigate()

  // Анимация загрузки
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => {
        const next = s + 1
        setProgress(Math.round((next / STEPS.length) * 100))
        
        // После завершения - переход на dashboard или auth
        if (next >= STEPS.length) {
          clearInterval(interval)
          setTimeout(() => {
            const token = localStorage.getItem('access_token')
            navigate(token ? '/dashboard' : '/auth')
          }, 1000)
        }
        return next
      })
    }, 500)
    
    return () => clearInterval(interval)
  }, [navigate])

  return (
    <div className="boot-page">
      {/* Фоновые эффекты */}
      <div className="boot-background">
        <div className="boot-grid" />
        <div className="boot-orb cyan" />
        <div className="boot-orb purple" />
      </div>

      {/* Основной контент */}
      <div className="boot-content">
        {/* Логотип с анимированными кольцами */}
        <div className="boot-logo">
          <div className="logo-core">
            <div className="core-ring outer" />
            <div className="core-ring middle" />
            <div className="core-ring inner" />
            <div className="core-center">A</div>
          </div>
          <h1 className="boot-title">AURION OS</h1>
          <span className="boot-version">Версия 2.0 • Secure Boot Protocol</span>
        </div>

        {/* Лог загрузки */}
        <div className="boot-log">
          {STEPS.slice(0, step + 1).map((s, i) => (
            <div
              key={i}
              className={`log-line ${i === step ? 'active' : 'done'}`}
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <span className="log-prompt">&gt;</span>
              <span>{s}</span>
            </div>
          ))}
        </div>

        {/* Прогресс-бар */}
        <div className="boot-progress">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-text">{progress}% ЗАГРУЗКА</span>
        </div>
      </div>
    </div>
  )
}
