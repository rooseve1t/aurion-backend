import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, Shield } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { CoreOrb } from '@/components/CoreOrb'
import toast from 'react-hot-toast'

type View = 'login' | 'register' | '2fa'

export default function AuthPage() {
  const navigate = useNavigate()
  const { login, verify2fa, register, isLoading, twoFactorPending } = useAuthStore()
  const [view, setView] = useState<View>(twoFactorPending ? '2fa' : 'login')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [showPwd, setShowPwd] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const ok = await login(email, password)
      if (ok) navigate('/dashboard')
      else setView('2fa')
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Ошибка входа')
    }
  }

  const handle2fa = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await verify2fa(code)
      navigate('/dashboard')
    } catch {
      toast.error('Неверный код')
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await register(email, username, password)
      toast.success('Аккаунт создан. Войдите.')
      setView('login')
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Ошибка регистрации')
    }
  }

  const inputCls = 'w-full bg-surface border border-cyan/20 rounded px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan/60 focus:ring-1 focus:ring-cyan/30 transition-all'

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6 animate-fade-in">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <CoreOrb size={72} />
          </div>
          <div>
            <div className="text-xl font-bold tracking-widest text-cyan">AURION OS</div>
            <div className="text-[10px] text-cyan/40 tracking-widest">
              {view === 'login' ? 'АВТОРИЗАЦИЯ' : view === 'register' ? 'РЕГИСТРАЦИЯ' : 'ДВУХФАКТОРНАЯ ЗАЩИТА'}
            </div>
          </div>
        </div>

        {/* Card */}
        <div className="bg-card border border-cyan/15 rounded-lg p-6 space-y-4">
          {view === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4" data-testid="login-form">
              <input type="email" placeholder="Email" value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputCls} required />
              <div className="relative">
                <input type={showPwd ? 'text' : 'password'} placeholder="Пароль"
                  value={password} onChange={(e) => setPassword(e.target.value)}
                  className={inputCls + ' pr-10'} required />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/70">
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <button type="submit" disabled={isLoading}
                className="w-full py-3 bg-cyan/10 hover:bg-cyan/20 border border-cyan/40 text-cyan text-sm font-bold tracking-widest rounded transition-all disabled:opacity-50">
                {isLoading ? 'ВХОД...' : 'ВОЙТИ'}
              </button>
            </form>
          )}

          {view === '2fa' && (
            <form onSubmit={handle2fa} className="space-y-4" data-testid="twofa-form">
              <div className="flex justify-center text-amber">
                <Shield size={32} />
              </div>
              <p className="text-xs text-white/50 text-center">Введите 6-значный код из приложения-аутентификатора</p>
              <input type="text" placeholder="000000" value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                className={inputCls + ' text-center text-2xl tracking-[0.5em]'}
                maxLength={6} required autoFocus />
              <button type="submit" disabled={code.length < 6}
                className="w-full py-3 bg-amber/10 hover:bg-amber/20 border border-amber/40 text-amber text-sm font-bold tracking-widest rounded transition-all disabled:opacity-50">
                ПОДТВЕРДИТЬ
              </button>
              <button type="button" onClick={() => setView('login')}
                className="w-full text-xs text-white/30 hover:text-white/60">← Назад</button>
            </form>
          )}

          {view === 'register' && (
            <form onSubmit={handleRegister} className="space-y-4" data-testid="register-form">
              <input type="email" placeholder="Email" value={email}
                onChange={(e) => setEmail(e.target.value)} className={inputCls} required />
              <input type="text" placeholder="Имя пользователя" value={username}
                onChange={(e) => setUsername(e.target.value)} className={inputCls} required />
              <div className="relative">
                <input type={showPwd ? 'text' : 'password'} placeholder="Пароль"
                  value={password} onChange={(e) => setPassword(e.target.value)}
                  className={inputCls + ' pr-10'} required minLength={8} />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/70">
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <button type="submit" disabled={isLoading}
                className="w-full py-3 bg-purple/10 hover:bg-purple/20 border border-purple/40 text-purple text-sm font-bold tracking-widest rounded transition-all disabled:opacity-50">
                {isLoading ? 'СОЗДАНИЕ...' : 'СОЗДАТЬ АККАУНТ'}
              </button>
            </form>
          )}

          {/* Switch */}
          <div className="text-center text-xs text-white/30 pt-2">
            {view === 'login' ? (
              <>Нет аккаунта?{' '}
                <button onClick={() => setView('register')} className="text-cyan hover:text-cyan/80">
                  Регистрация
                </button>
              </>
            ) : view === 'register' ? (
              <>Уже есть аккаунт?{' '}
                <button onClick={() => setView('login')} className="text-cyan hover:text-cyan/80">
                  Войти
                </button>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
