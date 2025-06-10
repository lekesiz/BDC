// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // PWA Service - Comprehensive Progressive Web App functionality
class PWAService {
  constructor() {
    this.swRegistration = null;
    // Always assume online in development mode
    this.isOnline = import.meta.env.DEV ? true : navigator.onLine;
    this.installPrompt = null;
    this.updateAvailable = false;
    this.listeners = new Map();
    this.init();
  }
  async init() {
    // Register service worker
    await this.registerServiceWorker();
    // Setup event listeners
    this.setupEventListeners();
    // Setup installation prompt
    this.setupInstallPrompt();
    // Setup update detection
    this.setupUpdateDetection();
    // Setup background sync
    this.setupBackgroundSync();
  }
  // Service Worker Registration
  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      return;
    }

    // Skip service worker in development mode to avoid errors
    if (import.meta.env.DEV) {
      console.info('Service Worker is disabled in development mode');
      return;
    }

    try {
      this.swRegistration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        this.handleServiceWorkerMessage(event);
      });
      // Handle service worker updates
      this.swRegistration.addEventListener('updatefound', () => {
        this.handleServiceWorkerUpdate();
      });
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  }
  // Event Listeners Setup
  setupEventListeners() {
    // Online/Offline detection
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.emit('online', { isOnline: true });
      this.syncPendingData();
    });
    window.addEventListener('offline', () => {
      // Don't trigger offline in development mode
      if (!import.meta.env.DEV) {
        this.isOnline = false;
        this.emit('offline', { isOnline: false });
      }
    });
    // Visibility change for background sync
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isOnline) {
        this.syncPendingData();
      }
    });
  }
  // Installation Prompt Setup
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault();
      this.installPrompt = event;
      this.emit('installAvailable', { canInstall: true });
    });
    window.addEventListener('appinstalled', () => {
      this.installPrompt = null;
      this.emit('appInstalled', { installed: true });
    });
  }
  // Update Detection Setup
  setupUpdateDetection() {
    if (this.swRegistration) {
      // Check for updates every 10 minutes
      setInterval(() => {
        this.swRegistration.update();
      }, 10 * 60 * 1000);
    }
  }
  // Background Sync Setup
  setupBackgroundSync() {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {}
  }
  // Service Worker Message Handler
  handleServiceWorkerMessage(event) {
    const { type, payload } = event.data;
    switch (type) {
      case 'SW_UPDATED':
        this.updateAvailable = true;
        this.emit('updateAvailable', payload);
        break;
      case 'SYNC_SUCCESS':
        this.emit('syncSuccess', payload);
        break;
      case 'SYNC_FAILED':
        this.emit('syncFailed', payload);
        break;
      case 'CACHE_UPDATED':
        this.emit('cacheUpdated', payload);
        break;
      default:
    }
  }
  // Service Worker Update Handler
  handleServiceWorkerUpdate() {
    const newWorker = this.swRegistration.installing;
    newWorker.addEventListener('statechange', () => {
      if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
        this.updateAvailable = true;
        this.emit('updateAvailable', {
          version: 'new version available',
          worker: newWorker
        });
      }
    });
  }
  // Installation Methods
  async promptInstall() {
    if (!this.installPrompt) {
      throw new Error('Install prompt not available');
    }
    const result = await this.installPrompt.prompt();
    this.installPrompt = null;
    return result;
  }
  canInstall() {
    return !!this.installPrompt;
  }
  isInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;
  }
  // Update Methods
  async applyUpdate() {
    if (!this.updateAvailable) {
      throw new Error('No update available');
    }
    await this.sendMessageToSW('SKIP_WAITING');
    window.location.reload();
  }
  hasUpdate() {
    return this.updateAvailable;
  }
  // Caching Methods
  async cacheUrls(urls) {
    return this.sendMessageToSW('CACHE_URLS', { urls });
  }
  async clearCache(cacheName) {
    return this.sendMessageToSW('CLEAR_CACHE', { cacheName });
  }
  // Background Sync Methods
  async syncData(tag, data) {
    if (!('serviceWorker' in navigator) || !this.swRegistration) {
      throw new Error('Service Worker not available for sync');
    }
    // Store data locally first
    await this.storeOfflineData(tag, data);
    // Register background sync
    try {
      await this.swRegistration.sync.register(tag);
    } catch (error) {}
  }
  async syncPendingData() {
    const pendingSync = await this.getPendingSync();
    for (const [tag, data] of Object.entries(pendingSync)) {
      try {
        await this.syncData(tag, data);
      } catch (error) {}
    }
  }
  // Offline Data Management
  async storeOfflineData(key, data) {
    const storageKey = `pwa_offline_${key}`;
    const offlineData = {
      timestamp: Date.now(),
      data: data,
      synced: false
    };
    try {
      localStorage.setItem(storageKey, JSON.stringify(offlineData));
    } catch (error) {
      console.error('Failed to store offline data:', error);
    }
  }
  async getOfflineData(key) {
    const storageKey = `pwa_offline_${key}`;
    try {
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Failed to get offline data:', error);
      return null;
    }
  }
  async removeOfflineData(key) {
    const storageKey = `pwa_offline_${key}`;
    localStorage.removeItem(storageKey);
  }
  async getPendingSync() {
    const pending = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('pwa_offline_')) {
        const tag = key.replace('pwa_offline_', '');
        const data = await this.getOfflineData(tag);
        if (data && !data.synced) {
          pending[tag] = data.data;
        }
      }
    }
    return pending;
  }
  // Push Notifications
  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      throw new Error('Notifications not supported');
    }
    const permission = await Notification.requestPermission();
    return permission;
  }
  async subscribeToPush() {
    if (!this.swRegistration) {
      throw new Error('Service Worker not registered');
    }
    const permission = await this.requestNotificationPermission();
    if (permission !== 'granted') {
      throw new Error('Notification permission denied');
    }
    try {
      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.getVapidPublicKey()
      });
      return subscription;
    } catch (error) {
      console.error('Push subscription failed:', error);
      throw error;
    }
  }
  getVapidPublicKey() {
    // Replace with your actual VAPID public key
    return 'YOUR_VAPID_PUBLIC_KEY';
  }
  // Utility Methods
  async sendMessageToSW(type, payload = {}) {
    if (!navigator.serviceWorker.controller) {
      throw new Error('No service worker controller');
    }
    return new Promise((resolve, reject) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        if (event.data.error) {
          reject(new Error(event.data.error));
        } else {
          resolve(event.data);
        }
      };
      navigator.serviceWorker.controller.postMessage(
        { type, payload },
        [messageChannel.port2]
      );
    });
  }
  getConnectionStatus() {
    return {
      isOnline: this.isOnline,
      effectiveType: navigator.connection?.effectiveType,
      downlink: navigator.connection?.downlink,
      rtt: navigator.connection?.rtt
    };
  }
  async getStorageEstimate() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      return await navigator.storage.estimate();
    }
    return null;
  }
  // Event System
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in PWA event listener:', error);
        }
      });
    }
  }
}
// Export singleton instance
export const pwaService = new PWAService();
export default pwaService;