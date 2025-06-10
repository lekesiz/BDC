import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Bell, BellOff, Settings, X, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';
import { MobileDrawer } from '../components/MobileDrawer';

/**
 * PushNotificationManager - Comprehensive push notification management
 * Features permission handling, subscription management, and notification display
 */
export const PushNotificationManager = ({
  children,
  vapidKey,
  serviceWorkerPath = '/sw.js',
  notificationEndpoint,
  autoRequestPermission = false,
  showPermissionPrompt = true,
  customPromptComponent,
  onPermissionGranted,
  onPermissionDenied,
  onNotificationReceived,
  onNotificationClicked,
  className,
  ...props
}) => {
  const { 
    capabilities, 
    hapticFeedback: triggerHaptic, 
    isMobile 
  } = useMobile();

  const [permissionState, setPermissionState] = useState('default');
  const [subscription, setSubscription] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const serviceWorkerRef = useRef(null);

  // Check for push notification support
  useEffect(() => {
    const checkSupport = async () => {
      const supported = (
        'serviceWorker' in navigator &&
        'PushManager' in window &&
        'Notification' in window
      );
      
      setIsSupported(supported);
      
      if (supported) {
        setPermissionState(Notification.permission);
      }
    };

    checkSupport();
  }, []);

  // Register service worker
  useEffect(() => {
    if (!isSupported) return;

    const registerServiceWorker = async () => {
      try {
        const registration = await navigator.serviceWorker.register(serviceWorkerPath);
        serviceWorkerRef.current = registration;
        
        // Listen for messages from service worker
        navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
        
        // Check for existing subscription
        const existingSubscription = await registration.pushManager.getSubscription();
        if (existingSubscription) {
          setSubscription(existingSubscription);
        }
      } catch (error) {
        console.error('Service worker registration failed:', error);
      }
    };

    registerServiceWorker();

    return () => {
      navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
    };
  }, [isSupported, serviceWorkerPath]);

  // Handle service worker messages
  const handleServiceWorkerMessage = useCallback((event) => {
    const { type, payload } = event.data;
    
    switch (type) {
      case 'notification-received':
        handleNotificationReceived(payload);
        break;
      case 'notification-clicked':
        handleNotificationClicked(payload);
        break;
      default:
        break;
    }
  }, []);

  // Handle notification received
  const handleNotificationReceived = useCallback((notification) => {
    setNotifications(prev => [
      {
        id: Date.now(),
        ...notification,
        timestamp: Date.now(),
        read: false
      },
      ...prev.slice(0, 49) // Keep only last 50 notifications
    ]);

    onNotificationReceived?.(notification);

    if (isMobile) {
      triggerHaptic('light');
    }
  }, [onNotificationReceived, isMobile, triggerHaptic]);

  // Handle notification clicked
  const handleNotificationClicked = useCallback((notification) => {
    // Mark as read
    setNotifications(prev => 
      prev.map(n => n.id === notification.id ? { ...n, read: true } : n)
    );

    onNotificationClicked?.(notification);

    if (isMobile) {
      triggerHaptic('medium');
    }
  }, [onNotificationClicked, isMobile, triggerHaptic]);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!isSupported) return false;

    try {
      const permission = await Notification.requestPermission();
      setPermissionState(permission);

      if (permission === 'granted') {
        onPermissionGranted?.();
        await subscribeUser();
        return true;
      } else {
        onPermissionDenied?.();
        return false;
      }
    } catch (error) {
      console.error('Permission request failed:', error);
      onPermissionDenied?.(error);
      return false;
    }
  }, [isSupported, onPermissionGranted, onPermissionDenied]);

  // Subscribe user for push notifications
  const subscribeUser = useCallback(async () => {
    if (!serviceWorkerRef.current || !vapidKey) return null;

    try {
      const subscription = await serviceWorkerRef.current.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey)
      });

      setSubscription(subscription);

      // Send subscription to server
      if (notificationEndpoint) {
        await fetch(notificationEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            subscription,
            action: 'subscribe'
          })
        });
      }

      return subscription;
    } catch (error) {
      console.error('Subscription failed:', error);
      return null;
    }
  }, [vapidKey, notificationEndpoint]);

  // Unsubscribe user
  const unsubscribeUser = useCallback(async () => {
    if (!subscription) return;

    try {
      await subscription.unsubscribe();
      setSubscription(null);

      // Notify server
      if (notificationEndpoint) {
        await fetch(notificationEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            subscription,
            action: 'unsubscribe'
          })
        });
      }
    } catch (error) {
      console.error('Unsubscribe failed:', error);
    }
  }, [subscription, notificationEndpoint]);

  // Show permission prompt
  useEffect(() => {
    if (
      autoRequestPermission &&
      isSupported &&
      permissionState === 'default' &&
      showPermissionPrompt
    ) {
      setShowPrompt(true);
    }
  }, [autoRequestPermission, isSupported, permissionState, showPermissionPrompt]);

  // Send test notification
  const sendTestNotification = useCallback(async () => {
    if (permissionState !== 'granted') return;

    try {
      const registration = serviceWorkerRef.current;
      if (registration) {
        await registration.showNotification('Test Notification', {
          body: 'This is a test notification from your app.',
          icon: '/icons/icon-192x192.png',
          badge: '/icons/icon-72x72.png',
          tag: 'test-notification',
          requireInteraction: false,
          actions: [
            {
              action: 'view',
              title: 'View',
              icon: '/icons/view-icon.png'
            },
            {
              action: 'dismiss',
              title: 'Dismiss',
              icon: '/icons/dismiss-icon.png'
            }
          ]
        });
      }
    } catch (error) {
      console.error('Test notification failed:', error);
    }
  }, [permissionState]);

  // Mark notification as read
  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev =>
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  }, []);

  // Clear all notifications
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Get unread count
  const unreadCount = notifications.filter(n => !n.read).length;

  // Provide notification context
  const notificationContext = {
    isSupported,
    permissionState,
    subscription,
    notifications,
    unreadCount,
    requestPermission,
    subscribeUser,
    unsubscribeUser,
    sendTestNotification,
    markAsRead,
    clearAllNotifications
  };

  return (
    <PushNotificationProvider value={notificationContext}>
      <div className={cn('relative', className)} {...props}>
        {children}

        {/* Permission Prompt */}
        {showPrompt && permissionState === 'default' && (
          customPromptComponent ? (
            customPromptComponent({
              onAccept: async () => {
                const granted = await requestPermission();
                if (granted) {
                  setShowPrompt(false);
                }
              },
              onDecline: () => setShowPrompt(false)
            })
          ) : (
            <PermissionPrompt
              onAccept={async () => {
                const granted = await requestPermission();
                if (granted) {
                  setShowPrompt(false);
                }
              }}
              onDecline={() => setShowPrompt(false)}
            />
          )
        )}

        {/* Notification Settings */}
        <MobileDrawer
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          title="Notification Settings"
          position="bottom"
        >
          <NotificationSettings
            context={notificationContext}
            onClose={() => setShowSettings(false)}
          />
        </MobileDrawer>
      </div>
    </PushNotificationProvider>
  );
};

/**
 * Permission Prompt Component
 */
const PermissionPrompt = ({ onAccept, onDecline }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
    <div className="bg-background rounded-lg shadow-xl max-w-md w-full p-6">
      <div className="flex items-center gap-3 mb-4">
        <Bell className="h-6 w-6 text-primary" />
        <h3 className="text-lg font-semibold">Enable Notifications</h3>
      </div>
      
      <p className="text-muted-foreground mb-6">
        Stay updated with important information and updates. You can change this setting later.
      </p>
      
      <div className="flex gap-2">
        <TouchOptimizedButton
          variant="outline"
          className="flex-1"
          onClick={onDecline}
        >
          Not Now
        </TouchOptimizedButton>
        <TouchOptimizedButton
          className="flex-1"
          onClick={onAccept}
        >
          Allow
        </TouchOptimizedButton>
      </div>
    </div>
  </div>
);

/**
 * Notification Settings Component
 */
const NotificationSettings = ({ context, onClose }) => {
  const { 
    isSupported, 
    permissionState, 
    subscription, 
    notifications,
    requestPermission,
    unsubscribeUser,
    sendTestNotification,
    clearAllNotifications
  } = context;

  return (
    <div className="p-4 space-y-6">
      {/* Permission Status */}
      <div>
        <h3 className="font-medium mb-3">Permission Status</h3>
        <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
          {permissionState === 'granted' ? (
            <Bell className="h-5 w-5 text-green-500" />
          ) : (
            <BellOff className="h-5 w-5 text-red-500" />
          )}
          <div className="flex-1">
            <p className="font-medium capitalize">{permissionState}</p>
            <p className="text-sm text-muted-foreground">
              {permissionState === 'granted' 
                ? 'Notifications are enabled'
                : 'Notifications are disabled'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-3">
        {permissionState === 'default' && (
          <TouchOptimizedButton
            className="w-full"
            onClick={requestPermission}
          >
            Enable Notifications
          </TouchOptimizedButton>
        )}

        {permissionState === 'granted' && (
          <>
            <TouchOptimizedButton
              variant="outline"
              className="w-full"
              onClick={sendTestNotification}
            >
              Send Test Notification
            </TouchOptimizedButton>
            
            {subscription && (
              <TouchOptimizedButton
                variant="destructive"
                className="w-full"
                onClick={unsubscribeUser}
              >
                Unsubscribe
              </TouchOptimizedButton>
            )}
          </>
        )}

        {notifications.length > 0 && (
          <TouchOptimizedButton
            variant="outline"
            className="w-full"
            onClick={clearAllNotifications}
          >
            Clear All Notifications
          </TouchOptimizedButton>
        )}
      </div>

      {/* Support Info */}
      <div className="text-sm text-muted-foreground">
        <p>Support: {isSupported ? 'Available' : 'Not available'}</p>
        <p>Subscription: {subscription ? 'Active' : 'Inactive'}</p>
        <p>Total notifications: {notifications.length}</p>
      </div>
    </div>
  );
};

/**
 * Notification Bell Icon with Badge
 */
export const NotificationBell = ({ 
  onClick, 
  className,
  showBadge = true,
  ...props 
}) => {
  const { unreadCount } = usePushNotification();

  return (
    <TouchOptimizedButton
      variant="ghost"
      size="icon"
      className={cn('relative', className)}
      onClick={onClick}
      {...props}
    >
      <Bell className="h-5 w-5" />
      {showBadge && unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 h-5 w-5 bg-destructive text-destructive-foreground text-xs font-medium rounded-full flex items-center justify-center">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </TouchOptimizedButton>
  );
};

/**
 * Context Provider and Hook
 */
const PushNotificationContext = React.createContext({});

const PushNotificationProvider = ({ children, value }) => (
  <PushNotificationContext.Provider value={value}>
    {children}
  </PushNotificationContext.Provider>
);

export const usePushNotification = () => {
  const context = React.useContext(PushNotificationContext);
  if (!context) {
    throw new Error('usePushNotification must be used within a PushNotificationManager');
  }
  return context;
};

/**
 * Utility function to convert VAPID key
 */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export default PushNotificationManager;