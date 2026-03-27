import React, { useState } from 'react'
import { Settings, Palette, Globe, Volume2, Shield, Database, Bell, Monitor, Smartphone, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import '@/styles/aurion-design-system.css'

export function SettingsPage() {
  const { theme } = useTheme()
  const [activeTab, setActiveTab] = useState('appearance')
  const [notifications, setNotifications] = useState(true)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [autoSave, setAutoSave] = useState(true)
  const [language, setLanguage] = useState('ru')

  const tabs = [
    { id: 'appearance', label: 'Внешний вид', icon: Palette },
    { id: 'system', label: 'Система', icon: Monitor },
    { id: 'security', label: 'Безопасность', icon: Shield },
    { id: 'data', label: 'Данные', icon: Database },
  ]

  return (
    <div className="min-h-screen bg-[var(--aurion-bg-primary)] text-[var(--aurion-text-secondary)] p-6 aurion-grid-bg">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-lg bg-[var(--aurion-cyan)]/10 border border-[var(--aurion-cyan)]/30 flex items-center justify-center">
            <Settings className="text-[var(--aurion-cyan)]" size={24} />
          </div>
          <div>
            <h1 className="aurion-headline text-3xl font-bold text-[var(--aurion-text-primary)] tracking-tight">
              НАСТРОЙКИ
            </h1>
            <p className="aurion-mono text-sm text-[var(--aurion-cyan)] tracking-widest">
              CONFIGURATION PANEL
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-12 gap-6">
        {/* Sidebar */}
        <aside className="col-span-3">
          <nav className="space-y-2">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                  activeTab === id
                    ? 'bg-[var(--aurion-cyan)]/10 border border-[var(--aurion-cyan)]/30 text-[var(--aurion-cyan)]'
                    : 'aurion-card hover:bg-[var(--aurion-bg-surface-high)] text-[var(--aurion-text-secondary)]'
                }`}
              >
                <Icon size={18} />
                <span className="aurion-mono text-sm uppercase tracking-wider">{label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Content */}
        <main className="col-span-9">
          {/* Appearance Tab */}
          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <div className="aurion-card p-6">
                <h2 className="aurion-headline text-xl font-bold text-[var(--aurion-text-primary)] mb-6">
                  ВНЕШНИЙ ВИД
                </h2>
                
                {/* Theme Selection */}
                <div className="space-y-4 mb-8">
                  <h3 className="aurion-label text-sm">ТЕМА ОФОРМЛЕНИЯ</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => {}}
                      className={`aurion-card p-4 border-2 transition-all ${
                        theme === 'dark' 
                          ? 'border-[var(--aurion-cyan)] bg-[var(--aurion-cyan)]/10' 
                          : 'border-[var(--aurion-text-dim)]/20'
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <Moon className="text-[var(--aurion-text-secondary)]" size={20} />
                        <span className="font-bold">Темная</span>
                      </div>
                      <p className="text-xs text-[var(--aurion-text-muted)]">Классическая тема Aurion OS</p>
                    </button>
                    
                    <button
                      onClick={() => {}}
                      className={`aurion-card p-4 border-2 transition-all ${
                        theme === 'light' 
                          ? 'border-[var(--aurion-cyan)] bg-[var(--aurion-cyan)]/10' 
                          : 'border-[var(--aurion-text-dim)]/20'
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <Sun className="text-[var(--aurion-text-secondary)]" size={20} />
                        <span className="font-bold">Светлая</span>
                      </div>
                      <p className="text-xs text-[var(--aurion-text-muted)]">Адаптивная светлая тема</p>
                    </button>
                  </div>
                  <div className="flex justify-center mt-4">
                    <ThemeToggle />
                  </div>
                </div>

                {/* Accent Color */}
                <div className="space-y-4">
                  <h3 className="aurion-label text-sm">АКЦЕНТНЫЙ ЦВЕТ</h3>
                  <div className="flex gap-3">
                    {['cyan', 'purple', 'green', 'red', 'amber'].map((color) => (
                      <button
                        key={color}
                        className={`w-12 h-12 rounded-lg border-2 transition-all ${
                          color === 'cyan' ? 'border-[var(--aurion-text-secondary)]' : 'border-[var(--aurion-text-dim)]/20'
                        }`}
                        style={{
                          backgroundColor: color === 'cyan' ? 'var(--aurion-cyan)' :
                                          color === 'purple' ? 'var(--aurion-purple)' :
                                          color === 'green' ? 'var(--aurion-green-dim)' :
                                          color === 'red' ? 'var(--aurion-error)' :
                                          'var(--aurion-warning)'
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* System Tab */}
          {activeTab === 'system' && (
            <div className="space-y-6">
              <div className="aurion-card p-6">
                <h2 className="aurion-headline text-xl font-bold text-[var(--aurion-text-primary)] mb-6">
                  СИСТЕМНЫЕ НАСТРОЙКИ
                </h2>
                
                <div className="space-y-6">
                  {/* Language */}
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold mb-1">Язык интерфейса</h3>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Выберите предпочитаемый язык</p>
                    </div>
                    <select 
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="aurion-input w-32"
                    >
                      <option value="ru">Русский</option>
                      <option value="en">English</option>
                    </select>
                  </div>

                  {/* Notifications */}
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold mb-1">Уведомления</h3>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Показывать системные уведомления</p>
                    </div>
                    <button
                      onClick={() => setNotifications(!notifications)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        notifications ? 'bg-[var(--aurion-cyan)]' : 'bg-[var(--aurion-bg-surface-high)]'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-[var(--aurion-text-primary)] transition-transform ${
                        notifications ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>

                  {/* Sound */}
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold mb-1">Звуковые эффекты</h3>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Воспроизводить звуки интерфейса</p>
                    </div>
                    <button
                      onClick={() => setSoundEnabled(!soundEnabled)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        soundEnabled ? 'bg-[var(--aurion-cyan)]' : 'bg-[var(--aurion-bg-surface-high)]'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-[var(--aurion-text-primary)] transition-transform ${
                        soundEnabled ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>

                  {/* Auto-save */}
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold mb-1">Автосохранение</h3>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Автоматически сохранять настройки</p>
                    </div>
                    <button
                      onClick={() => setAutoSave(!autoSave)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        autoSave ? 'bg-[var(--aurion-cyan)]' : 'bg-[var(--aurion-bg-surface-high)]'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-[var(--aurion-text-primary)] transition-transform ${
                        autoSave ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="aurion-card p-6">
                <h2 className="aurion-headline text-xl font-bold text-[var(--aurion-text-primary)] mb-6">
                  БЕЗОПАСНОСТЬ
                </h2>
                
                <div className="space-y-4">
                  <div className="p-4 aurion-card border-l-4 border-l-[var(--aurion-green-dim)]">
                    <div className="flex items-center gap-3 mb-2">
                      <Shield className="text-[var(--aurion-green-dim)]" size={20} />
                      <span className="font-bold">Шифрование включено</span>
                    </div>
                    <p className="text-sm text-[var(--aurion-text-muted)]">Все данные защищены AES-256</p>
                  </div>
                  
                  <div className="p-4 aurion-card border-l-4 border-l-[var(--aurion-cyan)]">
                    <div className="flex items-center gap-3 mb-2">
                      <Database className="text-[var(--aurion-cyan)]" size={20} />
                      <span className="font-bold">Резервное копирование</span>
                    </div>
                    <p className="text-sm text-[var(--aurion-text-muted)]">Последнее копирование: 2 часа назад</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Tab */}
          {activeTab === 'data' && (
            <div className="space-y-6">
              <div className="aurion-card p-6">
                <h2 className="aurion-headline text-xl font-bold text-[var(--aurion-text-primary)] mb-6">
                  УПРАВЛЕНИЕ ДАННЫМИ
                </h2>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="aurion-card p-4 text-center">
                      <div className="text-2xl font-bold text-[var(--aurion-cyan)] mb-2">1.2 GB</div>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Использовано памяти</p>
                    </div>
                    <div className="aurion-card p-4 text-center">
                      <div className="text-2xl font-bold text-[var(--aurion-green-dim)] mb-2">8.8 GB</div>
                      <p className="text-sm text-[var(--aurion-text-muted)]">Свободно</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-4">
                    <button className="aurion-btn aurion-btn-secondary flex-1">
                      Очистить кэш
                    </button>
                    <button className="aurion-btn aurion-btn-secondary flex-1">
                      Экспорт данных
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
