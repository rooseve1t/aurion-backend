/**
 * Тесты для VoiceIndicator — переключение состояний и автовозврат.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { VoiceIndicator } from '@/components/VoiceIndicator'

describe('VoiceIndicator', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('отображает "Ожидание" в состоянии idle', () => {
    render(<VoiceIndicator state="idle" />)
    expect(screen.getByText('Ожидание')).toBeTruthy()
  })

  it('отображает "Слушаю" в состоянии listening', () => {
    render(<VoiceIndicator state="listening" />)
    expect(screen.getByText('Слушаю')).toBeTruthy()
  })

  it('отображает "Обработка" в состоянии processing', () => {
    render(<VoiceIndicator state="processing" />)
    expect(screen.getByText('Обработка')).toBeTruthy()
  })

  it('вызывает onReset через 10 секунд в состоянии listening', () => {
    const onReset = vi.fn()
    render(<VoiceIndicator state="listening" autoResetMs={10_000} onReset={onReset} />)

    expect(onReset).not.toHaveBeenCalled()

    act(() => {
      vi.advanceTimersByTime(10_000)
    })

    expect(onReset).toHaveBeenCalledOnce()
  })

  it('не вызывает onReset в состоянии idle', () => {
    const onReset = vi.fn()
    render(<VoiceIndicator state="idle" autoResetMs={10_000} onReset={onReset} />)

    act(() => {
      vi.advanceTimersByTime(15_000)
    })

    expect(onReset).not.toHaveBeenCalled()
  })

  it('сбрасывает таймер при смене состояния', () => {
    const onReset = vi.fn()
    const { rerender } = render(
      <VoiceIndicator state="listening" autoResetMs={10_000} onReset={onReset} />
    )

    act(() => { vi.advanceTimersByTime(5_000) })
    expect(onReset).not.toHaveBeenCalled()

    // Переключаем в idle — таймер должен сброситься
    rerender(<VoiceIndicator state="idle" autoResetMs={10_000} onReset={onReset} />)

    act(() => { vi.advanceTimersByTime(10_000) })
    // onReset не должен вызваться — мы в idle
    expect(onReset).not.toHaveBeenCalled()
  })
})
