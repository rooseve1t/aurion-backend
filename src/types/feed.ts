// src/types/feed.ts — Activity Feed типы (Aurion Evolution)

export type FeedCardType = 'observation' | 'suggestion' | 'alert' | 'insight'

export type FeedDomain = 'health' | 'finance' | 'security' | 'calendar'

export type FeedPriority = 'low' | 'medium' | 'high' | 'critical'

export interface FeedCard {
  id: string
  type: FeedCardType
  domain: FeedDomain
  title: string
  body: string
  priority: FeedPriority
  requiresConfirmation: boolean
  confirmedAt?: string
  dismissedAt?: string
  createdAt: string
  userId: string
}

export interface FeedPage {
  items: FeedCard[]
  page: number
  hasMore: boolean
}
