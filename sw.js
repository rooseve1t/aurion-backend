// 🎨 Service Worker для Aurion OS Enhanced
const CACHE_NAME = 'aurion-os-enhanced-v2.0.0';
const STATIC_CACHE = 'aurion-static-v2.0.0';
const DYNAMIC_CACHE = 'aurion-dynamic-v2.0.0';

// 🎨 Файлы для кэширования
const STATIC_FILES = [
  '/',
  '/preview_enhanced.html',
  '/manifest.json',
  '/sw.js'
];

// 🎨 Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('🚀 Aurion OS Enhanced Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('📦 Caching static files...');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('✅ Static files cached successfully');
        return self.skipWaiting();
      })
  );
});

// 🎨 Активация Service Worker
self.addEventListener('activate', (event) => {
  console.log('🔄 Aurion OS Enhanced Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker activated');
        return self.clients.claim();
      })
  );
});

// 🎨 Обработка запросов
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // 🎨 Пропускаем non-GET запросы
  if (request.method !== 'GET') {
    return;
  }
  
  // 🎨 Пропускаем chrome-extension запросы
  if (url.protocol === 'chrome-extension:') {
    return;
  }
  
  event.respondWith(
    caches.match(request)
      .then((response) => {
        // 🎨 Если есть в кэше - возвращаем
        if (response) {
          return response;
        }
        
        // 🎨 Иначе делаем запрос
        return fetch(request)
          .then((fetchResponse) => {
            // 🎨 Проверяем статус ответа
            if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
              return fetchResponse;
            }
            
            // 🎨 Кэшируем динамический контент
            return caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                // 🎨 Ограничиваем размер кэша
                if (request.url.includes('localhost:8000')) {
                  cache.put(request, fetchResponse.clone());
                }
                return fetchResponse;
              });
          })
          .catch(() => {
            // 🎨 Если запрос не удался, пытаемся найти в кэше
            return caches.match(request);
          });
      })
  );
});

// 🎨 Обработка push уведомлений
self.addEventListener('push', (event) => {
  const options = {
    body: event.data.text(),
    icon: '/manifest.json',
    badge: '/manifest.json',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Открыть Aurion OS',
        icon: '/manifest.json'
      },
      {
        action: 'close',
        title: 'Закрыть',
        icon: '/manifest.json'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Aurion OS Enhanced', options)
  );
});

// 🎨 Обработка кликов по уведомлениям
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Закрыть уведомление (уже закрыто)
  } else {
    // Открыть приложение по умолчанию
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// 🎨 Обработка сообщений от клиента
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 🎨 Фоновая синхронизация
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // 🎨 Здесь можно добавить логику фоновой синхронизации
      console.log('🔄 Background sync triggered')
    );
  }
});

// 🎨 Периодическая синхронизация
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'periodic-sync') {
    event.waitUntil(
      // 🎨 Здесь можно добавить логику периодической синхронизации
      console.log('🔄 Periodic sync triggered')
    );
  }
});

// 🎨 Обработка ошибок
self.addEventListener('error', (event) => {
  console.error('🚨 Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('🚨 Unhandled promise rejection:', event.reason);
});

// 🎨 Логирование состояния
self.addEventListener('statechange', (event) => {
  console.log('🔄 Service Worker state:', event.target.state);
});

// 🎨 Утилиты для кэширования
const cacheUtils = {
  // 🎨 Очистка старого кэша
  async clearOldCache() {
    const cacheNames = await caches.keys();
    const oldCaches = cacheNames.filter(name => 
      name !== STATIC_CACHE && name !== DYNAMIC_CACHE
    );
    
    await Promise.all(
      oldCaches.map(name => caches.delete(name))
    );
  },
  
  // 🎨 Получение размера кэша
  async getCacheSize(cacheName) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    let size = 0;
    
    for (const request of keys) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        size += blob.size;
      }
    }
    
    return size;
  },
  
  // 🎨 Ограничение размера кэша
  async limitCacheSize(cacheName, maxSize = 50 * 1024 * 1024) { // 50MB
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    const entries = [];
    
    for (const request of keys) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        entries.push({
          request,
          size: blob.size,
          date: response.headers.get('date') || new Date(0).toISOString()
        });
      }
    }
    
    // 🎨 Сортируем по дате (старые первыми)
    entries.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    let currentSize = entries.reduce((sum, entry) => sum + entry.size, 0);
    
    // 🎨 Удаляем старые записи если превышен лимит
    for (const entry of entries) {
      if (currentSize <= maxSize) break;
      
      await cache.delete(entry.request);
      currentSize -= entry.size;
    }
  }
};

// 🎨 Экспорт утилит для отладки
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'DEBUG') {
    switch (event.data.action) {
      case 'getCacheSize':
        Promise.all([
          cacheUtils.getCacheSize(STATIC_CACHE),
          cacheUtils.getCacheSize(DYNAMIC_CACHE)
        ]).then(([staticSize, dynamicSize]) => {
          event.ports[0].postMessage({
            staticSize,
            dynamicSize,
            totalSize: staticSize + dynamicSize
          });
        });
        break;
        
      case 'clearCache':
        cacheUtils.clearOldCache().then(() => {
          event.ports[0].postMessage({ success: true });
        });
        break;
        
      case 'limitCache':
        cacheUtils.limitCacheSize(DYNAMIC_CACHE, event.data.maxSize).then(() => {
          event.ports[0].postMessage({ success: true });
        });
        break;
    }
  }
});

console.log('🎨 Aurion OS Enhanced Service Worker loaded successfully');
