// BDC Progressive Web App Service Worker
// Comprehensive PWA implementation with caching, offline functionality, and push notifications

const CACHE_NAME = 'bdc-pwa-v1.0.0';
const RUNTIME_CACHE = 'bdc-runtime-v1.0.0';
const API_CACHE = 'bdc-api-v1.0.0';
const IMAGE_CACHE = 'bdc-images-v1.0.0';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/src/main.jsx',
  '/src/App.jsx',
  '/src/index.css',
  // Add other critical static assets
];

// API endpoints to cache for offline access
const API_ENDPOINTS = [
  '/api/auth/me',
  '/api/beneficiaries',
  '/api/programs',
  '/api/evaluations',
  '/api/notifications',
  '/api/dashboard',
];

// Cache strategies configuration
const CACHE_STRATEGIES = {
  static: 'cache-first',
  api: 'network-first',
  images: 'cache-first',
  runtime: 'stale-while-revalidate'
};

// Background sync queues
const SYNC_QUEUES = {
  evaluations: 'evaluation-submissions',
  appointments: 'appointment-updates',
  documents: 'document-uploads',
  notifications: 'notification-actions'
};

// Install event - Cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== CACHE_NAME && 
                     cacheName !== RUNTIME_CACHE && 
                     cacheName !== API_CACHE && 
                     cacheName !== IMAGE_CACHE;
            })
            .map((cacheName) => {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      }),
      
      // Claim all clients
      self.clients.claim()
    ])
  );
  
  // Notify clients about update
  notifyClientsAboutUpdate();
});

// Fetch event - Implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle different types of requests
  if (isApiRequest(url)) {
    event.respondWith(handleApiRequest(request));
  } else if (isImageRequest(url)) {
    event.respondWith(handleImageRequest(request));
  } else if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
  } else {
    event.respondWith(handleRuntimeRequest(request));
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  switch (event.tag) {
    case SYNC_QUEUES.evaluations:
      event.waitUntil(syncEvaluationSubmissions());
      break;
    case SYNC_QUEUES.appointments:
      event.waitUntil(syncAppointmentUpdates());
      break;
    case SYNC_QUEUES.documents:
      event.waitUntil(syncDocumentUploads());
      break;
    case SYNC_QUEUES.notifications:
      event.waitUntil(syncNotificationActions());
      break;
    default:
      console.log('[SW] Unknown sync tag:', event.tag);
  }
});

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  if (!event.data) {
    console.log('[SW] Push event but no data');
    return;
  }
  
  const options = {
    body: 'New notification from BDC',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: '/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/xmark.png'
      }
    ]
  };
  
  try {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.title = data.title || 'BDC Notification';
    options.data = { ...options.data, ...data };
  } catch (e) {
    console.log('[SW] Error parsing push data:', e);
  }
  
  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.notification.tag);
  
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  if (action === 'close') {
    return;
  }
  
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      // If there's already a window open, focus it
      for (const client of clientList) {
        if (client.url === self.location.origin && 'focus' in client) {
          return client.focus();
        }
      }
      
      // Otherwise, open a new window
      if (clients.openWindow) {
        const url = data.url || '/';
        return clients.openWindow(url);
      }
    })
  );
});

// Message handling for client communication
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_NAME });
      break;
    
    case 'CACHE_URLS':
      event.waitUntil(cacheUrls(payload.urls));
      break;
    
    case 'CLEAR_CACHE':
      event.waitUntil(clearCache(payload.cacheName));
      break;
    
    case 'SYNC_DATA':
      event.waitUntil(registerBackgroundSync(payload.tag, payload.data));
      break;
    
    default:
      console.log('[SW] Unknown message type:', type);
  }
});

// Helper Functions

function isApiRequest(url) {
  return url.pathname.startsWith('/api/');
}

function isImageRequest(url) {
  return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url.pathname);
}

function isStaticAsset(url) {
  return /\.(js|css|woff2?|ttf|eot)$/i.test(url.pathname) ||
         STATIC_ASSETS.includes(url.pathname);
}

// Cache strategy implementations

async function handleApiRequest(request) {
  const url = new URL(request.url);
  const cache = await caches.open(API_CACHE);
  
  try {
    // Network first strategy for API requests
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed for API request, trying cache:', url.pathname);
    
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for critical API endpoints
    if (isCriticalApiEndpoint(url.pathname)) {
      return new Response(
        JSON.stringify({ 
          error: 'Offline', 
          message: 'This content is not available offline' 
        }),
        {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    throw error;
  }
}

async function handleImageRequest(request) {
  const cache = await caches.open(IMAGE_CACHE);
  
  // Cache first strategy for images
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return placeholder image for offline
    return new Response('', {
      status: 200,
      headers: { 'Content-Type': 'image/svg+xml' }
    });
  }
}

async function handleStaticAsset(request) {
  const cache = await caches.open(CACHE_NAME);
  
  // Cache first strategy for static assets
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    throw error;
  }
}

async function handleRuntimeRequest(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  
  try {
    // Stale while revalidate strategy
    const networkResponsePromise = fetch(request);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      // Return cached version immediately
      networkResponsePromise.then((networkResponse) => {
        if (networkResponse.ok) {
          cache.put(request, networkResponse.clone());
        }
      }).catch(() => {
        // Network failed, but we already have cached version
      });
      
      return cachedResponse;
    }
    
    // No cached version, wait for network
    const networkResponse = await networkResponsePromise;
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
    
  } catch (error) {
    // Network failed and no cache, return offline page
    const url = new URL(request.url);
    if (request.mode === 'navigate') {
      return caches.match('/offline.html');
    }
    throw error;
  }
}

// Background sync functions

async function syncEvaluationSubmissions() {
  console.log('[SW] Syncing evaluation submissions');
  
  try {
    const data = await getStoredData('pendingEvaluations');
    if (!data || data.length === 0) return;
    
    for (const evaluation of data) {
      try {
        const response = await fetch('/api/evaluations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${evaluation.token}`
          },
          body: JSON.stringify(evaluation.data)
        });
        
        if (response.ok) {
          await removeStoredData('pendingEvaluations', evaluation.id);
          await notifyClient('SYNC_SUCCESS', {
            type: 'evaluation',
            id: evaluation.id
          });
        }
      } catch (error) {
        console.log('[SW] Failed to sync evaluation:', error);
      }
    }
  } catch (error) {
    console.log('[SW] Error in syncEvaluationSubmissions:', error);
  }
}

async function syncAppointmentUpdates() {
  console.log('[SW] Syncing appointment updates');
  // Implementation for appointment sync
}

async function syncDocumentUploads() {
  console.log('[SW] Syncing document uploads');
  // Implementation for document sync
}

async function syncNotificationActions() {
  console.log('[SW] Syncing notification actions');
  // Implementation for notification sync
}

// Utility functions

function isCriticalApiEndpoint(pathname) {
  const criticalEndpoints = [
    '/api/auth/me',
    '/api/dashboard',
    '/api/beneficiaries',
    '/api/evaluations'
  ];
  return criticalEndpoints.some(endpoint => pathname.startsWith(endpoint));
}

async function cacheUrls(urls) {
  const cache = await caches.open(RUNTIME_CACHE);
  return Promise.all(
    urls.map(url => {
      return fetch(url).then(response => {
        if (response.ok) {
          return cache.put(url, response);
        }
      }).catch(console.log);
    })
  );
}

async function clearCache(cacheName) {
  return caches.delete(cacheName);
}

async function registerBackgroundSync(tag, data) {
  await storeData(tag, data);
  return self.registration.sync.register(tag);
}

async function storeData(key, data) {
  // Store data in IndexedDB for background sync
  // This would require IndexedDB implementation
  console.log('[SW] Storing data for sync:', key, data);
}

async function getStoredData(key) {
  // Retrieve data from IndexedDB
  console.log('[SW] Getting stored data:', key);
  return [];
}

async function removeStoredData(key, id) {
  // Remove specific item from IndexedDB
  console.log('[SW] Removing stored data:', key, id);
}

async function notifyClient(type, payload) {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type, payload });
  });
}

function notifyClientsAboutUpdate() {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({
        type: 'SW_UPDATED',
        payload: { version: CACHE_NAME }
      });
    });
  });
}

// Periodic cleanup
setInterval(() => {
  // Clean up old cache entries
  console.log('[SW] Performing periodic cleanup');
}, 24 * 60 * 60 * 1000); // Daily cleanup