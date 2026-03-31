import './LoadingScreen.css'

// Экран загрузки с анимацией
export function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-container">
        {/* Анимированный логотип */}
        <div className="loading-logo">
          <div className="logo-ring ring-1"></div>
          <div className="logo-ring ring-2"></div>
          <div className="logo-ring ring-3"></div>
          <div className="logo-center">A</div>
        </div>
        
        {/* Текст загрузки */}
        <h2 className="loading-text">Aurion OS</h2>
        <p className="loading-subtext">Загрузка...</p>
        
        {/* Прогресс бар */}
        <div className="loading-bar">
          <div className="loading-progress"></div>
        </div>
      </div>
    </div>
  )
}
