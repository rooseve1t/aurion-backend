import { useState, useEffect } from 'react'
import { CreditCard, Check, X, ExternalLink } from 'lucide-react'
import { paymentsService } from '@/services/payments'
import { useToast } from '@/hooks/useToast'
import type { Tariff, Subscription, Payment } from '@/types'
import { formatDate, formatRub } from '@/utils'
import styles from './PaymentsPage.module.css'

const FEATURE_LABELS: Record<string, string> = {
  voice: 'Голосовой ассистент',
  osint: 'OSINT-разведка',
  quantum: 'Квантовые вычисления',
  finance: 'Финансовый модуль',
  agents: 'Агенты и автоматизация',
  evolution: 'Саморазвитие системы',
}

export function PaymentsPage() {
  const [tariffs, setTariffs]         = useState<Tariff[]>([])
  const [subscription, setSubscription] = useState<(Subscription & { tariff?: Tariff; days_left?: number }) | null>(null)
  const [payments, setPayments]       = useState<Payment[]>([])
  const [tab, setTab]                 = useState<'plans' | 'history'>('plans')
  const [loading, setLoading]         = useState(false)
  const [subscribing, setSubscribing] = useState<number | null>(null)
  const toast = useToast()

  useEffect(() => {
    setLoading(true)
    Promise.all([
      paymentsService.listTariffs(),
      paymentsService.currentSubscription().catch(() => null),
      paymentsService.listPayments().catch(() => ({ payments: [], total: 0 })),
    ]).then(([t, s, p]) => {
      setTariffs(t)
      setSubscription(s)
      setPayments(p.payments)
    }).catch(() => toast.error('Ошибка загрузки'))
    .finally(() => setLoading(false))
  }, [])

  const handleSubscribe = async (tariffId: number, tariffName: string) => {
    setSubscribing(tariffId)
    try {
      const res = await paymentsService.subscribe(tariffId)
      toast.success(`Переход к оплате ${tariffName}...`)
      window.open(res.confirmation_url, '_blank')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка'
      toast.error(msg)
    } finally {
      setSubscribing(null)
    }
  }

  const handleCancel = async () => {
    if (!subscription) return
    if (!confirm('Отменить подписку? Доступ сохранится до конца периода.')) return
    try {
      await paymentsService.cancelSubscription(subscription.id)
      setSubscription((s) => s ? { ...s, status: 'cancelled', auto_renew: false } : s)
      toast.success('Подписка отменена')
    } catch { toast.error('Ошибка отмены') }
  }

  const currentTariffId = subscription?.tariff?.id

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <CreditCard size={20} color="var(--cyan)" />
          <span className={styles.title}>ПОДПИСКА И ПЛАТЕЖИ</span>
        </div>
        <div className={styles.tabs}>
          <button className={`${styles.tab} ${tab === 'plans' ? styles.activeTab : ''}`}
            onClick={() => setTab('plans')}>ТАРИФЫ</button>
          <button className={`${styles.tab} ${tab === 'history' ? styles.activeTab : ''}`}
            onClick={() => setTab('history')}>ИСТОРИЯ</button>
        </div>
      </div>

      {/* Current subscription */}
      {subscription && subscription.status === 'active' && (
        <div className={styles.currentSub} data-testid="subscription-banner">
          <div>
            <div className={styles.subName}>{subscription.tariff?.name || 'Pro'}</div>
            <div className={styles.subInfo}>
              Активна до {subscription.end_date ? formatDate(subscription.end_date) : '—'}
              {subscription.days_left !== undefined && ` · осталось ${subscription.days_left} дн.`}
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {subscription.auto_renew && (
              <span className={styles.renewBadge}>АВТОПРОДЛЕНИЕ</span>
            )}
            <button className="btn btn-danger" onClick={handleCancel}>
              <X size={12} /> ОТМЕНИТЬ
            </button>
          </div>
        </div>
      )}

      {loading && <div className={styles.loading}>ЗАГРУЗКА...</div>}

      {/* ─── Tariffs ─── */}
      {tab === 'plans' && !loading && (
        <div className={styles.tariffGrid}>
          {tariffs.map((tariff) => {
            const isCurrent = tariff.id === currentTariffId
            const isPro = tariff.name === 'Pro'
            return (
              <div
                key={tariff.id}
                className={`${styles.tariffCard} ${isPro ? styles.proPlan : ''} ${isCurrent ? styles.currentPlan : ''}`}
                data-testid="tariff-card"
              >
                {isPro && <div className={styles.badge}>РЕКОМЕНДУЕМ</div>}
                <div className={styles.tariffName}>{tariff.name.toUpperCase()}</div>
                <div className={styles.tariffPrice}>
                  {Number(tariff.price) === 0 ? 'БЕСПЛАТНО' : (
                    <>{formatRub(tariff.price)}<span className={styles.period}>/мес</span></>
                  )}
                </div>
                <div className={styles.features}>
                  {Object.entries(FEATURE_LABELS).map(([key, label]) => {
                    const val = tariff.features?.[key]
                    const enabled = val === true || (typeof val === 'number' && val > 0)
                    return (
                      <div key={key} className={`${styles.feature} ${enabled ? styles.featureOn : ''}`}>
                        {enabled ? <Check size={12} color="var(--green)" /> : <X size={12} color="var(--text-muted)" />}
                        <span>{label}</span>
                        {typeof val === 'number' && val > 0 && val !== -1 && (
                          <span style={{ color: 'var(--text-muted)', marginLeft: 'auto' }}>{val}</span>
                        )}
                      </div>
                    )
                  })}
                  <div className={styles.feature}>
                    <Check size={12} color={tariff.features?.memory_limit === -1 ? 'var(--green)' : 'var(--amber)'} />
                    <span>Память</span>
                    <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '11px' }}>
                      {tariff.features?.memory_limit === -1 ? '∞' : tariff.features?.memory_limit} записей
                    </span>
                  </div>
                  <div className={styles.feature}>
                    <Check size={12} color={tariff.features?.devices_limit === -1 ? 'var(--green)' : 'var(--amber)'} />
                    <span>Устройства</span>
                    <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '11px' }}>
                      {tariff.features?.devices_limit === -1 ? '∞' : tariff.features?.devices_limit}
                    </span>
                  </div>
                </div>
                <button
                  className={`btn ${isCurrent ? 'btn-ghost' : 'btn-cyan'}`}
                  style={{ width: '100%', justifyContent: 'center' }}
                  disabled={isCurrent || !tariff.is_active || subscribing === tariff.id}
                  onClick={() => handleSubscribe(tariff.id, tariff.name)}
                >
                  {subscribing === tariff.id ? 'ОБРАБОТКА...' :
                   isCurrent ? '✓ ТЕКУЩИЙ' :
                   Number(tariff.price) === 0 ? 'ВЫБРАТЬ' : 'ПОДПИСАТЬСЯ'}
                  {!isCurrent && Number(tariff.price) > 0 && <ExternalLink size={12} />}
                </button>
              </div>
            )
          })}
        </div>
      )}

      {/* ─── Payment history ─── */}
      {tab === 'history' && !loading && (
        <div className={styles.historyList}>
          {payments.length === 0 && (
            <div className={styles.empty}>Нет истории платежей</div>
          )}
          {payments.map((p) => (
            <div key={p.id} className={styles.paymentRow} data-testid="payment-row">
              <div>
                <div className={styles.payDesc}>{p.description}</div>
                <div className={styles.payDate}>{formatDate(p.created_at)}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ fontWeight: 600 }}>{formatRub(p.amount)}</span>
                <span className={`${styles.payStatus} ${styles[p.status]}`}>
                  {p.status === 'succeeded' ? '✓ ОПЛАЧЕНО' :
                   p.status === 'failed'    ? '✗ ОШИБКА' :
                   p.status === 'refunded'  ? '↩ ВОЗВРАТ' : '... ОЖИДАНИЕ'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
