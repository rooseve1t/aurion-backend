import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import './index.css'

// Pages
import { LandingPage } from './pages/Landing/LandingPage'
import { DashboardPage } from './pages/Dashboard/DashboardPage'
import { AuthPage } from './pages/Auth/AuthPage'
import { JarvisPage } from './pages/Jarvis/JarvisPage'
import { VPNPage } from './pages/VPN/VPNPage'
import { FinancePage } from './pages/Finance/FinancePage'
import { MemoryPage } from './pages/Memory/MemoryPage'
import { SettingsPage } from './pages/Settings/SettingsPage'

// Components
import { Layout } from './components/Layout/Layout'
import { LoadingScreen } from './components/LoadingScreen/LoadingScreen'

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [checking, setChecking] = useState(true)
  const [authenticated, setAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const response = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (response.ok) {
            setAuthenticated(true)
          } else {
            localStorage.removeItem('token')
          }
        } catch {
          localStorage.removeItem('token')
        }
      }
      setChecking(false)
    }
    checkAuth()
  }, [])

  if (checking) {
    return <LoadingScreen />
  }

  if (!authenticated) {
    return <Navigate to="/auth" replace />
  }

  return <>{children}</>
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout><DashboardPage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/jarvis" element={
          <ProtectedRoute>
            <Layout><JarvisPage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/vpn" element={
          <ProtectedRoute>
            <Layout><VPNPage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/finance" element={
          <ProtectedRoute>
            <Layout><FinancePage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/memory" element={
          <ProtectedRoute>
            <Layout><MemoryPage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/settings" element={
          <ProtectedRoute>
            <Layout><SettingsPage /></Layout>
          </ProtectedRoute>
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
