import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/theme.css'
import './styles/mobile.css'
import { App } from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)

// PWA Service Worker регистрация с обработкой обновлений
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      })

      // Проверяем обновления каждый час
      setInterval(() => {
        registration.update()
      }, 60 * 60 * 1000)

      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (
              newWorker.state === 'installed' &&
              navigator.serviceWorker.controller
            ) {
              // Есть обновление — активируем
              newWorker.postMessage({ type: 'SKIP_WAITING' })
              console.log(
                '🔄 Aurion OS обновлён. Перезагрузка для применения...'
              )
            }
          })
        }
      })

      console.log('✅ Aurion OS Service Worker зарегистрирован')
    } catch (error) {
      console.warn('⚠️ SW регистрация не удалась:', error)
    }
  })

  // Перезагрузка при смене контроллера (новый SW активировался)
  let refreshing = false
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!refreshing) {
      refreshing = true
      window.location.reload()
    }
  })
}
