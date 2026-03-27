import React, { useState, useEffect } from 'react'

interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  color?: 'cyan' | 'purple' | 'green' | 'red' | 'amber'
  label?: string
  sublabel?: string
  showPercentage?: boolean
  animated?: boolean
  gradient?: boolean
  pulse?: boolean
}

export function CircularProgress({ 
  value, 
  max = 100, 
  size = 120, 
  strokeWidth = 8,
  color = 'cyan',
  label,
  sublabel,
  showPercentage = true,
  animated = true,
  gradient = false,
  pulse = false
}: CircularProgressProps) {
  const [displayValue, setDisplayValue] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  // Анимация значения при изменении
  useEffect(() => {
    if (animated) {
      setIsAnimating(true)
      const duration = 1000
      const steps = 30
      const increment = (percentage - displayValue) / steps
      let currentStep = 0
      
      const timer = setInterval(() => {
        currentStep++
        if (currentStep >= steps) {
          setDisplayValue(percentage)
          setIsAnimating(false)
          clearInterval(timer)
        } else {
          setDisplayValue((prev: number) => prev + increment)
        }
      }, duration / steps)
      
      return () => clearInterval(timer)
    } else {
      setDisplayValue(percentage)
    }
  }, [percentage, animated])

  const colorClasses = {
    cyan: 'text-[var(--aurion-cyan)] drop-shadow-[0_0_8px_var(--aurion-cyan)]',
    purple: 'text-[var(--aurion-purple)] drop-shadow-[0_0_8px_var(--aurion-purple)]',
    green: 'text-[var(--aurion-green-dim)] drop-shadow-[0_0_8px_var(--aurion-green-dim)]',
    red: 'text-[var(--aurion-error)] drop-shadow-[0_0_8px_var(--aurion-error)]',
    amber: 'text-[var(--aurion-warning)] drop-shadow-[0_0_8px_var(--aurion-warning)]',
  }

  const bgColorClasses = {
    cyan: 'text-[var(--aurion-cyan)]/20',
    purple: 'text-[var(--aurion-purple)]/20',
    green: 'text-[var(--aurion-green-dim)]/20',
    red: 'text-[var(--aurion-error)]/20',
    amber: 'text-[var(--aurion-warning)]/20',
  }

  // Градиентные цвета
  const gradientColors = {
    cyan: 'url(#cyanGradient)',
    purple: 'url(#purpleGradient)',
    green: 'url(#greenGradient)',
    red: 'url(#redGradient)',
    amber: 'url(#amberGradient)',
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        {gradient && (
          <svg className="absolute" width="0" height="0">
            <defs>
              <linearGradient id="cyanGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--aurion-cyan)" />
                <stop offset="100%" stopColor="var(--aurion-purple)" />
              </linearGradient>
              <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--aurion-purple)" />
                <stop offset="100%" stopColor="var(--aurion-cyan)" />
              </linearGradient>
              <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--aurion-green-dim)" />
                <stop offset="100%" stopColor="var(--aurion-cyan)" />
              </linearGradient>
              <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--aurion-error)" />
                <stop offset="100%" stopColor="var(--aurion-warning)" />
              </linearGradient>
              <linearGradient id="amberGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--aurion-warning)" />
                <stop offset="100%" stopColor="var(--aurion-error)" />
              </linearGradient>
            </defs>
          </svg>
        )}
        
        <svg 
          className={`w-full h-full transform -rotate-90 ${pulse ? 'animate-pulse' : ''}`} 
          style={{ width: size, height: size }}
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className={bgColorClasses[color]}
          />
          
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={gradient ? gradientColors[color] : "currentColor"}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={`${gradient ? '' : colorClasses[color]} transition-all duration-1000 ease-out`}
            style={{
              filter: gradient ? 'drop-shadow(0 0 8px var(--aurion-cyan))' : undefined
            }}
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {showPercentage && (
            <span className={`text-2xl font-black text-[var(--aurion-text-secondary)] ${isAnimating ? 'animate-pulse' : ''}`}>
              {Math.round(displayValue)}%
            </span>
          )}
          {label && (
            <span className="aurion-mono text-[8px] uppercase tracking-tighter text-[var(--aurion-cyan)]">
              {label}
            </span>
          )}
        </div>
      </div>
      
      {sublabel && (
        <p className="aurion-mono text-[9px] text-center mt-4 text-[var(--aurion-text-muted)]/60 uppercase leading-relaxed tracking-widest max-w-[200px]">
          {sublabel}
        </p>
      )}
    </div>
  )
}
