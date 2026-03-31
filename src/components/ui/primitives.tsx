/**
 * Базовые UI-примитивы для Aurion HUD
 */
import React from 'react'

// Card
export interface CardProps {
  children: React.ReactNode
  className?: string
}
export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`aurion-card p-4 ${className}`}>{children}</div>
  )
}

// Button
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}
export function Button({ children, variant = 'default', size = 'md', className = '', ...props }: ButtonProps) {
  const variantClass = {
    default: 'bg-[var(--aurion-cyan)]/20 border border-[var(--aurion-cyan)]/40 text-[var(--aurion-cyan)] hover:bg-[var(--aurion-cyan)]/30',
    outline: 'border border-[var(--aurion-cyan)]/40 text-[var(--aurion-cyan)] hover:bg-[var(--aurion-cyan)]/10',
    ghost: 'text-[var(--aurion-text-secondary)] hover:bg-white/5',
    destructive: 'bg-[var(--aurion-error)]/20 border border-[var(--aurion-error)]/40 text-[var(--aurion-error)] hover:bg-[var(--aurion-error)]/30',
  }[variant]
  const sizeClass = { sm: 'px-3 py-1 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' }[size]
  return (
    <button className={`aurion-mono rounded transition-all duration-200 disabled:opacity-50 ${variantClass} ${sizeClass} ${className}`} {...props}>
      {children}
    </button>
  )
}

// Badge
export interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error'
  className?: string
}
export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variantClass = {
    default: 'bg-[var(--aurion-cyan)]/20 text-[var(--aurion-cyan)] border-[var(--aurion-cyan)]/30',
    success: 'bg-[var(--aurion-green-dim)]/20 text-[var(--aurion-green-dim)] border-[var(--aurion-green-dim)]/30',
    warning: 'bg-[var(--aurion-warning)]/20 text-[var(--aurion-warning)] border-[var(--aurion-warning)]/30',
    error: 'bg-[var(--aurion-error)]/20 text-[var(--aurion-error)] border-[var(--aurion-error)]/30',
  }[variant]
  return (
    <span className={`aurion-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded border ${variantClass} ${className}`}>
      {children}
    </span>
  )
}

// Switch
export interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  label?: string
}
export function Switch({ checked, onChange, disabled = false, label }: SwitchProps) {
  return (
    <label className="flex items-center gap-2 cursor-pointer select-none">
      <button
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`relative w-10 h-5 rounded-full border transition-all duration-200 ${
          checked
            ? 'bg-[var(--aurion-cyan)]/30 border-[var(--aurion-cyan)]/60'
            : 'bg-white/5 border-white/20'
        } disabled:opacity-50`}
      >
        <span className={`absolute top-0.5 w-4 h-4 rounded-full transition-all duration-200 ${
          checked ? 'left-5 bg-[var(--aurion-cyan)]' : 'left-0.5 bg-white/40'
        }`} />
      </button>
      {label && <span className="aurion-mono text-xs text-[var(--aurion-text-secondary)]">{label}</span>}
    </label>
  )
}

// Progress
export interface ProgressProps {
  value: number
  max?: number
  color?: 'cyan' | 'green' | 'amber' | 'red'
  className?: string
}
export function Progress({ value, max = 100, color = 'cyan', className = '' }: ProgressProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const colorClass = {
    cyan: 'bg-[var(--aurion-cyan)]',
    green: 'bg-[var(--aurion-green-dim)]',
    amber: 'bg-[var(--aurion-warning)]',
    red: 'bg-[var(--aurion-error)]',
  }[color]
  return (
    <div className={`w-full h-2 bg-white/10 rounded-full overflow-hidden ${className}`}>
      <div className={`h-full rounded-full transition-all duration-500 ${colorClass}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

// Alert
export interface AlertProps {
  children: React.ReactNode
  variant?: 'info' | 'success' | 'warning' | 'error'
  className?: string
}
export function Alert({ children, variant = 'info', className = '' }: AlertProps) {
  const variantClass = {
    info: 'border-[var(--aurion-cyan)]/30 bg-[var(--aurion-cyan)]/5 text-[var(--aurion-cyan)]',
    success: 'border-[var(--aurion-green-dim)]/30 bg-[var(--aurion-green-dim)]/5 text-[var(--aurion-green-dim)]',
    warning: 'border-[var(--aurion-warning)]/30 bg-[var(--aurion-warning)]/5 text-[var(--aurion-warning)]',
    error: 'border-[var(--aurion-error)]/30 bg-[var(--aurion-error)]/5 text-[var(--aurion-error)]',
  }[variant]
  return (
    <div className={`aurion-mono text-xs p-3 rounded border ${variantClass} ${className}`}>
      {children}
    </div>
  )
}
