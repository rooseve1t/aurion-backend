import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  moduleName?: string
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`[ErrorBoundary] ${this.props.moduleName || 'Module'} crashed:`, error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
          padding: '2rem',
          background: 'rgba(255, 50, 50, 0.05)',
          border: '1px solid rgba(255, 50, 50, 0.2)',
          borderRadius: '8px',
          color: '#ff6b6b',
          gap: '1rem',
        }}>
          <div style={{ fontSize: '2rem' }}>⚠️</div>
          <div style={{ fontWeight: 600 }}>
            {this.props.moduleName ? `Модуль "${this.props.moduleName}" недоступен` : 'Произошла ошибка'}
          </div>
          <div style={{ fontSize: '0.85rem', opacity: 0.7, maxWidth: '400px', textAlign: 'center' }}>
            {this.state.error?.message || 'Неизвестная ошибка'}
          </div>
          <button
            onClick={this.handleReset}
            style={{
              padding: '0.5rem 1.5rem',
              background: 'rgba(255, 50, 50, 0.15)',
              border: '1px solid rgba(255, 50, 50, 0.4)',
              borderRadius: '4px',
              color: '#ff6b6b',
              cursor: 'pointer',
            }}
          >
            Попробовать снова
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
