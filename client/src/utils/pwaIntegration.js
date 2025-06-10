// TODO: i18n - processed
// PWA Integration Utilities
// Comprehensive integration guide and utilities for BDC PWA
import { pwaService } from '../services/pwa.service';
import { PWAOptimizations } from './pwaOptimizations';
/**
 * PWA Integration Manager
 * Centralizes all PWA functionality for easy integration
 */import { useTranslation } from "react-i18next";
export class PWAIntegration {
  constructor() {
    this.isInitialized = false;
    this.features = {
      serviceWorker: false,
      manifest: false,
      offlineSupport: false,
      pushNotifications: false,
      installPrompt: false,
      backgroundSync: false
    };
  }
  /**
   * Initialize all PWA features
   */
  async initialize() {
    if (this.isInitialized) return;
    try {
      // 1. Initialize service worker
      await this.initializeServiceWorker();
      // 2. Setup offline support
      this.setupOfflineSupport();
      // 3. Initialize performance optimizations
      await this.initializePerformanceOptimizations();
      // 4. Setup push notifications
      await this.initializePushNotifications();
      // 5. Setup installation prompt
      this.setupInstallationPrompt();
      // 6. Initialize background sync
      this.initializeBackgroundSync();
      this.isInitialized = true;
      // Dispatch initialization event
      window.dispatchEvent(new CustomEvent('pwa-initialized', {
        detail: { features: this.features }
      }));
    } catch (error) {
      console.error('❌ PWA initialization failed:', error);
    }
  }
  /**
   * Initialize Service Worker
   */
  async initializeServiceWorker() {
    try {
      if ('serviceWorker' in navigator) {
        await pwaService.registerServiceWorker();
        this.features.serviceWorker = true;
      }
    } catch (error) {
      console.error('❌ Service Worker initialization failed:', error);
    }
  }
  /**
   * Setup offline support
   */
  setupOfflineSupport() {
    try {
      // Listen for online/offline events
      window.addEventListener('online', this.handleOnline.bind(this));
      window.addEventListener('offline', this.handleOffline.bind(this));
      this.features.offlineSupport = true;
    } catch (error) {
      console.error('❌ Offline support setup failed:', error);
    }
  }
  /**
   * Initialize performance optimizations
   */
  async initializePerformanceOptimizations() {
    try {
      // Preload critical resources
      await PWAOptimizations.preloadCritical();
    } catch (error) {
      console.error('❌ Performance optimization failed:', error);
    }
  }
  /**
   * Initialize push notifications
   */
  async initializePushNotifications() {
    try {
      if ('Notification' in window && 'serviceWorker' in navigator) {
        // Check if already granted
        if (Notification.permission === 'granted') {
          await this.setupPushSubscription();
        }
        this.features.pushNotifications = true;
      }
    } catch (error) {
      console.error('❌ Push notifications initialization failed:', error);
    }
  }
  /**
   * Setup installation prompt
   */
  setupInstallationPrompt() {
    try {
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        this.features.installPrompt = true;
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('pwa-install-available', {
          detail: { prompt: e }
        }));
      });
      window.addEventListener('appinstalled', () => {
        // Track installation
        this.trackInstallation();
      });
    } catch (error) {
      console.error('❌ Installation prompt setup failed:', error);
    }
  }
  /**
   * Initialize background sync
   */
  initializeBackgroundSync() {
    try {
      if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
        this.features.backgroundSync = true;
      }
    } catch (error) {
      console.error('❌ Background sync initialization failed:', error);
    }
  }
  /**
   * Setup push subscription
   */
  async setupPushSubscription() {
    try {
      const subscription = await pwaService.subscribeToPush();
      // Send subscription to server
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('❌ Push subscription setup failed:', error);
    }
  }
  /**
   * Handle online event
   */
  handleOnline() {
    // Trigger sync of pending data
    pwaService.syncPendingData();
    // Dispatch event
    window.dispatchEvent(new CustomEvent('pwa-online'));
  }
  /**
   * Handle offline event
   */
  handleOffline() {
    // Dispatch event
    window.dispatchEvent(new CustomEvent('pwa-offline'));
  }
  /**
   * Track PWA installation
   */
  trackInstallation() {
    try {
      // Analytics tracking
      if (window.gtag) {
        window.gtag('event', 'pwa_install', {
          event_category: 'engagement',
          event_label: 'PWA Installation'
        });
      }
      // Local storage tracking
      localStorage.setItem('pwa-installed', JSON.stringify({
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      }));
    } catch (error) {
      console.error('Failed to track installation:', error);
    }
  }
  /**
   * Get PWA capabilities
   */
  getCapabilities() {
    return {
      serviceWorker: 'serviceWorker' in navigator,
      pushNotifications: 'Notification' in window && 'serviceWorker' in navigator,
      backgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
      installable: 'beforeinstallprompt' in window,
      standalone: window.matchMedia('(display-mode: standalone)').matches,
      fullscreen: window.matchMedia('(display-mode: fullscreen)').matches
    };
  }
  /**
   * Check if PWA is installed
   */
  isInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true ||
    localStorage.getItem('pwa-installed') !== null;
  }
  /**
   * Get PWA metrics
   */
  getMetrics() {
    return {
      features: this.features,
      capabilities: this.getCapabilities(),
      installed: this.isInstalled(),
      performance: PWAOptimizations.getPerformanceInfo(),
      storage: pwaService.getStorageEstimate()
    };
  }
}
/**
 * PWA React Integration Hooks
 */
export const PWAReactIntegration = {
  /**
   * Initialize PWA in React app
   */
  async initializeInReact(App) {
    const pwaIntegration = new PWAIntegration();
    // Initialize PWA after React app mounts
    window.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        pwaIntegration.initialize();
      }, 1000); // Delay to allow React to fully mount
    });
    return pwaIntegration;
  },
  /**
   * Create PWA-aware route configuration
   */
  createPWARoutes(routes) {
    return routes.map((route) => ({
      ...route,
      component: PWAOptimizations.codeSplitter.importModule(route.component),
      preload: () => PWAOptimizations.resourcePreloader.preloadRoute(route.path)
    }));
  },
  /**
   * Wrap components with PWA optimizations
   */
  withPWAOptimizations(Component) {
    return function PWAOptimizedComponent(props) {
      React.useEffect(() => {
        // Preload component dependencies
        const route = window.location.pathname;
        PWAOptimizations.resourcePreloader.preloadRoute(route);
      }, []);
      return React.createElement(Component, props);
    };
  }
};
/**
 * PWA Configuration
 */
export const PWAConfig = {
  // Cache strategies
  cacheStrategies: {
    static: 'cache-first',
    api: 'network-first',
    images: 'cache-first',
    runtime: 'stale-while-revalidate'
  },
  // Notification settings
  notifications: {
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    requireInteraction: false,
    silent: false
  },
  // Install prompt settings
  installPrompt: {
    delay: 5000, // 5 seconds
    maxPrompts: 3,
    daysBetweenPrompts: 7
  },
  // Performance settings
  performance: {
    preloadDelay: 100,
    lazyLoadThreshold: 0.1,
    imageOptimization: true,
    codeSplitting: true
  }
};
/**
 * PWA Development Tools
 */
export const PWADevTools = {
  /**
   * Debug PWA state
   */
  debug() {
    const integration = new PWAIntegration();
    const metrics = integration.getMetrics();
    console.group('🔧 PWA Debug Information');
    console.groupEnd();
    return metrics;
  },
  /**
   * Test PWA features
   */
  async test() {
    console.group('🧪 PWA Feature Tests');
    // Test service worker
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.getRegistration();
    } else {}
    // Test push notifications
    if ('Notification' in window) {} else {}
    // Test background sync
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {} else {}
    console.groupEnd();
  },
  /**
   * Simulate offline mode
   */
  simulateOffline() {
    window.dispatchEvent(new Event('offline'));
  },
  /**
   * Simulate online mode
   */
  simulateOnline() {
    window.dispatchEvent(new Event('online'));
  }
};
// Export singleton instance
export const pwaIntegration = new PWAIntegration();
// Auto-initialize if in browser
if (typeof window !== 'undefined') {
  // Initialize after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      pwaIntegration.initialize();
    });
  } else {
    pwaIntegration.initialize();
  }
}
export default pwaIntegration;