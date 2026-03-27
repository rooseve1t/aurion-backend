// Звуковые эффекты для Aurion OS - сгенерированные программно

// Базовый класс для генерации звуков
class AurionSoundGenerator {
  private audioContext: AudioContext | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    }
  }

  // Создание простого тона
  private createTone(frequency: number, duration: number, type: OscillatorType = 'sine'): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = frequency
    oscillator.type = type

    gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + duration)
  }

  // Создание клика
  public createClick(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = 800
    oscillator.type = 'square'

    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.05)
  }

  // Создание навигационного звука
  public createNavigationSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.1)
    oscillator.type = 'sine'

    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.15)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.15)
  }

  // Создание звука успеха
  public createSuccessSound(): void {
    if (!this.audioContext) return

    const notes = [523.25, 659.25, 783.99] // C, E, G
    
    notes.forEach((frequency, index) => {
      setTimeout(() => {
        this.createTone(frequency, 0.3, 'sine')
      }, index * 100)
    })
  }

  // Создание звука ошибки
  public createErrorSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = 200
    oscillator.type = 'sawtooth'

    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.2)
  }

  // Создание звука уведомления
  public createNotificationSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(400, this.audioContext.currentTime + 0.2)
    oscillator.type = 'triangle'

    gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.3)
  }

  // Создание звука печатания
  public createTypingSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = 1000 + Math.random() * 500
    oscillator.type = 'square'

    gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.02)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.02)
  }

  // Создание звука загрузки
  public createLoadingSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(800, this.audioContext.currentTime + 0.5)
    oscillator.type = 'sine'

    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.5)
  }

  // Создание звука активации
  public createActivationSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(300, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.3)
    oscillator.type = 'sawtooth'

    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.4)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.4)
  }

  // Создание звука переключения
  public createToggleSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = 600
    oscillator.type = 'sine'

    gainNode.gain.setValueAtTime(0.15, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.1)
  }

  // Создание звука сообщения
  public createMessageSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(1000, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(600, this.audioContext.currentTime + 0.15)
    oscillator.type = 'triangle'

    gainNode.gain.setValueAtTime(0.25, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 0.2)
  }

  // Создание звука сканирования
  public createScanSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(2000, this.audioContext.currentTime + 1)
    oscillator.type = 'sawtooth'

    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 1)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 1)
  }

  // Создание космического звука
  public createSpaceAmbient(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()
    const filter = this.audioContext.createBiquadFilter()

    oscillator.connect(filter)
    filter.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.value = 100
    oscillator.type = 'sine'
    filter.type = 'lowpass'
    filter.frequency.value = 800

    gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 2)
  }

  // Создание звука телепортации
  public createTeleportSound(): void {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()
    const filter = this.audioContext.createBiquadFilter()

    oscillator.connect(filter)
    filter.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(100, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(2000, this.audioContext.currentTime + 0.5)
    oscillator.frequency.exponentialRampToValueAtTime(100, this.audioContext.currentTime + 1)
    oscillator.type = 'sawtooth'
    filter.type = 'highpass'
    filter.frequency.setValueAtTime(100, this.audioContext.currentTime)
    filter.frequency.exponentialRampToValueAtTime(2000, this.audioContext.currentTime + 0.5)

    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 1)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + 1)
  }
}

// Создаем экземпляр генератора звуков
const soundGenerator = new AurionSoundGenerator()

// Типы звуков
export type SoundType = 
  | 'click'
  | 'navigation'
  | 'success'
  | 'error'
  | 'notification'
  | 'typing'
  | 'loading'
  | 'activation'
  | 'toggle'
  | 'message'
  | 'scan'
  | 'space'
  | 'teleport'

// Менеджер звуковых эффектов
class AurionSoundManager {
  private enabled: boolean = true
  private volume: number = 0.5
  private lastPlayedTime: Map<SoundType, number> = new Map()
  private cooldownPeriod: number = 100 // 100ms cooldown

  constructor() {
    // Загружаем настройки из localStorage
    if (typeof window !== 'undefined') {
      const savedSettings = localStorage.getItem('aurion-sound-settings')
      if (savedSettings) {
        const settings = JSON.parse(savedSettings)
        this.enabled = settings.enabled ?? true
        this.volume = settings.volume ?? 0.5
      }
    }
  }

  // Воспроизведение звука
  public playSound(type: SoundType, force: boolean = false): void {
    if (!this.enabled) return

    // Проверяем cooldown период
    const now = Date.now()
    const lastPlayed = this.lastPlayedTime.get(type) || 0
    
    if (!force && now - lastPlayed < this.cooldownPeriod) {
      return
    }

    this.lastPlayedTime.set(type, now)

    try {
      switch (type) {
        case 'click':
          soundGenerator.createClick()
          break
        case 'navigation':
          soundGenerator.createNavigationSound()
          break
        case 'success':
          soundGenerator.createSuccessSound()
          break
        case 'error':
          soundGenerator.createErrorSound()
          break
        case 'notification':
          soundGenerator.createNotificationSound()
          break
        case 'typing':
          soundGenerator.createTypingSound()
          break
        case 'loading':
          soundGenerator.createLoadingSound()
          break
        case 'activation':
          soundGenerator.createActivationSound()
          break
        case 'toggle':
          soundGenerator.createToggleSound()
          break
        case 'message':
          soundGenerator.createMessageSound()
          break
        case 'scan':
          soundGenerator.createScanSound()
          break
        case 'space':
          soundGenerator.createSpaceAmbient()
          break
        case 'teleport':
          soundGenerator.createTeleportSound()
          break
      }
    } catch (error) {
      console.warn('Failed to play sound:', error)
    }
  }

  // Включение/выключение звуков
  public setEnabled(enabled: boolean): void {
    this.enabled = enabled
    this.saveSettings()
  }

  // Установка громкости
  public setVolume(volume: number): void {
    this.volume = Math.max(0, Math.min(1, volume))
    this.saveSettings()
  }

  // Получение статуса
  public isEnabled(): boolean {
    return this.enabled
  }

  // Получение громкости
  public getVolume(): number {
    return this.volume
  }

  // Сохранение настроек
  private saveSettings(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('aurion-sound-settings', JSON.stringify({
        enabled: this.enabled,
        volume: this.volume
      }))
    }
  }

  // Инициализация первого взаимодействия (для автоплея)
  public init(): void {
    if (typeof window !== 'undefined') {
      const initSound = () => {
        this.playSound('click', true)
        window.removeEventListener('click', initSound)
        window.removeEventListener('keydown', initSound)
        window.removeEventListener('touchstart', initSound)
      }
      
      window.addEventListener('click', initSound, { once: true })
      window.addEventListener('keydown', initSound, { once: true })
      window.addEventListener('touchstart', initSound, { once: true })
    }
  }
}

// Создаем экземпляр менеджера звуков
export const soundManager = new AurionSoundManager()

// React хук для звуковых эффектов
export function useSound() {
  const playSound = (type: SoundType, force: boolean = false) => {
    soundManager.playSound(type, force)
  }

  const toggleSound = () => {
    soundManager.setEnabled(!soundManager.isEnabled())
  }

  const setVolume = (volume: number) => {
    soundManager.setVolume(volume)
  }

  return {
    playSound,
    isEnabled: soundManager.isEnabled(),
    getVolume: () => soundManager.getVolume(),
    toggleSound,
    setVolume
  }
}

// Компонент для настройки звуков
import React, { useState, useEffect } from 'react'
import { Volume2, VolumeX, Settings } from 'lucide-react'

interface SoundSettingsProps {
  className?: string
}

export function SoundSettings({ className = '' }: SoundSettingsProps) {
  const { isEnabled, getVolume, toggleSound, setVolume } = useSound()
  const [volume, setLocalVolume] = useState(getVolume())

  useEffect(() => {
    setLocalVolume(getVolume())
  }, [getVolume])

  const handleVolumeChange = (newVolume: number) => {
    setLocalVolume(newVolume)
    setVolume(newVolume)
  }

  return (
    <div className={`aurion-card p-4 ${className}`}>
      <div className="flex items-center gap-3 mb-4">
        {isEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
        <h3 className="aurion-headline text-sm font-bold">Звуковые эффекты</h3>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="aurion-mono text-xs">Включены</span>
          <button
            onClick={toggleSound}
            className={`aurion-toggle w-12 h-6 ${isEnabled ? 'active' : ''}`}
          >
            <div className={`aurion-toggle-dot w-5 h-5 ${isEnabled ? 'translate-x-full' : 'translate-x-0'}`} />
          </button>
        </div>
        
        {isEnabled && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="aurion-mono text-xs">Громкость</span>
              <span className="aurion-mono text-xs">{Math.round(volume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={volume * 100}
              onChange={(e) => handleVolumeChange(Number(e.target.value) / 100)}
              className="w-full h-2 bg-[var(--aurion-bg-surface-high)] rounded-lg appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, var(--aurion-cyan) 0%, var(--aurion-cyan) ${volume * 100}%, var(--aurion-bg-surface-high) ${volume * 100}%, var(--aurion-bg-surface-high) 100%)`
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

// Экспорт всех компонентов и утилит
export {
  AurionSoundGenerator,
  AurionSoundManager,
  soundGenerator
}
export default useSound
