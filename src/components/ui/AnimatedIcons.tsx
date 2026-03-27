import React, { useEffect, useState } from 'react'
import { 
  Activity, 
  Brain, 
  Cpu, 
  Database, 
  Wifi, 
  WifiOff, 
  Shield, 
  Zap, 
  AlertCircle, 
  CheckCircle, 
  XCircle,
  Loader,
  Radio,
  Radar,
  Heart,
  Battery,
  Cloud,
  Download,
  Upload,
  RefreshCw,
  Power,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Volume2,
  VolumeX,
  Bell,
  BellOff,
  Star,
  StarOff,
  Moon,
  Sun,
  Globe,
  MapPin,
  Navigation,
  Compass,
  Target,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  Activity as ActivityIcon,
  Zap as ZapIcon,
  Radio as RadioIcon
} from 'lucide-react'

// Базовый компонент для анимированных иконок
export interface AnimatedIconProps {
  icon: React.ReactNode
  animation?: 'pulse' | 'spin' | 'bounce' | 'shake' | 'glow' | 'float' | 'rotate' | 'scale' | 'slide' | 'none'
  duration?: number
  size?: number
  color?: string
  className?: string
}

export function AnimatedIcon({ 
  icon, 
  animation = 'pulse', 
  duration = 2, 
  size = 24, 
  color = 'var(--aurion-cyan)', 
  className = '' 
}: AnimatedIconProps) {
  const animationClasses = {
    pulse: 'aurion-pulse',
    spin: 'animate-spin',
    bounce: 'aurion-bounce',
    shake: 'aurion-shake',
    glow: 'aurion-glow',
    float: 'aurion-float',
    rotate: 'aurion-rotate',
    scale: 'aurion-scale',
    slide: 'aurion-slide',
    none: ''
  }

  return (
    <div 
      className={`${animationClasses[animation]} ${className}`}
      style={{ 
        color, 
        fontSize: size,
        animationDuration: `${duration}s`
      }}
    >
      {icon}
    </div>
  )
}

// Статусный индикатор с анимацией
export interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'warning' | 'loading' | 'success' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  text?: string
  animated?: boolean
  className?: string
}

export function StatusIndicator({ 
  status, 
  size = 'md', 
  showText = true, 
  text, 
  animated = true,
  className = ''
}: StatusIndicatorProps) {
  const [isAnimating, setIsAnimating] = useState(animated)

  const statusConfig = {
    online: { 
      color: 'var(--aurion-green-dim)', 
      icon: <Wifi size={16} />,
      animation: 'pulse' as const,
      text: 'Онлайн'
    },
    offline: { 
      color: 'var(--aurion-text-muted)', 
      icon: <WifiOff size={16} />,
      animation: 'none' as const,
      text: 'Офлайн'
    },
    warning: { 
      color: 'var(--aurion-warning)', 
      icon: <AlertCircle size={16} />,
      animation: 'shake' as const,
      text: 'Предупреждение'
    },
    loading: { 
      color: 'var(--aurion-cyan)', 
      icon: <Loader size={16} />,
      animation: 'spin' as const,
      text: 'Загрузка'
    },
    success: { 
      color: 'var(--aurion-green-dim)', 
      icon: <CheckCircle size={16} />,
      animation: 'bounce' as const,
      text: 'Успешно'
    },
    error: { 
      color: 'var(--aurion-error)', 
      icon: <XCircle size={16} />,
      animation: 'shake' as const,
      text: 'Ошибка'
    }
  }

  const config = statusConfig[status]
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`${sizeClasses[size]} rounded-full flex items-center justify-center aurion-glass`}>
        <AnimatedIcon 
          icon={config.icon} 
          animation={isAnimating ? config.animation : 'none'}
          color={config.color}
          duration={2}
        />
      </div>
      {showText && (
        <span className="aurion-mono text-xs" style={{ color: config.color }}>
          {text || config.text}
        </span>
      )}
    </div>
  )
}

// Анимированный прогресс с иконкой
interface ProgressIconProps {
  value: number
  max?: number
  icon: React.ReactNode
  size?: number
  color?: string
  showPercentage?: boolean
  animated?: boolean
}

export function ProgressIcon({ 
  value, 
  max = 100, 
  icon, 
  size = 60, 
  color = 'var(--aurion-cyan)', 
  showPercentage = true,
  animated = true 
}: ProgressIconProps) {
  const [currentValue, setCurrentValue] = useState(0)
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setCurrentValue(percentage)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      setCurrentValue(percentage)
    }
  }, [percentage, animated])

  const circumference = 2 * Math.PI * ((size - 8) / 2)
  const offset = circumference - (currentValue / 100) * circumference

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={(size - 8) / 2}
          stroke="var(--aurion-bg-surface-high)"
          strokeWidth="4"
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={(size - 8) / 2}
          stroke={color}
          strokeWidth="4"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div style={{ color }}>
          {icon}
        </div>
        {showPercentage && (
          <span className="aurion-mono text-xs font-bold" style={{ color }}>
            {Math.round(currentValue)}%
          </span>
        )}
      </div>
    </div>
  )
}

// Анимированный индикатор активности
interface ActivityIndicatorProps {
  active?: boolean
  type?: 'pulse' | 'dots' | 'bars' | 'wave' | 'radar'
  size?: 'sm' | 'md' | 'lg'
  color?: string
  label?: string
}

export function ActivityIndicator({ 
  active = true, 
  type = 'pulse', 
  size = 'md', 
  color = 'var(--aurion-cyan)', 
  label 
}: ActivityIndicatorProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  if (!active) {
    return (
      <div className="flex items-center gap-2">
        <div className={`${sizeClasses[size]} rounded-full bg-[var(--aurion-text-dim)]`} />
        {label && <span className="aurion-mono text-xs text-[var(--aurion-text-muted)]">{label}</span>}
      </div>
    )
  }

  switch (type) {
    case 'pulse':
      return (
        <div className="flex items-center gap-2">
          <div className={`${sizeClasses[size]} rounded-full aurion-pulse`} style={{ backgroundColor: color }} />
          {label && <span className="aurion-mono text-xs" style={{ color }}>{label}</span>}
        </div>
      )

    case 'dots':
      return (
        <div className="flex items-center gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`${sizeClasses[size]} rounded-full aurion-pulse`}
              style={{ 
                backgroundColor: color,
                animationDelay: `${i * 0.2}s`
              }}
            />
          ))}
          {label && <span className="aurion-mono text-xs ml-2" style={{ color }}>{label}</span>}
        </div>
      )

    case 'bars':
      return (
        <div className="flex items-center gap-1">
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className={`${sizeClasses[size]} rounded-sm aurion-pulse`}
              style={{ 
                backgroundColor: color,
                animationDelay: `${i * 0.15}s`,
                height: `${Math.random() * 100}%`
              }}
            />
          ))}
          {label && <span className="aurion-mono text-xs ml-2" style={{ color }}>{label}</span>}
        </div>
      )

    case 'wave':
      return (
        <div className="flex items-center gap-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={`${sizeClasses[size]} rounded-full aurion-pulse`}
              style={{ 
                backgroundColor: color,
                animationDelay: `${i * 0.1}s`,
                transform: `scale(${0.5 + Math.sin(Date.now() / 200 + i) * 0.5})`
              }}
            />
          ))}
          {label && <span className="aurion-mono text-xs ml-2" style={{ color }}>{label}</span>}
        </div>
      )

    case 'radar':
      return (
        <div className="flex items-center gap-2">
          <div className={`${sizeClasses[size]} relative`}>
            <Radar className="w-full h-full aurion-rotate" style={{ color }} />
            <div className="absolute inset-0 rounded-full border-2 aurion-pulse" style={{ borderColor: color }} />
          </div>
          {label && <span className="aurion-mono text-xs" style={{ color }}>{label}</span>}
        </div>
      )

    default:
      return null
  }
}

// Анимированная иконка батареи
interface BatteryIconProps {
  level: number
  charging?: boolean
  size?: number
  showPercentage?: boolean
}

export function BatteryIcon({ level, charging = false, size = 24, showPercentage = false }: BatteryIconProps) {
  const [animatedLevel, setAnimatedLevel] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedLevel(level), 100)
    return () => clearTimeout(timer)
  }, [level])

  const getColor = () => {
    if (charging) return 'var(--aurion-cyan)'
    if (animatedLevel > 60) return 'var(--aurion-green-dim)'
    if (animatedLevel > 30) return 'var(--aurion-warning)'
    return 'var(--aurion-error)'
  }

  return (
    <div className="flex items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <Battery 
          size={size} 
          color={getColor()}
          className={charging ? 'aurion-pulse' : ''}
        />
        {charging && (
          <div className="absolute inset-0 flex items-center justify-center">
            <RefreshCw size={size * 0.4} className="animate-spin" style={{ color: getColor() }} />
          </div>
        )}
      </div>
      {showPercentage && (
        <span className="aurion-mono text-xs" style={{ color: getColor() }}>
          {Math.round(animatedLevel)}%
        </span>
      )}
    </div>
  )
}

// Анимированная иконка соединения
interface ConnectionIconProps {
  connected?: boolean
  strength?: number
  animated?: boolean
  size?: number
}

export function ConnectionIcon({ 
  connected = false, 
  strength = 100, 
  animated = true, 
  size = 24 
}: ConnectionIconProps) {
  const [animatedStrength, setAnimatedStrength] = useState(0)

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setAnimatedStrength(strength), 100)
      return () => clearTimeout(timer)
    } else {
      setAnimatedStrength(strength)
    }
  }, [strength, animated])

  const getBars = () => {
    const barCount = Math.ceil((animatedStrength / 100) * 4)
    return Array.from({ length: 4 }, (_, i) => i < barCount)
  }

  if (!connected) {
    return <WifiOff size={size} className="text-[var(--aurion-text-muted)]" />
  }

  return (
    <div className="relative">
      <Wifi size={size} className="text-[var(--aurion-green-dim)]" />
      <div className="absolute bottom-0 left-0 right-0 flex justify-center gap-0.5">
        {getBars().map((active, i) => (
          <div
            key={i}
            className={`w-0.5 transition-all duration-300 ${
              active ? 'bg-[var(--aurion-green-dim)]' : 'bg-[var(--aurion-text-dim)]'
            }`}
            style={{ height: `${(i + 1) * 2}px` }}
          />
        ))}
      </div>
    </div>
  )
}

// Анимированная иконка загрузки
interface LoadingIconProps {
  type?: 'spinner' | 'dots' | 'pulse' | 'bars'
  size?: number
  color?: string
  text?: string
}

export function LoadingIcon({ 
  type = 'spinner', 
  size = 24, 
  color = 'var(--aurion-cyan)', 
  text 
}: LoadingIconProps) {
  switch (type) {
    case 'spinner':
      return (
        <div className="flex items-center gap-2">
          <Loader size={size} className="animate-spin" style={{ color }} />
          {text && <span className="aurion-mono text-xs" style={{ color }}>{text}</span>}
        </div>
      )

    case 'dots':
      return (
        <div className="flex items-center gap-2">
          <ActivityIndicator active type="dots" color={color} />
          {text && <span className="aurion-mono text-xs" style={{ color }}>{text}</span>}
        </div>
      )

    case 'pulse':
      return (
        <div className="flex items-center gap-2">
          <ActivityIndicator active type="pulse" color={color} />
          {text && <span className="aurion-mono text-xs" style={{ color }}>{text}</span>}
        </div>
      )

    case 'bars':
      return (
        <div className="flex items-center gap-2">
          <ActivityIndicator active type="bars" color={color} />
          {text && <span className="aurion-mono text-xs" style={{ color }}>{text}</span>}
        </div>
      )

    default:
      return null
  }
}
