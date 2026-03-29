/**
 * @fileoverview Advanced Animation Service - Продвинутая система анимаций
 * @version 1.0.0
 * @author Aurion OS Team
 * @license Enterprise
 */

import { EventEmitter } from 'events'
import { 
  AnimationConfig, 
  AnimationPreset, 
  EasingFunction,
  AnimationTarget,
  AnimationSequence,
  PerformanceMetrics 
} from '../types/animation.types'

/**
 * Интерфейс анимационного движка
 */
export interface IAnimationEngine {
  registerAnimation(config: AnimationConfig): void
  playAnimation(id: string, target: AnimationTarget, options?: AnimationPlayOptions): Promise<AnimationResult>
  pauseAnimation(id: string): void
  resumeAnimation(id: string): void
  stopAnimation(id: string): void
  getActiveAnimations(): AnimationInstance[]
  setGlobalSpeed(speed: number): void
  optimizePerformance(): void
}

/**
 * Интерфейс менеджера последовательностей
 */
export interface ISequenceManager {
  createSequence(config: AnimationSequenceConfig): AnimationSequence
  playSequence(sequenceId: string): Promise<AnimationResult>
  pauseSequence(sequenceId: string): void
  stopSequence(sequenceId: string): void
  getActiveSequences(): AnimationSequence[]
}

/**
 * Интерфейс менеджера пресетов
 */
export interface IPresetManager {
  registerPreset(preset: AnimationPreset): void
  getPreset(presetId: string): AnimationPreset | undefined
  getAllPresets(): Record<string, AnimationPreset>
  applyPreset(presetId: string, target: AnimationTarget): Promise<AnimationResult>
  createCustomPreset(config: CustomPresetConfig): AnimationPreset
}

/**
 * Опции воспроизведения анимации
 */
export interface AnimationPlayOptions {
  duration?: number
  delay?: number
  easing?: EasingFunction
  iterations?: number
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse'
  fill?: 'none' | 'forwards' | 'backwards' | 'both'
  onComplete?: () => void
  onProgress?: (progress: number) => void
}

/**
 * Конфигурация последовательности анимаций
 */
export interface AnimationSequenceConfig {
  id: string
  name: string
  animations: Array<{
    animationId: string
    target: AnimationTarget
    delay?: number
    options?: AnimationPlayOptions
  }>
  parallel?: boolean
  loop?: boolean
}

/**
 * Конфигурация кастомного пресета
 */
export interface CustomPresetConfig {
  id: string
  name: string
  description?: string
  keyframes: Keyframe[]
  options: KeyframeAnimationOptions
  category: 'entrance' | 'exit' | 'emphasis' | 'loading' | 'interactive'
}

/**
 * Результат анимации
 */
export interface AnimationResult {
  success: boolean
  duration: number
  startTime: number
  endTime: number
  target: AnimationTarget
  animationId: string
}

/**
 * Экземпляр анимации
 */
export interface AnimationInstance {
  id: string
  target: AnimationTarget
  config: AnimationConfig
  startTime: number
  duration: number
  progress: number
  state: 'running' | 'paused' | 'completed' | 'cancelled'
  animation: Animation
}

/**
 * Основной класс сервиса анимаций
 */
export class AnimationService extends EventEmitter implements IAnimationEngine {
  private static instance: AnimationService
  private animations: Map<string, AnimationConfig> = new Map()
  private activeAnimations: Map<string, AnimationInstance> = new Map()
  private globalSpeed: number = 1.0
  private performanceMetrics: PerformanceMetrics
  private sequenceManager: ISequenceManager
  private presetManager: IPresetManager
  private isOptimized: boolean = false
  private frameRequestId: number | null = null

  constructor() {
    super()
    this.performanceMetrics = {
      totalAnimations: 0,
      activeAnimations: 0,
      averageDuration: 0,
      droppedFrames: 0,
      memoryUsage: 0
    }
    this.sequenceManager = new SequenceManager(this)
    this.presetManager = new PresetManager()
    this.initializePerformanceMonitoring()
  }

  /**
   * Получение singleton экземпляра
   */
  static getInstance(): AnimationService {
    if (!AnimationService.instance) {
      AnimationService.instance = new AnimationService()
    }
    return AnimationService.instance
  }

  /**
   * Регистрация анимации
   */
  public registerAnimation(config: AnimationConfig): void {
    this.validateAnimationConfig(config)
    this.animations.set(config.id, config)
    this.emit('animationRegistered', { animationId: config.id, timestamp: Date.now() })
  }

  /**
   * Воспроизведение анимации
   */
  public async playAnimation(
    id: string, 
    target: AnimationTarget, 
    options: AnimationPlayOptions = {}
  ): Promise<AnimationResult> {
    const config = this.animations.get(id)
    if (!config) {
      throw new Error(`Animation ${id} not found`)
    }

    const startTime = performance.now()
    const mergedOptions = this.mergeAnimationOptions(config, options)
    
    try {
      const animation = target.animate(config.keyframes, mergedOptions)
      const instance: AnimationInstance = {
        id: `${id}_${Date.now()}`,
        target,
        config,
        startTime,
        duration: mergedOptions.duration || 300,
        progress: 0,
        state: 'running',
        animation
      }

      this.activeAnimations.set(instance.id, instance)
      this.updatePerformanceMetrics('start', instance)

      animation.addEventListener('finish', () => {
        instance.state = 'completed'
        instance.progress = 1
        this.activeAnimations.delete(instance.id)
        this.updatePerformanceMetrics('complete', instance)
        this.emit('animationCompleted', { instance, timestamp: Date.now() })
        options.onComplete?.()
      })

      // Отслеживание прогресса
      if (options.onProgress) {
        this.trackProgress(instance, options.onProgress)
      }

      this.emit('animationStarted', { instance, timestamp: Date.now() })
      
      return new Promise((resolve) => {
        animation.addEventListener('finish', () => {
          resolve({
            success: true,
            duration: performance.now() - startTime,
            startTime,
            endTime: performance.now(),
            target,
            animationId: instance.id
          })
        })
      })
    } catch (error) {
      this.emit('animationError', { animationId: id, error, timestamp: Date.now() })
      throw error
    }
  }

  /**
   * Пауза анимации
   */
  public pauseAnimation(id: string): void {
    const instance = this.findAnimationInstance(id)
    if (instance && instance.state === 'running') {
      instance.animation.pause()
      instance.state = 'paused'
      this.emit('animationPaused', { instance, timestamp: Date.now() })
    }
  }

  /**
   * Возобновление анимации
   */
  public resumeAnimation(id: string): void {
    const instance = this.findAnimationInstance(id)
    if (instance && instance.state === 'paused') {
      instance.animation.play()
      instance.state = 'running'
      this.emit('animationResumed', { instance, timestamp: Date.now() })
    }
  }

  /**
   * Остановка анимации
   */
  public stopAnimation(id: string): void {
    const instance = this.findAnimationInstance(id)
    if (instance) {
      instance.animation.cancel()
      instance.state = 'cancelled'
      this.activeAnimations.delete(instance.id)
      this.updatePerformanceMetrics('stop', instance)
      this.emit('animationStopped', { instance, timestamp: Date.now() })
    }
  }

  /**
   * Получение активных анимаций
   */
  public getActiveAnimations(): AnimationInstance[] {
    return Array.from(this.activeAnimations.values())
  }

  /**
   * Установка глобальной скорости
   */
  public setGlobalSpeed(speed: number): void {
    this.globalSpeed = Math.max(0.1, Math.min(5, speed))
    this.activeAnimations.forEach(instance => {
      instance.animation.playbackRate = this.globalSpeed
    })
    this.emit('globalSpeedChanged', { speed: this.globalSpeed, timestamp: Date.now() })
  }

  /**
   * Оптимизация производительности
   */
  public optimizePerformance(): void {
    if (this.isOptimized) return

    // Остановка невидимых анимаций
    this.activeAnimations.forEach(instance => {
      if (!this.isElementVisible(instance.target as Element)) {
        this.pauseAnimation(instance.id)
      }
    })

    // Ограничение одновременных анимаций
    const maxConcurrent = 50
    if (this.activeAnimations.size > maxConcurrent) {
      const instances = Array.from(this.activeAnimations.values())
      instances.slice(maxConcurrent).forEach(instance => {
        this.stopAnimation(instance.id)
      })
    }

    this.isOptimized = true
    this.emit('performanceOptimized', { timestamp: Date.now() })
  }

  /**
   * Получение менеджера последовательностей
   */
  public getSequenceManager(): ISequenceManager {
    return this.sequenceManager
  }

  /**
   * Получение менеджера пресетов
   */
  public getPresetManager(): IPresetManager {
    return this.presetManager
  }

  /**
   * Получение метрик производительности
   */
  public getPerformanceMetrics(): PerformanceMetrics {
    return { ...this.performanceMetrics }
  }

  /**
   * Очистка ресурсов
   */
  public dispose(): void {
    this.activeAnimations.forEach(instance => {
      this.stopAnimation(instance.id)
    })
    
    if (this.frameRequestId) {
      cancelAnimationFrame(this.frameRequestId)
    }
    
    this.removeAllListeners()
    this.emit('disposed')
  }

  /**
   * Валидация конфигурации анимации
   */
  private validateAnimationConfig(config: AnimationConfig): void {
    if (!config.id || !config.keyframes) {
      throw new Error('Invalid animation config: missing id or keyframes')
    }
    
    if (!Array.isArray(config.keyframes) || config.keyframes.length === 0) {
      throw new Error('Invalid animation config: keyframes must be non-empty array')
    }
  }

  /**
   * Слияние опций анимации
   */
  private mergeAnimationOptions(
    config: AnimationConfig, 
    options: AnimationPlayOptions
  ): KeyframeAnimationOptions {
    return {
      duration: options.duration || config.duration || 300,
      delay: options.delay || 0,
      easing: options.easing || config.easing || 'ease',
      iterations: options.iterations || config.iterations || 1,
      direction: options.direction || config.direction || 'normal',
      fill: options.fill || config.fill || 'none'
    }
  }

  /**
   * Поиск экземпляра анимации
   */
  private findAnimationInstance(idOrAnimationId: string): AnimationInstance | undefined {
    return this.activeAnimations.get(idOrAnimationId) || 
           Array.from(this.activeAnimations.values()).find(
             instance => instance.config.id === idOrAnimationId
           )
  }

  /**
   * Отслеживание прогресса анимации
   */
  private trackProgress(instance: AnimationInstance, onProgress: (progress: number) => void): void {
    const updateProgress = () => {
      if (instance.state === 'running') {
        const currentTime = performance.now() - instance.startTime
        instance.progress = Math.min(currentTime / instance.duration, 1)
        onProgress(instance.progress)
        
        if (instance.progress < 1) {
          requestAnimationFrame(updateProgress)
        }
      }
    }
    requestAnimationFrame(updateProgress)
  }

  /**
   * Проверка видимости элемента
   */
  private isElementVisible(element: Element): boolean {
    if (!element) return false
    const rect = element.getBoundingClientRect()
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    )
  }

  /**
   * Обновление метрик производительности
   */
  private updatePerformanceMetrics(action: 'start' | 'complete' | 'stop', instance: AnimationInstance): void {
    switch (action) {
      case 'start':
        this.performanceMetrics.totalAnimations++
        this.performanceMetrics.activeAnimations++
        break
      case 'complete':
      case 'stop':
        this.performanceMetrics.activeAnimations--
        const totalDuration = this.performanceMetrics.averageDuration * (this.performanceMetrics.totalAnimations - 1) + instance.duration
        this.performanceMetrics.averageDuration = totalDuration / this.performanceMetrics.totalAnimations
        break
    }
  }

  /**
   * Инициализация мониторинга производительности
   */
  private initializePerformanceMonitoring(): void {
    const monitorPerformance = () => {
      this.performanceMetrics.memoryUsage = (performance as any).memory?.usedJSHeapSize || 0
      
      // Проверка dropped frames
      const frameTime = performance.now()
      if (frameTime - this.lastFrameTime > 16.67) { // 60fps = 16.67ms per frame
        this.performanceMetrics.droppedFrames++
      }
      this.lastFrameTime = frameTime
      
      this.frameRequestId = requestAnimationFrame(monitorPerformance)
    }
    
    const lastFrameTime = performance.now()
    this.lastFrameTime = lastFrameTime
    
    monitorPerformance()
  }

  private lastFrameTime: number = 0
}

/**
 * Менеджер последовательностей анимаций
 */
class SequenceManager implements ISequenceManager {
  private sequences: Map<string, AnimationSequence> = new Map()
  private activeSequences: Map<string, AnimationSequence> = new Map()
  private animationService: AnimationService

  constructor(animationService: AnimationService) {
    this.animationService = animationService
  }

  createSequence(config: AnimationSequenceConfig): AnimationSequence {
    const sequence: AnimationSequence = {
      id: config.id,
      name: config.name,
      animations: config.animations,
      parallel: config.parallel || false,
      loop: config.loop || false,
      isPlaying: false,
      progress: 0
    }
    
    this.sequences.set(sequence.id, sequence)
    return sequence
  }

  async playSequence(sequenceId: string): Promise<AnimationResult> {
    const sequence = this.sequences.get(sequenceId)
    if (!sequence) {
      throw new Error(`Sequence ${sequenceId} not found`)
    }

    this.activeSequences.set(sequenceId, sequence)
    sequence.isPlaying = true

    try {
      if (sequence.parallel) {
        const promises = sequence.animations.map(({ animationId, target, delay, options }) => {
          if (delay) {
            return new Promise(resolve => setTimeout(resolve, delay))
              .then(() => this.animationService.playAnimation(animationId, target, options))
          }
          return this.animationService.playAnimation(animationId, target, options)
        })
        
        await Promise.all(promises)
      } else {
        for (const { animationId, target, delay, options } of sequence.animations) {
          if (delay) {
            await new Promise(resolve => setTimeout(resolve, delay))
          }
          await this.animationService.playAnimation(animationId, target, options)
        }
      }

      sequence.progress = 1
      sequence.isPlaying = false
      this.activeSequences.delete(sequenceId)

      return {
        success: true,
        duration: 0,
        startTime: 0,
        endTime: 0,
        target: null,
        animationId: sequenceId
      }
    } catch (error) {
      sequence.isPlaying = false
      this.activeSequences.delete(sequenceId)
      throw error
    }
  }

  pauseSequence(sequenceId: string): void {
    const sequence = this.activeSequences.get(sequenceId)
    if (sequence) {
      sequence.isPlaying = false
      // TODO: Pause individual animations
    }
  }

  stopSequence(sequenceId: string): void {
    const sequence = this.activeSequences.get(sequenceId)
    if (sequence) {
      sequence.isPlaying = false
      sequence.progress = 0
      this.activeSequences.delete(sequenceId)
      // TODO: Stop individual animations
    }
  }

  getActiveSequences(): AnimationSequence[] {
    return Array.from(this.activeSequences.values())
  }
}

/**
 * Менеджер пресетов анимаций
 */
class PresetManager implements IPresetManager {
  private presets: Map<string, AnimationPreset> = new Map()

  registerPreset(preset: AnimationPreset): void {
    this.presets.set(preset.id, preset)
  }

  getPreset(presetId: string): AnimationPreset | undefined {
    return this.presets.get(presetId)
  }

  getAllPresets(): Record<string, AnimationPreset> {
    return Object.fromEntries(this.presets)
  }

  async applyPreset(presetId: string, target: AnimationTarget): Promise<AnimationResult> {
    const preset = this.presets.get(presetId)
    if (!preset) {
      throw new Error(`Preset ${presetId} not found`)
    }

    const animationService = AnimationService.getInstance()
    return animationService.playAnimation(preset.animationId, target, preset.options)
  }

  createCustomPreset(config: CustomPresetConfig): AnimationPreset {
    const animationService = AnimationService.getInstance()
    
    const animationConfig: AnimationConfig = {
      id: config.id,
      name: config.name,
      keyframes: config.keyframes,
      options: config.options,
      category: config.category
    }
    
    animationService.registerAnimation(animationConfig)
    
    const preset: AnimationPreset = {
      id: config.id,
      name: config.name,
      description: config.description,
      animationId: config.id,
      options: config.options,
      category: config.category
    }
    
    this.registerPreset(preset)
    return preset
  }
}

export default AnimationService
