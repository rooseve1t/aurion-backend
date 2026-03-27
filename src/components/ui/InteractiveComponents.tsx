import React, { useState } from 'react'
import { Check, X, AlertCircle, Info } from 'lucide-react'
import { useSound } from '@/services/soundEffects'

interface InteractiveButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  disabled?: boolean
  loading?: boolean
  className?: string
  soundType?: 'click' | 'activation' | 'navigation' | 'toggle'
}

export function InteractiveButton({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  onClick, 
  disabled = false, 
  loading = false,
  className = '',
  soundType = 'click'
}: InteractiveButtonProps) {
  const [isClicked, setIsClicked] = useState(false)
  const { playSound } = useSound()

  const handleClick = () => {
    if (!disabled && !loading) {
      setIsClicked(true)
      playSound(soundType)
      setTimeout(() => setIsClicked(false), 600)
      onClick?.()
    }
  }

  const baseClasses = 'aurion-btn aurion-interactive'
  const variantClasses = {
    primary: 'aurion-btn-primary',
    secondary: 'aurion-btn-secondary',
    danger: 'bg-[var(--aurion-error)] text-white hover:bg-[var(--aurion-error)]/90'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  const stateClasses = disabled ? 'opacity-50 cursor-not-allowed' : ''
  const loadingClasses = loading ? 'aurion-loading' : ''
  const clickClasses = isClicked ? 'aurion-bounce' : ''

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${stateClasses} ${loadingClasses} ${clickClasses} ${className}`}
      onClick={handleClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          Загрузка...
        </span>
      ) : (
        children
      )}
    </button>
  )
}

interface InteractiveCardProps {
  children: React.ReactNode
  hover?: boolean
  clickable?: boolean
  onClick?: () => void
  className?: string
  soundType?: 'click' | 'navigation' | 'activation'
}

export function InteractiveCard({ 
  children, 
  hover = true, 
  clickable = false, 
  onClick, 
  className = '',
  soundType = 'navigation'
}: InteractiveCardProps) {
  const [isClicked, setIsClicked] = useState(false)
  const { playSound } = useSound()

  const handleClick = () => {
    if (clickable) {
      setIsClicked(true)
      playSound(soundType)
      setTimeout(() => setIsClicked(false), 600)
      onClick?.()
    }
  }

  const baseClasses = 'aurion-card'
  const hoverClasses = hover ? 'aurion-glow-hover' : ''
  const clickableClasses = clickable ? 'cursor-pointer' : ''
  const clickClasses = isClicked ? 'aurion-scale-in' : ''

  return (
    <div
      className={`${baseClasses} ${hoverClasses} ${clickableClasses} ${clickClasses} ${className}`}
      onClick={handleClick}
    >
      {children}
    </div>
  )
}

interface InteractiveToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function InteractiveToggle({ 
  checked, 
  onChange, 
  label, 
  disabled = false, 
  size = 'md' 
}: InteractiveToggleProps) {
  const [isAnimating, setIsAnimating] = useState(false)
  const { playSound } = useSound()

  const handleClick = () => {
    if (!disabled) {
      setIsAnimating(true)
      playSound('toggle')
      onChange(!checked)
      setTimeout(() => setIsAnimating(false), 300)
    }
  }

  const sizeClasses = {
    sm: 'w-8 h-4',
    md: 'w-12 h-6',
    lg: 'w-16 h-8'
  }

  const dotSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-5 h-5',
    lg: 'w-7 h-7'
  }

  return (
    <div className="flex items-center gap-3">
      <button
        className={`aurion-toggle ${sizeClasses[size]} ${checked ? 'active' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${isAnimating ? 'aurion-bounce' : ''}`}
        onClick={handleClick}
        disabled={disabled}
      >
        <div className={`aurion-toggle-dot ${dotSizeClasses[size]} ${checked ? 'translate-x-full' : 'translate-x-0'}`} />
      </button>
      {label && (
        <span className={`aurion-label ${disabled ? 'text-[var(--aurion-text-muted)]' : ''}`}>
          {label}
        </span>
      )}
    </div>
  )
}

interface InteractiveCheckboxProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
  indeterminate?: boolean
}

export function InteractiveCheckbox({ 
  checked, 
  onChange, 
  label, 
  disabled = false, 
  indeterminate = false 
}: InteractiveCheckboxProps) {
  const [isAnimating, setIsAnimating] = useState(false)
  const { playSound } = useSound()

  const handleClick = () => {
    if (!disabled) {
      setIsAnimating(true)
      playSound('click')
      onChange(!checked)
      setTimeout(() => setIsAnimating(false), 300)
    }
  }

  return (
    <div className="flex items-center gap-3">
      <button
        className={`aurion-checkbox ${checked ? 'checked' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${isAnimating ? 'aurion-bounce' : ''}`}
        onClick={handleClick}
        disabled={disabled}
      >
        {indeterminate && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-2 h-0.5 bg-white" />
          </div>
        )}
      </button>
      {label && (
        <span className={`aurion-label ${disabled ? 'text-[var(--aurion-text-muted)]' : ''}`}>
          {label}
        </span>
      )}
    </div>
  )
}

interface InteractiveInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label?: string
  error?: string
  success?: string
  disabled?: boolean
  type?: 'text' | 'email' | 'password'
  icon?: React.ReactNode
}

export function InteractiveInput({ 
  value, 
  onChange, 
  placeholder, 
  label, 
  error, 
  success, 
  disabled = false, 
  type = 'text',
  icon
}: InteractiveInputProps) {
  const [isFocused, setIsFocused] = useState(false)
  const [hasValue, setHasValue] = useState(false)
  const { playSound } = useSound()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value)
    setHasValue(e.target.value.length > 0)
    if (e.target.value.length > value.length) {
      playSound('typing')
    }
  }

  const handleFocus = () => {
    setIsFocused(true)
    playSound('navigation')
  }
  
  const handleBlur = () => setIsFocused(false)

  const inputClasses = `
    aurion-input w-full
    ${isFocused ? 'aurion-glow-hover' : ''}
    ${error ? 'border-[var(--aurion-error)]' : ''}
    ${success ? 'border-[var(--aurion-green-dim)]' : ''}
    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
  `

  return (
    <div className="relative">
      {label && (
        <label className={`aurion-label block mb-2 ${isFocused ? 'text-[var(--aurion-cyan)]' : ''}`}>
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--aurion-text-muted)]">
            {icon}
          </div>
        )}
        <input
          type={type}
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          className={`${inputClasses} ${icon ? 'pl-10' : ''}`}
        />
        {error && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[var(--aurion-error)]">
            <X size={16} />
          </div>
        )}
        {success && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[var(--aurion-green-dim)]">
            <Check size={16} />
          </div>
        )}
      </div>
      {error && (
        <p className="aurion-mono text-xs text-[var(--aurion-error)] mt-1 flex items-center gap-1">
          <AlertCircle size={12} />
          {error}
        </p>
      )}
      {success && (
        <p className="aurion-mono text-xs text-[var(--aurion-green-dim)] mt-1 flex items-center gap-1">
          <Check size={12} />
          {success}
        </p>
      )}
    </div>
  )
}

interface InteractiveTooltipProps {
  content: string
  children: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export function InteractiveTooltip({ 
  content, 
  children, 
  position = 'top' 
}: InteractiveTooltipProps) {
  const { playSound } = useSound()

  const handleMouseEnter = () => {
    playSound('navigation')
  }

  return (
    <div 
      className="aurion-tooltip" 
      data-tooltip={content}
      onMouseEnter={handleMouseEnter}
    >
      {children}
    </div>
  )
}

interface InteractiveBadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  pulse?: boolean
}

export function InteractiveBadge({ 
  children, 
  variant = 'default', 
  size = 'md', 
  pulse = false 
}: InteractiveBadgeProps) {
  const variantClasses = {
    default: 'bg-[var(--aurion-cyan)]',
    success: 'bg-[var(--aurion-green-dim)]',
    warning: 'bg-[var(--aurion-warning)]',
    error: 'bg-[var(--aurion-error)]'
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[8px]',
    md: 'px-3 py-1 text-[10px]',
    lg: 'px-4 py-1.5 text-[12px]'
  }

  return (
    <span className={`aurion-badge ${variantClasses[variant]} ${sizeClasses[size]} ${pulse ? 'aurion-pulse' : ''}`}>
      {children}
    </span>
  )
}
