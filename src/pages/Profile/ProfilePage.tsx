import { useState } from 'react'
import { User, Shield, Key, ChevronRight } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import { useToast } from '@/hooks/useToast'
import { formatDate } from '@/utils'
import styles from './ProfilePage.module.css'

export function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const toast = useToast()
  const [show2FASetup, setShow2FASetup] = useState(false)
  const [qrData, setQrData]    = useState<{ qr_code: string; secret: string } | null>(null)
  const [code2FA, setCode2FA]  = useState('')
  const [loading2FA, setLoading2FA] = useState(false)

  const handle2FAEnable = async () => {
    setLoading2FA(true)
    try {
      const data = await authService.setup2fa()
      setQrData(data)
      setShow2FASetup(true)
    } catch { toast.error('Ошибка включения 2FA') }
    finally { setLoading2FA(false) }
  }

  const handle2FAConfirm = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await authService.confirmEnable2fa(code2FA)
      if (user) setUser({ ...user, is_2fa_enabled: true })
      setShow2FASetup(false)
      setQrData(null)
      setCode2FA('')
      toast.success('2FA включена')
    } catch { toast.error('Неверный код') }
  }

  const handle2FADisable = async () => {
    const code = prompt('Введите код 2FA для отключения:')
    if (!code) return
    try {
      await authService.disable2fa(code)
      if (user) setUser({ ...user, is_2fa_enabled: false })
      toast.success('2FA отключена')
    } catch { toast.error('Неверный код') }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <User size={20} color="var(--cyan)" />
        <span className={styles.title}>ПРОФИЛЬ</span>
      </div>

      {/* User info */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>ИНФОРМАЦИЯ</div>
        <div className={styles.infoGrid}>
          <InfoRow label="EMAIL"    value={user?.email || '—'} />
          <InfoRow label="ИМЯ"     value={user?.username || '—'} />
          <InfoRow label="РОЛЬ"    value={user?.role?.toUpperCase() || '—'} />
          <InfoRow label="СТАТУС"  value={user?.is_active ? 'АКТИВЕН' : 'ЗАБЛОКИРОВАН'} />
          <InfoRow label="АККАУНТ" value={user?.created_at ? formatDate(user.created_at) : '—'} />
        </div>
      </div>

      {/* Security */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>БЕЗОПАСНОСТЬ</div>
        <div className={styles.secPanel}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <Shield size={18} color={user?.is_2fa_enabled ? 'var(--green)' : 'var(--text-muted)'} />
              <div>
                <div className={styles.secTitle}>Двухфакторная аутентификация</div>
                <div className={styles.secSub}>
                  {user?.is_2fa_enabled ? '✓ ВКЛЮЧЕНА' : 'ВЫКЛЮЧЕНА — Рекомендуем включить'}
                </div>
              </div>
            </div>
            {user?.is_2fa_enabled ? (
              <button className="btn btn-danger" onClick={handle2FADisable}>ОТКЛЮЧИТЬ</button>
            ) : (
              <button className="btn btn-cyan" onClick={handle2FAEnable} disabled={loading2FA}>
                <Key size={14} /> ВКЛЮЧИТЬ
              </button>
            )}
          </div>

          {show2FASetup && qrData && (
            <div className={styles.qrSetup}>
              <p className={styles.hint}>
                Отсканируйте QR-код в Google Authenticator или Authy
              </p>
              <img src={qrData.qr_code} alt="QR 2FA" className={styles.qr} />
              <div className={styles.secret}>
                <span className="label">СЕКРЕТНЫЙ КЛЮЧ:</span>
                <code className={styles.secretCode}>{qrData.secret}</code>
              </div>
              <form onSubmit={handle2FAConfirm} className={styles.codeForm}>
                <input className="input" value={code2FA}
                  onChange={(e) => setCode2FA(e.target.value)}
                  placeholder="Код из приложения" maxLength={6} autoFocus />
                <button type="submit" className="btn btn-cyan">ПОДТВЕРДИТЬ</button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.infoRow}>
      <span className={styles.infoLabel}>{label}</span>
      <span className={styles.infoValue}>{value}</span>
      <ChevronRight size={12} color="var(--border)" />
    </div>
  )
}
