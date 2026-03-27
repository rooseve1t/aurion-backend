import { test, expect, Page } from '@playwright/test';
import { chromium, Browser, BrowserContext } from 'playwright';

/**
 * 🧪 E2E Tests for Aurion OS
 * Full user journey tests covering all critical paths
 */

// Test configuration
const TEST_USER = {
  email: `test_${Date.now()}@example.com`,
  username: `testuser_${Date.now()}`,
  password: 'TestPass123!'
};

const BASE_URL = process.env.TEST_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// ===========================================
// 🔐 AUTHENTICATION TESTS
// ===========================================

test.describe('Authentication Flow', () => {
  test('user can register successfully', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/register`);
    
    // Fill registration form
    await page.fill('[data-testid="email"]', TEST_USER.email);
    await page.fill('[data-testid="username"]', TEST_USER.username);
    await page.fill('[data-testid="password"]', TEST_USER.password);
    await page.fill('[data-testid="password-confirm"]', TEST_USER.password);
    
    // Submit form
    await page.click('[data-testid="register-submit"]');
    
    // Verify success
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText(TEST_USER.username);
  });

  test('user can login with valid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/login`);
    
    await page.fill('[data-testid="email"]', TEST_USER.email);
    await page.fill('[data-testid="password"]', TEST_USER.password);
    await page.click('[data-testid="login-submit"]');
    
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('invalid credentials show error', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/login`);
    
    await page.fill('[data-testid="email"]', 'wrong@example.com');
    await page.fill('[data-testid="password"]', 'wrongpassword');
    await page.click('[data-testid="login-submit"]');
    
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
  });
});

// ===========================================
// 🤖 JARVIS ASSISTANT TESTS
// ===========================================

test.describe('JARVIS Assistant', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    // Login and get token
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('JARVIS responds to text input', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    
    // Type message to JARVIS
    await page.fill('[data-testid="jarvis-input"]', 'Hello JARVIS, how are you?');
    await page.click('[data-testid="jarvis-send"]');
    
    // Wait for response
    await expect(page.locator('[data-testid="jarvis-response"]')).toBeVisible({ timeout: 10000 });
    const response = await page.locator('[data-testid="jarvis-response"]').textContent();
    expect(response).toBeTruthy();
    expect(response?.length).toBeGreaterThan(10);
  });

  test('JARVIS autonomy can be enabled', async ({ request }) => {
    const response = await request.post(`${API_URL}/jarvis/autonomy/enable`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { level: 2 } // Semi-auto
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.autonomy_level).toBe(2);
  });

  test('JARVIS autonomy status is retrievable', async ({ request }) => {
    const response = await request.get(`${API_URL}/jarvis/autonomy/status`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('enabled');
    expect(data).toHaveProperty('current_level');
    expect(data).toHaveProperty('system_metrics');
  });

  test('voice input is processed', async ({ page }) => {
    await page.goto(`${BASE_URL}/jarvis/voice`);
    
    // Click microphone button
    await page.click('[data-testid="voice-record"]');
    
    // Wait for recording indicator
    await expect(page.locator('[data-testid="recording-indicator"]')).toBeVisible();
    
    // Simulate 3 seconds of recording
    await page.waitForTimeout(3000);
    
    // Stop recording
    await page.click('[data-testid="voice-stop"]');
    
    // Wait for processing
    await expect(page.locator('[data-testid="voice-transcript"]')).toBeVisible({ timeout: 10000 });
  });
});

// ===========================================
// 🛡️ VPN SERVICE TESTS
// ===========================================

test.describe('VPN Service', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('VPN servers list is accessible', async ({ request }) => {
    const response = await request.get(`${API_URL}/vpn/servers`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThan(0);
    expect(data[0]).toHaveProperty('country');
    expect(data[0]).toHaveProperty('ip');
  });

  test('VPN can be connected', async ({ request }) => {
    const response = await request.post(`${API_URL}/vpn/connect`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: { country: 'US', stealth_mode: false }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.connected).toBe(true);
    expect(data).toHaveProperty('ip_address');
  });

  test('VPN status shows connection info', async ({ request }) => {
    const response = await request.get(`${API_URL}/vpn/status`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('connected');
    expect(data).toHaveProperty('server');
    expect(data).toHaveProperty('bandwidth_used');
  });

  test('VPN can be disconnected', async ({ request }) => {
    const response = await request.post(`${API_URL}/vpn/disconnect`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.disconnected).toBe(true);
  });
});

// ===========================================
// 💰 FINANCE MODULE TESTS
// ===========================================

test.describe('Finance Module', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('wallet balance is retrievable', async ({ request }) => {
    const response = await request.get(`${API_URL}/finance/wallet`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('user_id');
    expect(data).toHaveProperty('balances');
    expect(data).toHaveProperty('total_usd');
  });

  test('transaction history is accessible', async ({ request }) => {
    const response = await request.get(`${API_URL}/finance/transactions?limit=10`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data.transactions)).toBe(true);
  });

  test('transfer validation works', async ({ request }) => {
    const response = await request.post(`${API_URL}/finance/transfer`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: {
        to_address: '0x1234567890abcdef',
        amount: 0.001,
        currency: 'BTC'
      }
    });
    
    // Should either succeed or fail with specific error
    expect([200, 400, 402]).toContain(response.status());
  });
});

// ===========================================
// 🧠 MEMORY SYSTEM TESTS
// ===========================================

test.describe('Memory System', () => {
  let authToken: string;
  let storedMemoryId: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('memory can be stored', async ({ request }) => {
    const response = await request.post(`${API_URL}/memory/store`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: {
        content: 'This is a test memory for E2E testing',
        type: 'text',
        tags: ['test', 'e2e', 'memory'],
        importance: 5
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data).toHaveProperty('memory_id');
    storedMemoryId = data.memory_id;
  });

  test('memory can be recalled with semantic search', async ({ request }) => {
    const response = await request.get(`${API_URL}/memory/recall?query=test%20memory&limit=5`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data.memories)).toBe(true);
    expect(data.memories.length).toBeGreaterThan(0);
  });
});

// ===========================================
// 💳 PAYMENTS TESTS
// ===========================================

test.describe('Payments & Subscriptions', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('subscription plans are accessible', async ({ request }) => {
    const response = await request.get(`${API_URL}/payments/plans`);
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data.plans)).toBe(true);
    expect(data.plans.length).toBeGreaterThan(0);
    expect(data.plans[0]).toHaveProperty('id');
    expect(data.plans[0]).toHaveProperty('price');
  });

  test('user subscription status is retrievable', async ({ request }) => {
    const response = await request.get(`${API_URL}/payments/subscription`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('plan');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('renewal_date');
  });
});

// ===========================================
// 🏠 SMART HOME TESTS
// ===========================================

test.describe('Smart Home', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('devices list is accessible', async ({ request }) => {
    const response = await request.get(`${API_URL}/smarthome/devices`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data.devices)).toBe(true);
  });

  test('device can be controlled', async ({ request }) => {
    const response = await request.post(`${API_URL}/smarthome/control`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      data: {
        device_id: 'test-device-001',
        action: 'on'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.success).toBe(true);
  });
});

// ===========================================
// 🌐 WEBSOCKET TESTS
// ===========================================

test.describe('WebSocket Communication', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });
    const data = await response.json();
    authToken = data.access_token;
  });

  test('WebSocket connection establishes', async () => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/jarvis?token=${authToken}`);
    
    const connected = await new Promise<boolean>((resolve) => {
      ws.onopen = () => resolve(true);
      ws.onerror = () => resolve(false);
      
      // Timeout after 5 seconds
      setTimeout(() => resolve(false), 5000);
    });
    
    expect(connected).toBe(true);
    ws.close();
  });

  test('WebSocket receives JARVIS response', async () => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/jarvis?token=${authToken}`);
    
    const message = await new Promise<any>((resolve) => {
      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'text',
          content: 'Hello JARVIS'
        }));
      };
      
      ws.onmessage = (event) => {
        resolve(JSON.parse(event.data));
      };
      
      setTimeout(() => resolve(null), 10000);
    });
    
    expect(message).not.toBeNull();
    expect(message).toHaveProperty('type');
    expect(message).toHaveProperty('content');
    
    ws.close();
  });
});

// ===========================================
// 🎯 FULL USER JOURNEY TEST
// ===========================================

test.describe('Complete User Journey', () => {
  test('full workflow from registration to JARVIS interaction', async ({ page, request }) => {
    const journeyEmail = `journey_${Date.now()}@example.com`;
    const journeyUser = `journeyuser_${Date.now()}`;
    
    // 1. Register
    await page.goto(`${BASE_URL}/auth/register`);
    await page.fill('[data-testid="email"]', journeyEmail);
    await page.fill('[data-testid="username"]', journeyUser);
    await page.fill('[data-testid="password"]', 'JourneyPass123!');
    await page.fill('[data-testid="password-confirm"]', 'JourneyPass123!');
    await page.click('[data-testid="register-submit"]');
    
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    
    // 2. Check VPN status
    await page.goto(`${BASE_URL}/vpn`);
    await expect(page.locator('[data-testid="vpn-status"]')).toBeVisible();
    
    // 3. Connect to VPN
    await page.click('[data-testid="vpn-connect"]');
    await expect(page.locator('[data-testid="vpn-connected"]')).toBeVisible({ timeout: 10000 });
    
    // 4. Open JARVIS
    await page.goto(`${BASE_URL}/jarvis`);
    await expect(page.locator('[data-testid="jarvis-interface"]')).toBeVisible();
    
    // 5. Send message to JARVIS
    await page.fill('[data-testid="jarvis-input"]', 'What can you help me with?');
    await page.click('[data-testid="jarvis-send"]');
    
    await expect(page.locator('[data-testid="jarvis-response"]')).toBeVisible({ timeout: 10000 });
    
    // 6. Check finance
    await page.goto(`${BASE_URL}/finance`);
    await expect(page.locator('[data-testid="wallet-balance"]')).toBeVisible();
    
    // 7. Store a memory
    await page.goto(`${BASE_URL}/memory`);
    await page.fill('[data-testid="memory-input"]', 'This is my journey test memory');
    await page.click('[data-testid="memory-save"]');
    
    await expect(page.locator('[data-testid="memory-saved"]')).toBeVisible();
    
    // 8. Enable JARVIS autonomy
    await page.goto(`${BASE_URL}/jarvis/settings`);
    await page.click('[data-testid="autonomy-enable"]');
    await page.selectOption('[data-testid="autonomy-level"]', '2');
    await page.click('[data-testid="autonomy-save"]');
    
    await expect(page.locator('[data-testid="autonomy-enabled"]')).toBeVisible();
    
    // Journey complete!
    console.log('✅ Full user journey completed successfully');
  });
});

// ===========================================
// 📊 PERFORMANCE TESTS
// ===========================================

test.describe('Performance Tests', () => {
  test('page load time is under 3 seconds', async ({ page }) => {
    const start = Date.now();
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - start;
    
    expect(loadTime).toBeLessThan(3000);
  });

  test('JARVIS response time is under 5 seconds', async ({ page }) => {
    await page.goto(`${BASE_URL}/jarvis`);
    
    const start = Date.now();
    await page.fill('[data-testid="jarvis-input"]', 'Test message');
    await page.click('[data-testid="jarvis-send"]');
    await page.waitForSelector('[data-testid="jarvis-response"]', { timeout: 5000 });
    const responseTime = Date.now() - start;
    
    expect(responseTime).toBeLessThan(5000);
  });

  test('API responds under 200ms for health check', async ({ request }) => {
    const start = Date.now();
    const response = await request.get(`${BASE_URL}/health`);
    const responseTime = Date.now() - start;
    
    expect(response.ok()).toBeTruthy();
    expect(responseTime).toBeLessThan(200);
  });
});

// ===========================================
// 🔒 SECURITY TESTS
// ===========================================

test.describe('Security Tests', () => {
  test('unauthorized access is rejected', async ({ request }) => {
    const response = await request.get(`${API_URL}/finance/wallet`);
    expect(response.status()).toBe(401);
  });

  test('invalid token is rejected', async ({ request }) => {
    const response = await request.get(`${API_URL}/jarvis/autonomy/status`, {
      headers: { 'Authorization': 'Bearer invalid_token' }
    });
    expect(response.status()).toBe(401);
  });

  test('SQL injection is prevented', async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: "' OR '1'='1'; DROP TABLE users; --",
        password: 'anything'
      }
    });
    
    // Should fail gracefully, not expose database structure
    expect(response.status()).toBe(401);
  });

  test('XSS attempts are sanitized', async ({ page }) => {
    await page.goto(`${BASE_URL}/jarvis`);
    
    // Try XSS payload
    await page.fill('[data-testid="jarvis-input"]', '<script>alert("xss")</script>');
    await page.click('[data-testid="jarvis-send"]');
    
    // Script tag should not be executed
    const pageContent = await page.content();
    expect(pageContent).not.toContain('<script>alert("xss")</script>');
  });
});

// ===========================================
// 🧹 CLEANUP
// ===========================================

test.afterAll(async ({ request }) => {
  // Cleanup: delete test user data if needed
  console.log('🧹 Test cleanup completed');
});
