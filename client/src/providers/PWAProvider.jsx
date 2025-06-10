// TODO: i18n - processed
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useToast } from '../components/ui/use-toast';
import { offlineFirstManager } from '../utils/offlineFirst';
import { indexedDBManager } from '../services/indexeddb.service';

/**
 * PWA Provider Context
 * Comprehensive Progressive Web App integration and management
 */
const PWAContext = createContext({
  // App install
  isInstallable: false,
  isInstalled: false,
  installApp: () => {},
  dismissInstall: () => {},
  
  // Service Worker
  swRegistration: null,
  swUpdate: null,
  updateAvailable: false,
  updateApp: () => {},
  skipWaiting: () => {},
  
  // Offline status
  isOnline: true,
  wasOffline: false,
  
  // PWA features
  supportsNotifications: false,
  supportsServiceWorker: false,
  supportsInstall: false,
  supportsPushManager: false,
  supportsBackgroundSync: false,
  
  // Storage
  storageUsage: null,
  storageQuota: null,
  clearAllData: () => {},
  
  // Performance
  performanceMetrics: {},
  
  // Cache management
  cacheStatus: 'unknown',
  updateCache: () => {},
  clearCache: () => {}
});

/**
 * PWA Provider Component
 */
export function PWAProvider({ children }) {
  const { t } = useTranslation();
  const { toast } = useToast();
  
  // State management
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [installPrompt, setInstallPrompt] = useState(null);
  const [swRegistration, setSwRegistration] = useState(null);
  const [swUpdate, setSwUpdate] = useState(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);
  const [storageUsage, setStorageUsage] = useState(null);
  const [storageQuota, setStorageQuota] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [cacheStatus, setCacheStatus] = useState('unknown');

  // Feature detection
  const supportsNotifications = 'Notification' in window;
  const supportsServiceWorker = 'serviceWorker' in navigator;
  const supportsInstall = 'BeforeInstallPromptEvent' in window;
  const supportsPushManager = 'PushManager' in window;
  const supportsBackgroundSync = 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype;

  /**
   * Initialize PWA features
   */
  useEffect(() => {
    initializePWA();
    setupEventListeners();
    initializeOfflineFirst();
    
    return () => {
      cleanupEventListeners();
    };
  }, []);

  /**
   * Initialize PWA core features
   */
  const initializePWA = async () => {
    try {
      // Check if app is already installed
      const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;
      const isIOSStandalone = window.navigator.standalone === true;
      setIsInstalled(isStandaloneMode || isIOSStandalone);

      // Register service worker
      if (supportsServiceWorker) {
        await registerServiceWorker();
      }

      // Get storage information
      await updateStorageInfo();

      // Initialize performance monitoring
      initializePerformanceMonitoring();

      console.log('[PWA] Initialization completed');
    } catch (error) {
      console.error('[PWA] Initialization error:', error);
    }
  };

  /**
   * Register service worker
   */
  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
        updateViaCache: 'none'
      });

      setSwRegistration(registration);
      setCacheStatus('active');

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            setSwUpdate(newWorker);
            setUpdateAvailable(true);
            
            toast({
              title: t('pwa.update_available'),
              description: t('pwa.update_available_description'),
              action: {
                label: t('pwa.update_now'),
                onClick: () => updateApp()
              }
            });
          }
        });
      });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);

      console.log('[PWA] Service Worker registered');
    } catch (error) {
      console.error('[PWA] Service Worker registration failed:', error);
      setCacheStatus('failed');
    }
  };

  /**
   * Handle messages from service worker
   */
  const handleServiceWorkerMessage = useCallback((event) => {
    const { type, payload } = event.data;

    switch (type) {
      case 'CACHE_UPDATED':
        setCacheStatus('updated');
        break;
      case 'OFFLINE_PAGE_READY':
        console.log('[PWA] Offline page cached and ready');
        break;
      case 'PERFORMANCE_METRICS':
        setPerformanceMetrics(payload);
        break;
      default:
        console.log('[PWA] Unknown message from SW:', type);
    }
  }, []);

  /**
   * Setup event listeners
   */
  const setupEventListeners = () => {
    // Install prompt
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    
    // App installed
    window.addEventListener('appinstalled', handleAppInstalled);
    
    // Online/offline status
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Visibility change for performance monitoring
    document.addEventListener('visibilitychange', handleVisibilityChange);
  };

  /**
   * Cleanup event listeners
   */
  const cleanupEventListeners = () => {
    window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.removeEventListener('appinstalled', handleAppInstalled);
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    
    if (navigator.serviceWorker) {
      navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
    }
  };

  /**
   * Handle before install prompt
   */
  const handleBeforeInstallPrompt = (event) => {
    event.preventDefault();
    setInstallPrompt(event);
    setIsInstallable(true);
    
    // Show install banner after a delay
    setTimeout(() => {
      if (!isInstalled) {
        toast({
          title: t('pwa.install_available'),
          description: t('pwa.install_available_description'),
          action: {
            label: t('pwa.install_now'),
            onClick: () => installApp()
          },
          duration: 10000
        });
      }
    }, 5000);
  };

  /**
   * Handle app installed
   */
  const handleAppInstalled = () => {
    setIsInstalled(true);
    setIsInstallable(false);
    setInstallPrompt(null);
    
    toast({
      title: t('pwa.app_installed'),
      description: t('pwa.app_installed_description')
    });
  };

  /**
   * Handle online status
   */
  const handleOnline = () => {
    setIsOnline(true);
    
    if (wasOffline) {
      setWasOffline(false);
      toast({
        title: t('pwa.back_online'),
        description: t('pwa.back_online_description')
      });
      
      // Trigger sync when back online
      if (offlineFirstManager) {
        offlineFirstManager.syncAll().catch(console.error);
      }
    }
  };

  /**
   * Handle offline status
   */
  const handleOffline = () => {
    setIsOnline(false);
    setWasOffline(true);
    
    toast({
      title: t('pwa.offline_mode'),
      description: t('pwa.offline_mode_description'),
      variant: 'warning'
    });
  };

  /**
   * Handle visibility change for performance monitoring
   */
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      // App became visible, update metrics
      updateStorageInfo();
    }
  };

  /**
   * Install the app
   */
  const installApp = async () => {
    if (!installPrompt) return;

    try {
      const result = await installPrompt.prompt();
      
      if (result.outcome === 'accepted') {
        console.log('[PWA] App installation accepted');
      } else {
        console.log('[PWA] App installation dismissed');
      }
      
      setInstallPrompt(null);
      setIsInstallable(false);
    } catch (error) {
      console.error('[PWA] Install prompt error:', error);
    }
  };

  /**
   * Dismiss install prompt
   */
  const dismissInstall = () => {
    setIsInstallable(false);
    setInstallPrompt(null);
  };

  /**
   * Update the app
   */
  const updateApp = () => {
    if (swUpdate) {
      swUpdate.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  };

  /**
   * Skip waiting for service worker update
   */
  const skipWaiting = () => {
    if (swRegistration && swRegistration.waiting) {
      swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
  };

  /**
   * Update storage information
   */
  const updateStorageInfo = async () => {
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        setStorageUsage(estimate.usage);
        setStorageQuota(estimate.quota);
      }
    } catch (error) {
      console.error('[PWA] Storage estimate error:', error);
    }
  };

  /**
   * Clear all app data
   */
  const clearAllData = async () => {
    try {
      // Clear IndexedDB
      if (indexedDBManager) {
        await indexedDBManager.clearAllStores();
      }

      // Clear caches
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );

      // Clear local storage
      localStorage.clear();
      sessionStorage.clear();

      // Update storage info
      await updateStorageInfo();

      toast({
        title: t('pwa.data_cleared'),
        description: t('pwa.data_cleared_description')
      });

      console.log('[PWA] All data cleared');
    } catch (error) {
      console.error('[PWA] Clear data error:', error);
      toast({
        title: t('pwa.clear_data_error'),
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  /**
   * Update cache
   */
  const updateCache = async () => {
    try {
      if (swRegistration) {
        await swRegistration.update();
        setCacheStatus('updating');
        
        toast({
          title: t('pwa.cache_updating'),
          description: t('pwa.cache_updating_description')
        });
      }
    } catch (error) {
      console.error('[PWA] Cache update error:', error);
    }
  };

  /**
   * Clear cache
   */
  const clearCache = async () => {
    try {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );
      
      setCacheStatus('cleared');
      
      toast({
        title: t('pwa.cache_cleared'),
        description: t('pwa.cache_cleared_description')
      });
    } catch (error) {
      console.error('[PWA] Clear cache error:', error);
    }
  };

  /**
   * Initialize offline-first architecture
   */
  const initializeOfflineFirst = async () => {
    try {
      // Register offline-first stores
      offlineFirstManager.registerStore('beneficiaries', {
        syncEndpoint: '/api/beneficiaries',
        conflictResolution: 'server-wins'
      });

      offlineFirstManager.registerStore('evaluations', {
        syncEndpoint: '/api/evaluations',
        conflictResolution: 'manual'
      });

      offlineFirstManager.registerStore('documents', {
        syncEndpoint: '/api/documents',
        conflictResolution: 'client-wins'
      });

      offlineFirstManager.registerStore('calendar', {
        syncEndpoint: '/api/calendar',
        conflictResolution: 'merge'
      });

      // Initialize all stores
      await offlineFirstManager.init();

      console.log('[PWA] Offline-first stores initialized');
    } catch (error) {
      console.error('[PWA] Offline-first initialization error:', error);
    }
  };

  /**
   * Initialize performance monitoring
   */
  const initializePerformanceMonitoring = () => {
    // Monitor Core Web Vitals
    if ('web-vitals' in window) {
      // This would typically use the web-vitals library
      // For now, we'll simulate with basic performance metrics
    }

    // Basic performance monitoring
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'navigation') {
          setPerformanceMetrics(prev => ({
            ...prev,
            loadTime: entry.loadEventEnd - entry.loadEventStart,
            domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
            firstPaint: entry.responseStart - entry.requestStart
          }));
        }
      });
    });

    try {
      observer.observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint'] });
    } catch (error) {
      console.warn('[PWA] Performance observer not supported:', error);
    }
  };

  // Context value
  const contextValue = {
    // App install
    isInstallable,
    isInstalled,
    installApp,
    dismissInstall,
    
    // Service Worker
    swRegistration,
    swUpdate,
    updateAvailable,
    updateApp,
    skipWaiting,
    
    // Offline status
    isOnline,
    wasOffline,
    
    // PWA features
    supportsNotifications,
    supportsServiceWorker,
    supportsInstall,
    supportsPushManager,
    supportsBackgroundSync,
    
    // Storage
    storageUsage,
    storageQuota,
    clearAllData,
    
    // Performance
    performanceMetrics,
    
    // Cache management
    cacheStatus,
    updateCache,
    clearCache
  };

  return (
    <PWAContext.Provider value={contextValue}>
      {children}
    </PWAContext.Provider>
  );
}

/**
 * Hook to use PWA context
 */
export function usePWA() {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
}

/**
 * PWA Install Banner Component
 */
export function PWAInstallBanner() {
  const { t } = useTranslation();
  const { isInstallable, isInstalled, installApp, dismissInstall } = usePWA();

  if (!isInstallable || isInstalled) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 bg-blue-600 text-white p-4 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="font-semibold">{t('pwa.install_app')}</h4>
          <p className="text-sm opacity-90">{t('pwa.install_app_description')}</p>
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={installApp}
            className="bg-white text-blue-600 px-4 py-2 rounded font-medium hover:bg-gray-100 transition-colors"
          >
            {t('pwa.install')}
          </button>
          <button
            onClick={dismissInstall}
            className="text-white opacity-75 hover:opacity-100 transition-opacity"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * PWA Update Banner Component
 */
export function PWAUpdateBanner() {
  const { t } = useTranslation();
  const { updateAvailable, updateApp } = usePWA();

  if (!updateAvailable) {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 right-4 z-50 bg-green-600 text-white p-4 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="font-semibold">{t('pwa.update_available')}</h4>
          <p className="text-sm opacity-90">{t('pwa.update_available_description')}</p>
        </div>
        <button
          onClick={updateApp}
          className="bg-white text-green-600 px-4 py-2 rounded font-medium hover:bg-gray-100 transition-colors ml-4"
        >
          {t('pwa.update_now')}
        </button>
      </div>
    </div>
  );
}

/**
 * PWA Offline Banner Component
 */
export function PWAOfflineBanner() {
  const { t } = useTranslation();
  const { isOnline } = usePWA();

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 right-4 z-50 bg-yellow-600 text-white p-3 rounded-lg shadow-lg">
      <div className="flex items-center justify-center">
        <div className="text-center">
          <h4 className="font-semibold">{t('pwa.offline_mode')}</h4>
          <p className="text-sm opacity-90">{t('pwa.offline_mode_description')}</p>
        </div>
      </div>
    </div>
  );
}

export default PWAProvider;