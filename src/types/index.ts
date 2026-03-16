// ── Auth ──────────────────────────────────────────────────────────────────────
export interface User {
  id: string
  email: string
  username: string
  role: 'user' | 'admin' | 'creator'
  is_active: boolean
  is_2fa_enabled: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

// ── Memory ────────────────────────────────────────────────────────────────────
export interface MemoryEntry {
  id: number
  content: string
  importance: number
  tags: string[]
  created_at: string
  similarity?: number
}

// ── Devices (Smart Home) ──────────────────────────────────────────────────────
export type DeviceType = 'light' | 'switch' | 'thermostat' | 'lock' | 'sensor'

export interface Device {
  id: number
  name: string
  device_type: DeviceType
  room: string
  is_online: boolean
  state: Record<string, unknown>
  created_at: string
}

// ── Agents ────────────────────────────────────────────────────────────────────
export type AgentType = 'financial' | 'smarthome' | 'osint' | 'memory'

export interface Agent {
  id: number
  name: string
  agent_type: AgentType
  is_active: boolean
  config: Record<string, unknown>
  created_at: string
}

export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface AgentTask {
  id: number
  agent_id: number
  action: string
  parameters: Record<string, unknown>
  status: TaskStatus
  result: unknown
  created_at: string
}

// ── Payments ──────────────────────────────────────────────────────────────────
export interface Tariff {
  id: number
  name: string
  price: string
  duration_days: number
  features: Record<string, boolean | number>
  is_active: boolean
}

export type SubscriptionStatus = 'pending' | 'active' | 'cancelled' | 'expired'

export interface Subscription {
  id: number
  tariff_id: number
  status: SubscriptionStatus
  start_date: string | null
  end_date: string | null
  auto_renew: boolean
  cancelled_at: string | null
  created_at: string
}

export interface Payment {
  id: number
  subscription_id: number
  amount: string
  currency: string
  status: 'pending' | 'succeeded' | 'failed' | 'refunded'
  description: string
  created_at: string
}

// ── Finance ───────────────────────────────────────────────────────────────────
export interface BankAccount {
  id: number
  bank_name: string
  account_type: string
  balance: string
  currency: string
  account_number: string
}

export interface Transaction {
  id: number
  amount: string
  category: string
  description: string
  date: string
  type: 'debit' | 'credit'
}

export interface FinanceAnalytics {
  total_income: string
  total_expenses: string
  by_category: Record<string, string>
  period: string
}

// ── System ────────────────────────────────────────────────────────────────────
export interface SystemStats {
  devices_online: number
  memory_entries: number
  active_tasks: number
  quantum_status: 'online' | 'offline' | 'busy'
  subscription_tier: string
  uptime_hours: number
}

// ── Chat ──────────────────────────────────────────────────────────────────────
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}
