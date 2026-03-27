import React from 'react'
import { LucideIcon } from 'lucide-react'

interface QuickActionProps {
  label: string
  icon: LucideIcon
  color?: 'cyan' | 'purple' | 'green' | 'red' | 'amber'
  onClick?: () => void
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  description?: string
}

export function QuickAction({ 
  label, 
  icon: Icon, 
  color = 'cyan',
  onClick,
  disabled = false,
  size = 'md',
  description
}: QuickActionProps) {
  const colorClasses = {
    cyan: 'text-[var(--aurion-cyan)] hover:text-[var(--aurion-cyan)] hover:bg-[var(--aurion-cyan)]/10 hover:border-[var(--aurion-cyan)]/30',
    purple: 'text-[var(--aurion-purple)] hover:text-[var(--aurion-purple)] hover:bg-[var(--aurion-purple)]/10 hover:border-[var(--aurion-purple)]/30',
    green: 'text-[var(--aurion-green-dim)] hover:text-[var(--aurion-green-dim)] hover:bg-[var(--aurion-green-dim)]/10 hover:border-[var(--aurion-green-dim)]/30',
    red: 'text-[var(--aurion-error)] hover:text-[var(--aurion-error)] hover:bg-[var(--aurion-error)]/10 hover:border-[var(--aurion-error)]/30',
    amber: 'text-[var(--aurion-warning)] hover:text-[var(--aurion-warning)] hover:bg-[var(--aurion-warning)]/10 hover:border-[var(--aurion-warning)]/30',
  }

  const sizeClasses = {
    sm: 'p-3 gap-2',
    md: 'p-4 gap-3',
    lg: 'p-6 gap-4',
  }

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24,
  }

  return (
    <button
      className={`
        aurion-card flex flex-col items-center justify-center transition-all duration-300 group
        ${colorClasses[color]}
        ${sizeClasses[size]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105'}
        relative overflow-hidden
      `}
      onClick={onClick}
      disabled={disabled}
    >
      {/* Hover effect background */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent to-black/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      {/* Icon */}
      <div className="relative z-10">
        <Icon size={iconSizes[size]} />
      </div>
      
      {/* Label */}
      <span className="aurion-mono text-[10px] uppercase tracking-widest text-center relative z-10">
        {label}
      </span>
      
      {/* Description */}
      {description && (
        <span className="aurion-mono text-[8px] text-[var(--aurion-text-muted)] text-center relative z-10 mt-1">
          {description}
        </span>
      )}
      
      {/* Active indicator */}
      <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-current opacity-0 group-hover:opacity-100 transition-opacity" />
    </button>
  )
}
