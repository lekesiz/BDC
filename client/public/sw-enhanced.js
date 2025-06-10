// Enhanced BDC Progressive Web App Service Worker
// Advanced PWA implementation with comprehensive caching, offline functionality, and monitoring

const SW_VERSION = '2.0.0';
const CACHE_PREFIX = 'bdc-pwa';
const CACHE_NAMES = {
  static: `${CACHE_PREFIX}-static-v${SW_VERSION}`,
  runtime: `${CACHE_PREFIX}-runtime-v${SW_VERSION}`,
  api: `${CACHE_PREFIX}-api-v${SW_VERSION}`,
  images: `${CACHE_PREFIX}-images-v${SW_VERSION}`,
  i18n: `${CACHE_PREFIX}-i18n-v${SW_VERSION}`,
  documents: `${CACHE_PREFIX}-documents-v${SW_VERSION}`,
  fonts: `${CACHE_PREFIX}-fonts-v${SW_VERSION}`
};

// Cache configurations
const CACHE_CONFIG = {
  static: {
    strategy: 'cache-first',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    maxEntries: 100
  },
  runtime: {
    strategy: 'stale-while-revalidate',
    maxAge: 24 * 60 * 60 * 1000, // 1 day
    maxEntries: 200
  },
  api: {
    strategy: 'network-first',
    maxAge: 5 * 60 * 1000, // 5 minutes
    maxEntries: 50,
    networkTimeoutSeconds: 10
  },
  images: {
    strategy: 'cache-first',
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
    maxEntries: 100
  },
  i18n: {
    strategy: 'stale-while-revalidate',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    maxEntries: 20
  },
  documents: {
    strategy: 'cache-first',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    maxEntries: 50
  },
  fonts: {
    strategy: 'cache-first',
    maxAge: 365 * 24 * 60 * 60 * 1000, // 1 year
    maxEntries: 30
  }
};

// Static assets to precache
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/offline-enhanced.html',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Critical API endpoints to cache
const CRITICAL_API_ENDPOINTS = [
  '/api/auth/me',
  '/api/dashboard/stats',
  '/api/beneficiaries?limit=10',
  '/api/evaluations?limit=10',
  '/api/notifications?limit=10'
];

// Background sync configuration
const SYNC_CONFIG = {
  evaluations: { tag: 'evaluation-sync', maxRetries: 3 },
  beneficiaries: { tag: 'beneficiary-sync', maxRetries: 3 },
  documents: { tag: 'document-sync', maxRetries: 5 },
  notifications: { tag: 'notification-sync', maxRetries: 2 },
  analytics: { tag: 'analytics-sync', maxRetries: 1 }
};

// Performance monitoring
class PerformanceTracker {
  constructor() {
    this.metrics = new Map();
    this.startTimes = new Map();
  }

  start(name) {
    this.startTimes.set(name, performance.now());
  }

  end(name, metadata = {}) {
    const startTime = this.startTimes.get(name);
    if (startTime) {
      const duration = performance.now() - startTime;
      this.record(name, duration, metadata);
      this.startTimes.delete(name);
      return duration;
    }
  }

  record(name, value, metadata = {}) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    this.metrics.get(name).push({
      value,
      timestamp: Date.now(),
      metadata
    });

    // Keep only last 100 entries per metric
    const entries = this.metrics.get(name);
    if (entries.length > 100) {
      entries.splice(0, entries.length - 100);
    }
  }

  getMetrics(name = null) {
    if (name) {
      return this.metrics.get(name) || [];
    }
    return Object.fromEntries(this.metrics);
  }

  getAverageMetric(name) {
    const entries = this.metrics.get(name) || [];
    if (entries.length === 0) return 0;
    
    const sum = entries.reduce((acc, entry) => acc + entry.value, 0);
    return sum / entries.length;
  }
}

// Cache manager with advanced features
class CacheManager {
  constructor() {
    this.hitRates = new Map();
    this.missRates = new Map();
  }

  async get(cacheName, request) {
    const cache = await caches.open(cacheName);
    const response = await cache.match(request);
    
    if (response) {
      this.recordHit(cacheName);
      return response;
    } else {
      this.recordMiss(cacheName);
      return null;
    }
  }

  async put(cacheName, request, response, config = {}) {
    const cache = await caches.open(cacheName);
    
    // Check cache size limits
    if (config.maxEntries) {
      await this.enforceMaxEntries(cache, config.maxEntries);
    }
    
    // Add expiration metadata
    const responseClone = response.clone();
    const headers = new Headers(responseClone.headers);
    
    if (config.maxAge) {
      headers.set('sw-cache-expiry', Date.now() + config.maxAge);
    }
    
    const enhancedResponse = new Response(responseClone.body, {
      status: responseClone.status,
      statusText: responseClone.statusText,
      headers
    });
    
    await cache.put(request, enhancedResponse);
  }

  async enforceMaxEntries(cache, maxEntries) {
    const requests = await cache.keys();
    
    if (requests.length >= maxEntries) {
      // Remove oldest entries
      const entriesToRemove = requests.length - maxEntries + 1;
      
      for (let i = 0; i < entriesToRemove; i++) {
        await cache.delete(requests[i]);
      }
    }
  }

  async isExpired(response) {
    const expiry = response.headers.get('sw-cache-expiry');
    if (!expiry) return false;
    
    return parseInt(expiry) < Date.now();
  }

  recordHit(cacheName) {
    const hits = this.hitRates.get(cacheName) || 0;
    this.hitRates.set(cacheName, hits + 1);
  }

  recordMiss(cacheName) {
    const misses = this.missRates.get(cacheName) || 0;
    this.missRates.set(cacheName, misses + 1);
  }

  getHitRate(cacheName) {
    const hits = this.hitRates.get(cacheName) || 0;
    const misses = this.missRates.get(cacheName) || 0;
    const total = hits + misses;
    
    return total > 0 ? Math.round((hits / total) * 100) : 0;
  }

  async cleanupExpiredEntries() {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
      if (!cacheName.startsWith(CACHE_PREFIX)) continue;
      
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      
      for (const request of requests) {
        const response = await cache.match(request);
        if (response && await this.isExpired(response)) {
          await cache.delete(request);
          console.log(`[SW] Removed expired entry: ${request.url}`);
        }
      }
    }
  }
}

// Background sync manager
class SyncManager {
  constructor() {
    this.queue = new Map();
    this.retryDelays = [1000, 5000, 15000, 30000]; // Progressive delays
  }

  async add(tag, data, options = {}) {
    const syncItem = {
      id: this.generateId(),
      tag,
      data,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: options.maxRetries || 3,
      priority: options.priority || 'normal'
    };

    // Store in IndexedDB for persistence
    await this.persistSyncItem(syncItem);
    
    // Register background sync
    if ('serviceWorker' in self && 'sync' in self.ServiceWorkerRegistration.prototype) {
      try {
        await self.registration.sync.register(tag);
      } catch (error) {
        console.error(`[SW] Failed to register sync: ${tag}`, error);
      }
    }
    
    return syncItem.id;
  }

  async persistSyncItem(item) {
    // This would integrate with IndexedDB in a real implementation
    const stored = await this.getStoredSyncQueue();
    stored.push(item);
    
    try {
      await self.caches.open('sync-queue').then(cache => {
        return cache.put('/sync-queue', new Response(JSON.stringify(stored)));
      });
    } catch (error) {
      console.error('[SW] Failed to persist sync item:', error);
    }
  }

  async getStoredSyncQueue() {
    try {
      const cache = await self.caches.open('sync-queue');
      const response = await cache.match('/sync-queue');
      
      if (response) {
        const text = await response.text();
        return JSON.parse(text);
      }
    } catch (error) {
      console.error('[SW] Failed to get stored sync queue:', error);
    }
    
    return [];
  }

  async processSyncQueue(tag) {
    const queue = await this.getStoredSyncQueue();
    const itemsToSync = queue.filter(item => item.tag === tag && item.retryCount < item.maxRetries);
    
    for (const item of itemsToSync) {
      try {
        await this.syncItem(item);
        await this.removeSyncItem(item.id);
      } catch (error) {
        console.error(`[SW] Sync failed for item ${item.id}:`, error);
        item.retryCount++;
        item.lastRetry = Date.now();
        await this.persistSyncItem(item);
      }
    }
  }

  async syncItem(item) {
    switch (item.tag) {
      case 'evaluation-sync':
        return this.syncEvaluation(item.data);
      case 'beneficiary-sync':
        return this.syncBeneficiary(item.data);
      case 'document-sync':
        return this.syncDocument(item.data);
      case 'notification-sync':
        return this.syncNotification(item.data);
      case 'analytics-sync':
        return this.syncAnalytics(item.data);
      default:
        throw new Error(`Unknown sync tag: ${item.tag}`);
    }
  }

  async syncEvaluation(data) {
    const response = await fetch('/api/evaluations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
      },
      body: JSON.stringify(data.evaluation)
    });

    if (!response.ok) {
      throw new Error(`Evaluation sync failed: ${response.statusText}`);
    }

    return response.json();
  }

  async syncBeneficiary(data) {
    const method = data.beneficiary.id ? 'PUT' : 'POST';
    const url = data.beneficiary.id ? 
      `/api/beneficiaries/${data.beneficiary.id}` : 
      '/api/beneficiaries';

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
      },
      body: JSON.stringify(data.beneficiary)
    });

    if (!response.ok) {
      throw new Error(`Beneficiary sync failed: ${response.statusText}`);
    }

    return response.json();
  }

  async syncDocument(data) {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('metadata', JSON.stringify(data.metadata));

    const response = await fetch('/api/documents', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${data.token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Document sync failed: ${response.statusText}`);
    }

    return response.json();
  }

  async syncNotification(data) {
    const response = await fetch('/api/notifications/action', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
      },
      body: JSON.stringify(data.action)
    });

    if (!response.ok) {
      throw new Error(`Notification sync failed: ${response.statusText}`);
    }

    return response.json();
  }

  async syncAnalytics(data) {
    const response = await fetch('/api/analytics/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
      },
      body: JSON.stringify(data.events)
    });

    if (!response.ok) {
      throw new Error(`Analytics sync failed: ${response.statusText}`);
    }

    return response.json();
  }

  async removeSyncItem(id) {
    const queue = await this.getStoredSyncQueue();
    const filtered = queue.filter(item => item.id !== id);
    
    try {
      await self.caches.open('sync-queue').then(cache => {
        return cache.put('/sync-queue', new Response(JSON.stringify(filtered)));
      });
    } catch (error) {
      console.error('[SW] Failed to remove sync item:', error);
    }
  }

  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
}

// Initialize managers
const perfTracker = new PerformanceTracker();
const cacheManager = new CacheManager();
const syncManager = new SyncManager();

// Request routing and strategy implementation
class RequestRouter {
  constructor() {
    this.routes = new Map();
    this.setupDefaultRoutes();
  }

  setupDefaultRoutes() {
    // Static assets
    this.addRoute(/\.(js|css|html)$/i, 'static');
    
    // Images
    this.addRoute(/\.(jpg|jpeg|png|gif|webp|svg|ico)$/i, 'images');
    
    // Fonts
    this.addRoute(/\.(woff|woff2|ttf|eot)$/i, 'fonts');
    
    // API endpoints
    this.addRoute(/^\/api\//, 'api');
    
    // i18n assets
    this.addRoute(/\/locales\/.*\.json$/i, 'i18n');
    
    // Documents
    this.addRoute(/\.(pdf|doc|docx|xls|xlsx)$/i, 'documents');
  }

  addRoute(pattern, cacheType) {
    this.routes.set(pattern, cacheType);
  }

  getCacheType(url) {
    for (const [pattern, cacheType] of this.routes) {
      if (pattern.test(url)) {
        return cacheType;
      }
    }
    return 'runtime';
  }

  async handleRequest(request) {
    const url = new URL(request.url);
    const cacheType = this.getCacheType(url.pathname);
    const config = CACHE_CONFIG[cacheType];
    const cacheName = CACHE_NAMES[cacheType];

    perfTracker.start(`${cacheType}-request`);

    try {
      let response;

      switch (config.strategy) {
        case 'cache-first':
          response = await this.cacheFirst(request, cacheName, config);
          break;
        case 'network-first':
          response = await this.networkFirst(request, cacheName, config);
          break;
        case 'stale-while-revalidate':
          response = await this.staleWhileRevalidate(request, cacheName, config);
          break;
        default:
          response = await fetch(request);
      }

      perfTracker.end(`${cacheType}-request`, {
        url: url.pathname,
        cacheType,
        strategy: config.strategy,
        fromCache: response.headers.has('sw-cache-hit')
      });

      return response;
    } catch (error) {
      perfTracker.end(`${cacheType}-request`, {
        url: url.pathname,
        cacheType,
        error: error.message
      });

      return this.handleRequestError(request, error);
    }
  }

  async cacheFirst(request, cacheName, config) {
    const cachedResponse = await cacheManager.get(cacheName, request);
    
    if (cachedResponse && !await cacheManager.isExpired(cachedResponse)) {
      const response = cachedResponse.clone();
      response.headers.set('sw-cache-hit', 'true');
      return response;
    }

    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      await cacheManager.put(cacheName, request, networkResponse.clone(), config);
    }

    return networkResponse;
  }

  async networkFirst(request, cacheName, config) {
    try {
      const networkResponse = await this.fetchWithTimeout(request, config.networkTimeoutSeconds);
      
      if (networkResponse.ok) {
        await cacheManager.put(cacheName, request, networkResponse.clone(), config);
      }
      
      return networkResponse;
    } catch (error) {
      const cachedResponse = await cacheManager.get(cacheName, request);
      
      if (cachedResponse) {
        const response = cachedResponse.clone();
        response.headers.set('sw-cache-hit', 'true');
        response.headers.set('sw-fallback', 'true');
        return response;
      }
      
      throw error;
    }
  }

  async staleWhileRevalidate(request, cacheName, config) {
    const cachedResponse = await cacheManager.get(cacheName, request);
    
    // Start network request in background
    const networkPromise = fetch(request).then(response => {
      if (response.ok) {
        cacheManager.put(cacheName, request, response.clone(), config);
      }
      return response;
    }).catch(() => {
      // Ignore network errors for background updates
    });

    if (cachedResponse && !await cacheManager.isExpired(cachedResponse)) {
      const response = cachedResponse.clone();
      response.headers.set('sw-cache-hit', 'true');
      
      // Don't wait for background update
      networkPromise;
      
      return response;
    }

    // Wait for network if no cache or expired
    return networkPromise;
  }

  async fetchWithTimeout(request, timeoutSeconds = 10) {
    const timeout = timeoutSeconds * 1000;
    
    return Promise.race([
      fetch(request),
      new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Network timeout')), timeout);
      })
    ]);
  }

  async handleRequestError(request, error) {
    const url = new URL(request.url);
    
    // For navigation requests, serve offline page
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match('/offline-enhanced.html');
      return offlineResponse || caches.match('/offline.html');
    }
    
    // For API requests, return error response
    if (url.pathname.startsWith('/api/')) {
      return new Response(
        JSON.stringify({
          error: 'Service Unavailable',
          message: 'This request is not available offline',
          offline: true,
          timestamp: new Date().toISOString()
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

const requestRouter = new RequestRouter();

// Service Worker Event Handlers

// Install event
self.addEventListener('install', (event) => {
  console.log(`[SW] Installing service worker v${SW_VERSION}`);
  
  event.waitUntil(
    Promise.all([
      // Precache static assets
      caches.open(CACHE_NAMES.static).then(cache => {
        console.log('[SW] Precaching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Precache critical API endpoints
      cacheManager.warmupCriticalEndpoints(),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log(`[SW] Activating service worker v${SW_VERSION}`);
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        const validCacheNames = Object.values(CACHE_NAMES);
        return Promise.all(
          cacheNames
            .filter(cacheName => 
              cacheName.startsWith(CACHE_PREFIX) && 
              !validCacheNames.includes(cacheName)
            )
            .map(cacheName => {
              console.log(`[SW] Deleting old cache: ${cacheName}`);
              return caches.delete(cacheName);
            })
        );
      }),
      
      // Claim all clients
      self.clients.claim(),
      
      // Setup periodic cleanup
      setupPeriodicTasks()
    ])
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }
  
  event.respondWith(requestRouter.handleRequest(request));
});

// Background sync events
self.addEventListener('sync', (event) => {
  console.log(`[SW] Background sync triggered: ${event.tag}`);
  
  event.waitUntil(syncManager.processSyncQueue(event.tag));
});

// Push notification events
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  let options = {
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
        icon: '/icons/view.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/close.png'
      }
    ],
    requireInteraction: false,
    silent: false
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      options = { ...options, ...data };
    } catch (error) {
      console.error('[SW] Error parsing push data:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(options.title || 'BDC Notification', options)
  );
});

// Notification click events
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.notification.tag);
  
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  if (action === 'close') {
    return;
  }
  
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(clientList => {
      // Try to focus existing window
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      
      // Open new window
      if (clients.openWindow) {
        const url = data?.url || '/';
        return clients.openWindow(url);
      }
    })
  );
});

// Message handling for client communication
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: SW_VERSION });
      break;
      
    case 'GET_CACHE_STATS':
      event.ports[0].postMessage({
        hitRates: Object.fromEntries(cacheManager.hitRates),
        missRates: Object.fromEntries(cacheManager.missRates)
      });
      break;
      
    case 'GET_PERFORMANCE_METRICS':
      event.ports[0].postMessage(perfTracker.getMetrics());
      break;
      
    case 'CACHE_URLS':
      event.waitUntil(warmupCache(payload.urls));
      break;
      
    case 'CLEAR_CACHE':
      event.waitUntil(clearSpecificCache(payload.cacheName));
      break;
      
    case 'ADD_TO_SYNC_QUEUE':
      event.waitUntil(syncManager.add(payload.tag, payload.data, payload.options));
      break;
      
    default:
      console.log(`[SW] Unknown message type: ${type}`);
  }
});

// Utility functions
async function setupPeriodicTasks() {
  // Setup periodic cache cleanup (every 6 hours)
  setInterval(async () => {
    try {
      await cacheManager.cleanupExpiredEntries();
      console.log('[SW] Periodic cache cleanup completed');
    } catch (error) {
      console.error('[SW] Cache cleanup error:', error);
    }
  }, 6 * 60 * 60 * 1000);
  
  // Setup performance metrics collection (every hour)
  setInterval(() => {
    perfTracker.record('cache-hit-rate', cacheManager.getHitRate('overall'));
    perfTracker.record('memory-usage', performance.memory?.usedJSHeapSize || 0);
  }, 60 * 60 * 1000);
}

async function warmupCache(urls) {
  const promises = urls.map(async (url) => {
    try {
      const response = await fetch(url);
      if (response.ok) {
        const cacheType = requestRouter.getCacheType(new URL(url).pathname);
        const cacheName = CACHE_NAMES[cacheType];
        const config = CACHE_CONFIG[cacheType];
        
        await cacheManager.put(cacheName, url, response, config);
        return { url, success: true };
      }
      return { url, success: false, error: 'Response not ok' };
    } catch (error) {
      return { url, success: false, error: error.message };
    }
  });
  
  return Promise.all(promises);
}

async function clearSpecificCache(cacheName) {
  if (cacheName && CACHE_NAMES[cacheName]) {
    return caches.delete(CACHE_NAMES[cacheName]);
  }
  return false;
}

// Error handling
self.addEventListener('error', (event) => {
  console.error('[SW] Error:', event.error);
  perfTracker.record('sw-error', 1, {
    message: event.error?.message,
    filename: event.filename,
    lineno: event.lineno
  });
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('[SW] Unhandled rejection:', event.reason);
  perfTracker.record('sw-unhandled-rejection', 1, {
    reason: event.reason?.message || event.reason
  });
});

console.log(`[SW] Service Worker v${SW_VERSION} loaded and ready`);

// Extend cache manager with warmup functionality
cacheManager.warmupCriticalEndpoints = async function() {
  console.log('[SW] Warming up critical API endpoints');
  
  for (const endpoint of CRITICAL_API_ENDPOINTS) {
    try {
      const response = await fetch(endpoint, {
        headers: { 'X-SW-Warmup': 'true' }
      });
      
      if (response.ok) {
        await this.put(CACHE_NAMES.api, endpoint, response.clone(), CACHE_CONFIG.api);
      }
    } catch (error) {
      console.log(`[SW] Failed to warmup ${endpoint}:`, error.message);
    }
  }
};