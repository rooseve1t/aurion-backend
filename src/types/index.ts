// ── Auth ──────────────────────────────────────────────────────────────────────
export interface User {
  id: string
  email: string
  username: string
  role: 'user' | 'admin' | 'creator'
  is_active: boolean
  is_2fa_enabled: boolean
  two_factor_enabled?: boolean
  created_at: string
}

export type VoicePersona = 'calm' | 'ironic' | 'sarcastic' | 'jarvis'

export interface UserPreferences {
  voice_persona: VoicePersona
  proactive_enabled: boolean
  family_mode: boolean
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
  id: string
  name: string
  device_type: DeviceType
  type?: DeviceType
  room: string
  is_online: boolean
  is_enabled?: boolean
  state: Record<string, unknown>
  capabilities?: string[]
  created_at?: string
}

// ── Agents ────────────────────────────────────────────────────────────────────
export type AgentType = 'financial' | 'smarthome' | 'osint' | 'memory'

export interface Agent {
  id: string
  name: string
  agent_type: AgentType
  is_active: boolean
  config: Record<string, unknown>
  created_at: string
  status?: string
  tasks_completed?: number
  success_rate?: number
}

export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface AgentTask {
  id: string
  agent_id: string
  action: string
  type?: string
  parameters: Record<string, unknown>
  input_data?: Record<string, unknown>
  status: TaskStatus
  result: unknown
  output_data?: unknown
  error_message?: string | null
  created_at: string
  updated_at?: string
}

// ── Payments ──────────────────────────────────────────────────────────────────
export interface Tariff {
  id: string
  name: string
  display_name?: string
  description?: string
  price: number
  duration_days: number
  features: Record<string, boolean | number>
  is_active: boolean
  currency?: string
  badge?: string | null
}

export type SubscriptionStatus = 'pending' | 'active' | 'cancelled' | 'expired'

export interface Subscription {
  id: string
  tariff_id: string
  status: SubscriptionStatus
  start_date: string | null
  end_date: string | null
  auto_renew: boolean
  cancelled_at: string | null
  created_at: string
  current_period_start?: string | null
  current_period_end?: string | null
  days_left?: number
  tariff?: Tariff | null
  features?: Record<string, boolean | number>
  next_billing_amount?: number | null
}

export interface Payment {
  id: string
  subscription_id: string | null
  amount: number
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

// ── Health / Twin / Reminders / Social / Media ──────────────────────────────
export interface HealthConnection {
  id: number
  provider: string
  status: string
  last_sync_at: string | null
  metrics: {
    steps: number
    sleep_hours: number
    recovery: number
    hydration_liters: number
    stress_index?: number
  }
  updated_at: string
}

export interface HealthData {
  summary: {
    steps: number
    sleep_hours: number
    recovery: number
    hydration_liters: number
  }
  connections: HealthConnection[]
  insights: string[]
  timeline: Array<{
    date: string
    steps: number
    sleep_hours: number
  }>
}

export interface TwinProfile {
  archetype: string
  focus_index: number
  voice_persona: VoicePersona
  strengths: string[]
  routines: string[]
  watchouts: string[]
  memory_highlights: MemoryEntry[]
}

export interface TwinPrediction {
  id: number
  title: string
  confidence: number
  message: string
  source: string
}

export interface Reminder {
  id: number
  title: string
  note: string
  due_at: string | null
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'completed' | 'archived'
  created_at: string
  updated_at: string
}

export interface SocialPost {
  id: number
  author_name: string
  content: string
  source: string
  mood: 'focus' | 'warning' | 'insight' | 'calm'
  reactions: Record<string, number>
  created_at: string
}

export interface MediaItem {
  id: number
  title: string
  media_type: 'playlist' | 'music' | 'briefing' | 'video'
  mood: 'focus' | 'warning' | 'insight' | 'calm'
  duration_minutes: number
  status: 'queued' | 'active' | 'completed' | 'paused'
  description: string
  created_at: string
  updated_at: string
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
  emotion?: string
  voice_persona?: VoicePersona
  tts_audio_b64?: string
  tts_provider?: string
  tts_mime_type?: string
}

export interface WsMessage {
  type: 'chat_response' | 'agent_task_update' | 'error'
    // New types for JARVIS features
    | 'system_hud_update' | 'house_party_started' | 'house_party_agent_update'
    | 'house_party_complete' | 'emergency_protocol_triggered' | 'research_insight_ready' | 'stress_alert'
  content?: string
  status?: string
  task_id?: number
  emotion?: string
  voice_persona?: VoicePersona
  tts?: {
    provider: string
    audio_b64?: string
    mime_type?: string
    emotion?: string
    persona?: string
    note?: string
  }
  snapshot?: HUDSnapshot
  message?: string
}

// ── HUD ───────────────────────────────────────────────────────────────────────
export interface HUDSnapshot {
  timestamp: string
  cpu_percent: number
  memory_percent: number
  memory_used_gb: number
  active_agents: number
  pending_tasks: number
  threat_level: 'low' | 'medium' | 'high' | 'critical' | 'unknown'
  autonomy_level: string
  active_missions: number
  stress_index: number
  uptime_seconds: number
}
