import { useEffect, useState } from 'react'
import { CreditCard, Check, Zap, Crown, Star, X } from 'lucide-react'
import { useSubscriptionStore } from '@/store/subscriptionStore'
import { formatDate, formatMoney, daysLeft } from '@/utils'
import type { Tariff } from '@/types'
import toast from 'react-hot-toast'

const TIER_ICONS = { Free: Star, Basic: Zap, Pro: Crown }
const TIER_COLORS = { Free: 'text-white/60 border-white/20', Basic: 'text-cyan border-cyan/40', Pro: 'text-amber border-amber/40' }
const TIER_BG = { Free: 'bg-white/5', Basic: 'bg-cyan/5', Pro: 'bg-amber/5' }

function TariffCard({ tariff, current, onSelect }: { tariff: Tariff; current: boolean; onSelect: (t: Tariff) => void }) {
  const colorCls = TIER_COLORS[tariff.name as keyof typeof TIER_COLORS] ?? 'text-white/60 border-white/20'
  const bgCls = TIER_BG[tariff.name as keyof typeof TIER_BG] ?? 'bg-white/5'
  const Icon = TIER_ICONS[tariff.name as keyof typeof TIER_ICONS] ?? Star
  const f = tariff.features

  return (
    <div className={`relative rounded-lg border p-5 space-y-4 transition-all ${colorCls} ${bgCls} ${current ? 'ring-1 ring-current' : 'hover:ring-1 hover:ring-current/30 cursor-pointer'}`}
      data-testid="subscription-card"
      onClick={() => !current && onSelect(tariff)}>
      {current && (
        <div className="absolute -top-2 right-3 bg-emerald text-[9px] text-black font-bold px-2 py-0.5 rounded tracking-wider">
          АКТИВЕН
        </div>
      )}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Icon size={16} />
            <span className="font-bold tracking-wider">{tariff.name.toUpperCase()}</span>
          </div>
          <div className="text-2xl font-bold mt-1">
            {tariff.price === 0 ? 'Бесплатно' : formatMoney(tariff.price)}
            {tariff.price > 0 && <span className="text-sm font-normal text-white/40">/мес</span>}
          </div>
        </div>
      </div>
      <ul className="space-y-1.5">
        {[
          { key: 'voice',   label: 'Голосовой ассистент' },
          { key: 'finance', label: 'Финансовый модуль' },
          { key: 'agents',  label: 'Агенты' },
          { key: 'osint',   label: 'OSINT' },
          { key: 'quantum', label: 'Квантовый модуль' },
        ].map(({ key, label }) => (
          <li key={key} className="flex items-center gap-2 text-xs">
            {f[key as keyof typeof f]
              ? <Check size={12} className="text-emerald flex-shrink-0" />
              : <X size={12} className="text-white/20 flex-shrink-0" />}
            <span className={f[key as keyof typeof f] ? '' : 'text-white/30'}>{label}</span>
          </li>
        ))}
        <li className="text-xs text-white/50">
          Память: {f.memory_limit === -1 ? '∞' : f.memory_limit} записей
        </li>
        <li className="text-xs text-white/50">
          Устройства: {f.devices_limit === -1 ? '∞' : f.devices_limit}
        </li>
      </ul>
      {!current && tariff.price > 0 && (
        <button className={`w-full py-2 rounded text-xs font-bold tracking-wider border transition-all hover:opacity-90 ${colorCls}`}>
          ПОДКЛЮЧИТЬ
        </button>
      )}
    </div>
  )
}

export default function PaymentsPage() {
  const { tariffs, current, history, fetchTariffs, fetchCurrent, fetchHistory, subscribe, cancel } = useSubscriptionStore()
  const [tab, setTab] = useState<'plans' | 'history'>('plans')
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    fetchTariffs()
    fetchCurrent()
    fetchHistory()
  }, [])

  const handleSelect = async (tariff: Tariff) => {
    if (tariff.price === 0) return
    try {
      const url = await subscribe(tariff.id)
      window.location.href = url
    } catch {
      toast.error('Ошибка при создании подписки')
    }
  }

  const handleCancel = async () => {
    if (!current?.id) return
    setCancelling(true)
    try {
      await cancel(current.id)
    } finally {
      setCancelling(false)
    }
  }

  const days = daysLeft(current?.end_date ?? null)

  return (
    <div className="p-4 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <CreditCard size={20} className="text-cyan" />
        <div>
          <div className="font-bold text-sm tracking-wider">ПОДПИСКА И ПЛАТЕЖИ</div>
          {current?.status === 'active' && (
            <div className="text-[10px] text-emerald">
              {current.tariff?.name ?? ''} · {days} дней осталось
            </div>
          )}
        </div>
      </div>

      {/* Active sub info */}
      {current?.status === 'active' && (
        <div className="bg-card border border-emerald/20 rounded-lg p-4 flex items-center justify-between">
          <div className="space-y-0.5">
            <div className="text-sm font-bold text-emerald">{current.tariff?.name ?? 'Подписка активна'}</div>
            <div className="text-[10px] text-white/40">
              до {current.end_date ? formatDate(current.end_date) : '—'}
              {current.auto_renew && ' · автопродление'}
            </div>
          </div>
          <button onClick={handleCancel} disabled={cancelling}
            className="text-xs text-danger/60 hover:text-danger border border-danger/20 hover:border-danger/40 px-3 py-1.5 rounded transition-all disabled:opacity-50">
            {cancelling ? 'Отмена...' : 'Отменить'}
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-card border border-white/10 rounded p-1 w-fit">
        {(['plans', 'history'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 text-xs rounded transition-all ${tab === t ? 'bg-cyan/15 text-cyan' : 'text-white/40 hover:text-white/70'}`}>
            {t === 'plans' ? 'Тарифы' : 'История'}
          </button>
        ))}
      </div>

      {tab === 'plans' && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {tariffs.map((t) => (
            <TariffCard
              key={t.id}
              tariff={t}
              current={current?.tariff_id === t.id && current.status === 'active'}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}

      {tab === 'history' && (
        <div className="space-y-2">
          {history.length === 0 ? (
            <div className="text-center py-8 text-white/20 text-sm">История платежей пуста</div>
          ) : history.map((p) => (
            <div key={p.id} className="bg-card border border-white/8 rounded-lg p-3 flex items-center gap-4">
              <div className={`text-[10px] px-2 py-0.5 rounded ${p.status === 'succeeded' ? 'bg-emerald/10 text-emerald' : 'bg-danger/10 text-danger'}`}>
                {p.status}
              </div>
              <div className="flex-1 text-sm text-white/70 truncate">{p.description}</div>
              <div className="text-sm font-bold text-cyan">{formatMoney(p.amount)}</div>
              <div className="text-[10px] text-white/30">{formatDate(p.created_at)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
