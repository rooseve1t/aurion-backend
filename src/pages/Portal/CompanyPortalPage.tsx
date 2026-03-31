import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const PLANS = [
  {
    name: 'Basic',
    price: 'Бесплатно',
    features: ['Текстовый чат с JARVIS', 'Базовая память (100 записей)', 'Activity Feed'],
    accent: '#374151',
  },
  {
    name: 'Standard',
    price: '990 ₽/мес',
    features: ['Всё из Basic', 'Голосовое управление', 'Умный дом', 'Здоровье', 'Telegram-бот'],
    accent: '#00d4ff',
    highlight: true,
  },
  {
    name: 'Premium',
    price: '2 490 ₽/мес',
    features: ['Всё из Standard', 'Квантовые вычисления', 'Все интеграции здоровья', 'Память до 10 000 записей'],
    accent: '#8b5cf6',
  },
]

const PLATFORMS = [
  { label: 'iOS', icon: '🍎' },
  { label: 'Android', icon: '🤖' },
  { label: 'macOS', icon: '💻' },
  { label: 'Windows', icon: '🪟' },
  { label: 'Linux', icon: '🐧' },
]

const FEATURES = [
  { icon: '🤖', title: 'Проактивный JARVIS', desc: 'Сам инициирует диалог при важных событиях — здоровье, финансы, безопасность' },
  { icon: '🎙️', title: 'Голосовое управление', desc: 'Русскоязычный голос на базе ElevenLabs и Yandex SpeechKit' },
  { icon: '🏠', title: 'Умный дом', desc: 'Автоматическое обнаружение IoT-устройств, поддержка Matter, Zigbee, Z-Wave' },
  { icon: '❤️', title: 'Цифровой двойник', desc: 'Три уровня анализа здоровья: показатели, паттерны, рекомендации' },
  { icon: '🔒', title: 'Безопасность', desc: 'AES-256 шифрование, 2FA через Telegram, доверенные устройства' },
  { icon: '⚛️', title: 'Квантовые вычисления', desc: 'Оптимизация задач через квантовые бэкенды (Premium)' },
]

export const CompanyPortalPage: React.FC = () => {
  const [scrolled] = useState(false)

  const s: Record<string, React.CSSProperties> = {
    page: { minHeight: '100vh', background: '#0a0a0f', color: '#e0f4ff', fontFamily: 'var(--font-ui, sans-serif)' },
    header: {
      position: 'sticky',
      top: 0,
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      height: 56,
      background: scrolled ? 'rgba(10,10,15,0.95)' : 'rgba(10,10,15,0.7)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(0,212,255,0.1)',
    },
    logo: { display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: '#e0f4ff' },
    logoIcon: {
      width: 32, height: 32, borderRadius: '50%',
      background: 'linear-gradient(135deg, #00d4ff, #1e3a5f)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 14, fontWeight: 700, color: '#0a0a0f',
    },
    logoText: { fontSize: 16, fontWeight: 600, letterSpacing: '0.05em' },
    nav: { display: 'flex', gap: 24 },
    navLink: { color: 'rgba(224,244,255,0.6)', textDecoration: 'none', fontSize: 14 },
    btnPrimary: {
      background: 'linear-gradient(135deg, #00d4ff, #1e3a5f)',
      color: '#0a0a0f',
      border: 'none',
      borderRadius: 6,
      padding: '8px 20px',
      fontSize: 14,
      fontWeight: 600,
      cursor: 'pointer',
      textDecoration: 'none',
      display: 'inline-block',
    },
    btnSecondary: {
      background: 'transparent',
      color: '#00d4ff',
      border: '1px solid rgba(0,212,255,0.4)',
      borderRadius: 6,
      padding: '8px 20px',
      fontSize: 14,
      cursor: 'pointer',
      textDecoration: 'none',
      display: 'inline-block',
    },
    section: { padding: '64px 24px', maxWidth: 960, margin: '0 auto' },
    sectionTitle: {
      fontSize: 28,
      fontWeight: 700,
      color: '#e0f4ff',
      marginBottom: 8,
      fontFamily: 'var(--font-hud, monospace)',
      letterSpacing: '0.03em',
    },
    sectionSub: { fontSize: 15, color: 'rgba(224,244,255,0.5)', marginBottom: 40 },
    grid2: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 },
    grid3: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 },
    card: {
      background: 'rgba(13,13,24,0.85)',
      border: '1px solid rgba(0,212,255,0.12)',
      borderRadius: 10,
      padding: '20px',
      backdropFilter: 'blur(12px)',
    },
    footer: {
      borderTop: '1px solid rgba(0,212,255,0.1)',
      padding: '32px 24px',
      textAlign: 'center',
      color: 'rgba(224,244,255,0.3)',
      fontSize: 13,
    },
  }

  return (
    <div style={s.page}>
      <header style={s.header}>
        <a href="#" style={s.logo}>
          <div style={s.logoIcon}>A</div>
          <span style={s.logoText}>Aurion OS</span>
        </a>
        <nav style={s.nav}>
          <a href="#features" style={s.navLink}>Возможности</a>
          <a href="#plans" style={s.navLink}>Тарифы</a>
          <a href="#download" style={s.navLink}>Скачать</a>
        </nav>
        <div style={{ display: 'flex', gap: 10 }}>
          <Link to="/auth/login" style={s.btnSecondary}>Войти</Link>
          <Link to="/auth/register" style={s.btnPrimary}>Начать бесплатно</Link>
        </div>
      </header>

      <section style={{ ...s.section, textAlign: 'center', paddingTop: 96 }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, ease: 'easeOut' }}>
          <div style={{
            display: 'inline-block',
            fontSize: 11,
            fontFamily: 'var(--font-hud, monospace)',
            letterSpacing: '0.15em',
            color: '#00d4ff',
            border: '1px solid rgba(0,212,255,0.3)',
            borderRadius: 20,
            padding: '4px 14px',
            marginBottom: 24,
          }}>
            v22.0 · THE GOLDEN STANDARD
          </div>
          <h1 style={{ ...s.sectionTitle, fontSize: 42, marginBottom: 16 }}>
            Ваш персональный<br />
            <span style={{ color: '#00d4ff', textShadow: '0 0 20px rgba(0,212,255,0.4)' }}>ИИ-ассистент JARVIS</span>
          </h1>
          <p style={{ ...s.sectionSub, maxWidth: 560, margin: '0 auto 40px' }}>
            Aurion OS — операционная система с искусственным интеллектом. Голосовое управление,
            проактивный мониторинг и полная безопасность ваших данных.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/auth/register" style={s.btnPrimary}>Попробовать бесплатно</Link>
            <Link to="/auth/login" style={s.btnSecondary}>Войти в систему</Link>
          </div>
        </motion.div>
      </section>

      <section id="features" style={s.section}>
        <h2 style={s.sectionTitle}>Возможности</h2>
        <p style={s.sectionSub}>Всё для управления вашей цифровой жизнью</p>
        <div style={s.grid2}>
          {FEATURES.map((f) => (
            <div key={f.title} style={s.card}>
              <div style={{ fontSize: 28, marginBottom: 10 }}>{f.icon}</div>
              <div style={{ fontSize: 15, fontWeight: 600, color: '#e0f4ff', marginBottom: 6 }}>{f.title}</div>
              <div style={{ fontSize: 13, color: 'rgba(224,244,255,0.5)', lineHeight: 1.6 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="plans" style={s.section}>
        <h2 style={s.sectionTitle}>Тарифы</h2>
        <p style={s.sectionSub}>Выберите подходящий уровень</p>
        <div style={s.grid3}>
          {PLANS.map((plan) => (
            <div key={plan.name} style={{ ...s.card, border: `1px solid ${plan.accent}${plan.highlight ? '66' : '22'}`, position: 'relative' }}>
              {plan.highlight && (
                <div style={{
                  position: 'absolute',
                  top: -10,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: '#00d4ff',
                  color: '#0a0a0f',
                  fontSize: 10,
                  fontWeight: 700,
                  padding: '2px 10px',
                  borderRadius: 10,
                  letterSpacing: '0.1em',
                }}>
                  ПОПУЛЯРНЫЙ
                </div>
              )}
              <div style={{ fontSize: 16, fontWeight: 700, color: plan.accent, marginBottom: 4 }}>{plan.name}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#e0f4ff', marginBottom: 16 }}>{plan.price}</div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {plan.features.map((f) => (
                  <li key={f} style={{ fontSize: 13, color: 'rgba(224,244,255,0.65)', display: 'flex', gap: 8 }}>
                    <span style={{ color: plan.accent }}>✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link to="/auth/register" style={{ ...s.btnPrimary, marginTop: 20, width: '100%', textAlign: 'center', boxSizing: 'border-box' }}>
                Выбрать
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section id="download" style={s.section}>
        <h2 style={s.sectionTitle}>Скачать</h2>
        <p style={s.sectionSub}>Доступно на всех платформах</p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {PLATFORMS.map((p) => (
            <button key={p.label} disabled style={{
              background: 'rgba(13,13,24,0.85)',
              border: '1px solid rgba(0,212,255,0.15)',
              borderRadius: 8,
              padding: '12px 20px',
              color: 'rgba(224,244,255,0.5)',
              fontSize: 14,
              cursor: 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <span>{p.icon}</span> {p.label}
              <span style={{ fontSize: 10, color: 'rgba(224,244,255,0.3)', marginLeft: 4 }}>Скоро</span>
            </button>
          ))}
        </div>
        <p style={{ marginTop: 20, fontSize: 13, color: 'rgba(224,244,255,0.4)' }}>
          Веб-версия доступна прямо сейчас —{' '}
          <Link to="/auth/register" style={{ color: '#00d4ff', textDecoration: 'none' }}>начать без установки</Link>
        </p>
      </section>

      <footer style={s.footer}>
        <div style={{ marginBottom: 8 }}>© 2026 Aurion OS. Все права защищены.</div>
        <div style={{ display: 'flex', gap: 20, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="#" style={{ color: 'rgba(224,244,255,0.3)', textDecoration: 'none' }}>Политика конфиденциальности</a>
          <a href="#" style={{ color: 'rgba(224,244,255,0.3)', textDecoration: 'none' }}>Условия использования</a>
          <a href="#" style={{ color: 'rgba(224,244,255,0.3)', textDecoration: 'none' }}>Поддержка</a>
        </div>
      </footer>
    </div>
  )
}
