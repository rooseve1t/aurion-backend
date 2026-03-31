/**
 * Property-based tests for feedService utilities
 * Feature: aurion-evolution
 */
import { describe, test } from 'vitest'
import * as fc from 'fast-check'
import { paginateFeed, sortFeedCards } from '@/services/feedService'
import type { FeedCard } from '@/types/feed'

// Генератор ISO-даты через timestamp (избегаем невалидных дат при shrinking)
const isoDateArb = fc
  .integer({ min: 1577836800000, max: 1893456000000 }) // 2020-01-01 .. 2030-01-01
  .map((ts) => new Date(ts).toISOString())

// Генератор FeedCard
const feedCardArb = fc.record<FeedCard>({
  id: fc.uuid(),
  type: fc.constantFrom('observation', 'suggestion', 'alert', 'insight'),
  domain: fc.constantFrom('health', 'finance', 'security', 'calendar'),
  title: fc.string({ minLength: 1, maxLength: 100 }),
  body: fc.string({ minLength: 1, maxLength: 500 }),
  priority: fc.constantFrom('low', 'medium', 'high', 'critical'),
  requiresConfirmation: fc.boolean(),
  createdAt: isoDateArb,
  userId: fc.uuid(),
})

/**
 * Property 14: Пагинация Activity Feed
 * paginateFeed(cards, page, 20).length <= 20
 * Validates: Requirements 4.4
 */
describe('Property 14: пагинация не превышает 20 карточек', () => {
  test('paginateFeed всегда возвращает не более 20 карточек', () => {
    fc.assert(
      fc.property(
        fc.array(feedCardArb, { maxLength: 100 }),
        fc.integer({ min: 0, max: 10 }),
        (cards, page) => {
          const result = paginateFeed(cards, page, 20)
          return result.length <= 20
        }
      ),
      { numRuns: 200 }
    )
  })

  test('paginateFeed возвращает правильный срез', () => {
    fc.assert(
      fc.property(
        fc.array(feedCardArb, { minLength: 0, maxLength: 100 }),
        fc.integer({ min: 0, max: 10 }),
        (cards, page) => {
          const result = paginateFeed(cards, page, 20)
          const expected = cards.slice(page * 20, page * 20 + 20)
          return result.length === expected.length &&
            result.every((c, i) => c.id === expected[i].id)
        }
      ),
      { numRuns: 200 }
    )
  })
})

/**
 * Property 15: Хронологический порядок Feed
 * sortFeedCards возвращает карточки по убыванию createdAt
 * Validates: Requirements 4.2
 */
describe('Property 15: хронологический порядок (новые сверху)', () => {
  test('sortFeedCards сортирует по убыванию createdAt', () => {
    fc.assert(
      fc.property(
        fc.array(feedCardArb, { minLength: 2, maxLength: 50 }),
        (cards) => {
          const sorted = sortFeedCards(cards)
          for (let i = 0; i < sorted.length - 1; i++) {
            const a = new Date(sorted[i].createdAt).getTime()
            const b = new Date(sorted[i + 1].createdAt).getTime()
            if (a < b) return false
          }
          return true
        }
      ),
      { numRuns: 200 }
    )
  })

  test('sortFeedCards не изменяет исходный массив', () => {
    fc.assert(
      fc.property(
        fc.array(feedCardArb, { minLength: 1, maxLength: 30 }),
        (cards) => {
          const original = cards.map((c) => c.id)
          sortFeedCards(cards)
          return cards.map((c) => c.id).every((id, i) => id === original[i])
        }
      ),
      { numRuns: 100 }
    )
  })
})
