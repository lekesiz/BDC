import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../lib/api';
import { toast } from 'react-hot-toast';
import { BellIcon, BellSlashIcon } from '@heroicons/react/24/outline';

// Firebase config (should be in environment variables)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
};

export default function PushNotificationRegistration() {
  const { t } = useTranslation();
  const [permission, setPermission] = useState('default');
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);

  useEffect(() => {
    // Check notification permission status
    if ('Notification' in window) {
      setPermission(Notification.permission);
      checkRegistrationStatus();
    }
  }, []);

  const checkRegistrationStatus = async () => {
    try {
      const response = await api.get('/api/push-notifications/devices');
      const devices = response.data.devices;
      
      // Check if current device is registered
      if ('serviceWorker' in navigator && devices.length > 0) {
        const registration = await navigator.serviceWorker.ready;
        if (registration.pushManager) {
          const subscription = await registration.pushManager.getSubscription();
          if (subscription) {
            setRegistered(true);
          }
        }
      }
    } catch (error) {
      console.error('Error checking registration status:', error);
    }
  };

  const requestPermission = async () => {
    if (!('Notification' in window)) {
      toast.error(t('pushNotifications.error.notSupported'));
      return;
    }

    if (Notification.permission === 'denied') {
      toast.error(t('pushNotifications.error.permissionDenied'));
      return;
    }

    setLoading(true);
    try {
      // Request notification permission
      const permission = await Notification.requestPermission();
      setPermission(permission);

      if (permission === 'granted') {
        // Initialize Firebase if available
        if (firebaseConfig.apiKey && window.firebase) {
          await initializeFirebaseMessaging();
        } else {
          // Use native web push
          await initializeWebPush();
        }
      } else {
        toast.error(t('pushNotifications.error.permissionDenied'));
      }
    } catch (error) {
      console.error('Error requesting permission:', error);
      toast.error(t('pushNotifications.error.registrationFailed'));
    } finally {
      setLoading(false);
    }
  };

  const initializeFirebaseMessaging = async () => {
    try {
      // Initialize Firebase
      if (!window.firebase.apps.length) {
        window.firebase.initializeApp(firebaseConfig);
      }

      const messaging = window.firebase.messaging();
      
      // Get FCM token
      const token = await messaging.getToken({ vapidKey: firebaseConfig.vapidKey });
      
      if (token) {
        // Register device with backend
        await registerDevice(token, 'fcm');
        
        // Handle token refresh
        messaging.onTokenRefresh(async () => {
          const newToken = await messaging.getToken({ vapidKey: firebaseConfig.vapidKey });
          if (newToken) {
            await registerDevice(newToken, 'fcm');
          }
        });

        // Handle foreground messages
        messaging.onMessage((payload) => {
          const { title, body, icon } = payload.notification;
          new Notification(title, { body, icon });
        });

        setRegistered(true);
        toast.success(t('pushNotifications.success.registered'));
      }
    } catch (error) {
      console.error('Firebase initialization error:', error);
      // Fallback to web push
      await initializeWebPush();
    }
  };

  const initializeWebPush = async () => {
    try {
      // Register service worker if not already registered
      let registration = await navigator.serviceWorker.getRegistration();
      if (!registration) {
        registration = await navigator.serviceWorker.register('/service-worker.js');
      }

      // Wait for service worker to be ready
      await navigator.serviceWorker.ready;

      // Get VAPID public key from backend
      const vapidResponse = await api.get('/api/push-notifications/vapid-public-key');
      const vapidPublicKey = vapidResponse.data.vapid_public_key;

      // Convert VAPID key
      const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey
      });

      // Register device with backend
      await registerDevice(JSON.stringify(subscription), 'webpush');

      setRegistered(true);
      toast.success(t('pushNotifications.success.registered'));
    } catch (error) {
      console.error('Web push initialization error:', error);
      throw error;
    }
  };

  const registerDevice = async (token, provider) => {
    try {
      const deviceInfo = {
        device_token: token,
        device_type: 'web',
        provider: provider,
        device_name: navigator.userAgent,
        app_version: import.meta.env.VITE_APP_VERSION || '1.0.0'
      };

      await api.post('/api/push-notifications/register', deviceInfo);
    } catch (error) {
      console.error('Device registration error:', error);
      throw error;
    }
  };

  const unregisterDevice = async () => {
    setLoading(true);
    try {
      // Get current subscription
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      
      if (subscription) {
        // Unsubscribe from push
        await subscription.unsubscribe();
        
        // Get device token
        let deviceToken;
        if (window.firebase && window.firebase.messaging) {
          const messaging = window.firebase.messaging();
          deviceToken = await messaging.getToken();
        } else {
          deviceToken = JSON.stringify(subscription);
        }

        // Unregister from backend
        await api.post('/api/push-notifications/unregister', {
          device_token: deviceToken
        });

        setRegistered(false);
        toast.success(t('pushNotifications.success.unregistered'));
      }
    } catch (error) {
      console.error('Unregister error:', error);
      toast.error(t('pushNotifications.error.unregisterFailed'));
    } finally {
      setLoading(false);
    }
  };

  // Convert VAPID key from base64 to Uint8Array
  const urlBase64ToUint8Array = (base64String) => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  };

  if (!('Notification' in window)) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">
          {t('pushNotifications.error.notSupported')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {registered ? (
            <BellIcon className="h-6 w-6 text-green-500" />
          ) : (
            <BellSlashIcon className="h-6 w-6 text-gray-400" />
          )}
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {t('pushNotifications.registration.title')}
            </h3>
            <p className="text-sm text-gray-500">
              {registered
                ? t('pushNotifications.registration.registered')
                : t('pushNotifications.registration.notRegistered')}
            </p>
          </div>
        </div>

        <div>
          {!registered ? (
            <button
              onClick={requestPermission}
              disabled={loading || permission === 'denied'}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('pushNotifications.registration.enabling')}
                </span>
              ) : (
                t('pushNotifications.registration.enable')
              )}
            </button>
          ) : (
            <button
              onClick={unregisterDevice}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('pushNotifications.registration.disabling')}
                </span>
              ) : (
                t('pushNotifications.registration.disable')
              )}
            </button>
          )}
        </div>
      </div>

      {permission === 'denied' && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            {t('pushNotifications.error.permissionDeniedHelp')}
          </p>
        </div>
      )}
    </div>
  );
}