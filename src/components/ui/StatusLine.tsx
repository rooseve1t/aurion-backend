import React from 'react'
import { LucideIcon } from 'lucide-react'

interface StatusLineProps {
  label: string
  status: 'online' | 'offline' | 'warning'
  icon?: LucideIcon
  value?: string | number
}

export function StatusLine({ label, status, icon: Icon, value }: StatusLineProps) {
  const statusColors = {
    online: 'text-[var(--aurion-green-dim)] border-[var(--aurion-green-dim)]',
    offline: 'text-[var(--aurion-error)] border-[var(--aurion-error)]',
    warning: 'text-[var(--aurion-warning)] border-[var(--aurion-warning)]',
  }

  const statusText = {
    online: 'АКТИВЕН',
    offline: 'ОФЛАЙН',
    warning: 'ПРЕДУПРЕЖДЕНИЕ',
  }

  return (
    <div className="flex items-center justify-between p-3 aurion-card">
      <div className="flex items-center gap-3">
        {Icon && <Icon className={`${statusColors[status]}`} size={16} />}
        <div>
          <span className="aurion-label text-xs">{label}</span>
          <div className={`aurion-mono text-xs font-bold ${statusColors[status]}`}>
            {statusText[status]}
          </div>
        </div>
      </div>
      {value && (
        <span className="aurion-mono text-xs text-[var(--aurion-text-muted)]">
          {value}
        </span>
      )}
    </div>
  )
}
