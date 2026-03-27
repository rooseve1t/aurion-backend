import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { ToastContainer } from '@/components/Toast/ToastContainer'
import { ThemeProvider } from '@/contexts/ThemeContext'
import '@/index.css'
import '@/styles/aurion-design-system.css'

export function App() {
  return (
    <ThemeProvider>
      <RouterProvider router={router} />
      <ToastContainer />
    </ThemeProvider>
  )
}
