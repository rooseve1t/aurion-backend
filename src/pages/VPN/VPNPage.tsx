import { useState } from 'react'
import './VPNPage.css'

// Страница VPN сервиса
export function VPNPage() {
  const [connected, setConnected] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState('US')
  const [loading, setLoading] = useState(false)

  // Список доступных стран
  const countries = [
    { code: 'US', name: 'США', flag: '🇺🇸' },
    { code: 'UK', name: 'Великобритания', flag: '🇬🇧' },
    { code: 'DE', name: 'Германия', flag: '🇩🇪' },
    { code: 'FR', name: 'Франция', flag: '🇫🇷' },
    { code: 'NL', name: 'Нидерланды', flag: '🇳🇱' },
    { code: 'JP', name: 'Япония', flag: '🇯🇵' },
    { code: 'SG', name: 'Сингапур', flag: '🇸🇬' },
  ]

  // Подключение/отключение VPN
  const toggleVPN = () => {
    setLoading(true)
    // Имитация API вызова
    setTimeout(() => {
      setConnected(!connected)
      setLoading(false)
    }, 1500)
  }

  return (
    <div className="vpn-page">
      <h1 className="page-title">🛡️ VPN</h1>
      <p className="page-subtitle">Защищенное интернет-соединение</p>

      {/* Статус VPN */}
      <div className={`vpn-status-card ${connected ? 'connected' : 'disconnected'}`}>
        <div className="status-indicator"></div>
        <div className="status-info">
          <h2>{connected ? 'Подключено' : 'Отключено'}</h2>
          <p>{connected 
            ? `Вы подключены через ${countries.find(c => c.code === selectedCountry)?.name}` 
            : 'VPN не активен. Ваше соединение не защищено.'}
          </p>
        </div>
      </div>

      {/* Выбор страны */}
      <div className="country-selection">
        <h3>Выберите локацию:</h3>
        <div className="countries-grid">
          {countries.map(country => (
            <button
              key={country.code}
              className={`country-card ${selectedCountry === country.code ? 'selected' : ''}`}
              onClick={() => setSelectedCountry(country.code)}
              disabled={connected}
            >
              <span className="country-flag">{country.flag}</span>
              <span className="country-name">{country.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Кнопка подключения */}
      <button 
        className={`vpn-toggle-button ${connected ? 'disconnect' : 'connect'}`}
        onClick={toggleVPN}
        disabled={loading}
      >
        {loading ? 'Подключение...' : (connected ? 'Отключить' : 'Подключить VPN')}
      </button>

      {/* Информация о подключении */}
      {connected && (
        <div className="connection-info">
          <div className="info-item">
            <span className="info-label">IP-адрес:</span>
            <span className="info-value">185.***.***.***</span>
          </div>
          <div className="info-item">
            <span className="info-label">Протокол:</span>
            <span className="info-value">WireGuard</span>
          </div>
          <div className="info-item">
            <span className="info-label">Шифрование:</span>
            <span className="info-value">AES-256-GCM</span>
          </div>
        </div>
      )}
    </div>
  )
}
