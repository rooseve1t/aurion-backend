import React, { useEffect, useState } from 'react'
import { User, MessageSquare, Activity, Zap, Shield, Brain, Mic, Settings } from 'lucide-react'

// Базовый skeleton элемент
interface SkeletonProps {
  width?: string | number
  height?: string | number
  className?: string
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded'
  animation?: 'pulse' | 'wave' | 'shimmer' | 'none'
}

export function Skeleton({ 
  width = '100%', 
  height = '1rem', 
  className = '', 
  variant = 'rectangular',
  animation = 'shimmer'
}: SkeletonProps) {
  const [isAnimating, setIsAnimating] = useState(true)

  const variantClasses = {
    text: 'aurion-skeleton-text',
    circular: 'aurion-skeleton-circular',
    rectangular: 'aurion-skeleton-rectangular',
    rounded: 'aurion-skeleton-rounded'
  }

  const animationClasses = {
    pulse: 'aurion-skeleton-pulse',
    wave: 'aurion-skeleton-wave',
    shimmer: 'aurion-skeleton-shimmer',
    none: ''
  }

  return (
    <div
      className={`aurion-skeleton ${variantClasses[variant]} ${isAnimating ? animationClasses[animation] : ''} ${className}`}
      style={{ width, height }}
    />
  )
}

// Skeleton карточки
interface SkeletonCardProps {
  showAvatar?: boolean
  showTitle?: boolean
  showSubtitle?: boolean
  lines?: number
  showButton?: boolean
  className?: string
}

export function SkeletonCard({ 
  showAvatar = true, 
  showTitle = true, 
  showSubtitle = true, 
  lines = 3,
  showButton = false,
  className = ''
}: SkeletonCardProps) {
  return (
    <div className={`aurion-card p-4 ${className}`}>
      {showAvatar && (
        <div className="flex items-center gap-3 mb-4">
          <Skeleton variant="circular" width={40} height={40} />
          <div className="flex-1">
            {showTitle && <Skeleton width="60%" height={16} className="mb-2" />}
            {showSubtitle && <Skeleton width="40%" height={12} />}
          </div>
        </div>
      )}
      
      <div className="space-y-2">
        {Array.from({ length: lines }, (_, i) => (
          <Skeleton 
            key={i} 
            width={i === lines - 1 ? '80%' : '100%'} 
            height={14}
            variant="text"
          />
        ))}
      </div>
      
      {showButton && (
        <div className="mt-4 flex justify-end">
          <Skeleton width={80} height={32} variant="rounded" />
        </div>
      )}
    </div>
  )
}

// Skeleton для списка сообщений чата
interface SkeletonMessageProps {
  isOwn?: boolean
  showAvatar?: boolean
  showTime?: boolean
  lines?: number
}

export function SkeletonMessage({ 
  isOwn = false, 
  showAvatar = true, 
  showTime = true,
  lines = 2
}: SkeletonMessageProps) {
  return (
    <div className={`flex gap-3 mb-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
      {showAvatar && (
        <Skeleton variant="circular" width={32} height={32} />
      )}
      
      <div className={`flex-1 max-w-[70%] ${isOwn ? 'text-right' : ''}`}>
        <div className={`aurion-card p-3 ${isOwn ? 'aurion-card-reverse' : ''}`}>
          <div className="space-y-1">
            {Array.from({ length: lines }, (_, i) => (
              <Skeleton 
                key={i} 
                width={i === lines - 1 ? '90%' : '100%'} 
                height={12}
                variant="text"
              />
            ))}
          </div>
        </div>
        
        {showTime && (
          <Skeleton width={60} height={10} className="mt-1" variant="text" />
        )}
      </div>
    </div>
  )
}

// Skeleton для дашборда
interface SkeletonDashboardProps {
  showCoreOrb?: boolean
  showStats?: boolean
  showModules?: boolean
  showCommands?: boolean
}

export function SkeletonDashboard({ 
  showCoreOrb = true, 
  showStats = true,
  showModules = true,
  showCommands = true
}: SkeletonDashboardProps) {
  return (
    <div className="grid grid-cols-12 gap-6 h-full">
      {/* Left Panel */}
      <div className="col-span-3 flex flex-col gap-6">
        {showCoreOrb && (
          <div className="aurion-card p-6 flex flex-col items-center">
            <Skeleton variant="circular" width={80} height={80} className="mb-4" />
            <Skeleton width={120} height={20} className="mb-2" />
            <Skeleton width={100} height={14} />
          </div>
        )}
        
        {showModules && (
          <div className="flex flex-col gap-3">
            {Array.from({ length: 3 }, (_, i) => (
              <div key={i} className="aurion-card p-4 flex justify-between items-center">
                <div className="flex-1">
                  <Skeleton width={80} height={14} className="mb-2" />
                  <Skeleton width={60} height={10} />
                </div>
                <Skeleton variant="circular" width={20} height={20} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Center Panel - Chat */}
      <div className="col-span-6 flex flex-col">
        <div className="aurion-card flex-1 flex flex-col">
          <div className="p-4 border-b border-[var(--aurion-text-dim)]/15">
            <Skeleton width={150} height={20} />
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-4">
              <SkeletonMessage isOwn={false} lines={2} />
              <SkeletonMessage isOwn={true} lines={3} />
              <SkeletonMessage isOwn={false} lines={1} />
            </div>
          </div>
          
          <div className="p-4 border-t border-[var(--aurion-text-dim)]/15">
            <div className="flex gap-2">
              <Skeleton className="flex-1" height={40} variant="rounded" />
              <Skeleton width={40} height={40} variant="circular" />
              <Skeleton width={40} height={40} variant="circular" />
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="col-span-3 flex flex-col gap-6">
        {showCommands && (
          <div>
            <Skeleton width={100} height={20} className="mb-4" />
            <div className="grid grid-cols-2 gap-3">
              {Array.from({ length: 8 }, (_, i) => (
                <div key={i} className="aurion-card p-4 flex flex-col items-center gap-2">
                  <Skeleton variant="circular" width={24} height={24} />
                  <Skeleton width={40} height={10} />
                  <Skeleton width={50} height={8} />
                </div>
              ))}
            </div>
          </div>
        )}
        
        {showStats && (
          <div className="mt-auto">
            <Skeleton width={120} height={14} className="mb-3" />
            <div className="aurion-card p-3">
              <div className="flex justify-between items-end">
                <Skeleton width={80} height={24} />
                <Skeleton variant="circular" width={16} height={16} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Skeleton для таблицы
interface SkeletonTableProps {
  rows?: number
  columns?: number
  showHeader?: boolean
}

export function SkeletonTable({ 
  rows = 5, 
  columns = 4, 
  showHeader = true 
}: SkeletonTableProps) {
  return (
    <div className="aurion-card overflow-hidden">
      {showHeader && (
        <div className="p-4 border-b border-[var(--aurion-text-dim)]/15">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }, (_, i) => (
              <Skeleton key={i} height={16} variant="text" />
            ))}
          </div>
        </div>
      )}
      
      <div className="p-4">
        <div className="space-y-3">
          {Array.from({ length: rows }, (_, rowIndex) => (
            <div key={rowIndex} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {Array.from({ length: columns }, (_, colIndex) => (
                <Skeleton 
                  key={colIndex} 
                  height={14} 
                  variant="text"
                  width={colIndex === columns - 1 ? '60%' : '100%'}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Skeleton для настроек
export function SkeletonSettings() {
  return (
    <div className="max-w-6xl mx-auto grid grid-cols-12 gap-6">
      {/* Sidebar */}
      <div className="col-span-3">
        <nav className="space-y-2">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} height={40} variant="rounded" className="w-full" />
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="col-span-9">
        <div className="space-y-6">
          <div className="aurion-card p-6">
            <Skeleton width={200} height={24} className="mb-6" />
            
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <Skeleton width={120} height={16} className="mb-2" />
                  <Skeleton width={200} height={12} />
                </div>
                <Skeleton width={48} height={24} variant="rounded" />
              </div>
              
              <div className="flex justify-between items-center">
                <div>
                  <Skeleton width={100} height={16} className="mb-2" />
                  <Skeleton width={180} height={12} />
                </div>
                <Skeleton width={48} height={24} variant="rounded" />
              </div>
            </div>
          </div>
          
          <div className="aurion-card p-6">
            <Skeleton width={150} height={20} className="mb-4" />
            <div className="flex gap-3">
              {Array.from({ length: 5 }, (_, i) => (
                <Skeleton key={i} variant="circular" width={32} height={32} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Skeleton для профиля пользователя
export function SkeletonProfile() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="aurion-card p-8">
        <div className="flex items-center gap-6 mb-8">
          <Skeleton variant="circular" width={100} height={100} />
          <div className="flex-1">
            <Skeleton width={200} height={28} className="mb-3" />
            <Skeleton width={150} height={16} className="mb-2" />
            <Skeleton width={300} height={14} />
          </div>
          <Skeleton width={120} height={36} variant="rounded" />
        </div>
        
        <div className="grid grid-cols-3 gap-6">
          {Array.from({ length: 3 }, (_, i) => (
            <div key={i} className="aurion-card p-4 text-center">
              <Skeleton width={60} height={24} className="mx-auto mb-2" />
              <Skeleton width={80} height={14} className="mx-auto" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Loading overlay с skeleton
interface SkeletonLoaderProps {
  isLoading: boolean
  children: React.ReactNode
  type?: 'card' | 'dashboard' | 'table' | 'settings' | 'profile' | 'custom'
  skeletonProps?: any
}

export function SkeletonLoader({ 
  isLoading, 
  children, 
  type = 'card',
  skeletonProps = {}
}: SkeletonLoaderProps) {
  const [showSkeleton, setShowSkeleton] = useState(false)

  useEffect(() => {
    if (isLoading) {
      const timer = setTimeout(() => setShowSkeleton(true), 100)
      return () => clearTimeout(timer)
    } else {
      setShowSkeleton(false)
    }
  }, [isLoading])

  if (!showSkeleton) {
    return <>{children}</>
  }

  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return <SkeletonCard {...skeletonProps} />
      case 'dashboard':
        return <SkeletonDashboard {...skeletonProps} />
      case 'table':
        return <SkeletonTable {...skeletonProps} />
      case 'settings':
        return <SkeletonSettings />
      case 'profile':
        return <SkeletonProfile />
      case 'custom':
        return skeletonProps.children
      default:
        return <SkeletonCard {...skeletonProps} />
    }
  }

  return (
    <div className="aurion-skeleton-loader">
      {renderSkeleton()}
    </div>
  )
}

// Animated pulse skeleton для активных состояний
export function PulseSkeleton({ children, isLoading }: { children: React.ReactNode; isLoading: boolean }) {
  return (
    <div className={`relative ${isLoading ? 'aurion-pulse-skeleton' : ''}`}>
      {children}
      {isLoading && (
        <div className="absolute inset-0 aurion-skeleton-overlay" />
      )}
    </div>
  )
}

// Экспорт всех компонентов
export {
  Skeleton,
  SkeletonCard,
  SkeletonMessage,
  SkeletonDashboard,
  SkeletonTable,
  SkeletonSettings,
  SkeletonProfile,
  SkeletonLoader,
  PulseSkeleton
}
