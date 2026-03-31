import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './LandingPage.css'

// Современная Landing Page с анимациями
export function LandingPage() {
  const [scrolled, setScrolled] = useState(false)
  const [animated, setAnimated] = useState(false)

  // Отслеживание скролла для шапки
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    
    // Запуск анимаций после загрузки
    setTimeout(() => setAnimated(true), 100)
    
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="landing-page">
      {/* Шапка */}
      <header className={`landing-header ${scrolled ? 'scrolled' : ''}`}>
        <div className="header-logo">
          <div className="logo-icon">A</div>
          <span>Aurion OS</span>
        </div>
        <nav className="header-nav">
          <a href="#features">Возможности</a>
          <a href="#jarvis">JARVIS</a>
          <a href="#security">Безопасность</a>
        </nav>
        <div className="header-actions">
          <Link to="/auth" className="btn-login">Войти</Link>
          <Link to="/auth" className="btn-primary">Начать</Link>
        </div>
      </header>

      {/* Герой-секция */}
      <section className="hero-section">
        <div className="hero-background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
        </div>
        
        <div className={`hero-content ${animated ? 'animated' : ''}`}>
          <div className="hero-badge">
            <span className="badge-dot"></span>
            Бета-версия 2.0
          </div>
          
          <h1 className="hero-title">
            Ваш персональный
            <span className="gradient-text"> AI-ассистент</span>
          </h1>
          
          <p className="hero-description">
            Aurion OS — это операционная система с искусственным интеллектом 
            нового поколения. Голосовое управление, автономность и полная 
            безопасность ваших данных.
          </p>
          
          <div className="hero-actions">
            <Link to="/auth" className="btn-hero-primary">
              Попробовать бесплатно
              <span className="btn-arrow">→</span>
            </Link>
            <a href="#demo" className="btn-hero-secondary">
              Смотреть демо
            </a>
          </div>
          
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">50K+</span>
              <span className="stat-label">Пользователей</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">99.9%</span>
              <span className="stat-label">Uptime</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">4.9</span>
              <span className="stat-label">Рейтинг</span>
            </div>
          </div>
        </div>

        {/* Визуализация JARVIS */}
        <div className={`hero-visual ${animated ? 'animated' : ''}`}>
          <div className="jarvis-core">
            <div className="core-ring ring-1"></div>
            <div className="core-ring ring-2"></div>
            <div className="core-ring ring-3"></div>
            <div className="core-center">
              <span>J</span>
            </div>
          </div>
          <div className="visual-glow"></div>
        </div>
      </section>

      {/* Секция возможностей */}
      <section id="features" className="features-section">
        <div className="section-header">
          <h2>Возможности системы</h2>
          <p>Всё, что нужно для управления вашей цифровой жизнью</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>JARVIS AI</h3>
            <p>Персональный ассистент с эмоциональным интеллектом и автономностью</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🛡️</div>
            <h3>VPN & Защита</h3>
            <p>Встроенный VPN и квантовое шифрование данных</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">💰</div>
            <h3>Криптокошелек</h3>
            <p>Управление криптовалютами и безопасные переводы</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>Векторная память</h3>
            <p>Семантический поиск и хранение воспоминаний</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔊</div>
            <h3>Голосовое управление</h3>
            <p>Управление системой голосом без касания экрана</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🏠</div>
            <h3>Умный дом</h3>
            <p>Интеграция с IoT устройствами и автоматизация</p>
          </div>
        </div>
      </section>

      {/* Секция JARVIS */}
      <section id="jarvis" className="jarvis-section">
        <div className="jarvis-content">
          <h2>Познакомьтесь с JARVIS</h2>
          <p className="jarvis-subtitle">
            Искусственный интеллект, который понимает эмоции и действует автономно
          </p>
          
          <div className="jarvis-features">
            <div className="jarvis-feature">
              <div className="jf-icon">😊</div>
              <h4>Эмоциональный интеллект</h4>
              <p>Распознает настроение и адаптирует поведение</p>
            </div>
            <div className="jarvis-feature">
              <div className="jf-icon">🎯</div>
              <h4>Автономность</h4>
              <p>Принимает решения и действует без команды</p>
            </div>
            <div className="jarvis-feature">
              <div className="jf-icon">🧠</div>
              <h4>Самообучение</h4>
              <p>Улучшается с каждым разговором</p>
            </div>
          </div>
        </div>
      </section>

      {/* Секция безопасности */}
      <section id="security" className="security-section">
        <div className="security-content">
          <h2>Безопасность превыше всего</h2>
          <p>Ваши данные защищены на уровне военных технологий</p>
          
          <div className="security-grid">
            <div className="security-item">
              <span className="security-check">✓</span>
              <span>AES-256 шифрование</span>
            </div>
            <div className="security-item">
              <span className="security-check">✓</span>
              <span>Квантовая криптография</span>
            </div>
            <div className="security-item">
              <span className="security-check">✓</span>
              <span>Двухфакторная аутентификация</span>
            </div>
            <div className="security-item">
              <span className="security-check">✓</span>
              <span>Локальное хранение данных</span>
            </div>
          </div>
        </div>
      </section>

      {/* Футер */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">A</div>
            <span>Aurion OS</span>
          </div>
          <p className="footer-copy">© 2024 Aurion OS. Все права защищены.</p>
          <div className="footer-links">
            <a href="#">Политика конфиденциальности</a>
            <a href="#">Условия использования</a>
            <a href="#">Поддержка</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
