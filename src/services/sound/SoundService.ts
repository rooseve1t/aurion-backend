/**
 * @fileoverview Enhanced Sound Service - Продвинутая система звуковых эффектов
 * @version 1.0.0
 * @author Aurion OS Team
 * @license Enterprise
 */

import { EventEmitter } from 'events'
import { 
  SoundConfig, 
  SoundPreset, 
  AudioContextConfig,
  SoundEffect,
  SoundSpatialConfig,
  SoundMixerConfig,
  SoundAnalysisData 
} from '../types/sound.types'

/**
 * Интерфейс аудио движка
 */
export interface IAudioEngine {
  initialize(config: AudioContextConfig): Promise<void>
  generateSound(config: SoundConfig): AudioBuffer
  playSound(buffer: AudioBuffer, options?: SoundPlayOptions): Promise<void>
  stopSound(soundId: string): void
  setVolume(volume: number): void
  setMasterVolume(volume: number): void
  getAudioContext(): AudioContext
  suspend(): void
  resume(): void
}

/**
 * Интерфейс менеджера пресетов
 */
export interface ISoundPresetManager {
  registerPreset(preset: SoundPreset): void
  getPreset(presetId: string): SoundPreset | undefined
  getAllPresets(): Record<string, SoundPreset>
  applyPreset(presetId: string, target?: AudioNode): void
  createCustomPreset(config: CustomSoundPresetConfig): SoundPreset
}

/**
 * Интерфейс микшера
 */
export interface ISoundMixer {
  addChannel(channelId: string, config: SoundMixerConfig): void
  removeChannel(channelId: string): void
  setChannelVolume(channelId: string, volume: number): void
  setChannelPan(channelId: string, pan: number): void
  setChannelEffects(channelId: string, effects: SoundEffect[]): void
  getChannelLevels(): Record<string, number>
  mixChannels(): AudioBuffer
}

/**
 * Интерфейс анализатора аудио
 */
export interface ISoundAnalyzer {
  analyze(buffer: AudioBuffer): SoundAnalysisData
  getFrequencyData(): Uint8Array
  getTimeDomainData(): Uint8Array
  getPeakLevel(): number
  getRMSLevel(): number
  startRealtimeAnalysis(): void
  stopRealtimeAnalysis(): void
}

/**
 * Опции воспроизведения звука
 */
export interface SoundPlayOptions {
  volume?: number
  pitch?: number
  pan?: number
  loop?: boolean
  delay?: number
  fadeIn?: number
  fadeOut?: number
  spatial?: SoundSpatialConfig
  effects?: SoundEffect[]
}

/**
 * Конфигурация кастомного пресета
 */
export interface CustomSoundPresetConfig {
  id: string
  name: string
  description?: string
  waveform: OscillatorType
  frequency: number | [number, number]
  duration: number
  envelope: ADSREnvelope
  filters?: AudioFilterConfig[]
  effects?: SoundEffect[]
}

/**
 * Конфигурация ADSR огибающей
 */
export interface ADSREnvelope {
  attack: number
  decay: number
  sustain: number
  release: number
}

/**
 * Конфигурация фильтра
 */
export interface AudioFilterConfig {
  type: BiquadFilterType
  frequency: number
  Q?: number
  gain?: number
}

/**
 * Основной класс звукового сервиса
 */
export class SoundService extends EventEmitter implements IAudioEngine {
  private static instance: SoundService
  private audioContext: AudioContext | null = null
  private masterGainNode: GainNode | null = null
  private compressorNode: DynamicsCompressorNode | null = null
  private analyserNode: AnalyserNode | null = null
  private activeSounds: Map<string, AudioBufferSourceNode> = new Map()
  private presetManager: ISoundPresetManager
  private mixer: ISoundMixer
  private analyzer: ISoundAnalyzer
  private isInitialized = false
  private config: AudioContextConfig
  private masterVolume: number = 1.0
  private isSuspended = false

  constructor(config: AudioContextConfig = {}) {
    super()
    this.config = {
      sampleRate: 44100,
      latency: 'interactive',
      ...config
    }
    this.presetManager = new SoundPresetManager()
    this.mixer = new SoundMixer(this)
    this.analyzer = new SoundAnalyzer()
  }

  /**
   * Получение singleton экземпляра
   */
  static getInstance(config?: AudioContextConfig): SoundService {
    if (!SoundService.instance) {
      SoundService.instance = new SoundService(config)
    }
    return SoundService.instance
  }

  /**
   * Инициализация аудио контекста
   */
  public async initialize(config: AudioContextConfig = {}): Promise<void> {
    if (this.isInitialized) return

    try {
      this.config = { ...this.config, ...config }
      
      // Создание аудио контекста
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)(this.config)
      
      // Создание аудио нод
      this.setupAudioNodes()
      
      // Загрузка пресетов
      await this.loadDefaultPresets()
      
      this.isInitialized = true
      
      this.emit('initialized', {
        sampleRate: this.audioContext.sampleRate,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      this.emit('error', { 
        type: 'initialization_failed', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
      throw error
    }
  }

  /**
   * Генерация звука
   */
  public generateSound(config: SoundConfig): AudioBuffer {
    this.ensureInitialized()
    
    const sampleRate = this.audioContext!.sampleRate
    const duration = config.duration || 0.1
    const buffer = this.audioContext!.createBuffer(2, sampleRate * duration, sampleRate)
    
    // Генерация волновой формы
    this.generateWaveform(buffer, config)
    
    // Применение эффектов
    if (config.effects) {
      this.applyEffects(buffer, config.effects)
    }
    
    return buffer
  }

  /**
   * Воспроизведение звука
   */
  public async playSound(
    buffer: AudioBuffer, 
    options: SoundPlayOptions = {}
  ): Promise<void> {
    this.ensureInitialized()
    
    if (this.isSuspended) {
      await this.resume()
    }

    const soundId = `sound_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    try {
      const source = this.audioContext!.createBufferSource()
      source.buffer = buffer
      
      // Создание цепочки эффектов
      const lastNode = this.createEffectChain(source, options)
      
      // Подключение к выходу
      lastNode.connect(this.masterGainNode!)
      
      // Применение опций
      if (options.pitch) {
        source.playbackRate.value = options.pitch
      }
      
      if (options.loop) {
        source.loop = true
      }
      
      // Обработка fade in/out
      if (options.fadeIn || options.fadeOut) {
        this.applyFadeEffects(source, options)
      }
      
      // Задержка воспроизведения
      const startTime = this.audioContext!.currentTime + (options.delay || 0)
      source.start(startTime)
      
      this.activeSounds.set(soundId, source)
      
      // Обработка завершения
      source.addEventListener('ended', () => {
        this.activeSounds.delete(soundId)
        this.emit('soundEnded', { soundId, timestamp: Date.now() })
      })
      
      this.emit('soundStarted', { soundId, timestamp: Date.now() })
      
    } catch (error) {
      this.emit('soundError', { soundId, error, timestamp: Date.now() })
      throw error
    }
  }

  /**
   * Остановка звука
   */
  public stopSound(soundId: string): void {
    const source = this.activeSounds.get(soundId)
    if (source) {
      try {
        source.stop()
        this.activeSounds.delete(soundId)
        this.emit('soundStopped', { soundId, timestamp: Date.now() })
      } catch (error) {
        // Звук уже остановлен
      }
    }
  }

  /**
   * Установка громкости
   */
  public setVolume(volume: number): void {
    this.ensureInitialized()
    this.masterVolume = Math.max(0, Math.min(1, volume))
    if (this.masterGainNode) {
      this.masterGainNode.gain.value = this.masterVolume
    }
    this.emit('volumeChanged', { volume: this.masterVolume, timestamp: Date.now() })
  }

  /**
   * Установка мастер громкости
   */
  public setMasterVolume(volume: number): void {
    this.setVolume(volume)
  }

  /**
   * Получение аудио контекста
   */
  public getAudioContext(): AudioContext {
    this.ensureInitialized()
    return this.audioContext!
  }

  /**
   * Приостановка аудио контекста
   */
  public suspend(): void {
    if (this.audioContext && this.audioContext.state === 'running') {
      this.audioContext.suspend()
      this.isSuspended = true
      this.emit('suspended', { timestamp: Date.now() })
    }
  }

  /**
   * Возобновление аудио контекста
   */
  public async resume(): Promise<void> {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      await this.audioContext.resume()
      this.isSuspended = false
      this.emit('resumed', { timestamp: Date.now() })
    }
  }

  /**
   * Получение менеджера пресетов
   */
  public getPresetManager(): ISoundPresetManager {
    return this.presetManager
  }

  /**
   * Получение микшера
   */
  public getMixer(): ISoundMixer {
    return this.mixer
  }

  /**
   * Получение анализатора
   */
  public getAnalyzer(): ISoundAnalyzer {
    return this.analyzer
  }

  /**
   * Воспроизведение пресета
   */
  public async playPreset(presetId: string, options?: SoundPlayOptions): Promise<void> {
    const preset = this.presetManager.getPreset(presetId)
    if (!preset) {
      throw new Error(`Preset ${presetId} not found`)
    }
    
    const buffer = this.generateSound(preset.config)
    await this.playSound(buffer, options)
  }

  /**
   * Получение активных звуков
   */
  public getActiveSounds(): string[] {
    return Array.from(this.activeSounds.keys())
  }

  /**
   * Остановка всех звуков
   */
  public stopAllSounds(): void {
    this.activeSounds.forEach((_, soundId) => {
      this.stopSound(soundId)
    })
    this.emit('allSoundsStopped', { timestamp: Date.now() })
  }

  /**
   * Получение статистики
   */
  public getStats(): SoundServiceStats {
    return {
      isInitialized: this.isInitialized,
      isSuspended: this.isSuspended,
      activeSoundsCount: this.activeSounds.size,
      masterVolume: this.masterVolume,
      sampleRate: this.audioContext?.sampleRate || 0,
      presetsCount: Object.keys(this.presetManager.getAllPresets()).length,
      channelsCount: this.mixer.getChannelLevels().length,
      audioContextState: this.audioContext?.state || 'closed'
    }
  }

  /**
   * Очистка ресурсов
   */
  public dispose(): void {
    this.stopAllSounds()
    
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    this.removeAllListeners()
    this.emit('disposed')
  }

  /**
   * Настройка аудио нод
   */
  private setupAudioNodes(): void {
    if (!this.audioContext) return

    // Мастер громкость
    this.masterGainNode = this.audioContext.createGain()
    this.masterGainNode.gain.value = this.masterVolume

    // Компрессор
    this.compressorNode = this.audioContext.createDynamicsCompressor()
    this.compressorNode.threshold.value = -24
    this.compressorNode.knee.value = 30
    this.compressorNode.ratio.value = 12
    this.compressorNode.attack.value = 0.003
    this.compressorNode.release.value = 0.25

    // Анализатор
    this.analyserNode = this.audioContext.createAnalyser()
    this.analyserNode.fftSize = 2048

    // Соединение нод
    this.compressorNode.connect(this.masterGainNode)
    this.masterGainNode.connect(this.analyserNode)
    this.analyserNode.connect(this.audioContext.destination)
  }

  /**
   * Генерация волновой формы
   */
  private generateWaveform(buffer: AudioBuffer, config: SoundConfig): void {
    const sampleRate = buffer.sampleRate
    const duration = buffer.duration
    const channels = buffer.numberOfChannels
    
    for (let channel = 0; channel < channels; channel++) {
      const channelData = buffer.getChannelData(channel)
      
      for (let i = 0; i < channelData.length; i++) {
        const t = i / sampleRate
        let sample = 0
        
        switch (config.waveform) {
          case 'sine':
            sample = Math.sin(2 * Math.PI * config.frequency * t)
            break
          case 'square':
            sample = Math.sign(Math.sin(2 * Math.PI * config.frequency * t))
            break
          case 'sawtooth':
            sample = 2 * ((config.frequency * t) % 1) - 1
            break
          case 'triangle':
            sample = 2 * Math.abs(2 * ((config.frequency * t) % 1) - 1) - 1
            break
          case 'noise':
            sample = Math.random() * 2 - 1
            break
        }
        
        // Применение ADSR огибающей
        if (config.envelope) {
          sample *= this.applyADSR(t, duration, config.envelope)
        }
        
        channelData[i] = sample * (config.amplitude || 0.5)
      }
    }
  }

  /**
   * Применение ADSR огибающей
   */
  private applyADSR(t: number, duration: number, envelope: ADSREnvelope): number {
    const { attack, decay, sustain, release } = envelope
    const sustainLevel = sustain
    
    if (t < attack) {
      return t / attack
    } else if (t < attack + decay) {
      const decayProgress = (t - attack) / decay
      return 1 - decayProgress * (1 - sustainLevel)
    } else if (t < duration - release) {
      return sustainLevel
    } else {
      const releaseProgress = (t - (duration - release)) / release
      return sustainLevel * (1 - releaseProgress)
    }
  }

  /**
   * Применение эффектов
   */
  private applyEffects(buffer: AudioBuffer, effects: SoundEffect[]): void {
    // TODO: Implement offline effects processing
    console.log('Applying effects:', effects)
  }

  /**
   * Создание цепочки эффектов
   */
  private createEffectChain(source: AudioBufferSourceNode, options: SoundPlayOptions): AudioNode {
    const currentNode: AudioNode = source
    
    // Применение эффектов
    if (options.effects) {
      options.effects.forEach(effect => {
        // TODO: Create effect nodes
      })
    }
    
    return currentNode
  }

  /**
   * Применение fade эффектов
   */
  private applyFadeEffects(source: AudioBufferSourceNode, options: SoundPlayOptions): void {
    // TODO: Implement fade effects
    console.log('Applying fade effects:', options)
  }

  /**
   * Загрузка пресетов по умолчанию
   */
  private async loadDefaultPresets(): Promise<void> {
    const defaultPresets: SoundPreset[] = [
      {
        id: 'click',
        name: 'Click',
        description: 'Short click sound',
        config: {
          waveform: 'square',
          frequency: 800,
          duration: 0.05,
          amplitude: 0.3,
          envelope: { attack: 0.001, decay: 0.01, sustain: 0, release: 0.01 }
        }
      },
      {
        id: 'success',
        name: 'Success',
        description: 'Success sound effect',
        config: {
          waveform: 'sine',
          frequency: [523.25, 659.25, 783.99],
          duration: 0.3,
          amplitude: 0.4,
          envelope: { attack: 0.01, decay: 0.1, sustain: 0.3, release: 0.1 }
        }
      },
      {
        id: 'error',
        name: 'Error',
        description: 'Error sound effect',
        config: {
          waveform: 'sawtooth',
          frequency: 200,
          duration: 0.2,
          amplitude: 0.3,
          envelope: { attack: 0.01, decay: 0.05, sustain: 0.1, release: 0.1 }
        }
      }
    ]
    
    defaultPresets.forEach(preset => {
      this.presetManager.registerPreset(preset)
    })
  }

  /**
   * Проверка инициализации
   */
  private ensureInitialized(): void {
    if (!this.isInitialized || !this.audioContext) {
      throw new Error('SoundService is not initialized')
    }
  }
}

/**
 * Менеджер пресетов звуков
 */
class SoundPresetManager implements ISoundPresetManager {
  private presets: Map<string, SoundPreset> = new Map()

  registerPreset(preset: SoundPreset): void {
    this.presets.set(preset.id, preset)
  }

  getPreset(presetId: string): SoundPreset | undefined {
    return this.presets.get(presetId)
  }

  getAllPresets(): Record<string, SoundPreset> {
    return Object.fromEntries(this.presets)
  }

  applyPreset(presetId: string, target?: AudioNode): void {
    const preset = this.getPreset(presetId)
    if (!preset) {
      throw new Error(`Preset ${presetId} not found`)
    }
    // TODO: Apply preset to target
  }

  createCustomPreset(config: CustomSoundPresetConfig): SoundPreset {
    const preset: SoundPreset = {
      id: config.id,
      name: config.name,
      description: config.description,
      config: {
        waveform: config.waveform,
        frequency: config.frequency,
        duration: config.duration,
        amplitude: 1,
        envelope: config.envelope,
        filters: config.filters,
        effects: config.effects
      }
    }
    
    this.registerPreset(preset)
    return preset
  }
}

/**
 * Микшер звуков
 */
class SoundMixer implements ISoundMixer {
  private channels: Map<string, SoundMixerChannel> = new Map()
  private soundService: SoundService

  constructor(soundService: SoundService) {
    this.soundService = soundService
  }

  addChannel(channelId: string, config: SoundMixerConfig): void {
    const audioContext = this.soundService.getAudioContext()
    
    const channel: SoundMixerChannel = {
      id: channelId,
      gainNode: audioContext.createGain(),
      panNode: audioContext.createStereoPanner(),
      config,
      effects: []
    }
    
    channel.gainNode.gain.value = config.volume || 1
    channel.panNode.pan.value = config.pan || 0
    
    // Соединение нод
    channel.gainNode.connect(channel.panNode)
    
    this.channels.set(channelId, channel)
  }

  removeChannel(channelId: string): void {
    const channel = this.channels.get(channelId)
    if (channel) {
      channel.gainNode.disconnect()
      channel.panNode.disconnect()
      this.channels.delete(channelId)
    }
  }

  setChannelVolume(channelId: string, volume: number): void {
    const channel = this.channels.get(channelId)
    if (channel) {
      channel.gainNode.gain.value = Math.max(0, Math.min(1, volume))
    }
  }

  setChannelPan(channelId: string, pan: number): void {
    const channel = this.channels.get(channelId)
    if (channel) {
      channel.panNode.pan.value = Math.max(-1, Math.min(1, pan))
    }
  }

  setChannelEffects(channelId: string, effects: SoundEffect[]): void {
    const channel = this.channels.get(channelId)
    if (channel) {
      channel.effects = effects
    }
  }

  getChannelLevels(): Record<string, number> {
    const levels: Record<string, number> = {}
    this.channels.forEach((channel, id) => {
      levels[id] = channel.gainNode.gain.value
    })
    return levels
  }

  mixChannels(): AudioBuffer {
    // TODO: Implement channel mixing
    throw new Error('Channel mixing not implemented yet')
  }
}

/**
 * Анализатор аудио
 */
class SoundAnalyzer implements ISoundAnalyzer {
  private analyser: AnalyserNode | null = null
  private isAnalyzing = false
  private animationId: number | null = null

  constructor() {}

  analyze(buffer: AudioBuffer): SoundAnalysisData {
    // TODO: Implement buffer analysis
    return {
      peakLevel: 0,
      rmsLevel: 0,
      frequencyData: new Uint8Array(0),
      timeDomainData: new Uint8Array(0)
    }
  }

  getFrequencyData(): Uint8Array {
    if (!this.analyser) return new Uint8Array(0)
    
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount)
    this.analyser.getByteFrequencyData(dataArray)
    return dataArray
  }

  getTimeDomainData(): Uint8Array {
    if (!this.analyser) return new Uint8Array(0)
    
    const dataArray = new Uint8Array(this.analyser.fftSize)
    this.analyser.getByteTimeDomainData(dataArray)
    return dataArray
  }

  getPeakLevel(): number {
    const frequencyData = this.getFrequencyData()
    return Math.max(...frequencyData) / 255
  }

  getRMSLevel(): number {
    const timeDomainData = this.getTimeDomainData()
    const sum = timeDomainData.reduce((acc, val) => acc + val * val, 0)
    return Math.sqrt(sum / timeDomainData.length) / 255
  }

  startRealtimeAnalysis(): void {
    this.isAnalyzing = true
    // TODO: Implement realtime analysis
  }

  stopRealtimeAnalysis(): void {
    this.isAnalyzing = false
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }
  }
}

// Типы для звукового сервиса
export interface SoundServiceStats {
  isInitialized: boolean
  isSuspended: boolean
  activeSoundsCount: number
  masterVolume: number
  sampleRate: number
  presetsCount: number
  channelsCount: number
  audioContextState: AudioContextState
}

interface SoundMixerChannel {
  id: string
  gainNode: GainNode
  panNode: StereoPannerNode
  config: SoundMixerConfig
  effects: SoundEffect[]
}

export default SoundService
