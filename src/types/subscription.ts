// src/types/subscription.ts — Subscription и TrustedDevice типы (Aurion Evolution)

export type SubscriptionLevel = 'basic' | 'standard' | 'premium'

export interface AurionSubscription {
  userId: string
  level: SubscriptionLevel
  validUntil?: string
  features: string[]
}

export interface TrustedDevice {
  id: string
  userId: string
  deviceFingerprint: string
  userAgent: string
  ip: string
  addedAt: string
  lastSeenAt: string
  revoked?: boolean
}
