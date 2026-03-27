/**
 * @fileoverview Animation Types - Типы для системы анимаций
 * @version 1.0.0
 * @author Aurion OS Team
 * @license Enterprise
 */

import { Element } from '../types/design-system.types'

// Основные типы анимаций
export interface AnimationConfig {
  id: string
  name: string
  keyframes: Keyframe[]
  options: KeyframeAnimationOptions
  category?: 'entrance' | 'exit' | 'emphasis' | 'loading' | 'interactive' | 'transition'
  description?: string
  tags?: string[]
  dependencies?: string[]
  metadata?: Record<string, any>
}

export interface AnimationPreset {
  id: string
  name: string
  description?: string
  animationId: string
  options: KeyframeAnimationOptions
  category: 'entrance' | 'exit' | 'emphasis' | 'loading' | 'interactive'
  preview?: string
  metadata?: Record<string, any>
}

export interface AnimationTarget {
  element: Element
  selector?: string
  id?: string
  class?: string
}

export interface AnimationSequence {
  id: string
  name: string
  animations: Array<{
    animationId: string
    target: AnimationTarget
    delay?: number
    options?: KeyframeAnimationOptions
  }>
  parallel?: boolean
  loop?: boolean
  isPlaying: boolean
  progress: number
  metadata?: Record<string, any>
}

export interface AnimationSequenceConfig {
  id: string
  name: string
  description?: string
  animations: Array<{
    animationId: string
    target: AnimationTarget
    delay?: number
    options?: KeyframeAnimationOptions
  }>
  parallel?: boolean
  loop?: boolean
  metadata?: Record<string, any>
}

export interface AnimationInstance {
  id: string
  target: AnimationTarget
  config: AnimationConfig
  startTime: number
  duration: number
  progress: number
  state: 'running' | 'paused' | 'completed' | 'cancelled'
  animation: Animation
  metadata?: Record<string, any>
}

export interface AnimationResult {
  success: boolean
  duration: number
  startTime: number
  endTime: number
  target: AnimationTarget
  animationId: string
  metadata?: Record<string, any>
}

export interface AnimationPlayOptions {
  duration?: number
  delay?: number
  easing?: EasingFunction
  iterations?: number
  direction?: AnimationDirection
  fill?: AnimationFillMode
  onComplete?: () => void
  onProgress?: (progress: number) => void
  onStart?: () => void
  onCancel?: () => void
  metadata?: Record<string, any>
}

// Типы для easing функций
export type EasingFunction = 
  | 'linear'
  | 'ease'
  | 'ease-in'
  | 'ease-out'
  | 'ease-in-out'
  | 'step-start'
  | 'step-end'
  | `cubic-bezier(${number},${number},${number},${number})`
  | CustomEasingFunction

export interface CustomEasingFunction {
  name: string
  fn: (t: number) => number
  description?: string
}

export interface EasingPreset {
  name: string
  function: EasingFunction
  curve?: string
  description?: string
  category?: 'basic' | 'advanced' | 'physics' | 'elastic' | 'bounce'
}

// Типы для управления анимациями
export interface AnimationController {
  play(): Promise<void>
  pause(): void
  resume(): void
  stop(): void
  reverse(): void
  seek(time: number): void
  setSpeed(speed: number): void
  getState(): AnimationState
  getProgress(): number
  getDuration(): number
}

export interface AnimationState {
  isPlaying: boolean
  isPaused: boolean
  isCompleted: boolean
  isCancelled: boolean
  currentTime: number
  duration: number
  playbackRate: number
  direction: AnimationDirection
}

export interface AnimationTimeline {
  id: string
  name: string
  animations: AnimationInstance[]
  duration: number
  currentTime: number
  isPlaying: boolean
  playbackRate: number
  metadata?: Record<string, any>
}

// Типы для производительности
export interface PerformanceMetrics {
  totalAnimations: number
  activeAnimations: number
  completedAnimations: number
  cancelledAnimations: number
  averageDuration: number
  droppedFrames: number
  memoryUsage: number
  cpuUsage?: number
  fps: number
  frameTime: number
}

export interface AnimationPerformanceData {
  animationId: string
  startTime: number
  endTime: number
  duration: number
  frames: number
  droppedFrames: number
  averageFrameTime: number
  memoryBefore: number
  memoryAfter: number
}

export interface PerformanceThresholds {
  maxActiveAnimations: number
  maxFrameTime: number
  minFps: number
  maxMemoryUsage: number
  maxDroppedFrames: number
}

// Типы для оптимизации
export interface OptimizationStrategy {
  name: string
  description: string
  priority: number
  conditions: OptimizationCondition[]
  actions: OptimizationAction[]
}

export interface OptimizationCondition {
  type: 'memory' | 'fps' | 'activeAnimations' | 'cpu'
  operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte'
  value: number
}

export interface OptimizationAction {
  type: 'pause' | 'stop' | 'reduceQuality' | 'disableEffects' | 'reduceFps'
  target?: string
  parameters?: Record<string, any>
}

export interface OptimizationConfig {
  enabled: boolean
  strategy: 'auto' | 'manual' | 'adaptive'
  thresholds: PerformanceThresholds
  strategies: OptimizationStrategy[]
  monitoring: boolean
}

// Типы для физики анимаций
export interface PhysicsAnimation {
  type: 'spring' | 'gravity' | 'friction' | 'bounce' | 'elastic'
  config: PhysicsConfig
}

export interface PhysicsConfig {
  mass?: number
  stiffness?: number
  damping?: number
  velocity?: number
  acceleration?: number
  friction?: number
  gravity?: number
  bounciness?: number
  elasticity?: number
}

export interface SpringConfig extends PhysicsConfig {
  tension: number
  friction: number
  mass?: number
  velocity?: number
  clamp?: boolean
  precision?: number
}

export interface GravityConfig extends PhysicsConfig {
  gravity: number
  bounce: number
  friction: number
  mass?: number
  velocity?: { x: number; y: number }
}

// Типы для интерактивных анимаций
export interface InteractiveAnimation {
  trigger: InteractiveTrigger
  animation: AnimationConfig
  conditions?: InteractionCondition[]
  metadata?: Record<string, any>
}

export interface InteractiveTrigger {
  type: 'hover' | 'click' | 'focus' | 'scroll' | 'drag' | 'swipe' | 'pinch' | 'keyboard'
  target: AnimationTarget
  parameters?: Record<string, any>
}

export interface InteractionCondition {
  type: 'device' | 'viewport' | 'userPreference' | 'time' | 'location'
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'contains' | 'matches'
  value: any
}

export interface GestureAnimation {
  gesture: GestureType
  animation: AnimationConfig
  sensitivity: number
  threshold: number
  metadata?: Record<string, any>
}

export type GestureType = 
  | 'tap'
  | 'doubleTap'
  | 'longPress'
  | 'swipeLeft'
  | 'swipeRight'
  | 'swipeUp'
  | 'swipeDown'
  | 'pinch'
  | 'spread'
  | 'rotate'
  | 'drag'

// Типы для параллакс и скролл анимаций
export interface ScrollAnimation {
  trigger: ScrollTrigger
  animation: AnimationConfig
  scrub?: boolean
  startOffset?: number
  endOffset?: number
  direction?: 'vertical' | 'horizontal'
  metadata?: Record<string, any>
}

export interface ScrollTrigger {
  type: 'element' | 'position' | 'direction' | 'velocity'
  target?: AnimationTarget
  start: number | string
  end: number | string
  scrub?: boolean
}

export interface ParallaxConfig {
  speed: number
  direction: 'vertical' | 'horizontal' | 'both'
  depth: number
  perspective?: number
  origin?: string
}

// Типы для морфинга и трансформаций
export interface MorphAnimation {
  type: 'path' | 'shape' | 'text' | 'color'
  from: MorphTarget
  to: MorphTarget
  duration: number
  easing?: EasingFunction
  intermediate?: MorphTarget[]
}

export interface MorphTarget {
  type: string
  data: any
  attributes?: Record<string, any>
}

export interface TransformConfig {
  translate?: { x?: number; y?: number; z?: number }
  rotate?: { x?: number; y?: number; z?: number }
  scale?: { x?: number; y?: number; z?: number }
  skew?: { x?: number; y?: number }
  origin?: string
}

// Типы для particle анимаций
export interface ParticleAnimation {
  type: 'emit' | 'burst' | 'trail' | 'field' | 'flow'
  config: ParticleConfig
  count: number
  lifetime: number
  emission?: EmissionConfig
}

export interface ParticleConfig {
  shape: 'circle' | 'square' | 'triangle' | 'star' | 'custom'
  size: { min: number; max: number }
  color: { start: string; end: string } | string[]
  velocity: { min: number; max: number }
  acceleration: { x: number; y: number }
  opacity: { start: number; end: number }
  rotation?: { start: number; end: number }
  scale?: { start: number; end: number }
}

export interface EmissionConfig {
  rate: number
  duration: number
  spread: number
  direction: number
  cone: number
}

// Типы для текстовых анимаций
export interface TextAnimation {
  type: 'typewriter' | 'fade' | 'slide' | 'glitch' | 'wave' | 'morph'
  config: TextAnimationConfig
  target: string
  options?: TextAnimationOptions
}

export interface TextAnimationConfig {
  speed: number
  delay?: number
  stagger?: number
  direction?: 'forward' | 'backward' | 'center'
  preserveSpaces?: boolean
}

export interface TextAnimationOptions {
  cursor?: boolean
  cursorChar?: string
  blinkSpeed?: number
  randomize?: boolean
  caseSensitive?: boolean
}

// Типы для реактивных анимаций
export interface ReactiveAnimation {
  trigger: ReactiveTrigger
  animation: AnimationConfig
  debounce?: number
  throttle?: number
  metadata?: Record<string, any>
}

export interface ReactiveTrigger {
  type: 'state' | 'prop' | 'event' | 'data' | 'computed'
  source: string
  property?: string
  condition?: (value: any) => boolean
}

// Типы для конфигурации системы
export interface AnimationSystemConfig {
  enabled: boolean
  performance: OptimizationConfig
  defaults: {
    duration: number
    easing: EasingFunction
    fill: AnimationFillMode
  }
  features: {
    physics: boolean
    particles: boolean
    text: boolean
    interactive: boolean
    scroll: boolean
    morph: boolean
  }
  debugging: {
    enabled: boolean
    showBoundingBoxes: boolean
    showPerformance: boolean
    logEvents: boolean
  }
}

// Типы для событий
export interface AnimationEvent {
  type: 'start' | 'complete' | 'pause' | 'resume' | 'cancel' | 'error' | 'progress'
  animationId: string
  instanceId?: string
  timestamp: number
  data?: any
  target?: AnimationTarget
}

export interface AnimationSystemEvent {
  type: 'initialized' | 'disposed' | 'performanceWarning' | 'optimizationApplied'
  timestamp: number
  data?: any
}

// Utility types
export type AnimationDirection = 'normal' | 'reverse' | 'alternate' | 'alternate-reverse'
export type AnimationFillMode = 'none' | 'forwards' | 'backwards' | 'both'

export type AnimationCallback = (event: AnimationEvent) => void
export type AnimationProgressCallback = (progress: number, instance: AnimationInstance) => void

export type AnimationFactory<T = any> = (config: T) => AnimationConfig
export type AnimationValidator = (config: AnimationConfig) => ValidationResult
export type AnimationTransformer = (config: AnimationConfig) => AnimationConfig

// Type guards
export function isAnimationConfig(obj: any): obj is AnimationConfig {
  return obj && typeof obj === 'object' && 
         typeof obj.id === 'string' && 
         typeof obj.name === 'string' && 
         Array.isArray(obj.keyframes)
}

export function isAnimationTarget(obj: any): obj is AnimationTarget {
  return obj && typeof obj === 'object' && 
         (obj.element instanceof Element || obj.selector || obj.id || obj.class)
}

export function isValidEasingFunction(value: string): value is EasingFunction {
  return [
    'linear', 'ease', 'ease-in', 'ease-out', 'ease-in-out', 
    'step-start', 'step-end'
  ].includes(value) || value.startsWith('cubic-bezier')
}

// Export all types
export * from './design-system.types'
