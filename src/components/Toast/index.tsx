import { Toaster } from 'react-hot-toast'

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: '#0a1214',
          color: '#fff',
          border: '1px solid rgba(0,229,255,0.2)',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '13px',
          borderRadius: '4px',
        },
        success: { iconTheme: { primary: '#10b981', secondary: '#0a1214' } },
        error:   { iconTheme: { primary: '#ef4444', secondary: '#0a1214' } },
      }}
    />
  )
}
