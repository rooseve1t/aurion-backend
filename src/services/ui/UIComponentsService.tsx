/**
 * @fileoverview UI Components Service - Сервис управления UI компонентами
 * @version 1.0.0
 * @author Aurion OS Team
 * @license Enterprise
 */

import { EventEmitter } from 'events'
import React, { ComponentType, ReactNode } from 'react'
import { 
  UIComponent, 
  ComponentRegistry, 
  ComponentMetadata,
  ComponentInstance,
  ComponentTheme,
  ComponentState,
  ComponentEvent,
  ComponentMetrics 
} from '../types/ui-components.types'

/**
 * Интерфейс реестра компонентов
 */
export interface IComponentRegistry {
  register<T extends UIComponent>(component: ComponentRegistry<T>): void
  unregister(componentId: string): void
  get<T extends UIComponent>(componentId: string): ComponentRegistry<T> | undefined
  getAll(): Record<string, ComponentRegistry<UIComponent>>
  getByCategory(category: string): ComponentRegistry<UIComponent>[]
  search(query: string): ComponentRegistry<UIComponent>[]
}

/**
 * Интерфейс менеджера тем компонентов
 */
export interface IComponentThemeManager {
  applyTheme(theme: ComponentTheme): void
  getTheme(): ComponentTheme
  registerTheme(theme: ComponentTheme): void
  getAvailableThemes(): string[]
  setTheme(themeId: string): void
}

/**
 * Интерфейс менеджера состояния компонентов
 */
export interface IComponentStateManager {
  getState(componentId: string): ComponentState
  setState(componentId: string, state: Partial<ComponentState>): void
  subscribe(componentId: string, callback: (state: ComponentState) => void): () => void
  getGlobalState(): Record<string, ComponentState>
  resetState(componentId: string): void
}

/**
 * Интерфейс менеджера метрик
 */
export interface IComponentMetricsManager {
  recordEvent(event: ComponentEvent): void
  getMetrics(componentId: string): ComponentMetrics
  getAllMetrics(): Record<string, ComponentMetrics>
  resetMetrics(componentId?: string): void
  exportMetrics(): string
}

/**
 * Опции рендеринга компонента
 */
export interface ComponentRenderOptions {
  theme?: string
  props?: Record<string, any>
  state?: ComponentState
  className?: string
  style?: Record<string, any>
  children?: ReactNode
  events?: Record<string, Function>
}

/**
 * Конфигурация компонента
 */
export interface ComponentConfig {
  id: string
  name: string
  version: string
  category: string
  description?: string
  tags?: string[]
  dependencies?: string[]
  props?: Record<string, any>
  defaultProps?: Record<string, any>
  styles?: Record<string, any>
  animations?: string[]
  sounds?: string[]
}

/**
 * Основной класс сервиса UI компонентов
 */
export class UIComponentsService extends EventEmitter implements IComponentRegistry {
  private static instance: UIComponentsService
  private components: Map<string, ComponentRegistry<UIComponent>> = new Map()
  private instances: Map<string, ComponentInstance> = new Map()
  private themeManager: IComponentThemeManager
  private stateManager: IComponentStateManager
  private metricsManager: IComponentMetricsManager
  private isInitialized = false

  constructor() {
    super()
    this.themeManager = new ComponentThemeManager()
    this.stateManager = new ComponentStateManager()
    this.metricsManager = new ComponentMetricsManager()
    this.setupEventListeners()
  }

  /**
   * Получение singleton экземпляра
   */
  static getInstance(): UIComponentsService {
    if (!UIComponentsService.instance) {
      UIComponentsService.instance = new UIComponentsService()
    }
    return UIComponentsService.instance
  }

  /**
   * Инициализация сервиса
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) return

    try {
      await this.loadCoreComponents()
      await this.loadThemes()
      this.isInitialized = true
      
      this.emit('initialized', {
        timestamp: new Date().toISOString(),
        componentsCount: this.components.size
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
   * Регистрация компонента
   */
  public register<T extends UIComponent>(component: ComponentRegistry<T>): void {
    this.validateComponentRegistry(component)
    
    this.components.set(component.config.id, component)
    this.stateManager.initializeState(component.config.id)
    
    this.emit('componentRegistered', {
      componentId: component.config.id,
      category: component.config.category,
      timestamp: Date.now()
    })
  }

  /**
   * Удаление компонента
   */
  public unregister(componentId: string): void {
    const component = this.components.get(componentId)
    if (!component) {
      throw new Error(`Component ${componentId} not found`)
    }

    // Очистка экземпляров
    const instances = this.getInstancesByComponent(componentId)
    instances.forEach(instance => this.destroyInstance(instance.id))

    this.components.delete(componentId)
    this.stateManager.resetState(componentId)
    this.metricsManager.resetMetrics(componentId)

    this.emit('componentUnregistered', {
      componentId,
      timestamp: Date.now()
    })
  }

  /**
   * Получение компонента
   */
  public get<T extends UIComponent>(componentId: string): ComponentRegistry<T> | undefined {
    return this.components.get(componentId) as ComponentRegistry<T> | undefined
  }

  /**
   * Получение всех компонентов
   */
  public getAll(): Record<string, ComponentRegistry<UIComponent>> {
    return Object.fromEntries(this.components)
  }

  /**
   * Получение компонентов по категории
   */
  public getByCategory(category: string): ComponentRegistry<UIComponent>[] {
    return Array.from(this.components.values()).filter(
      component => component.config.category === category
    )
  }

  /**
   * Поиск компонентов
   */
  public search(query: string): ComponentRegistry<UIComponent>[] {
    const lowerQuery = query.toLowerCase()
    return Array.from(this.components.values()).filter(component => 
      component.config.name.toLowerCase().includes(lowerQuery) ||
      component.config.description?.toLowerCase().includes(lowerQuery) ||
      component.config.tags?.some(tag => tag.toLowerCase().includes(lowerQuery))
    )
  }

  /**
   * Создание экземпляра компонента
   */
  public createInstance(
    componentId: string, 
    options: ComponentRenderOptions = {}
  ): ComponentInstance {
    const component = this.components.get(componentId)
    if (!component) {
      throw new Error(`Component ${componentId} not found`)
    }

    const instanceId = `${componentId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const instance: ComponentInstance = {
      id: instanceId,
      componentId,
      component,
      props: { ...component.config.defaultProps, ...options.props },
      state: { ...this.stateManager.getState(componentId), ...options.state },
      theme: options.theme || this.themeManager.getTheme().id,
      className: options.className || '',
      style: options.style || {},
      children: options.children,
      events: options.events || {},
      isMounted: false,
      renderCount: 0,
      lastRenderTime: 0,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    this.instances.set(instanceId, instance)
    this.stateManager.setState(componentId, instance.state)
    
    this.emit('instanceCreated', {
      instanceId,
      componentId,
      timestamp: Date.now()
    })

    return instance
  }

  /**
   * Обновление экземпляра компонента
   */
  public updateInstance(
    instanceId: string, 
    updates: Partial<ComponentRenderOptions>
  ): ComponentInstance {
    const instance = this.instances.get(instanceId)
    if (!instance) {
      throw new Error(`Instance ${instanceId} not found`)
    }

    const oldProps = { ...instance.props }
    const oldState = { ...instance.state }

    // Обновление свойств
    if (updates.props) {
      instance.props = { ...instance.props, ...updates.props }
    }

    // Обновление состояния
    if (updates.state) {
      instance.state = { ...instance.state, ...updates.state }
      this.stateManager.setState(instance.componentId, instance.state)
    }

    // Обновление темы
    if (updates.theme) {
      instance.theme = updates.theme
    }

    // Обновление стилей
    if (updates.style) {
      instance.style = { ...instance.style, ...updates.style }
    }

    // Обновление className
    if (updates.className !== undefined) {
      instance.className = updates.className
    }

    // Обновление children
    if (updates.children !== undefined) {
      instance.children = updates.children
    }

    // Обновление событий
    if (updates.events) {
      instance.events = { ...instance.events, ...updates.events }
    }

    instance.updatedAt = Date.now()
    instance.renderCount++

    // Запись событий
    this.metricsManager.recordEvent({
      type: 'update',
      instanceId,
      componentId: instance.componentId,
      timestamp: Date.now(),
      data: {
        propsChanged: JSON.stringify(oldProps) !== JSON.stringify(instance.props),
        stateChanged: JSON.stringify(oldState) !== JSON.stringify(instance.state)
      }
    })

    this.emit('instanceUpdated', {
      instanceId,
      componentId: instance.componentId,
      timestamp: Date.now()
    })

    return instance
  }

  /**
   * Уничтожение экземпляра компонента
   */
  public destroyInstance(instanceId: string): void {
    const instance = this.instances.get(instanceId)
    if (!instance) return

    this.metricsManager.recordEvent({
      type: 'destroy',
      instanceId,
      componentId: instance.componentId,
      timestamp: Date.now()
    })

    this.instances.delete(instanceId)
    
    this.emit('instanceDestroyed', {
      instanceId,
      componentId: instance.componentId,
      timestamp: Date.now()
    })
  }

  /**
   * Получение экземпляра
   */
  public getInstance(instanceId: string): ComponentInstance | undefined {
    return this.instances.get(instanceId)
  }

  /**
   * Получение всех экземпляров
   */
  public getAllInstances(): ComponentInstance[] {
    return Array.from(this.instances.values())
  }

  /**
   * Получение экземпляров компонента
   */
  public getInstancesByComponent(componentId: string): ComponentInstance[] {
    return Array.from(this.instances.values()).filter(
      instance => instance.componentId === componentId
    )
  }

  /**
   * Рендеринг компонента
   */
  public renderComponent(
    componentId: string, 
    options: ComponentRenderOptions = {}
  ): React.ReactElement {
    const component = this.components.get(componentId)
    if (!component) {
      throw new Error(`Component ${componentId} not found`)
    }

    const instance = this.createInstance(componentId, options)
    
    // Применение темы
    const theme = this.themeManager.getTheme()
    
    // Применение стилей темы
    const themedStyle = {
      ...theme.styles?.[componentId],
      ...instance.style
    }

    const Component = component.component as ComponentType<any>

    return (
      <Component
        key={instance.id}
        {...instance.props}
        {...instance.state}
        className={`${instance.className} ${theme.classes?.[componentId] || ''}`}
        style={themedStyle}
        instance={instance}
        theme={theme}
        onStateChange={(newState: any) => {
          this.updateInstance(instance.id, { state: newState })
        }}
        onEvent={(eventName: string, eventData: any) => {
          this.handleComponentEvent(instance.id, eventName, eventData)
        }}
      >
        {instance.children}
      </Component>
    )
  }

  /**
   * Получение менеджера тем
   */
  public getThemeManager(): IComponentThemeManager {
    return this.themeManager
  }

  /**
   * Получение менеджера состояний
   */
  public getStateManager(): IComponentStateManager {
    return this.stateManager
  }

  /**
   * Получение менеджера метрик
   */
  public getMetricsManager(): IComponentMetricsManager {
    return this.metricsManager
  }

  /**
   * Валидация системы
   */
  public validateSystem(): ValidationResult {
    const results = {
      components: this.validateComponents(),
      instances: this.validateInstances(),
      themes: this.themeManager.getAvailableThemes().length > 0,
      states: true // TODO: Implement state validation
    }

    const isValid = Object.values(results).every(Boolean)
    
    return {
      isValid,
      details: results,
      timestamp: new Date().toISOString()
    }
  }

  /**
   * Получение статистики
   */
  public getStats(): ComponentServiceStats {
    return {
      componentsCount: this.components.size,
      instancesCount: this.instances.size,
      categoriesCount: new Set(Array.from(this.components.values()).map(c => c.config.category)).size,
      themesCount: this.themeManager.getAvailableThemes().length,
      isInitialized: this.isInitialized,
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage()
    }
  }

  /**
   * Очистка ресурсов
   */
  public dispose(): void {
    this.instances.forEach(instance => this.destroyInstance(instance.id))
    this.components.clear()
    this.removeAllListeners()
    this.emit('disposed')
  }

  /**
   * Валидация реестра компонента
   */
  private validateComponentRegistry<T extends UIComponent>(component: ComponentRegistry<T>): void {
    if (!component.config.id || !component.config.name || !component.component) {
      throw new Error('Invalid component registry: missing required fields')
    }

    if (this.components.has(component.config.id)) {
      throw new Error(`Component ${component.config.id} already registered`)
    }
  }

  /**
   * Валидация компонентов
   */
  private validateComponents(): boolean {
    for (const [id, component] of this.components) {
      if (!component.config.id || !component.config.name || !component.component) {
        console.warn(`Invalid component: ${id}`)
        return false
      }
    }
    return true
  }

  /**
   * Валидация экземпляров
   */
  private validateInstances(): boolean {
    for (const [id, instance] of this.instances) {
      if (!instance.componentId || !this.components.has(instance.componentId)) {
        console.warn(`Invalid instance: ${id}`)
        return false
      }
    }
    return true
  }

  /**
   * Загрузка базовых компонентов
   */
  private async loadCoreComponents(): Promise<void> {
    // TODO: Load core components dynamically
    console.log('Loading core components...')
  }

  /**
   * Загрузка тем
   */
  private async loadThemes(): Promise<void> {
    // TODO: Load themes dynamically
    console.log('Loading themes...')
  }

  /**
   * Настройка слушателей событий
   */
  private setupEventListeners(): void {
    this.stateManager.on('stateChanged', (data) => {
      this.emit('stateChanged', data)
    })

    this.themeManager.on('themeChanged', (data) => {
      this.emit('themeChanged', data)
    })
  }

  /**
   * Обработка событий компонента
   */
  private handleComponentEvent(instanceId: string, eventName: string, eventData: any): void {
    const instance = this.instances.get(instanceId)
    if (!instance) return

    this.metricsManager.recordEvent({
      type: 'user_event',
      instanceId,
      componentId: instance.componentId,
      timestamp: Date.now(),
      data: { eventName, eventData }
    })

    // Вызов обработчика события
    const handler = instance.events[eventName]
    if (typeof handler === 'function') {
      handler(eventData)
    }

    this.emit('componentEvent', {
      instanceId,
      componentId: instance.componentId,
      eventName,
      eventData,
      timestamp: Date.now()
    })
  }
}

/**
 * Менеджер тем компонентов
 */
class ComponentThemeManager extends EventEmitter implements IComponentThemeManager {
  private themes: Map<string, ComponentTheme> = new Map()
  private currentTheme: ComponentTheme

  constructor() {
    super()
    this.currentTheme = this.createDefaultTheme()
  }

  applyTheme(theme: ComponentTheme): void {
    this.currentTheme = theme
    this.emit('themeChanged', { themeId: theme.id, timestamp: Date.now() })
  }

  getTheme(): ComponentTheme {
    return this.currentTheme
  }

  registerTheme(theme: ComponentTheme): void {
    this.themes.set(theme.id, theme)
    this.emit('themeRegistered', { themeId: theme.id, timestamp: Date.now() })
  }

  getAvailableThemes(): string[] {
    return Array.from(this.themes.keys())
  }

  setTheme(themeId: string): void {
    const theme = this.themes.get(themeId)
    if (!theme) {
      throw new Error(`Theme ${themeId} not found`)
    }
    this.applyTheme(theme)
  }

  private createDefaultTheme(): ComponentTheme {
    return {
      id: 'default',
      name: 'Default Theme',
      colors: {
        primary: '#00fbfb',
        secondary: '#b200fb',
        success: '#4ede63',
        warning: '#ffb800',
        error: '#ff4757',
        background: '#0a0a23',
        surface: '#1a1a3e',
        text: '#ffffff',
        textSecondary: '#b8bcc8'
      },
      typography: {
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          md: '1rem',
          lg: '1.125rem',
          xl: '1.25rem'
        }
      },
      spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem'
      },
      borderRadius: {
        sm: '0.25rem',
        md: '0.5rem',
        lg: '1rem',
        xl: '1.5rem'
      },
      shadows: {
        sm: '0 1px 2px rgba(0,0,0,0.1)',
        md: '0 4px 6px rgba(0,0,0,0.1)',
        lg: '0 10px 15px rgba(0,0,0,0.1)',
        xl: '0 20px 25px rgba(0,0,0,0.1)'
      },
      classes: {},
      styles: {}
    }
  }
}

/**
 * Менеджер состояний компонентов
 */
class ComponentStateManager extends EventEmitter {
  private states: Map<string, ComponentState> = new Map()
  private subscribers: Map<string, Set<(state: ComponentState) => void>> = new Map()

  initializeState(componentId: string): void {
    if (!this.states.has(componentId)) {
      this.states.set(componentId, {
        isLoading: false,
        isDisabled: false,
        isVisible: true,
        hasError: false,
        isValid: true,
        value: null,
        metadata: {}
      })
    }
  }

  getState(componentId: string): ComponentState {
    return this.states.get(componentId) || {
      isLoading: false,
      isDisabled: false,
      isVisible: true,
      hasError: false,
      isValid: true,
      value: null,
      metadata: {}
    }
  }

  setState(componentId: string, state: Partial<ComponentState>): void {
    const currentState = this.getState(componentId)
    const newState = { ...currentState, ...state }
    
    this.states.set(componentId, newState)
    
    // Уведомление подписчиков
    const subscribers = this.subscribers.get(componentId)
    if (subscribers) {
      subscribers.forEach(callback => callback(newState))
    }
    
    this.emit('stateChanged', { componentId, state: newState, timestamp: Date.now() })
  }

  subscribe(componentId: string, callback: (state: ComponentState) => void): () => void {
    if (!this.subscribers.has(componentId)) {
      this.subscribers.set(componentId, new Set())
    }
    
    this.subscribers.get(componentId)!.add(callback)
    
    // Возврат функции отписки
    return () => {
      const subscribers = this.subscribers.get(componentId)
      if (subscribers) {
        subscribers.delete(callback)
        if (subscribers.size === 0) {
          this.subscribers.delete(componentId)
        }
      }
    }
  }

  getGlobalState(): Record<string, ComponentState> {
    return Object.fromEntries(this.states)
  }

  resetState(componentId: string): void {
    this.initializeState(componentId)
    this.emit('stateReset', { componentId, timestamp: Date.now() })
  }
}

/**
 * Менеджер метрик компонентов
 */
class ComponentMetricsManager implements IComponentMetricsManager {
  private metrics: Map<string, ComponentMetrics> = new Map()
  private events: ComponentEvent[] = []

  recordEvent(event: ComponentEvent): void {
    this.events.push(event)
    
    // Обновление метрик компонента
    const metrics = this.metrics.get(event.componentId) || {
      componentId: event.componentId,
      renderCount: 0,
      updateCount: 0,
      eventCount: 0,
      errorCount: 0,
      averageRenderTime: 0,
      lastActivity: Date.now(),
      createdAt: Date.now()
    }

    switch (event.type) {
      case 'render':
        metrics.renderCount++
        break
      case 'update':
        metrics.updateCount++
        break
      case 'user_event':
        metrics.eventCount++
        break
      case 'error':
        metrics.errorCount++
        break
    }

    metrics.lastActivity = Date.now()
    this.metrics.set(event.componentId, metrics)
  }

  getMetrics(componentId: string): ComponentMetrics {
    return this.metrics.get(componentId) || {
      componentId,
      renderCount: 0,
      updateCount: 0,
      eventCount: 0,
      errorCount: 0,
      averageRenderTime: 0,
      lastActivity: Date.now(),
      createdAt: Date.now()
    }
  }

  getAllMetrics(): Record<string, ComponentMetrics> {
    return Object.fromEntries(this.metrics)
  }

  resetMetrics(componentId?: string): void {
    if (componentId) {
      this.metrics.delete(componentId)
    } else {
      this.metrics.clear()
      this.events = []
    }
  }

  exportMetrics(): string {
    return JSON.stringify({
      metrics: Object.fromEntries(this.metrics),
      events: this.events,
      exportedAt: new Date().toISOString()
    }, null, 2)
  }
}

// Типы для UI компонентов
export interface UIComponent {
  render(): React.ReactElement
  componentDidMount?(): void
  componentWillUnmount?(): void
  shouldComponentUpdate?(nextProps: any, nextState: any): boolean
}

export interface ValidationResult {
  isValid: boolean
  details: Record<string, boolean>
  timestamp: string
}

export interface ComponentServiceStats {
  componentsCount: number
  instancesCount: number
  categoriesCount: number
  themesCount: number
  isInitialized: boolean
  uptime: number
  memoryUsage: NodeJS.MemoryUsage
}

export default UIComponentsService
