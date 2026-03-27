import React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="aurion-glass p-3 rounded-full text-[var(--aurion-text-muted)] hover:text-[var(--aurion-cyan)] transition-all duration-300 group"
      title={`Переключить на ${theme === 'dark' ? 'светлую' : 'темную'} тему`}
    >
      <div className="relative w-5 h-5">
        {theme === 'dark' ? (
          <Moon className="absolute inset-0 w-5 h-5 group-hover:rotate-12 transition-transform" />
        ) : (
          <Sun className="absolute inset-0 w-5 h-5 group-hover:rotate-12 transition-transform" />
        )}
      </div>
    </button>
  )
}
