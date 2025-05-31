/**
 * Service Worker for BDC Application
 * Handles caching, offline support, and performance optimization
 */

const CACHE_NAME = 'bdc-cache-v1';
const STATIC_CACHE_NAME = 'bdc-static-v1';
const DYNAMIC_CACHE_NAME = 'bdc-dynamic-v1';
const API_CACHE_NAME = 'bdc-api-v1';

// URLs to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  // Add your static assets here
];

// API routes pattern
const API_PATTERN = /^\/api\//;

// Cache strategies
const CacheStrategy = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  NETWORK_ONLY: 'network-only',
  CACHE_ONLY: 'cache-only',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Route cache strategies
const ROUTE_STRATEGIES = {
  // Static assets - cache first
  '/static/': CacheStrategy.CACHE_FIRST,
  '/assets/': CacheStrategy.CACHE_FIRST,
  '/images/': CacheStrategy.CACHE_FIRST,
  
  // API routes - network first with cache fallback
  '/api/': CacheStrategy.NETWORK_FIRST,
  
  // Dynamic content - stale while revalidate
  '/': CacheStrategy.STALE_WHILE_REVALIDATE
};

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName.startsWith('bdc-') && 
                     cacheName !== CACHE_NAME &&
                     cacheName !== STATIC_CACHE_NAME &&
                     cacheName !== DYNAMIC_CACHE_NAME &&
                     cacheName !== API_CACHE_NAME;
            })
            .map((cacheName) => caches.delete(cacheName))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - handle requests with appropriate strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-HTTP(S) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // Determine cache strategy
  const strategy = getStrategyForRequest(request);
  
  event.respondWith(
    handleRequest(request, strategy)
      .catch(() => {
        // Fallback to offline page for navigation requests
        if (request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
        throw new Error('Offline');
      })
  );
});

// Get cache strategy for request
function getStrategyForRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Check route strategies
  for (const [route, strategy] of Object.entries(ROUTE_STRATEGIES)) {
    if (path.startsWith(route)) {
      return strategy;
    }
  }
  
  // Default strategy
  return CacheStrategy.NETWORK_FIRST;
}

// Handle request with given strategy
async function handleRequest(request, strategy) {
  switch (strategy) {
    case CacheStrategy.CACHE_FIRST:
      return cacheFirst(request);
    case CacheStrategy.NETWORK_FIRST:
      return networkFirst(request);
    case CacheStrategy.CACHE_ONLY:
      return cacheOnly(request);
    case CacheStrategy.NETWORK_ONLY:
      return networkOnly(request);
    case CacheStrategy.STALE_WHILE_REVALIDATE:
      return staleWhileRevalidate(request);
    default:
      return networkFirst(request);
  }
}

// Cache first strategy
async function cacheFirst(request) {
  const cached = await caches.match(request);
  
  if (cached) {
    console.log('[Service Worker] Cache hit:', request.url);
    return cached;
  }
  
  console.log('[Service Worker] Cache miss, fetching:', request.url);
  const response = await fetch(request);
  
  // Cache successful responses
  if (response.ok && response.status === 200) {
    const responseClone = response.clone();
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    cache.put(request, responseClone);
  }
  
  return response;
}

// Network first strategy
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok && response.status === 200) {
      const responseClone = response.clone();
      const cacheName = API_PATTERN.test(request.url) ? API_CACHE_NAME : DYNAMIC_CACHE_NAME;
      const cache = await caches.open(cacheName);
      cache.put(request, responseClone);
    }
    
    return response;
  } catch (error) {
    // Fallback to cache
    const cached = await caches.match(request);
    if (cached) {
      console.log('[Service Worker] Network failed, using cache:', request.url);
      return cached;
    }
    throw error;
  }
}

// Cache only strategy
async function cacheOnly(request) {
  const cached = await caches.match(request);
  
  if (cached) {
    return cached;
  }
  
  throw new Error('No cache available');
}

// Network only strategy
async function networkOnly(request) {
  return fetch(request);
}

// Stale while revalidate strategy
async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok && response.status === 200) {
      // Clone the response before using it
      const responseClone = response.clone();
      caches.open(DYNAMIC_CACHE_NAME).then((cache) => {
        cache.put(request, responseClone);
      });
    }
    return response;
  });
  
  return cached || fetchPromise;
}

// Message handling
self.addEventListener('message', (event) => {
  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'CACHE_URLS':
        event.waitUntil(
          cacheUrls(event.data.payload.urls)
            .then(() => event.ports[0].postMessage({ cached: true }))
        );
        break;
        
      case 'DELETE_CACHE':
        event.waitUntil(
          deleteCaches()
            .then(() => event.ports[0].postMessage({ deleted: true }))
        );
        break;
        
      case 'SKIP_WAITING':
        self.skipWaiting();
        break;
    }
  }
});

// Cache specific URLs
async function cacheUrls(urls) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  return cache.addAll(urls);
}

// Delete all caches
async function deleteCaches() {
  const cacheNames = await caches.keys();
  return Promise.all(
    cacheNames.map((cacheName) => caches.delete(cacheName))
  );
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-api-requests') {
    event.waitUntil(syncApiRequests());
  }
});

// Sync failed API requests
async function syncApiRequests() {
  // Implementation for syncing failed requests
  console.log('[Service Worker] Syncing API requests...');
}