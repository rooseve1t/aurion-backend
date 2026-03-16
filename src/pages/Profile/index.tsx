import { useState } from 'react'
import { User, Shield, Key, Bell } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, loadUser } = useAuthStore()
  const [tab, setTab] = useState<'profile' | '2fa'>('profile')
  const [qr, setQr] = useState('')
  const [secret, setSecret] = useState('')
  const [code2fa, setCode2fa] = useState('')

  const handleEnable2fa = async () => {
    try {
      const data = await authService.enable2fa()
      setQr(data.qr_code)
      setSecret(data.secret)
    } catch { toast.error('Ошибка') }
  }

  const handleVerify2fa = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await authService.verify2fa(code2fa)
      await loadUser()
      toast.success('2FA включена')
      setQr('')
    } catch { toast.error('Неверный код') }
  }

  const handleDisable2fa = async () => {
    if (!code2fa) return
    try {
      await authService.disable2fa(code2fa)
      await loadUser()
      toast.success('2FA отключена')
      setCode2fa('')
    } catch { toast.error('Неверный код') }
  }

  const inputCls = 'w-full bg-surface border border-white/10 rounded px-3 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan/40'

  return (
    <div className="p-4 max-w-xl mx-auto space-y-4">
      <div className="flex items-center gap-3">
        <User size={20} className="text-cyan" />
        <div className="font-bold text-sm tracking-wider">ПРОФИЛЬ</div>
      </div>

      <div className="flex gap-1 bg-card border border-white/10 rounded p-1 w-fit">
        {(['profile', '2fa'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 text-xs rounded transition-all ${tab === t ? 'bg-cyan/15 text-cyan' : 'text-white/40 hover:text-white/70'}`}>
            {t === 'profile' ? 'Данные' : '2FA'}
          </button>
        ))}
      </div>

      {tab === 'profile' && user && (
        <div className="bg-card border border-white/8 rounded-lg p-5 space-y-4">
          <div className="w-12 h-12 rounded-full bg-cyan/10 border border-cyan/20 flex items-center justify-center text-cyan font-bold text-lg">
            {user.username[0].toUpperCase()}
          </div>
          {[
            { label: 'Username', value: user.username },
            { label: 'Email',    value: user.email },
            { label: 'Роль',     value: user.role.toUpperCase() },
          ].map((f) => (
            <div key={f.label} className="space-y-1">
              <label className="text-[10px] text-white/30 tracking-wider">{f.label}</label>
              <div className="text-sm text-white/80 bg-surface border border-white/8 rounded px-3 py-2">{f.value}</div>
            </div>
          ))}
        </div>
      )}

      {tab === '2fa' && (
        <div className="bg-card border border-white/8 rounded-lg p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-amber" />
            <span className="text-sm font-bold">Двухфакторная аутентификация</span>
            <span className={`ml-auto text-[10px] px-2 py-0.5 rounded ${user?.two_factor_enabled ? 'bg-emerald/10 text-emerald' : 'bg-white/5 text-white/30'}`}>
              {user?.two_factor_enabled ? 'ВКЛЮЧЕНА' : 'ВЫКЛЮЧЕНА'}
            </span>
          </div>

          {!user?.two_factor_enabled && !qr && (
            <button onClick={handleEnable2fa}
              className="w-full py-2.5 bg-amber/10 hover:bg-amber/20 border border-amber/30 text-amber text-xs font-bold rounded tracking-wider transition-all">
              ВКЛЮЧИТЬ 2FA
            </button>
          )}

          {qr && (
            <div className="space-y-3">
              <p className="text-xs text-white/50">Отсканируйте QR-код в приложении-аутентификаторе:</p>
              <div className="flex justify-center">
                <img src={qr} alt="QR" className="w-36 h-36 rounded" />
              </div>
              <p className="text-[10px] text-white/30 text-center font-mono">{secret}</p>
              <form onSubmit={handleVerify2fa} className="flex gap-2">
                <input value={code2fa} onChange={(e) => setCode2fa(e.target.value)}
                  placeholder="Код подтверждения" className={inputCls} maxLength={6} />
                <button type="submit" className="px-4 bg-emerald/10 border border-emerald/30 text-emerald text-xs rounded">OK</button>
              </form>
            </div>
          )}

          {user?.two_factor_enabled && !qr && (
            <div className="space-y-3">
              <p className="text-xs text-white/50">Введите код для отключения 2FA:</p>
              <div className="flex gap-2">
                <input value={code2fa} onChange={(e) => setCode2fa(e.target.value)}
                  placeholder="6-значный код" className={inputCls} maxLength={6} />
                <button onClick={handleDisable2fa}
                  className="px-4 bg-danger/10 border border-danger/30 text-danger text-xs rounded">Откл.</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
