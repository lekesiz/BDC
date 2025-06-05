import { useState, useEffect, useCallback } from 'react';
import { pwaService } from '../services/pwa.service';
/**
 * Main PWA hook providing comprehensive PWA functionality
 */
export function usePWA() {
  // Always assume online in development to avoid false offline warnings
  const [isOnline, setIsOnline] = useState(import.meta.env.DEV ? true : navigator.onLine);
  const [canInstall, setCanInstall] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [hasUpdate, setHasUpdate] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [syncStatus, setSyncStatus] = useState({
    pending: 0,
    syncing: false,
    lastSync: null
  });
  useEffect(() => {
    // Initialize PWA state
    setIsInstalled(pwaService.isInstalled());
    setCanInstall(pwaService.canInstall());
    setHasUpdate(pwaService.hasUpdate());
    // Setup event listeners
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => {
      // Don't show offline in development mode
      if (!import.meta.env.DEV) {
        setIsOnline(false);
      }
    };
    const handleInstallAvailable = () => setCanInstall(true);
    const handleAppInstalled = () => {
      setCanInstall(false);
      setIsInstalled(true);
    };
    const handleUpdateAvailable = () => setHasUpdate(true);
    const handleSyncSuccess = () => {
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        lastSync: new Date()
      }));
    };
    pwaService.on('online', handleOnline);
    pwaService.on('offline', handleOffline);
    pwaService.on('installAvailable', handleInstallAvailable);
    pwaService.on('appInstalled', handleAppInstalled);
    pwaService.on('updateAvailable', handleUpdateAvailable);
    pwaService.on('syncSuccess', handleSyncSuccess);
    return () => {
      pwaService.off('online', handleOnline);
      pwaService.off('offline', handleOffline);
      pwaService.off('installAvailable', handleInstallAvailable);
      pwaService.off('appInstalled', handleAppInstalled);
      pwaService.off('updateAvailable', handleUpdateAvailable);
      pwaService.off('syncSuccess', handleSyncSuccess);
    };
  }, []);
  const install = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      await pwaService.promptInstall();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);
  const update = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      await pwaService.applyUpdate();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);
  const syncData = useCallback(async (tag, data) => {
    try {
      setSyncStatus(prev => ({ ...prev, syncing: true }));
      await pwaService.syncData(tag, data);
    } catch (err) {
      setError(err.message);
      setSyncStatus(prev => ({ ...prev, syncing: false }));
    }
  }, []);
  return {
    isOnline,
    canInstall,
    isInstalled,
    hasUpdate,
    isLoading,
    error,
    syncStatus,
    install,
    update,
    syncData,
    clearError: () => setError(null)
  };
}
/**
 * Hook for managing app installation
 */
export function useInstallPrompt() {
  const [canInstall, setCanInstall] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  useEffect(() => {
    setCanInstall(pwaService.canInstall());
    setIsInstalled(pwaService.isInstalled());
    const handleInstallAvailable = () => setCanInstall(true);
    const handleAppInstalled = () => {
      setCanInstall(false);
      setIsInstalled(true);
    };
    pwaService.on('installAvailable', handleInstallAvailable);
    pwaService.on('appInstalled', handleAppInstalled);
    return () => {
      pwaService.off('installAvailable', handleInstallAvailable);
      pwaService.off('appInstalled', handleAppInstalled);
    };
  }, []);
  const promptInstall = useCallback(async () => {
    try {
      setIsLoading(true);
      await pwaService.promptInstall();
    } catch (error) {
      console.error('Install failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);
  return {
    canInstall,
    isInstalled,
    isLoading,
    promptInstall
  };
}
/**
 * Hook for managing app updates
 */
export function useAppUpdate() {
  const [hasUpdate, setHasUpdate] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  useEffect(() => {
    setHasUpdate(pwaService.hasUpdate());
    const handleUpdateAvailable = () => setHasUpdate(true);
    pwaService.on('updateAvailable', handleUpdateAvailable);
    return () => {
      pwaService.off('updateAvailable', handleUpdateAvailable);
    };
  }, []);
  const applyUpdate = useCallback(async () => {
    try {
      setIsUpdating(true);
      await pwaService.applyUpdate();
    } catch (error) {
      console.error('Update failed:', error);
    } finally {
      setIsUpdating(false);
    }
  }, []);
  return {
    hasUpdate,
    isUpdating,
    applyUpdate
  };
}
/**
 * Hook for monitoring online/offline status
 */
export function useOnlineStatus() {
  // Always assume online in development to avoid false offline warnings
  const [isOnline, setIsOnline] = useState(import.meta.env.DEV ? true : navigator.onLine);
  const [connectionInfo, setConnectionInfo] = useState(null);
  useEffect(() => {
    const updateConnectionInfo = () => {
      setConnectionInfo(pwaService.getConnectionStatus());
    };
    const handleOnline = () => {
      setIsOnline(true);
      updateConnectionInfo();
    };
    const handleOffline = () => {
      // Don't show offline in development mode
      if (!import.meta.env.DEV) {
        setIsOnline(false);
      }
      updateConnectionInfo();
    };
    updateConnectionInfo();
    pwaService.on('online', handleOnline);
    pwaService.on('offline', handleOffline);
    return () => {
      pwaService.off('online', handleOnline);
      pwaService.off('offline', handleOffline);
    };
  }, []);
  return {
    isOnline,
    connectionInfo
  };
}
/**
 * Hook for managing background sync
 */
export function useBackgroundSync() {
  const [syncQueue, setSyncQueue] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);
  const addToSyncQueue = useCallback(async (tag, data) => {
    try {
      await pwaService.syncData(tag, data);
      setSyncQueue(prev => [...prev, { tag, data, timestamp: Date.now() }]);
    } catch (error) {
      console.error('Failed to queue sync:', error);
    }
  }, []);
  const clearSyncQueue = useCallback(() => {
    setSyncQueue([]);
  }, []);
  useEffect(() => {
    const handleSyncSuccess = (data) => {
      setLastSync(new Date());
      setSyncQueue(prev => prev.filter(item => item.tag !== data.tag));
    };
    const handleSyncStart = () => setIsSyncing(true);
    const handleSyncEnd = () => setIsSyncing(false);
    pwaService.on('syncSuccess', handleSyncSuccess);
    pwaService.on('syncStart', handleSyncStart);
    pwaService.on('syncEnd', handleSyncEnd);
    return () => {
      pwaService.off('syncSuccess', handleSyncSuccess);
      pwaService.off('syncStart', handleSyncStart);
      pwaService.off('syncEnd', handleSyncEnd);
    };
  }, []);
  return {
    syncQueue,
    isSyncing,
    lastSync,
    addToSyncQueue,
    clearSyncQueue
  };
}
/**
 * Hook for managing push notifications
 */
export function usePushNotifications() {
  const [permission, setPermission] = useState(Notification.permission);
  const [subscription, setSubscription] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const requestPermission = useCallback(async () => {
    try {
      setIsLoading(true);
      const result = await pwaService.requestNotificationPermission();
      setPermission(result);
      return result;
    } catch (error) {
      console.error('Permission request failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  const subscribe = useCallback(async () => {
    try {
      setIsLoading(true);
      const sub = await pwaService.subscribeToPush();
      setSubscription(sub);
      return sub;
    } catch (error) {
      console.error('Push subscription failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return {
    permission,
    subscription,
    isLoading,
    requestPermission,
    subscribe,
    isSupported: 'Notification' in window
  };
}
/**
 * Hook for managing storage and cache
 */
export function useStorageManager() {
  const [storageEstimate, setStorageEstimate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const getStorageEstimate = useCallback(async () => {
    try {
      setIsLoading(true);
      const estimate = await pwaService.getStorageEstimate();
      setStorageEstimate(estimate);
      return estimate;
    } catch (error) {
      console.error('Storage estimate failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);
  const clearCache = useCallback(async (cacheName) => {
    try {
      setIsLoading(true);
      await pwaService.clearCache(cacheName);
      await getStorageEstimate(); // Refresh estimate
    } catch (error) {
      console.error('Cache clear failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [getStorageEstimate]);
  useEffect(() => {
    getStorageEstimate();
  }, [getStorageEstimate]);
  return {
    storageEstimate,
    isLoading,
    getStorageEstimate,
    clearCache
  };
}