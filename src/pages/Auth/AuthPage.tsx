import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Eye, EyeOff, Fingerprint, KeyRound, LogIn, Mail, ShieldCheck, UserPlus } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import { useToast } from '@/hooks/useToast'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import '@/styles/aurion-design-system.css'

type Mode = 'login' | 'register' | '2fa'

export function AuthPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const isRegister = location.pathname.includes('register')

  const [mode, setMode] = useState<Mode>(isRegister ? 'register' : 'login')
  const [loginValue, setLoginValue] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode]         = useState('')
  const [showPw, setShowPw]     = useState(false)
  const [loading, setLoading]   = useState(false)

  const {
    login,
    setTokens,
    setUser,
    needs2FA,
    pending2FAToken,
    setNeeds2FA,
    error,
    clearError,
    isLoading,
  } = useAuthStore()
  const toast = useToast()

  useEffect(() => { if (needs2FA) setMode('2fa') }, [needs2FA])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    const ok = await login(loginValue, password)
    if (ok) navigate('/dashboard')
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authService.register(loginValue, username, password)
      toast.success('Аккаунт создан. Войдите.')
      setMode('login')
      navigate('/auth/login')
      setPassword('')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handle2FA = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!pending2FAToken) {
      toast.error('Сессия 2FA истекла, войдите заново')
      setMode('login')
      setNeeds2FA(false)
      return
    }
    setLoading(true)
    try {
      const tokens = await authService.verify2fa(code, pending2FAToken)
      setTokens(tokens.access_token, tokens.refresh_token)
      const user = await authService.getMe()
      setUser(user)
      setNeeds2FA(false)
      navigate('/dashboard')
    } catch {
      toast.error('Неверный код 2FA')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-8 relative overflow-hidden aurion-grid-bg">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--aurion-cyan)] opacity-5 rounded-full blur-3xl" />
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-[var(--aurion-purple)] opacity-3 rounded-full blur-3xl" />
      </div>

      {/* Top Navigation */}
      <div className="fixed top-0 left-0 w-full p-6 flex justify-between items-center z-50">
        <button 
          className="flex items-center gap-2 text-[var(--aurion-text-dim)] hover:text-[var(--aurion-cyan)] transition-colors aurion-mono text-xs uppercase"
          onClick={() => navigate('/')}
        >
          <span className="text-lg">←</span>
          <span>НАЗАД</span>
        </button>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[var(--aurion-green)] aurion-pulse" />
          <span className="aurion-mono text-xs text-[var(--aurion-green)] uppercase">СИСТЕМА ОНЛАЙН</span>
        </div>
      </div>

      {/* Main Content */}
      <main className="w-full max-w-[480px] relative z-10 flex flex-col gap-8">
        {/* Header Section */}
        <header className="flex flex-col items-center text-center gap-6">
          {/* Enhanced Core Orb */}
          <div className="relative">
            <div className="aurion-orb w-24 h-24">
              <ShieldCheck className="text-[var(--aurion-bg-primary)] text-4xl" />
            </div>
            {/* Orbital Rings */}
            <div className="absolute inset-0 border border-[var(--aurion-cyan)]/20 rounded-full w-32 h-32 -m-4" />
            <div className="absolute inset-0 border border-[var(--aurion-purple)]/10 border-dashed rounded-full w-40 h-40 -m-8" />
          </div>
          
          <div className="flex flex-col gap-2">
            <h1 className="aurion-headline text-3xl text-[var(--aurion-text-primary)] tracking-tight">
              ВХОД В СИСТЕМУ
            </h1>
            <p className="aurion-mono text-sm text-[var(--aurion-cyan)] tracking-widest">
              CORE LINK ACTIVE :: AURION_OS_v4.2
            </p>
          </div>
        </header>

        {/* Auth Form */}
        <div className="aurion-glass-panel p-8 relative overflow-hidden">
          {/* HUD Grid Overlay */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <div className="w-full h-full" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='20' height='20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1h2v2H1z' fill='%2300fbfb' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E")`,
            }} />
          </div>

          <form className="flex flex-col gap-6 relative z-10">
            {error && (
              <div className="aurion-status aurion-status-offline w-full justify-center">
                {error}
              </div>
            )}

            {/* 2FA Form */}
            {mode === '2fa' && (
              <>
                <p className="text-center text-[var(--aurion-text-secondary)] text-sm">
                  Введите 6-значный код из приложения-аутентификатора
                </p>
                <div className="flex flex-col gap-2">
                  <label className="aurion-label">КОД 2FA</label>
                  <div className="relative">
                    <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-4 py-4 text-center font-mono text-lg tracking-widest"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="000000"
                      maxLength={6}
                      autoFocus
                      required
                    />
                  </div>
                </div>
                <button 
                  type="submit" 
                  className="aurion-btn aurion-btn-primary w-full py-4" 
                  disabled={loading}
                  onClick={handle2FA}
                >
                  {loading ? 'ПРОВЕРКА...' : 'ПОДТВЕРДИТЬ'}
                </button>
                <button 
                  type="button" 
                  className="aurion-btn aurion-btn-secondary w-full"
                  onClick={() => { setMode('login'); setNeeds2FA(false) }}
                >
                  ← НАЗАД
                </button>
              </>
            )}

            {/* Login Form */}
            {mode === 'login' && (
              <>
                <div className="flex flex-col gap-2">
                  <label className="aurion-label">ИДЕНТИФИКАТОР</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-4 py-4"
                      type="text"
                      value={loginValue}
                      onChange={(e) => setLoginValue(e.target.value)}
                      placeholder="SYS_ADMIN_ID"
                      required
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="aurion-label">ПАРОЛЬ</label>
                  <div className="relative">
                    <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-12 py-4 font-mono tracking-widest"
                      type={showPw ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      required
                    />
                    <button
                      type="button"
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--aurion-text-dim)] hover:text-[var(--aurion-cyan)] transition-colors"
                      onClick={() => setShowPw(!showPw)}
                    >
                      {showPw ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="aurion-btn aurion-btn-primary w-full py-4" 
                  disabled={isLoading}
                  onClick={handleLogin}
                >
                  {isLoading ? 'ВХОД...' : 'АУТЕНТИФИКАЦИЯ'}
                </button>

                <button 
                  type="button" 
                  className="aurion-btn aurion-btn-secondary w-full"
                  onClick={() => { setMode('register'); navigate('/auth/register') }}
                >
                  <UserPlus size={16} />
                  СОЗДАТЬ АККАУНТ
                </button>

                {/* Biometric Alternative */}
                <div className="mt-4 flex flex-col items-center gap-4">
                  <div className="flex items-center w-full gap-4">
                    <div className="h-px bg-[var(--aurion-text-dim)] flex-1" />
                    <span className="aurion-mono text-xs">ИЛИ ИСПОЛЬЗУЙТЕ</span>
                    <div className="h-px bg-[var(--aurion-text-dim)] flex-1" />
                  </div>
                  <button 
                    className="w-16 h-16 aurion-glass flex items-center justify-center text-[var(--aurion-cyan)] hover:bg-[var(--aurion-bg-surface-high)] transition-all group"
                    type="button"
                  >
                    <Fingerprint className="text-3xl group-hover:scale-110 transition-transform" />
                  </button>
                  <span className="aurion-mono text-xs text-[var(--aurion-text-dim)]">БИОМЕТРИЯ</span>
                </div>
              </>
            )}

            {/* Register Form */}
            {mode === 'register' && (
              <>
                <div className="flex flex-col gap-2">
                  <label className="aurion-label">EMAIL</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-4 py-4"
                      type="email"
                      value={loginValue}
                      onChange={(e) => setLoginValue(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="aurion-label">ИМЯ ПОЛЬЗОВАТЕЛЯ</label>
                  <div className="relative">
                    <UserPlus className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-4 py-4"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="aurion-label">ПАРОЛЬ</label>
                  <div className="relative">
                    <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--aurion-cyan)]" size={16} />
                    <input
                      className="aurion-input pl-12 pr-12 py-4"
                      type={showPw ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--aurion-text-dim)] hover:text-[var(--aurion-cyan)] transition-colors"
                      onClick={() => setShowPw(!showPw)}
                    >
                      {showPw ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="aurion-btn aurion-btn-primary w-full py-4" 
                  disabled={loading}
                  onClick={handleRegister}
                >
                  {loading ? 'СОЗДАНИЕ...' : 'ЗАРЕГИСТРИРОВАТЬСЯ'}
                </button>

                <button 
                  type="button" 
                  className="aurion-btn aurion-btn-secondary w-full"
                  onClick={() => { setMode('login'); navigate('/auth/login') }}
                >
                  УЖЕ ЕСТЬ АККАУНТ
                </button>
              </>
            )}
          </form>
        </div>

        {/* Security Badges */}
        <footer className="flex justify-center gap-6 mt-4 opacity-60">
          <div className="flex items-center gap-2 text-[var(--aurion-purple)]">
            <ShieldCheck size={16} />
            <span className="aurion-mono text-xs">256-BIT ENCRYPTION</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--aurion-green)]">
            <Fingerprint size={16} />
            <span className="aurion-mono text-xs">A.I. THREAT GUARD</span>
          </div>
        </footer>
      </main>
    </div>
  )
}
