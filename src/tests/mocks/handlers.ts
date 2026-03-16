import { http, HttpResponse } from 'msw'

const BASE = '/api/v1'

export const handlers = [
  // Auth
  http.post(`${BASE}/auth/token`, () =>
    HttpResponse.json({
      access_token: 'mock_access_token',
      refresh_token: 'mock_refresh_token',
      token_type: 'bearer',
    })
  ),
  http.get(`${BASE}/auth/me`, () =>
    HttpResponse.json({
      id: 'user-123',
      email: 'test@aurion.ru',
      username: 'TestUser',
      role: 'user',
      is_active: true,
      two_factor_enabled: false,
    })
  ),
  http.post(`${BASE}/auth/register`, () =>
    HttpResponse.json({ id: 'user-new', email: 'new@aurion.ru', username: 'NewUser', role: 'user', is_active: true, two_factor_enabled: false })
  ),
  http.post(`${BASE}/auth/logout`, () => HttpResponse.json({ ok: true })),

  // Memory
  http.get(`${BASE}/memory/search`, () =>
    HttpResponse.json([
      { id: 1, content: 'Встреча в пятницу в 15:00', importance: 0.8, source: 'user', created_at: new Date().toISOString() },
      { id: 2, content: 'Купить молоко и хлеб', importance: 0.4, source: 'chat', created_at: new Date().toISOString() },
      { id: 3, content: 'Пароль от сервера: xxx', importance: 0.9, source: 'user', created_at: new Date().toISOString() },
    ])
  ),
  http.post(`${BASE}/memory/`, () =>
    HttpResponse.json({ id: 10, content: 'Новая запись', importance: 0.5, source: 'user', created_at: new Date().toISOString() })
  ),
  http.delete(`${BASE}/memory/:id`, () => HttpResponse.json({ ok: true })),
  http.get(`${BASE}/memory/count`, () => HttpResponse.json({ count: 42 })),

  // Devices
  http.get(`${BASE}/smarthome/devices`, () =>
    HttpResponse.json([
      { id: 1, name: 'Люстра гостиная', type: 'light', room: 'Гостиная', is_online: true, topic: 't/1', state: { on: true, brightness: 80 }, created_at: new Date().toISOString() },
      { id: 2, name: 'Термостат', type: 'thermostat', room: 'Спальня', is_online: true, topic: 't/2', state: { temperature: 22 }, created_at: new Date().toISOString() },
      { id: 3, name: 'Умный замок', type: 'lock', room: 'Прихожая', is_online: false, topic: 't/3', state: { locked: true }, created_at: new Date().toISOString() },
    ])
  ),
  http.post(`${BASE}/smarthome/control`, () => HttpResponse.json({ ok: true })),
  http.post(`${BASE}/smarthome/optimize`, () => HttpResponse.json({ saved_kwh: 2.4 })),

  // Agents
  http.get(`${BASE}/agents/`, () =>
    HttpResponse.json([
      { id: 1, name: 'FinAgent', type: 'financial', description: '', config: {}, is_active: true, created_at: new Date().toISOString() },
    ])
  ),
  http.get(`${BASE}/agents/tasks`, () =>
    HttpResponse.json({
      tasks: [
        { id: 1, type: 'analyze_spending', status: 'completed', input_data: {}, output_data: { result: 'ok' }, priority: 5, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ],
      total: 1,
    })
  ),
  http.post(`${BASE}/agents/tasks`, () =>
    HttpResponse.json({ id: 2, type: 'analyze_spending', status: 'pending', input_data: {}, priority: 5, created_at: new Date().toISOString(), updated_at: new Date().toISOString() })
  ),

  // Payments
  http.get(`${BASE}/payments/tariffs`, () =>
    HttpResponse.json([
      { id: 1, name: 'Free',  price: 0,    duration_days: 30, is_active: true, features: { voice: true, memory_limit: 100, devices_limit: 5, osint: false, quantum: false, finance: false, agents: false, evolution: false } },
      { id: 2, name: 'Basic', price: 990,  duration_days: 30, is_active: true, features: { voice: true, memory_limit: 1000, devices_limit: 20, osint: false, quantum: false, finance: true, agents: false, evolution: false } },
      { id: 3, name: 'Pro',   price: 2990, duration_days: 30, is_active: true, features: { voice: true, memory_limit: -1, devices_limit: -1, osint: true, quantum: true, finance: true, agents: true, evolution: false } },
    ])
  ),
  http.get(`${BASE}/payments/subscriptions/current`, () =>
    HttpResponse.json({
      id: 1, tariff_id: 3, status: 'active',
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + 25 * 86400000).toISOString(),
      auto_renew: true, cancelled_at: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
      tariff: { id: 3, name: 'Pro', price: 2990, duration_days: 30, is_active: true, features: { voice: true, memory_limit: -1, devices_limit: -1, osint: true, quantum: true, finance: true, agents: true, evolution: false } },
      days_left: 25,
    })
  ),
  http.get(`${BASE}/payments/subscriptions`, () => HttpResponse.json([])),
  http.get(`${BASE}/payments/payments`, () => HttpResponse.json({ payments: [], total: 0 })),
  http.post(`${BASE}/payments/subscribe`, () =>
    HttpResponse.json({ subscription_id: 5, payment_id: 'yk_test', confirmation_url: 'https://yookassa.ru/checkout/test', tariff_name: 'Pro', amount: 2990, status: 'pending' })
  ),
  http.post(`${BASE}/payments/subscriptions/:id/cancel`, () =>
    HttpResponse.json({ id: 1, status: 'cancelled', auto_renew: false })
  ),

  // System
  http.get(`${BASE}/system/stats`, () =>
    HttpResponse.json({
      devices_online: 3, memory_entries: 42, active_tasks: 1,
      quantum_status: 'online', subscription_tier: 'Pro', uptime_hours: 72,
    })
  ),
]
