// BDC Progressive Web App Service Worker
// Comprehensive PWA implementation with caching, offline functionality, and push notifications

const CACHE_NAME = 'bdc-pwa-v1.0.0';
const RUNTIME_CACHE = 'bdc-runtime-v1.0.0';
const API_CACHE = 'bdc-api-v1.0.0';
const IMAGE_CACHE = 'bdc-images-v1.0.0';
const I18N_CACHE = 'bdc-i18n-v1.0.0';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/src/main.jsx',
  '/src/App.jsx',
  '/src/index.css',
  // Add other critical static assets
];

// i18n assets to cache
const I18N_ASSETS = [
  '/locales/en/translation.json',
  '/locales/tr/translation.json',
  '/locales/fr/translation.json',
  '/locales/es/translation.json',
  '/locales/ar/translation.json',
  '/locales/he/translation.json',
  '/locales/de/translation.json',
  '/locales/ru/translation.json',
  '/locales/zh/translation.json',
  '/locales/ja/translation.json'
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
  runtime: 'stale-while-revalidate',
  i18n: 'stale-while-revalidate'
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
      
      // Cache i18n assets
      caches.open(I18N_CACHE).then((cache) => {
        console.log('[SW] Caching i18n assets');
        return cache.addAll(I18N_ASSETS.filter(asset => asset !== null));
      }).catch((error) => {
        console.log('[SW] Some i18n assets could not be cached:', error);
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
                     cacheName !== IMAGE_CACHE &&
                     cacheName !== I18N_CACHE;
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
  } else if (isI18nRequest(url)) {
    event.respondWith(handleI18nRequest(request));
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
    
    case 'CACHE_I18N':
      event.waitUntil(cacheI18nResource(payload.language, payload.url));
      break;
    
    case 'UPDATE_LANGUAGE':
      event.waitUntil(handleLanguageUpdate(payload.language));
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

function isI18nRequest(url) {
  return url.pathname.startsWith('/locales/') || 
         url.pathname.includes('/translation.json') ||
         I18N_ASSETS.some(asset => url.pathname.endsWith(asset.split('/').pop()));
}

function isImageRequest(url) {
  return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url.pathname);
}

function isStaticAsset(url) {
  return /\.(js|css|woff2?|ttf|eot)$/i.test(url.pathname) ||
         STATIC_ASSETS.includes(url.pathname);
}

// Cache strategy implementations

async function handleI18nRequest(request) {
  const cache = await caches.open(I18N_CACHE);
  
  try {
    // Stale while revalidate strategy for i18n resources
    const cachedResponse = await cache.match(request);
    const networkResponsePromise = fetch(request);
    
    // If we have a cached version, return it immediately
    if (cachedResponse) {
      console.log('[SW] Serving i18n from cache:', request.url);
      
      // Update cache in background
      networkResponsePromise.then((networkResponse) => {
        if (networkResponse.ok) {
          cache.put(request, networkResponse.clone());
          console.log('[SW] Updated i18n cache:', request.url);
        }
      }).catch((error) => {
        console.log('[SW] Failed to update i18n cache:', error);
      });
      
      return cachedResponse;
    }
    
    // No cached version, wait for network
    console.log('[SW] Fetching i18n from network:', request.url);
    const networkResponse = await networkResponsePromise;
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
      console.log('[SW] Cached new i18n resource:', request.url);
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('[SW] i18n request failed:', error);
    
    // Return cached version if available
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      console.log('[SW] Serving stale i18n from cache:', request.url);
      return cachedResponse;
    }
    
    // Return fallback English translation if available
    const fallbackUrl = request.url.replace(/\/locales\/[a-z]{2}(-[A-Z]{2})?\//, '/locales/en/');
    if (fallbackUrl !== request.url) {
      const fallbackResponse = await cache.match(fallbackUrl);
      if (fallbackResponse) {
        console.log('[SW] Serving English fallback for i18n:', request.url);
        return fallbackResponse;
      }
    }
    
    // Return empty object as last resort
    return new Response('{}', {
      status: 200,
      statusText: 'OK',
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

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

// IndexedDB utility class for offline data storage
class IndexedDBManager {
  constructor() {
    this.dbName = 'BDC_PWA_DB';
    this.version = 1;
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create stores for different data types
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
          syncStore.createIndex('tag', 'tag', { unique: false });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('offlineData')) {
          const offlineStore = db.createObjectStore('offlineData', { keyPath: 'key' });
          offlineStore.createIndex('type', 'type', { unique: false });
          offlineStore.createIndex('expiry', 'expiry', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('userActions')) {
          const actionsStore = db.createObjectStore('userActions', { keyPath: 'id', autoIncrement: true });
          actionsStore.createIndex('action', 'action', { unique: false });
          actionsStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('performance')) {
          const perfStore = db.createObjectStore('performance', { keyPath: 'id', autoIncrement: true });
          perfStore.createIndex('metric', 'metric', { unique: false });
          perfStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  async add(storeName, data) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(data);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async put(storeName, data) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async get(storeName, key) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async getAll(storeName, indexName = null, indexValue = null) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      
      let request;
      if (indexName && indexValue) {
        const index = store.index(indexName);
        request = index.getAll(indexValue);
      } else {
        request = store.getAll();
      }
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async delete(storeName, key) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async clear(storeName) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }
}

// Initialize IndexedDB manager
const dbManager = new IndexedDBManager();

// Performance monitoring class
class PerformanceMonitor {
  constructor() {
    this.metrics = {};
    this.startTimes = {};
  }

  startTimer(name) {
    this.startTimes[name] = performance.now();
  }

  endTimer(name) {
    if (this.startTimes[name]) {
      const duration = performance.now() - this.startTimes[name];
      this.metrics[name] = (this.metrics[name] || []).concat(duration);
      delete this.startTimes[name];
      
      // Store metric in IndexedDB
      dbManager.add('performance', {
        metric: name,
        duration,
        timestamp: Date.now()
      }).catch(console.error);
      
      return duration;
    }
  }

  recordMetric(name, value, metadata = {}) {
    dbManager.add('performance', {
      metric: name,
      value,
      metadata,
      timestamp: Date.now()
    }).catch(console.error);
  }

  getMetrics() {
    return this.metrics;
  }
}

const perfMonitor = new PerformanceMonitor();

// Advanced cache management
class CacheManager {
  constructor() {
    this.maxCacheSize = 50 * 1024 * 1024; // 50MB
    this.maxCacheAge = 7 * 24 * 60 * 60 * 1000; // 7 days
  }

  async cleanupExpiredCache() {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      
      for (const request of requests) {
        const response = await cache.match(request);
        const dateHeader = response?.headers.get('date');
        
        if (dateHeader) {
          const cacheDate = new Date(dateHeader);
          const isExpired = Date.now() - cacheDate.getTime() > this.maxCacheAge;
          
          if (isExpired) {
            await cache.delete(request);
            console.log('[SW] Deleted expired cache entry:', request.url);
          }
        }
      }
    }
  }

  async getCacheSize() {
    let totalSize = 0;
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      
      for (const request of requests) {
        const response = await cache.match(request);
        if (response) {
          const blob = await response.blob();
          totalSize += blob.size;
        }
      }
    }
    
    return totalSize;
  }

  async enforceQuota() {
    const currentSize = await this.getCacheSize();
    
    if (currentSize > this.maxCacheSize) {
      console.log('[SW] Cache size exceeded, cleaning up...');
      
      // Remove oldest entries from runtime cache first
      const cache = await caches.open(RUNTIME_CACHE);
      const requests = await cache.keys();
      
      // Sort by date and remove oldest entries
      const entriesWithDates = await Promise.all(
        requests.map(async (request) => {
          const response = await cache.match(request);
          const dateHeader = response?.headers.get('date');
          return {
            request,
            date: dateHeader ? new Date(dateHeader) : new Date(0)
          };
        })
      );
      
      entriesWithDates.sort((a, b) => a.date - b.date);
      
      // Remove oldest 25% of entries
      const entriesToRemove = Math.ceil(entriesWithDates.length * 0.25);
      for (let i = 0; i < entriesToRemove; i++) {
        await cache.delete(entriesWithDates[i].request);
      }
    }
  }
}

const cacheManager = new CacheManager();

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
  perfMonitor.startTimer('cache-urls');
  const cache = await caches.open(RUNTIME_CACHE);
  
  const results = await Promise.all(
    urls.map(async (url) => {
      try {
        const response = await fetch(url);
        if (response.ok) {
          await cache.put(url, response);
          return { url, success: true };
        }
        return { url, success: false, error: 'Response not ok' };
      } catch (error) {
        return { url, success: false, error: error.message };
      }
    })
  );
  
  perfMonitor.endTimer('cache-urls');
  return results;
}

async function clearCache(cacheName) {
  perfMonitor.startTimer('clear-cache');
  const result = await caches.delete(cacheName);
  perfMonitor.endTimer('clear-cache');
  return result;
}

async function cacheI18nResource(language, url) {
  try {
    const cache = await caches.open(I18N_CACHE);
    const response = await fetch(url);
    
    if (response.ok) {
      await cache.put(url, response);
      console.log(`[SW] Cached i18n resource for ${language}:`, url);
      
      // Notify clients about successful cache
      notifyClient('I18N_CACHED', {
        language,
        url,
        success: true
      });
    }
  } catch (error) {
    console.error('[SW] Failed to cache i18n resource:', error);
    
    // Notify clients about cache failure
    notifyClient('I18N_CACHED', {
      language,
      url,
      success: false,
      error: error.message
    });
  }
}

async function handleLanguageUpdate(language) {
  try {
    // Pre-cache translation files for the new language
    const translationUrl = `/locales/${language}/translation.json`;
    await cacheI18nResource(language, translationUrl);
    
    // Store current language preference
    await dbManager.put('offlineData', {
      key: 'current_language',
      value: language,
      type: 'preference',
      timestamp: Date.now()
    });
    
    console.log('[SW] Language updated to:', language);
  } catch (error) {
    console.error('[SW] Failed to handle language update:', error);
  }
}

async function registerBackgroundSync(tag, data) {
  try {
    await storeData(tag, data);
    await self.registration.sync.register(tag);
    return true;
  } catch (error) {
    console.error('[SW] Failed to register background sync:', error);
    return false;
  }
}

async function storeData(tag, data) {
  try {
    await dbManager.add('syncQueue', {
      tag,
      data,
      timestamp: Date.now(),
      retryCount: 0
    });
    
    console.log('[SW] Stored data for background sync:', tag);
  } catch (error) {
    console.error('[SW] Failed to store sync data:', error);
    throw error;
  }
}

async function getStoredData(tag) {
  try {
    const items = await dbManager.getAll('syncQueue', 'tag', tag);
    return items || [];
  } catch (error) {
    console.error('[SW] Failed to get stored data:', error);
    return [];
  }
}

async function removeStoredData(tag, id) {
  try {
    await dbManager.delete('syncQueue', id);
    console.log('[SW] Removed stored data:', tag, id);
  } catch (error) {
    console.error('[SW] Failed to remove stored data:', error);
  }
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

// Enhanced periodic cleanup and monitoring
setInterval(async () => {
  console.log('[SW] Performing periodic cleanup and monitoring');
  
  try {
    // Clean up expired cache entries
    await cacheManager.cleanupExpiredCache();
    
    // Enforce cache quota
    await cacheManager.enforceQuota();
    
    // Record cache size metrics
    const cacheSize = await cacheManager.getCacheSize();
    perfMonitor.recordMetric('cache-size', cacheSize);
    
    // Clean up old performance metrics (keep only last 7 days)
    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    const oldMetrics = await dbManager.getAll('performance');
    const expiredMetrics = oldMetrics.filter(metric => metric.timestamp < sevenDaysAgo);
    
    for (const metric of expiredMetrics) {
      await dbManager.delete('performance', metric.id);
    }
    
    // Update i18n cache size metrics
    const i18nCache = await caches.open(I18N_CACHE);
    const i18nRequests = await i18nCache.keys();
    perfMonitor.recordMetric('i18n-cache-entries', i18nRequests.length);
    
    // Clean up old sync queue items (failed items older than 24 hours)
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
    const oldSyncItems = await dbManager.getAll('syncQueue');
    const expiredSyncItems = oldSyncItems.filter(item => 
      item.timestamp < oneDayAgo && item.retryCount > 3
    );
    
    for (const item of expiredSyncItems) {
      await dbManager.delete('syncQueue', item.id);
      console.log('[SW] Removed expired sync item:', item.tag);
    }
    
    // Report cleanup results
    console.log(`[SW] Cleanup completed: ${expiredMetrics.length} old metrics, ${expiredSyncItems.length} expired sync items removed`);
    
  } catch (error) {
    console.error('[SW] Error during periodic cleanup:', error);
  }
}, 24 * 60 * 60 * 1000); // Daily cleanup

// Initialize performance monitoring on startup
(async function initializeMonitoring() {
  try {
    await dbManager.init();
    
    // Record service worker startup
    perfMonitor.recordMetric('sw-startup', 1, {
      version: CACHE_NAME,
      timestamp: Date.now()
    });
    
    // Monitor cache sizes at startup
    const cacheSize = await cacheManager.getCacheSize();
    perfMonitor.recordMetric('cache-size-startup', cacheSize);
    
    // Check for stored language preference
    try {
      const storedLang = await dbManager.get('offlineData', 'current_language');
      if (storedLang) {
        console.log('[SW] Restored language preference:', storedLang.value);
      }
    } catch (error) {
      console.log('[SW] No stored language preference found');
    }
    
    console.log('[SW] Performance monitoring initialized');
  } catch (error) {
    console.error('[SW] Failed to initialize monitoring:', error);
  }
})();