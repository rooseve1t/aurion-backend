import { http, HttpResponse } from 'msw'

const API = 'http://localhost:8000/api/v1'

export const handlers = [
  http.options(new RegExp(`^${API}/.*`), () => new HttpResponse(null, { status: 204 })),

  // Auth
  http.post(`${API}/auth/token`, () =>
    HttpResponse.json({ access_token: 'test_token', refresh_token: 'test_refresh', token_type: 'bearer' })
  ),
  http.post(`${API}/auth/register`, () =>
    HttpResponse.json({
      id: 'u2',
      email: 'new@test.com',
      username: 'new.user',
      role: 'user',
      is_active: true,
      is_2fa_enabled: false,
      created_at: '2024-01-01T00:00:00Z',
    })
  ),
  http.post(`${API}/auth/refresh`, () =>
    HttpResponse.json({ access_token: 'refreshed_token', refresh_token: 'refreshed_refresh', token_type: 'bearer' })
  ),
  http.post(`${API}/auth/logout`, () => HttpResponse.json({ ok: true })),
  http.get(`${API}/auth/me`, () =>
    HttpResponse.json({
      id: 'u1',
      email: 'test@test.com',
      username: 'Тестовый',
      role: 'user',
      is_active: true,
      is_2fa_enabled: false,
      created_at: '2024-01-01T00:00:00Z',
    })
  ),

  // Tariffs
  http.get(`${API}/payments/tariffs`, () =>
    HttpResponse.json([
      { id: 1, name: 'Free',  price: '0',    duration_days: 30, features: { voice: true, memory_limit: 100,  devices_limit: 5,  osint: false, quantum: false, finance: false, agents: false }, is_active: true },
      { id: 2, name: 'Basic', price: '990',  duration_days: 30, features: { voice: true, memory_limit: 1000, devices_limit: 20, osint: false, quantum: false, finance: true,  agents: false }, is_active: true },
      { id: 3, name: 'Pro',   price: '2990', duration_days: 30, features: { voice: true, memory_limit: -1,   devices_limit: -1, osint: true,  quantum: true,  finance: true,  agents: true  }, is_active: true },
    ])
  ),
  http.get(`${API}/payments/subscriptions/current`, () =>
    HttpResponse.json({ id: 1, tariff_id: 1, status: 'active', start_date: '2024-01-01T00:00:00Z', end_date: '2099-01-01T00:00:00Z', auto_renew: true, cancelled_at: null, created_at: '2024-01-01T00:00:00Z', tariff: { id: 1, name: 'Free', price: '0', duration_days: 30, features: {}, is_active: true }, days_left: 30 }, { status: 200 })
  ),
  http.get(`${API}/payments/payments`, () =>
    HttpResponse.json({ payments: [], total: 0 })
  ),
  http.post(`${API}/payments/subscribe`, () =>
    HttpResponse.json({
      subscription_id: 10,
      payment_id: 'pay-10',
      confirmation_url: 'https://example.test/checkout/pay-10',
      tariff_name: 'Pro',
      amount: '2990',
      status: 'succeeded',
    })
  ),
  http.post(`${API}/payments/subscriptions/:id/cancel`, () =>
    HttpResponse.json({
      id: 1,
      tariff_id: 1,
      status: 'cancelled',
      start_date: '2024-01-01T00:00:00Z',
      end_date: '2099-01-01T00:00:00Z',
      auto_renew: false,
      cancelled_at: '2024-01-10T00:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
    })
  ),

  // Memory
  http.get(`${API}/memory/search`, () =>
    HttpResponse.json([
      { id: 1, content: 'Тестовая запись в памяти', importance: 7, tags: ['тест'], created_at: '2024-01-01T00:00:00Z' },
    ])
  ),
  http.post(`${API}/memory/`, () =>
    HttpResponse.json({ id: 2, content: 'Новая запись', importance: 6, tags: [], created_at: '2024-01-02T00:00:00Z' })
  ),
  http.get(`${API}/memory/count`, () => HttpResponse.json({ count: 1 })),
  http.delete(`${API}/memory/:id`, () => new HttpResponse(null, { status: 204 })),

  // Devices
  http.get(`${API}/smarthome/devices`, () =>
    HttpResponse.json([
      { id: 1, name: 'Лампа', device_type: 'light', room: 'Гостиная', is_online: true, state: { power: true }, created_at: '2024-01-01T00:00:00Z' },
    ])
  ),
  http.post(`${API}/smarthome/control`, () => HttpResponse.json({ status: 'ok' })),
  http.post(`${API}/smarthome/optimize`, () => HttpResponse.json({ savings_kwh: 1.2, actions: ['x'] })),
  http.post(`${API}/smarthome/devices`, () =>
    HttpResponse.json({ id: 2, name: 'Новая лампа', device_type: 'light', room: 'Кухня', is_online: true, state: { power: false }, created_at: '2024-01-02T00:00:00Z' })
  ),

  // System
  http.get(`${API}/system/stats`, () =>
    HttpResponse.json({ devices_online: 3, memory_entries: 42, active_tasks: 1, quantum_status: 'online', subscription_tier: 'Free', uptime_hours: 24 })
  ),
]
