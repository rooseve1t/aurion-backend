import '@testing-library/jest-dom'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './server'

if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = vi.fn()
}

if (!window.open) {
  window.open = vi.fn()
}
window.confirm = vi.fn(() => true)

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' })
})

afterEach(() => {
  server.resetHandlers()
  localStorage.clear()
  sessionStorage.clear()
  cleanup()
})

afterAll(() => {
  server.close()
})
