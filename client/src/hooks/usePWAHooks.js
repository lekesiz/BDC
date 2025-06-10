// TODO: i18n - processed
import { useState, useEffect, useCallback } from 'react';
import { usePWA as usePWAContext } from '../providers/PWAProvider';

/**
 * Re-export the main PWA hook from the provider
 */
export { usePWA } from '../providers/PWAProvider';

/**
 * Hook for managing push notifications
 */
export function usePushNotifications() {
  const [permission, setPermission] = useState(Notification.permission);
  const [subscription, setSubscription] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { swRegistration, supportsPushManager } = usePWAContext();

  const isSupported = 'Notification' in window && supportsPushManager;

  const requestPermission = useCallback(async () => {
    if (!isSupported) {
      throw new Error('Push notifications not supported');
    }

    setIsLoading(true);
    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result;
    } finally {
      setIsLoading(false);
    }
  }, [isSupported]);

  const subscribe = useCallback(async () => {
    if (!swRegistration || permission !== 'granted') {
      throw new Error('Cannot subscribe: no registration or permission denied');
    }

    setIsLoading(true);
    try {
      // This would typically use your VAPID public key
      const subscription = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: 'YOUR_VAPID_PUBLIC_KEY' // Replace with actual key
      });

      setSubscription(subscription);
      
      // Send subscription to your server
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscription),
      });

      return subscription;
    } finally {
      setIsLoading(false);
    }
  }, [swRegistration, permission]);

  const unsubscribe = useCallback(async () => {
    if (!subscription) return;

    setIsLoading(true);
    try {
      await subscription.unsubscribe();
      setSubscription(null);
      
      // Notify server of unsubscription
      await fetch('/api/push/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      });
    } finally {
      setIsLoading(false);
    }
  }, [subscription]);

  useEffect(() => {
    if (swRegistration) {
      swRegistration.pushManager.getSubscription().then(setSubscription);
    }
  }, [swRegistration]);

  return {
    permission,
    subscription,
    isLoading,
    isSupported,
    requestPermission,
    subscribe,
    unsubscribe
  };
}

/**
 * Hook for managing background sync
 */
export function useBackgroundSync() {
  const [syncQueue, setSyncQueue] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);
  const { swRegistration, supportsBackgroundSync } = usePWAContext();

  const addToSyncQueue = useCallback(async (tag, data) => {
    if (!supportsBackgroundSync) {
      throw new Error('Background sync not supported');
    }

    const queueItem = {
      id: Date.now().toString(),
      tag,
      data,
      timestamp: Date.now()
    };

    setSyncQueue(prev => [...prev, queueItem]);

    if (swRegistration) {
      try {
        await swRegistration.sync.register(tag);
      } catch (error) {
        console.error('Failed to register background sync:', error);
      }
    }

    return queueItem.id;
  }, [swRegistration, supportsBackgroundSync]);

  const clearSyncQueue = useCallback(() => {
    setSyncQueue([]);
  }, []);

  return {
    syncQueue,
    isSyncing,
    lastSync,
    addToSyncQueue,
    clearSyncQueue,
    isSupported: supportsBackgroundSync
  };
}

/**
 * Hook for managing online/offline status
 */
export function useOnlineStatus() {
  const { isOnline, wasOffline } = usePWAContext();
  const [connectionInfo, setConnectionInfo] = useState(null);

  useEffect(() => {
    if ('connection' in navigator) {
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      setConnectionInfo({
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData
      });

      const handleConnectionChange = () => {
        setConnectionInfo({
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData
        });
      };

      connection.addEventListener('change', handleConnectionChange);
      return () => connection.removeEventListener('change', handleConnectionChange);
    }
  }, []);

  return {
    isOnline,
    wasOffline,
    connectionInfo
  };
}

/**
 * Hook for managing storage
 */
export function useStorageManager() {
  const { storageUsage, storageQuota, clearAllData, clearCache } = usePWAContext();
  const [isLoading, setIsLoading] = useState(false);

  const getStorageEstimate = useCallback(async () => {
    setIsLoading(true);
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        return estimate;
      }
      return null;
    } catch (error) {
      console.error('Storage estimate error:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    storageEstimate: { usage: storageUsage, quota: storageQuota },
    isLoading,
    getStorageEstimate,
    clearCache,
    clearAllData
  };
}

export default {
  usePWA,
  usePushNotifications,
  useBackgroundSync,
  useOnlineStatus,
  useStorageManager
};