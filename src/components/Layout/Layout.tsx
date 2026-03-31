import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import './Layout.css'

// Компонент основного layout с навигацией
export function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  // Функция выхода из аккаунта
  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/auth')
  }

  return (
    <div className="layout">
      {/* Верхняя панель */}
      <header className="header">
        <div className="header-left">
          <button 
            className="menu-button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h1 className="logo">Aurion OS</h1>
        </div>
        <div className="header-right">
          <span className="user-name">Пользователь</span>
          <button onClick={handleLogout} className="logout-button">
            Выйти
          </button>
        </div>
      </header>

      <div className="main-container">
        {/* Боковая панель навигации */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav className="nav-menu">
            <NavLink to="/dashboard" className="nav-link" end>
              📊 Дашборд
            </NavLink>
            <NavLink to="/jarvis" className="nav-link">
              🤖 JARVIS
            </NavLink>
            <NavLink to="/vpn" className="nav-link">
              🛡️ VPN
            </NavLink>
            <NavLink to="/finance" className="nav-link">
              💰 Финансы
            </NavLink>
            <NavLink to="/memory" className="nav-link">
              🧠 Память
            </NavLink>
            <NavLink to="/settings" className="nav-link">
              ⚙️ Настройки
            </NavLink>
          </nav>
        </aside>

        {/* Основное содержимое */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}
