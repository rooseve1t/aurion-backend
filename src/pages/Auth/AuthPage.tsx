import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Eye, EyeOff, LogIn, UserPlus } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import { useToast } from '@/hooks/useToast'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import styles from './AuthPage.module.css'

type Mode = 'login' | 'register' | '2fa'

export function AuthPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const isRegister = location.pathname.includes('register')

  const [mode, setMode] = useState<Mode>(isRegister ? 'register' : 'login')
  const [email, setEmail]       = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode]         = useState('')
  const [showPw, setShowPw]     = useState(false)
  const [loading, setLoading]   = useState(false)

  const { login, setTokens, setUser, needs2FA, setNeeds2FA, error, clearError } = useAuthStore()
  const toast = useToast()

  useEffect(() => { if (needs2FA) setMode('2fa') }, [needs2FA])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    const ok = await login(email, password)
    if (ok) navigate('/dashboard')
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authService.register(email, username, password)
      toast.success('Аккаунт создан. Войдите.')
      setMode('login')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handle2FA = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const tokens = await authService.verify2fa(code)
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
    <div className={styles.page}>
      <div className={styles.scan} />
      <div className={styles.card}>
        <div className={styles.header}>
          <CoreOrb size={48} />
          <div>
            <div className={styles.title}>AURION OS</div>
            <div className={styles.sub}>
              {mode === 'login' && 'АВТОРИЗАЦИЯ'}
              {mode === 'register' && 'РЕГИСТРАЦИЯ'}
              {mode === '2fa' && 'ДВУХФАКТОРНАЯ АУТЕНТИФИКАЦИЯ'}
            </div>
          </div>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        {/* ─── 2FA ─── */}
        {mode === '2fa' && (
          <form onSubmit={handle2FA} className={styles.form}>
            <p className={styles.hint}>Введите 6-значный код из приложения-аутентификатора</p>
            <div className={styles.field}>
              <label className="label">КОД 2FA</label>
              <input
                className="input"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="000000"
                maxLength={6}
                autoFocus
                required
              />
            </div>
            <button type="submit" className="btn btn-cyan" style={{ width: '100%' }} disabled={loading}>
              <LogIn size={14} />
              {loading ? 'ПРОВЕРКА...' : 'ПОДТВЕРДИТЬ'}
            </button>
            <button type="button" className="btn btn-ghost" style={{ width: '100%' }}
              onClick={() => { setMode('login'); setNeeds2FA(false) }}>
              ← НАЗАД
            </button>
          </form>
        )}

        {/* ─── LOGIN ─── */}
        {mode === 'login' && (
          <form onSubmit={handleLogin} className={styles.form}>
            <div className={styles.field}>
              <label className="label">EMAIL</label>
              <input className="input" type="email" value={email}
                onChange={(e) => setEmail(e.target.value)} placeholder="user@aurionai.ru" required />
            </div>
            <div className={styles.field}>
              <label className="label">ПАРОЛЬ</label>
              <div className={styles.pwWrap}>
                <input className="input" type={showPw ? 'text' : 'password'}
                  value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" required />
                <button type="button" className={styles.eyeBtn} onClick={() => setShowPw(!showPw)}>
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-cyan" style={{ width: '100%' }}
              disabled={loading}>
              <LogIn size={14} />
              {loading ? 'ВХОД...' : 'ВОЙТИ'}
            </button>
            <button type="button" className="btn btn-ghost" style={{ width: '100%' }}
              onClick={() => { setMode('register'); navigate('/auth/register') }}>
              <UserPlus size={14} />
              СОЗДАТЬ АККАУНТ
            </button>
          </form>
        )}

        {/* ─── REGISTER ─── */}
        {mode === 'register' && (
          <form onSubmit={handleRegister} className={styles.form}>
            <div className={styles.field}>
              <label className="label">EMAIL</label>
              <input className="input" type="email" value={email}
                onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className={styles.field}>
              <label className="label">ИМЯ ПОЛЬЗОВАТЕЛЯ</label>
              <input className="input" value={username}
                onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className={styles.field}>
              <label className="label">ПАРОЛЬ</label>
              <div className={styles.pwWrap}>
                <input className="input" type={showPw ? 'text' : 'password'}
                  value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button type="button" className={styles.eyeBtn} onClick={() => setShowPw(!showPw)}>
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-cyan" style={{ width: '100%' }} disabled={loading}>
              <UserPlus size={14} />
              {loading ? 'СОЗДАНИЕ...' : 'ЗАРЕГИСТРИРОВАТЬСЯ'}
            </button>
            <button type="button" className="btn btn-ghost" style={{ width: '100%' }}
              onClick={() => { setMode('login'); navigate('/auth/login') }}>
              УЖЕ ЕСТЬ АККАУНТ
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
