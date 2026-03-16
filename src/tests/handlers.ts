import { http, HttpResponse } from 'msw'

export const handlers = [
  // Auth
  http.post('/api/v1/auth/token', () =>
    HttpResponse.json({ access_token: 'test_token', refresh_token: 'test_refresh', token_type: 'bearer' })
  ),
  http.get('/api/v1/auth/me', () =>
    HttpResponse.json({ id: 'u1', email: 'test@test.com', username: 'Тестовый', role: 'user', is_active: true, is_2fa_enabled: false, created_at: '2024-01-01T00:00:00Z' })
  ),

  // Tariffs
  http.get('/api/v1/payments/tariffs', () =>
    HttpResponse.json([
      { id: 1, name: 'Free',  price: '0',    duration_days: 30, features: { voice: true, memory_limit: 100,  devices_limit: 5,  osint: false, quantum: false, finance: false, agents: false }, is_active: true },
      { id: 2, name: 'Basic', price: '990',  duration_days: 30, features: { voice: true, memory_limit: 1000, devices_limit: 20, osint: false, quantum: false, finance: true,  agents: false }, is_active: true },
      { id: 3, name: 'Pro',   price: '2990', duration_days: 30, features: { voice: true, memory_limit: -1,   devices_limit: -1, osint: true,  quantum: true,  finance: true,  agents: true  }, is_active: true },
    ])
  ),
  http.get('/api/v1/payments/subscriptions/current', () =>
    HttpResponse.json({ id: 1, tariff_id: 1, status: 'active', start_date: '2024-01-01T00:00:00Z', end_date: '2099-01-01T00:00:00Z', auto_renew: true, cancelled_at: null, created_at: '2024-01-01T00:00:00Z', tariff: { id: 1, name: 'Free', price: '0', duration_days: 30, features: {}, is_active: true }, days_left: 30 }, { status: 200 })
  ),
  http.get('/api/v1/payments/payments', () =>
    HttpResponse.json({ payments: [], total: 0 })
  ),

  // Memory
  http.get('/api/v1/memory/search', () =>
    HttpResponse.json([
      { id: 1, content: 'Тестовая запись в памяти', importance: 7, tags: ['тест'], created_at: '2024-01-01T00:00:00Z' },
    ])
  ),
  http.get('/api/v1/memory/count', () => HttpResponse.json({ count: 1 })),
  http.delete('/api/v1/memory/:id', () => new HttpResponse(null, { status: 204 })),

  // Devices
  http.get('/api/v1/smarthome/devices', () =>
    HttpResponse.json([
      { id: 1, name: 'Лампа', device_type: 'light', room: 'Гостиная', is_online: true, state: { power: true }, created_at: '2024-01-01T00:00:00Z' },
    ])
  ),
  http.post('/api/v1/smarthome/control', () => HttpResponse.json({ status: 'ok' })),

  // System
  http.get('/api/v1/system/stats', () =>
    HttpResponse.json({ devices_online: 3, memory_entries: 42, active_tasks: 1, quantum_status: 'online', subscription_tier: 'Free', uptime_hours: 24 })
  ),
]
