// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * PWA Utilities
 * Helper functions for Progressive Web App functionality
 */

/**
 * Check if the app is running as a PWA
 */
export function isPWA() {
  // Check if running in standalone mode
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return true;
  }

  // Check for iOS standalone mode
  if (window.navigator.standalone === true) {
    return true;
  }

  // Check for Android TWA (Trusted Web Activity)
  if (document.referrer.includes('android-app://')) {
    return true;
  }

  return false;
}

/**
 * Check if the device is mobile
 */
export function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

/**
 * Check if the device is iOS
 */
export function isIOS() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
}

/**
 * Check if the device is Android
 */
export function isAndroid() {
  return /Android/.test(navigator.userAgent);
}

/**
 * Get PWA installation prompt strategy based on browser
 */
export function getInstallPromptStrategy() {
  if (isIOS()) {
    return 'ios-manual'; // iOS requires manual instructions
  }

  if (isAndroid()) {
    return 'android-automatic'; // Android supports beforeinstallprompt
  }

  if (navigator.userAgent.includes('Chrome')) {
    return 'chrome-automatic';
  }

  if (navigator.userAgent.includes('Edge')) {
    return 'edge-automatic';
  }

  return 'manual';
}

/**
 * Check if browser supports PWA features
 */
export function getPWASupport() {
  return {
    serviceWorker: 'serviceWorker' in navigator,
    pushNotifications: 'Notification' in window && 'PushManager' in window,
    backgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
    webAppManifest: 'serviceWorker' in navigator,
    cacheStorage: 'caches' in window,
    indexedDB: 'indexedDB' in window,
    webShare: 'share' in navigator,
    badgeAPI: 'setAppBadge' in navigator,
    fullscreen: 'requestFullscreen' in document.documentElement,
    screenOrientation: 'screen' in window && 'orientation' in window.screen,
    wakeLock: 'wakeLock' in navigator,
    deviceMotion: 'DeviceMotionEvent' in window,
    geolocation: 'geolocation' in navigator,
    webRTC: 'RTCPeerConnection' in window,
    fileSystemAccess: 'showOpenFilePicker' in window
  };
}

/**
 * Get network connection information
 */
export function getConnectionInfo() {
  if ('connection' in navigator) {
    const connection = navigator.connection;
    return {
      type: connection.type,
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData
    };
  }

  return null;
}

/**
 * Check if the app should use offline-first strategy
 */
export function shouldUseOfflineFirst() {
  const connection = getConnectionInfo();

  if (!connection) {
    return false;
  }

  // Use offline-first for slow connections
  if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
    return true;
  }

  // Use offline-first if user has data saver enabled
  if (connection.saveData) {
    return true;
  }

  return false;
}

/**
 * Get optimal cache strategy based on content type
 */
export function getCacheStrategy(url, contentType) {
  // Static assets - cache first
  if (/\.(js|css|woff2?|ttf|eot|ico|png|jpg|jpeg|gif|svg|webp)$/i.test(url)) {
    return 'cache-first';
  }

  // API endpoints - network first
  if (url.includes('/api/')) {
    return 'network-first';
  }

  // HTML pages - stale while revalidate
  if (contentType?.includes('text/html') || url.match(/\/$/) || !url.includes('.')) {
    return 'stale-while-revalidate';
  }

  // Default strategy
  return 'network-first';
}

/**
 * Calculate app shell resources to cache
 */
export function getAppShellResources() {
  return [
  '/',
  '/offline.html',
  '/manifest.json'
  // Core CSS and JS files would be added here
  // These should be determined dynamically in a real implementation
  ];
}

/**
 * Get critical resources for immediate caching
 */
export function getCriticalResources() {
  return [
  '/',
  '/offline.html',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'];

}

/**
 * Calculate cache size limit based on device capabilities
 */
export function calculateCacheLimit() {
  // Get available storage
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    return navigator.storage.estimate().then((estimate) => {
      const quota = estimate.quota || 0;
      const usage = estimate.usage || 0;
      const available = quota - usage;

      // Use up to 25% of available storage for cache
      return Math.min(available * 0.25, 100 * 1024 * 1024); // Max 100MB
    });
  }

  // Fallback limits based on device type
  if (isMobile()) {
    return Promise.resolve(50 * 1024 * 1024); // 50MB for mobile
  }

  return Promise.resolve(100 * 1024 * 1024); // 100MB for desktop
}

/**
 * Check if content should be cached based on response
 */
export function shouldCache(response, url) {
  // Don't cache error responses
  if (!response.ok) {
    return false;
  }

  // Don't cache authentication endpoints
  if (url.includes('/auth/') || url.includes('/login')) {
    return false;
  }

  // Don't cache POST, PUT, DELETE requests
  if (response.request && response.request.method !== 'GET') {
    return false;
  }

  // Don't cache responses without cache headers on API endpoints
  if (url.includes('/api/') && !response.headers.get('cache-control')) {
    return false;
  }

  return true;
}

/**
 * Generate cache key for request
 */
export function generateCacheKey(request) {
  const url = new URL(request.url);

  // Remove cache-busting parameters
  url.searchParams.delete('_t');
  url.searchParams.delete('timestamp');
  url.searchParams.delete('v');

  // Include relevant parameters for API requests
  if (url.pathname.includes('/api/')) {
    // Keep important parameters like user ID, page, etc.
    const importantParams = ['userId', 'page', 'limit', 'filter', 'sort'];
    const newParams = new URLSearchParams();

    importantParams.forEach((param) => {
      if (url.searchParams.has(param)) {
        newParams.set(param, url.searchParams.get(param));
      }
    });

    url.search = newParams.toString();
  }

  return url.toString();
}

/**
 * Check if update is available for PWA
 */
export function checkForUpdate() {
  if ('serviceWorker' in navigator) {
    return navigator.serviceWorker.getRegistration().then((registration) => {
      if (registration) {
        return registration.update().then(() => {
          return registration.waiting !== null;
        });
      }
      return false;
    });
  }

  return Promise.resolve(false);
}

/**
 * Apply pending PWA update
 */
export function applyUpdate() {
  if ('serviceWorker' in navigator) {
    return navigator.serviceWorker.getRegistration().then((registration) => {
      if (registration && registration.waiting) {
        // Send message to waiting service worker to skip waiting
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });

        // Reload page after service worker activates
        return new Promise((resolve) => {
          navigator.serviceWorker.addEventListener('controllerchange', () => {
            window.location.reload();
            resolve();
          });
        });
      }
    });
  }

  return Promise.resolve();
}

/**
 * Show platform-specific install instructions
 */
export function getInstallInstructions() {
  if (isIOS()) {
    return {
      platform: 'iOS',
      steps: [
      'Tap the Share button in Safari',
      'Scroll down and tap "Add to Home Screen"',
      'Tap "Add" to install the app'],

      icon: '⬆️'
    };
  }

  if (isAndroid()) {
    return {
      platform: 'Android',
      steps: [
      'Tap the menu button (three dots)',
      'Select "Add to Home screen"',
      'Tap "Add" to install the app'],

      icon: '📱'
    };
  }

  return {
    platform: 'Desktop',
    steps: [
    'Look for the install icon in the address bar',
    'Click it and select "Install"',
    'The app will be added to your desktop'],

    icon: '💻'
  };
}

/**
 * Track PWA usage analytics
 */
export function trackPWAEvent(eventName, properties = {}) {
  const eventData = {
    event: eventName,
    timestamp: new Date().toISOString(),
    isPWA: isPWA(),
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    displayMode: window.matchMedia('(display-mode: standalone)').matches ? 'standalone' : 'browser',
    ...properties
  };

  // Send to analytics service or store locally
  if (navigator.onLine) {
    // Send immediately if online
    fetch('/api/analytics/pwa', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(eventData)
    }).catch(console.error);
  } else {
    // Store for later sync if offline
    const events = JSON.parse(localStorage.getItem('pwa-analytics') || '[]');
    events.push(eventData);
    localStorage.setItem('pwa-analytics', JSON.stringify(events));
  }
}

/**
 * Sync offline PWA analytics when back online
 */
export function syncPWAAnalytics() {
  const events = JSON.parse(localStorage.getItem('pwa-analytics') || '[]');

  if (events.length === 0) {
    return Promise.resolve();
  }

  return fetch('/api/analytics/pwa/bulk', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ events })
  }).then(() => {
    localStorage.removeItem('pwa-analytics');
  }).catch((error) => {
    console.error('Failed to sync PWA analytics:', error);
  });
}

export default {
  isPWA,
  isMobile,
  isIOS,
  isAndroid,
  getInstallPromptStrategy,
  getPWASupport,
  getConnectionInfo,
  shouldUseOfflineFirst,
  getCacheStrategy,
  getAppShellResources,
  getCriticalResources,
  calculateCacheLimit,
  shouldCache,
  generateCacheKey,
  checkForUpdate,
  applyUpdate,
  getInstallInstructions,
  trackPWAEvent,
  syncPWAAnalytics
};