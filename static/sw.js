/**
 * Laura-bot PWA Service Worker
 * Provides offline functionality, caching, and background sync
 */

const CACHE_NAME = 'laura-bot-v1.0.0';
const STATIC_CACHE_NAME = 'laura-bot-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'laura-bot-dynamic-v1.0.0';

// Core files to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/static/css/mobile-app.css',
  '/static/css/modern-ui.css',
  '/static/js/app.js',
  '/static/manifest.json',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.4/socket.io.js'
];

// Dynamic content patterns to cache
const DYNAMIC_PATTERNS = [
  /^\/learn/,
  /^\/quiz/,
  /^\/progress/,
  /^\/hardware/,
  /^\/api\//
];

// Network-first patterns (always try network first)
const NETWORK_FIRST_PATTERNS = [
  /^\/api\/ai/,
  /^\/api\/voice/,
  /^\/api\/hardware/,
  /socket\.io/
];

// Cache-first patterns (serve from cache if available)
const CACHE_FIRST_PATTERNS = [
  /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
  /\.(?:css|js)$/,
  /fonts\.googleapis\.com/,
  /cdnjs\.cloudflare\.com/
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Static assets cached successfully');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME &&
                cacheName.startsWith('laura-bot-')) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Service worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle all network requests
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-HTTP requests
  if (!request.url.startsWith('http')) {
    return;
  }
  
  // Skip socket.io and other real-time connections
  if (isNetworkFirst(request.url)) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Handle static assets with cache-first strategy
  if (isCacheFirst(request.url)) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Handle dynamic content with network-first strategy
  if (isDynamic(request.url)) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Default: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(request));
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync-learning') {
    event.waitUntil(syncLearningData());
  }
  
  if (event.tag === 'background-sync-progress') {
    event.waitUntil(syncProgressData());
  }
});

// Push notifications
self.addEventListener('push', event => {
  console.log('[SW] Push message received');
  
  const options = {
    body: event.data ? event.data.text() : 'New learning content available!',
    icon: '/static/images/icon-192.png',
    badge: '/static/images/icon-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: 'Start Learning',
        icon: '/static/images/icon-96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/images/icon-96.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Laura-bot Learning Assistant', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/learn')
    );
  } else if (event.action === 'close') {
    // Just close the notification
  } else {
    // Default action - open app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Cache strategies
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE_NAME);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache-first strategy failed:', error);
    return new Response('Offline content not available', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses for dynamic content
    if (networkResponse.ok && isDynamic(request.url)) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/');
    }
    
    return new Response('Network error and no cached version available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    console.log('[SW] Network failed for:', request.url);
  });
  
  return cachedResponse || fetchPromise;
}

// URL pattern matching functions
function isNetworkFirst(url) {
  return NETWORK_FIRST_PATTERNS.some(pattern => pattern.test(url));
}

function isCacheFirst(url) {
  return CACHE_FIRST_PATTERNS.some(pattern => pattern.test(url));
}

function isDynamic(url) {
  return DYNAMIC_PATTERNS.some(pattern => pattern.test(url));
}

// Sync functions
async function syncLearningData() {
  try {
    // Get stored learning data from IndexedDB
    const learningData = await getStoredLearningData();
    
    if (learningData.length > 0) {
      // Send to server
      const response = await fetch('/api/sync/learning', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: learningData })
      });
      
      if (response.ok) {
        // Clear synced data
        await clearSyncedLearningData();
        console.log('[SW] Learning data synced successfully');
      }
    }
  } catch (error) {
    console.error('[SW] Failed to sync learning data:', error);
  }
}

async function syncProgressData() {
  try {
    // Get stored progress data from IndexedDB
    const progressData = await getStoredProgressData();
    
    if (progressData.length > 0) {
      // Send to server
      const response = await fetch('/api/sync/progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: progressData })
      });
      
      if (response.ok) {
        // Clear synced data
        await clearSyncedProgressData();
        console.log('[SW] Progress data synced successfully');
      }
    }
  } catch (error) {
    console.error('[SW] Failed to sync progress data:', error);
  }
}

// IndexedDB helper functions (simplified)
async function getStoredLearningData() {
  // Implementation would use IndexedDB to retrieve stored data
  return [];
}

async function clearSyncedLearningData() {
  // Implementation would clear synced data from IndexedDB
}

async function getStoredProgressData() {
  // Implementation would use IndexedDB to retrieve stored data
  return [];
}

async function clearSyncedProgressData() {
  // Implementation would clear synced data from IndexedDB
}

// Version and update handling
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

console.log('[SW] Laura-bot Service Worker loaded successfully');
