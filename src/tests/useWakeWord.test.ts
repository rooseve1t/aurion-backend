/**
 * Тесты для useWakeWord — обнаружение wake-word и активация.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWakeWord } from '@/hooks/useWakeWord'

// Мок Web Speech API
class MockSpeechRecognition {
  lang = ''
  continuous = false
  interimResults = false
  maxAlternatives = 1
  onresult: ((e: SpeechRecognitionEvent) => void) | null = null
  onend: (() => void) | null = null
  onerror: ((e: SpeechRecognitionErrorEvent) => void) | null = null

  start = vi.fn()
  stop = vi.fn()

  // Симулируем распознавание слова
  simulateResult(transcript: string) {
    if (this.onresult) {
      const event = {
        resultIndex: 0,
        results: [
          [{ transcript, confidence: 0.9 }],
        ],
      } as unknown as SpeechRecognitionEvent
      this.onresult(event)
    }
  }
}

let mockInstance: MockSpeechRecognition

beforeEach(() => {
  mockInstance = new MockSpeechRecognition()
  ;(window as Window & { SpeechRecognition?: unknown }).SpeechRecognition = vi.fn(
    () => mockInstance
  )
})

afterEach(() => {
  delete (window as Window & { SpeechRecognition?: unknown }).SpeechRecognition
  vi.clearAllMocks()
})

describe('useWakeWord', () => {
  it('запускает распознавание при enabled=true', () => {
    const onActivated = vi.fn()
    renderHook(() => useWakeWord({ onActivated, enabled: true }))
    expect(mockInstance.start).toHaveBeenCalled()
  })

  it('не запускает распознавание при enabled=false', () => {
    const onActivated = vi.fn()
    renderHook(() => useWakeWord({ onActivated, enabled: false }))
    expect(mockInstance.start).not.toHaveBeenCalled()
  })

  it('вызывает onActivated при обнаружении "jarvis"', () => {
    const onActivated = vi.fn()
    renderHook(() => useWakeWord({ onActivated, enabled: true }))

    act(() => {
      mockInstance.simulateResult('jarvis включи свет')
    })

    expect(onActivated).toHaveBeenCalledOnce()
  })

  it('вызывает onActivated при обнаружении "джарвис"', () => {
    const onActivated = vi.fn()
    renderHook(() => useWakeWord({ onActivated, enabled: true }))

    act(() => {
      mockInstance.simulateResult('джарвис какая погода')
    })

    expect(onActivated).toHaveBeenCalledOnce()
  })

  it('не вызывает onActivated при обычной речи', () => {
    const onActivated = vi.fn()
    renderHook(() => useWakeWord({ onActivated, enabled: true }))

    act(() => {
      mockInstance.simulateResult('привет как дела')
    })

    expect(onActivated).not.toHaveBeenCalled()
  })

  it('останавливает распознавание при unmount', () => {
    const onActivated = vi.fn()
    const { unmount } = renderHook(() => useWakeWord({ onActivated, enabled: true }))
    unmount()
    expect(mockInstance.stop).toHaveBeenCalled()
  })
})
