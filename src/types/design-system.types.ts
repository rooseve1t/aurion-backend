/**
 * @fileoverview Design System Types - Типы для дизайн-системы
 * @version 1.0.0
 * @author Aurion OS Team
 * @license Enterprise
 */

// Базовые типы дизайн-системы
export interface DesignToken {
  value: string | number
  type: 'color' | 'size' | 'spacing' | 'typography' | 'animation' | 'sound' | 'shadow' | 'border'
  category: string
  description?: string
  metadata?: Record<string, any>
}

export interface ThemeConfig {
  id: string
  name: string
  description?: string
  tokens: Record<string, string>
  extends?: string[]
  metadata?: Record<string, any>
}

export interface ComponentConfig {
  id: string
  name: string
  version: string
  description?: string
  props: Record<string, any>
  variants?: string[]
  dependencies?: string[]
  tokens?: Record<string, string>
  metadata?: Record<string, any>
}

export interface AnimationConfig {
  id: string
  name: string
  keyframes: Keyframe[]
  options: KeyframeAnimationOptions
  category?: 'entrance' | 'exit' | 'emphasis' | 'loading' | 'interactive'
  metadata?: Record<string, any>
}

export interface SoundConfig {
  id: string
  name: string
  waveform: OscillatorType
  frequency: number | number[]
  duration: number
  amplitude?: number
  envelope?: ADSREnvelope
  effects?: SoundEffect[]
  metadata?: Record<string, any>
}

export interface DesignSystemConfig {
  version: string
  name: string
  description?: string
  tokens: Record<string, DesignToken>
  themes: Record<string, ThemeConfig>
  components: Record<string, ComponentConfig>
  animations: Record<string, AnimationConfig>
  sounds: Record<string, SoundConfig>
  metadata?: Record<string, any>
}

export interface ValidationResult {
  isValid: boolean
  details: Record<string, boolean>
  errors?: string[]
  warnings?: string[]
  timestamp: string
}

export interface SystemStats {
  version: string
  uptime: number
  memoryUsage: NodeJS.MemoryUsage
  componentsCount: number
  tokensCount: number
  themesCount: number
  isInitialized: boolean
  performance?: PerformanceMetrics
}

export interface PerformanceMetrics {
  totalAnimations: number
  activeAnimations: number
  averageDuration: number
  droppedFrames: number
  memoryUsage: number
  cpuUsage?: number
}

export interface ADSREnvelope {
  attack: number
  decay: number
  sustain: number
  release: number
}

export interface SoundEffect {
  type: 'reverb' | 'delay' | 'distortion' | 'filter' | 'compressor'
  params: Record<string, any>
}

export interface AudioFilterConfig {
  type: BiquadFilterType
  frequency: number
  Q?: number
  gain?: number
}

export interface AudioContextConfig {
  sampleRate?: number
  latency?: AudioContextLatencyCategory
  numberOfChannels?: number
}

// Типы для событий
export interface SystemEvent {
  type: string
  timestamp: number
  data?: any
  source?: string
}

export interface ComponentEvent {
  type: 'mount' | 'unmount' | 'update' | 'click' | 'focus' | 'blur' | 'change'
  componentId: string
  instanceId?: string
  timestamp: number
  data?: any
}

export interface AnimationEvent {
  type: 'start' | 'complete' | 'pause' | 'resume' | 'cancel'
  animationId: string
  target?: Element
  timestamp: number
  data?: any
}

export interface SoundEvent {
  type: 'start' | 'complete' | 'stop' | 'error'
  soundId: string
  presetId?: string
  timestamp: number
  data?: any
}

// Типы для конфигурации
export interface ServiceConfig {
  name: string
  version: string
  enabled: boolean
  options?: Record<string, any>
}

export interface LoggingConfig {
  level: 'debug' | 'info' | 'warn' | 'error'
  enabled: boolean
  outputs: ('console' | 'file' | 'remote')[]
  format?: 'json' | 'text'
}

export interface CacheConfig {
  maxSize: number
  ttl: number
  strategy: 'lru' | 'fifo' | 'lfu'
}

export interface SecurityConfig {
  enabled: boolean
  cors?: {
    enabled: boolean
    origins: string[]
    credentials: boolean
  }
  csrf?: {
    enabled: boolean
    token: string
  }
  rateLimit?: {
    enabled: boolean
    requests: number
    window: number
  }
}

// Типы для API
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
  requestId?: string
}

export interface PaginationParams {
  page: number
  limit: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
}

// Типы для пользователей и аутентификации
export interface User {
  id: string
  username: string
  email: string
  role: UserRole
  permissions: Permission[]
  preferences: UserPreferences
  metadata: Record<string, any>
  createdAt: string
  updatedAt: string
}

export interface UserRole {
  id: string
  name: string
  permissions: Permission[]
  hierarchy: number
}

export interface Permission {
  id: string
  name: string
  resource: string
  action: string
  conditions?: Record<string, any>
}

export interface UserPreferences {
  theme: string
  language: string
  notifications: NotificationPreferences
  accessibility: AccessibilityPreferences
  privacy: PrivacyPreferences
}

export interface NotificationPreferences {
  email: boolean
  push: boolean
  sound: boolean
  types: Record<string, boolean>
}

export interface AccessibilityPreferences {
  reducedMotion: boolean
  highContrast: boolean
  largeText: boolean
  screenReader: boolean
  keyboardNavigation: boolean
}

export interface PrivacyPreferences {
  analytics: boolean
  cookies: boolean
  personalization: boolean
  dataSharing: boolean
}

// Типы для состояний
export interface LoadingState {
  isLoading: boolean
  message?: string
  progress?: number
}

export interface ErrorState {
  hasError: boolean
  message?: string
  code?: string
  details?: any
}

export interface ValidationState {
  isValid: boolean
  errors: Record<string, string[]>
  warnings: Record<string, string[]>
}

// Типы для кэширования
export interface CacheItem<T = any> {
  key: string
  value: T
  timestamp: number
  ttl: number
  hits: number
  metadata?: Record<string, any>
}

export interface CacheStats {
  size: number
  hits: number
  misses: number
  hitRate: number
  memoryUsage: number
}

// Типы для мониторинга
export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded'
  timestamp: string
  checks: Record<string, HealthCheckResult>
  uptime: number
  version: string
}

export interface HealthCheckResult {
  status: 'pass' | 'fail' | 'warn'
  message?: string
  duration?: number
  metadata?: Record<string, any>
}

export interface MetricData {
  name: string
  value: number
  timestamp: number
  labels?: Record<string, string>
  type: 'counter' | 'gauge' | 'histogram' | 'summary'
}

export interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error'
  message: string
  timestamp: string
  context?: Record<string, any>
  stack?: string
}

// Типы для конфигурации окружения
export interface EnvironmentConfig {
  name: 'development' | 'staging' | 'production'
  debug: boolean
  api: {
    baseUrl: string
    timeout: number
    retries: number
  }
  database: {
    host: string
    port: number
    name: string
    ssl: boolean
  }
  cache: {
    enabled: boolean
    type: 'redis' | 'memory' | 'file'
    config: Record<string, any>
  }
  logging: LoggingConfig
  security: SecurityConfig
  features: Record<string, boolean>
}

// Типы для интернационализации
export interface I18nConfig {
  defaultLocale: string
  supportedLocales: string[]
  fallbackLocale: string
  resources: Record<string, Record<string, string>>
  interpolation?: {
    prefix?: string
    suffix?: string
  }
  pluralization?: Record<string, (count: number) => string>
}

export interface LocaleData {
  code: string
  name: string
  nativeName: string
  rtl: boolean
  resources: Record<string, string>
  metadata?: Record<string, any>
}

// Типы для тестирования
export interface TestConfig {
  framework: 'jest' | 'vitest' | 'mocha'
  coverage: {
    enabled: boolean
    threshold: number
    reporters: string[]
  }
  reporters: string[]
  setupFiles: string[]
  testMatch: string[]
  testIgnore: string[]
}

export interface TestResult {
  name: string
  status: 'passed' | 'failed' | 'skipped' | 'pending'
  duration: number
  error?: string
  assertions?: number
}

export interface CoverageReport {
  lines: {
    total: number
    covered: number
    percentage: number
  }
  functions: {
    total: number
    covered: number
    percentage: number
  }
  branches: {
    total: number
    covered: number
    percentage: number
  }
  statements: {
    total: number
    covered: number
    percentage: number
  }
}

// Типы для CI/CD
export interface PipelineConfig {
  name: string
  triggers: string[]
  stages: PipelineStage[]
  environment: Record<string, string>
  notifications: NotificationConfig[]
}

export interface PipelineStage {
  name: string
  type: 'build' | 'test' | 'deploy' | 'security' | 'performance'
  commands: string[]
  timeout?: number
  retries?: number
  conditions?: string[]
}

export interface NotificationConfig {
  type: 'email' | 'slack' | 'webhook' | 'sms'
  enabled: boolean
  conditions: string[]
  recipients: string[]
  template?: string
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type EventHandler<T = any> = (data: T) => void

export type AsyncEventHandler<T = any> = (data: T) => Promise<void>

export type Comparator<T> = (a: T, b: T) => number

export type Predicate<T> = (value: T) => boolean

export type Transformer<T, U> = (value: T) => U

export type Validator<T> = (value: T) => ValidationResult

// Export all types
export * from './animation.types'
export * from './ui-components.types'
export * from './sound.types'
