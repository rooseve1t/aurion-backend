import { Activity } from 'lucide-react'
import clsx from 'clsx'

type MetricWidgetProps = {
  label: string
  value: string | number
  subValue?: string
  trend?: string
  color?: 'amber' | 'green' | 'red'
}

const colorMap = {
  amber: 'text-[var(--amber)]',
  green: 'text-[var(--green)]',
  red: 'text-[var(--red)]',
}

export function MetricWidget({ label, value, subValue, trend, color = 'amber' }: MetricWidgetProps) {
  return (
    <div className="bg-white/[0.02] border border-white/5 p-3 rounded-lg flex flex-col gap-1 hover:border-white/10 transition-all">
      <span className="text-[8px] font-display font-bold uppercase tracking-widest text-slate-500">{label}</span>
      <div className="flex items-baseline gap-2">
        <span className={clsx('text-xl font-mono font-bold tracking-tight', colorMap[color])}>{value}</span>
        {subValue && <span className="text-[10px] text-slate-500 font-mono">{subValue}</span>}
      </div>
      {trend && (
        <div className="flex items-center gap-1">
          <Activity className={clsx('w-2 h-2', trend.startsWith('+') ? 'text-[var(--green)]' : 'text-[var(--red)]')} />
          <span className={clsx('text-[8px] font-mono font-bold', trend.startsWith('+') ? 'text-[var(--green)]' : 'text-[var(--red)]')}>{trend}</span>
        </div>
      )}
    </div>
  )
}
