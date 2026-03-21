import React, { useState, useEffect } from 'react'

// 🏆 УЛУЧШЕННАЯ ВЕРСИЯ С ELEMENT ИЗ СТАРОЙ
export function AurionEnhanced() {
  const [activeModule, setActiveModule] = useState('overview')
  const [isConnected, setIsConnected] = useState(false)
  const [isDark, setIsDark] = useState(true)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Проверка мобильного устройства
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)

    // Проверка соединения
    fetch('http://localhost:8000/health')
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false))

    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const modules = [
    { id: 'overview', name: 'Обзор', icon: '🏠', color: 'from-blue-500 to-purple-600' },
    { id: 'voice', name: 'Голос JARVIS', icon: '🎤', color: 'from-purple-500 to-pink-600' },
    { id: 'quantum', name: 'Квантовые вычисления', icon: '⚛️', color: 'from-cyan-500 to-blue-600' },
    { id: 'memory', name: 'Векторная память', icon: '🧠', color: 'from-green-500 to-teal-600' },
    { id: 'osint', name: 'OSINT разведка', icon: '🔍', color: 'from-orange-500 to-red-600' },
    { id: 'finance', name: 'Финансы', icon: '💰', color: 'from-yellow-500 to-orange-600' },
    { id: 'smarthome', name: 'Умный дом', icon: '🏠', color: 'from-indigo-500 to-purple-600' },
    { id: 'agents', name: 'Агенты', icon: '🤖', color: 'from-pink-500 to-rose-600' }
  ]

  const renderContent = () => {
    switch (activeModule) {
      case 'overview':
        return <OverviewModule />
      case 'voice':
        return <VoiceModule />
      case 'quantum':
        return <QuantumModule />
      case 'memory':
        return <MemoryModule />
      case 'osint':
        return <OSINTModule />
      case 'finance':
        return <FinanceModule />
      case 'smarthome':
        return <SmartHomeModule />
      case 'agents':
        return <AgentsModule />
      default:
        return <OverviewModule />
    }
  }

  return (
    <div className={`min-h-screen transition-all duration-500 ${
      isDark 
        ? 'bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900' 
        : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50'
    }`}>
      {/* 🎨 Bioluminescent эффекты */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-2000"></div>
      </div>

      {/* Header с улучшенным дизайном */}
      <header className={`relative backdrop-blur-xl border-b ${
        isDark ? 'bg-black/20 border-white/10' : 'bg-white/20 border-gray-200/10'
      }`}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* 🎨 Лого с bioluminescent эффектом */}
              <div className="relative">
                <div className={`absolute inset-0 bg-gradient-to-r ${modules[0].color} rounded-lg blur-lg opacity-50 animate-pulse`}></div>
                <div className="relative w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">A</span>
                </div>
              </div>
              <div>
                <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Aurion OS</h1>
                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Персональный ИИ-ассистент нового поколения</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* 🌙 Переключатель темы */}
              <button
                onClick={() => setIsDark(!isDark)}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  isDark 
                    ? 'bg-white/10 text-yellow-400 hover:bg-white/20' 
                    : 'bg-gray-200/10 text-gray-700 hover:bg-gray-200/20'
                }`}
              >
                {isDark ? '🌙' : '☀️'}
              </button>
              
              {/* 📱 Статус соединения */}
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                isConnected 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-red-500/20 text-red-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                <span className="text-sm">{isConnected ? 'Подключено' : 'Offline'}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 🎨 Улучшенная навигация */}
      <nav className={`relative backdrop-blur-xl border-b ${
        isDark ? 'bg-black/10 border-white/10' : 'bg-white/10 border-gray-200/10'
      }`}>
        <div className="max-w-7xl mx-auto px-4 py-2">
          <div className={`flex space-x-2 overflow-x-auto ${isMobile ? 'justify-start' : 'justify-center'}`}>
            {modules.map((module) => (
              <button
                key={module.id}
                onClick={() => setActiveModule(module.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 whitespace-nowrap transform hover:scale-105 ${
                  activeModule === module.id
                    ? `bg-gradient-to-r ${module.color} text-white shadow-lg shadow-purple-500/25`
                    : isDark 
                      ? 'bg-white/10 text-gray-300 hover:bg-white/20 hover:text-white'
                      : 'bg-gray-200/10 text-gray-700 hover:bg-gray-200/20 hover:text-gray-900'
                }`}
              >
                <span className="text-lg">{module.icon}</span>
                <span className={`text-sm font-medium ${isMobile ? 'hidden' : 'block'}`}>
                  {module.name}
                </span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* 🎨 Контент с улучшенными эффектами */}
      <main className="relative max-w-7xl mx-auto px-4 py-8">
        <div className="transition-all duration-500 ease-out">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}

// 🎨 Улучшенные компоненты модулей с bioluminescent эффектами
function OverviewModule() {
  const [isDark] = useState(true)
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* 🎨 Карточка с bioluminescent эффектом */}
      <div className={`relative group backdrop-blur-xl rounded-xl p-6 border transition-all duration-300 transform hover:scale-105 ${
        isDark 
          ? 'bg-white/10 border-white/20 hover:bg-white/15 hover:border-white/30' 
          : 'bg-white/80 border-gray-200/20 hover:bg-white/90 hover:border-gray-300/30'
      }`}>
        {/* 🌟 Свечение */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg blur-lg opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        
        <div className="relative">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Система готова</h3>
            <span className="text-2xl animate-bounce">🚀</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Backend API</span>
              <span className="text-green-400 animate-pulse">✅ Активен</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">База данных</span>
              <span className="text-green-400 animate-pulse">✅ Подключена</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Модули</span>
              <span className="text-blue-400 animate-pulse">8/8 готово</span>
            </div>
          </div>
        </div>
      </div>

      <div className={`relative group backdrop-blur-xl rounded-xl p-6 border transition-all duration-300 transform hover:scale-105 ${
        isDark 
          ? 'bg-white/10 border-white/20 hover:bg-white/15 hover:border-white/30' 
          : 'bg-white/80 border-gray-200/20 hover:bg-white/90 hover:border-gray-300/30'
      }`}>
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg blur-lg opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        
        <div className="relative">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">JARVIS Ассистент</h3>
            <span className="text-2xl animate-pulse">🎤</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Голос</span>
              <span className="text-green-400 animate-pulse">✅ Готов</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Нейросеть</span>
              <span className="text-green-400 animate-pulse">✅ GPT-4</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Свобода</span>
              <span className="text-green-400 animate-pulse">✅ 100%</span>
            </div>
          </div>
        </div>
      </div>

      <div className={`relative group backdrop-blur-xl rounded-xl p-6 border transition-all duration-300 transform hover:scale-105 ${
        isDark 
          ? 'bg-white/10 border-white/20 hover:bg-white/15 hover:border-white/30' 
          : 'bg-white/80 border-gray-200/20 hover:bg-white/90 hover:border-gray-300/30'
      }`}>
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg blur-lg opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        
        <div className="relative">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Технологии</h3>
            <span className="text-2xl animate-spin">⚛️</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Квантовые вычисления</span>
              <span className="text-purple-400 animate-pulse">✨ Активны</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Векторная память</span>
              <span className="text-blue-400 animate-pulse">🧠 Работает</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">OSINT</span>
              <span className="text-orange-400 animate-pulse">🔍 Готов</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 🎨 Остальные модули с улучшенными эффектами...
function VoiceModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">🎤 Голловой ассистент JARVIS</h2>
        <p className="text-gray-300">Абсолютно свободное общение с голосом из Marvel</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-purple-500/20 rounded-lg p-6 border border-purple-400/30 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-4">🎭 Голсовые возможности</h3>
            <ul className="space-y-2 text-gray-300">
              <li>✅ Точный голос из Marvel</li>
              <li>✅ Британский акцент на русском</li>
              <li>✅ Эмоциональная интонация</li>
              <li>✅ Естественное общение</li>
            </ul>
          </div>
          
          <div className="bg-blue-500/20 rounded-lg p-6 border border-blue-400/30 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-4">🧠 Интеллект</h3>
            <ul className="space-y-2 text-gray-300">
              <li>✅ GPT-4 Turbo</li>
              <li>✅ Абсолютно свободные ответы</li>
              <li>✅ Контекстная память</li>
              <li>✅ Адаптация под вас</li>
            </ul>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-green-500/20 rounded-lg p-6 border border-green-400/30 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-4">🔊 Технологии</h3>
            <ul className="space-y-2 text-gray-300">
              <li>✅ ElevenLabs TTS</li>
              <li>✅ OpenAI Whisper STT</li>
              <li>✅ 48kHz качество</li>
              <li>✅ Реальное время</li>
            </ul>
          </div>
          
          <div className="bg-orange-500/20 rounded-lg p-6 border border-orange-400/30 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-4">💬 Пример общения</h3>
            <div className="space-y-2 text-gray-300">
              <p><strong>Вы:</strong> "Привет, JARVIS!"</p>
              <p><strong>JARVIS:</strong> "Добрый день, сэр! Рад слышать вас. Чем могу помочь сегодня?"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function QuantumModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">⚛️ Квантовые вычисления</h2>
        <p className="text-gray-300">Реальные квантовые алгоритмы для оптимизации</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-cyan-500/20 rounded-lg p-6 border border-cyan-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🔬 Квантовые алгоритмы</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ QUBO решатель</li>
            <li>✅ Квантовая оптимизация</li>
            <li>✅ Гибридные алгоритмы</li>
            <li>✅ Портфельная оптимизация</li>
          </ul>
        </div>
        
        <div className="bg-blue-500/20 rounded-lg p-6 border border-blue-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">💼 Бизнес применение</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Финансовая оптимизация</li>
            <li>✅ Логистика</li>
            <li>✅ Риск-менеджмент</li>
            <li>✅ Инвестиционные стратегии</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function MemoryModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">🧠 Векторная память</h2>
        <p className="text-gray-300">pgvector + sentence-transformers для семантического поиска</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-green-500/20 rounded-lg p-6 border border-green-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">📚 Память</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Семантический поиск</li>
            <li>✅ Векторные эмбеддинги</li>
            <li>✅ Категоризация</li>
            <li>✅ Тегирование</li>
          </ul>
        </div>
        
        <div className="bg-teal-500/20 rounded-lg p-6 border border-teal-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🔍 Поиск</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ По смыслу</li>
            <li>✅ По категориям</li>
            <li>✅ По тегам</li>
            <li>✅ По времени</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function OSINTModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">🔍 OSINT разведка</h2>
        <p className="text-gray-300">Разведка по открытым источникам с AI анализом</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-orange-500/20 rounded-lg p-6 border border-orange-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🌐 Источники</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Censys</li>
            <li>✅ Shodan</li>
            <li>✅ Apify</li>
            <li>✅ WHOIS</li>
          </ul>
        </div>
        
        <div className="bg-red-500/20 rounded-lg p-6 border border-red-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Аналитика</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ AI анализ</li>
            <li>✅ Визуализация</li>
            <li>✅ Отчеты</li>
            <li>✅ Алерты</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function FinanceModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">💰 Финансовый модуль</h2>
        <p className="text-gray-300">Управление финансами с AI анализом</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-yellow-500/20 rounded-lg p-6 border border-yellow-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🏦 Банки</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ OAuth2 подключение</li>
            <li>✅ Шифрование данных</li>
            <li>✅ Транзакции</li>
            <li>✅ Аналитика</li>
          </ul>
        </div>
        
        <div className="bg-orange-500/20 rounded-lg p-6 border border-orange-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">📈 Инвестиции</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Портфель</li>
            <li>✅ Риски</li>
            <li>✅ Прогнозы</li>
            <li>✅ Советы</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function SmartHomeModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">🏠 Умный дом</h2>
        <p className="text-gray-300">Управление устройствами через MQTT</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-indigo-500/20 rounded-lg p-6 border border-indigo-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🔌 Устройства</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ MQTT протокол</li>
            <li>✅ Управление</li>
            <li>✅ Статус</li>
            <li>✅ Автоматизация</li>
          </ul>
        </div>
        
        <div className="bg-purple-500/20 rounded-lg p-6 border border-purple-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">⚡ Оптимизация</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Энергопотребление</li>
            <li>✅ Квантовая оптимизация</li>
            <li>✅ Графики</li>
            <li>✅ Отчеты</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function AgentsModule() {
  return (
    <div className="backdrop-blur-xl rounded-xl p-8 border border-white/20">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">🤖 Роевой интеллект</h2>
        <p className="text-gray-300">Мультиагентная система с оркестрацией</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-pink-500/20 rounded-lg p-6 border border-pink-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🤖 Агенты</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Аналитик</li>
            <li>✅ Исследователь</li>
            <li>✅ Помощник</li>
            <li>✅ Охранник</li>
          </ul>
        </div>
        
        <div className="bg-rose-500/20 rounded-lg p-6 border border-rose-400/30 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-white mb-4">🎯 Оркестрация</h3>
          <ul className="space-y-2 text-gray-300">
            <li>✅ Распределение задач</li>
            <li>✅ Координация</li>
            <li>✅ Retry логика</li>
            <li>✅ Swarm режим</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
