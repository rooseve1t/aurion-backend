import React from 'react'
import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  unit?: string
  icon?: LucideIcon
  trend?: 'up' | 'down' | 'stable'
  color?: 'cyan' | 'purple' | 'green' | 'red' | 'amber'
  progress?: number
  description?: string
}

export function MetricCard({ 
  title, 
  value, 
  unit, 
  icon: Icon, 
  trend, 
  color = 'cyan',
  progress,
  description 
}: MetricCardProps) {
  const colorClasses = {
    cyan: 'text-[var(--aurion-cyan)]',
    purple: 'text-[var(--aurion-purple)]',
    green: 'text-[var(--aurion-green-dim)]',
    red: 'text-[var(--aurion-error)]',
    amber: 'text-[var(--aurion-warning)]',
  }

  const bgColorClasses = {
    cyan: 'bg-[var(--aurion-cyan)]/10 border-[var(--aurion-cyan)]/20',
    purple: 'bg-[var(--aurion-purple)]/10 border-[var(--aurion-purple)]/20',
    green: 'bg-[var(--aurion-green-dim)]/10 border-[var(--aurion-green-dim)]/20',
    red: 'bg-[var(--aurion-error)]/10 border-[var(--aurion-error)]/20',
    amber: 'bg-[var(--aurion-warning)]/10 border-[var(--aurion-warning)]/20',
  }

  return (
    <div className="aurion-card p-6 relative overflow-hidden group hover:scale-[1.02] transition-all duration-300">
      {/* Background decoration */}
      <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
        {Icon && <Icon size={64} />}
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h4 className="aurion-label text-[10px] uppercase tracking-widest text-[var(--aurion-text-muted)]">
            {title}
          </h4>
          {Icon && (
            <div className={`w-8 h-8 rounded-lg ${bgColorClasses[color]} border flex items-center justify-center`}>
              <Icon className={`${colorClasses[color]}`} size={16} />
            </div>
          )}
        </div>

        {/* Value */}
        <div className="flex items-baseline gap-2 mb-4">
          <span className={`text-3xl font-black ${colorClasses[color]}`}>
            {value}
          </span>
          {unit && (
            <span className="aurion-mono text-sm text-[var(--aurion-text-muted)]">
              {unit}
            </span>
          )}
        </div>

        {/* Progress bar */}
        {progress !== undefined && (
          <div className="mb-4">
            <div className="w-full h-2 bg-[var(--aurion-bg-surface-high)] rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ${
                  color === 'cyan' ? 'bg-[var(--aurion-cyan)]' :
                  color === 'purple' ? 'bg-[var(--aurion-purple)]' :
                  color === 'green' ? 'bg-[var(--aurion-green-dim)]' :
                  color === 'red' ? 'bg-[var(--aurion-error)]' :
                  'bg-[var(--aurion-warning)]'
                }`}
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              />
            </div>
          </div>
        )}

        {/* Description */}
        {description && (
          <p className="aurion-mono text-[9px] text-[var(--aurion-text-muted)] leading-relaxed">
            {description}
          </p>
        )}

        {/* Trend indicator */}
        {trend && (
          <div className="flex items-center gap-1 mt-2">
            <div className={`w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent ${
              trend === 'up' ? 'border-b-[var(--aurion-green-dim)]' :
              trend === 'down' ? 'border-b-[var(--aurion-error)]' :
              'border-b-[var(--aurion-text-muted)]'
            }`} />
            <span className={`aurion-mono text-[8px] ${
              trend === 'up' ? 'text-[var(--aurion-green-dim)]' :
              trend === 'down' ? 'text-[var(--aurion-error)]' :
              'text-[var(--aurion-text-muted)]'
            }`}>
              {trend === 'up' ? 'ВВЕРХ' : trend === 'down' ? 'ВНИЗ' : 'СТАБИЛЬНО'}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
