// TODO: i18n - processed
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bell, 
  BellOff, 
  Settings, 
  Check, 
  X, 
  AlertCircle, 
  Shield,
  Clock,
  Smartphone,
  Globe,
  Volume2,
  VolumeX,
  Calendar,
  FileText,
  Users,
  Megaphone,
  Trash2,
  Edit,
  Play,
  Pause,
  BarChart3
} from 'lucide-react';
import { usePushNotifications } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Alert, AlertDescription } from '../ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { useToast } from '../ui/use-toast';

/**
 * Advanced Push Notification Manager Component
 * Comprehensive push notification management with scheduling, analytics, and advanced settings
 */import { useTranslation } from "react-i18next";
export function PushNotificationManager({ className = '' }) {const { t } = useTranslation();
  const {
    permission,
    subscription,
    isLoading,
    requestPermission,
    subscribe,
    isSupported
  } = usePushNotifications();
  const { toast } = useToast();

  // Enhanced notification settings with more categories and options
  const [notificationSettings, setNotificationSettings] = useState({
    evaluations: { enabled: true, priority: 'high', sound: true, vibrate: true },
    appointments: { enabled: true, priority: 'high', sound: true, vibrate: true },
    documents: { enabled: true, priority: 'normal', sound: false, vibrate: true },
    general: { enabled: true, priority: 'normal', sound: false, vibrate: false },
    marketing: { enabled: false, priority: 'low', sound: false, vibrate: false },
    reminders: { enabled: true, priority: 'normal', sound: true, vibrate: false },
    system: { enabled: true, priority: 'high', sound: false, vibrate: true }
  });

  // Advanced settings
  const [advancedSettings, setAdvancedSettings] = useState({
    quietHours: { enabled: true, start: '22:00', end: '08:00' },
    batching: { enabled: true, interval: 15 }, // minutes
    persistence: { enabled: true, duration: 24 }, // hours
    location: { enabled: false },
    frequency: { enabled: true, maxPerHour: 5 }
  });

  // Notification history and analytics
  const [notificationHistory, setNotificationHistory] = useState([]);
  const [notificationStats, setNotificationStats] = useState({
    sent: 0,
    delivered: 0,
    clicked: 0,
    dismissed: 0
  });

  const [activeTab, setActiveTab] = useState('settings');
  const [scheduledNotifications, setScheduledNotifications] = useState([]);
  const [testNotification, setTestNotification] = useState(null);

  // Load saved preferences and initialize
  useEffect(() => {
    loadSettings();
    loadNotificationHistory();
    updateNotificationStats();
  }, []);

  const loadSettings = () => {
    const savedSettings = localStorage.getItem('bdc-notification-settings');
    const savedAdvanced = localStorage.getItem('bdc-notification-advanced');
    
    if (savedSettings) {
      setNotificationSettings(JSON.parse(savedSettings));
    }
    if (savedAdvanced) {
      setAdvancedSettings(JSON.parse(savedAdvanced));
    }
  };

  const saveSettings = (newSettings) => {
    setNotificationSettings(newSettings);
    localStorage.setItem('bdc-notification-settings', JSON.stringify(newSettings));
  };

  const saveAdvancedSettings = (newSettings) => {
    setAdvancedSettings(newSettings);
    localStorage.setItem('bdc-notification-advanced', JSON.stringify(newSettings));
  };

  const loadNotificationHistory = () => {
    // Mock history data - in real implementation, this would come from storage or API
    const mockHistory = [
      {
        id: '1',
        title: 'New Evaluation Available',
        body: 'Technical Assessment is ready for review',
        timestamp: Date.now() - 3600000,
        category: 'evaluations',
        clicked: true,
        delivered: true
      },
      {
        id: '2',
        title: 'Appointment Reminder',
        body: 'Meeting with John Doe in 30 minutes',
        timestamp: Date.now() - 7200000,
        category: 'appointments',
        clicked: false,
        delivered: true
      },
      {
        id: '3',
        title: 'Document Shared',
        body: 'Training materials have been shared with you',
        timestamp: Date.now() - 86400000,
        category: 'documents',
        clicked: true,
        delivered: true
      }
    ];
    setNotificationHistory(mockHistory);
  };

  const updateNotificationStats = () => {
    // Mock stats - in real implementation, this would be calculated from actual data
    setNotificationStats({
      sent: 45,
      delivered: 42,
      clicked: 18,
      dismissed: 24
    });
  };

  const handlePermissionRequest = async () => {
    try {
      const result = await requestPermission();
      if (result === 'granted') {
        await subscribe();
      }
    } catch (error) {
      console.error('Failed to request permission:', error);
    }
  };

  const handleSubscribe = async () => {
    try {
      await subscribe();
    } catch (error) {
      console.error('Failed to subscribe:', error);
    }
  };

  const sendTestNotification = useCallback((type = 'basic') => {
    if (permission !== 'granted') {
      toast({
        title: 'Permission required',
        description: 'Please enable notifications first',
        variant: 'destructive'
      });
      return;
    }

    const notificationTypes = {
      basic: {
        title: 'BDC Test Notification',
        body: 'This is a basic test notification from BDC app.',
        actions: []
      },
      interactive: {
        title: 'Interactive Test',
        body: 'This notification has action buttons.',
        actions: [
          { action: 'view', title: 'View', icon: '/icons/view.png' },
          { action: 'dismiss', title: 'Dismiss', icon: '/icons/dismiss.png' }
        ]
      },
      rich: {
        title: 'Rich Notification',
        body: 'This notification includes an image and vibration.',
        image: '/icons/notification-image.png',
        vibrate: [200, 100, 200]
      }
    };

    const config = notificationTypes[type];
    
    const notification = new Notification(config.title, {
      body: config.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      tag: `test-notification-${type}`,
      requireInteraction: type === 'interactive',
      actions: config.actions || [],
      image: config.image,
      vibrate: config.vibrate || [100]
    });

    setTestNotification(`${type} test notification sent!`);

    setTimeout(() => {
      setTestNotification(null);
    }, 3000);

    notification.onclick = () => {
      window.focus();
      notification.close();
      // Track click
      updateNotificationStats();
    };
  }, [permission, toast]);

  const scheduleNotification = useCallback((title, body, delay, category = 'general') => {
    if (permission !== 'granted') return;

    const scheduleId = setTimeout(() => {
      const notification = new Notification(title, {
        body,
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        tag: `scheduled-${Date.now()}`,
        vibrate: notificationSettings[category]?.vibrate ? [200, 100, 200] : undefined
      });

      // Remove from scheduled list
      setScheduledNotifications(prev => 
        prev.filter(item => item.id !== scheduleId)
      );

      notification.onclick = () => {
        window.focus();
        notification.close();
      };
    }, delay);

    // Add to scheduled list
    setScheduledNotifications(prev => [...prev, {
      id: scheduleId,
      title,
      body,
      category,
      scheduledFor: Date.now() + delay
    }]);

    return scheduleId;
  }, [permission, notificationSettings]);

  const cancelScheduledNotification = useCallback((id) => {
    clearTimeout(id);
    setScheduledNotifications(prev => prev.filter(item => item.id !== id));
  }, []);

  const getPermissionStatus = () => {
    switch (permission) {
      case 'granted':
        return {
          icon: <Bell className="h-4 w-4 text-green-600" />,
          text: 'Enabled',
          variant: 'success',
          className: 'bg-green-100 text-green-800'
        };
      case 'denied':
        return {
          icon: <BellOff className="h-4 w-4 text-red-600" />,
          text: 'Blocked',
          variant: 'destructive',
          className: 'bg-red-100 text-red-800'
        };
      default:
        return {
          icon: <AlertCircle className="h-4 w-4 text-yellow-600" />,
          text: 'Not Set',
          variant: 'warning',
          className: 'bg-yellow-100 text-yellow-800'
        };
    }
  };

  const status = getPermissionStatus();

  if (!isSupported) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="h-5 w-5" />{t("components.push_notifications")}

          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{t("components.push_notifications_are_not_supported_in_this_brows")}

            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>);

  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <CardTitle>{t("components.push_notifications")}</CardTitle>
          </div>
          <Badge className={status.className}>
            {status.icon}
            <span className="ml-1">{status.text}</span>
          </Badge>
        </div>
        <CardDescription>{t("components.stay_updated_with_realtime_notifications_for_impor")}

        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Permission Status */}
        <div className="space-y-4">
          {permission === 'default' &&
          <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>{t("components.enable_notifications_to_receive_updates_about_eval")}

            </AlertDescription>
            </Alert>
          }

          {permission === 'denied' &&
          <Alert variant="destructive">
              <BellOff className="h-4 w-4" />
              <AlertDescription>{t("components.notifications_are_blocked_to_enable_them_click_the")}

            </AlertDescription>
            </Alert>
          }

          {permission === 'granted' && !subscription &&
          <Alert variant="warning">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{t("components.permissions_granted_but_not_subscribed_subscribe_t")}

            </AlertDescription>
            </Alert>
          }

          {permission === 'granted' && subscription &&
          <Alert variant="default" className="border-green-200 bg-green-50">
              <Check className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700">{t("components.youre_subscribed_to_push_notifications_youll_recei")}

            </AlertDescription>
            </Alert>
          }
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          {permission === 'default' &&
          <Button
            onClick={handlePermissionRequest}
            disabled={isLoading}
            className="flex-1">

              {isLoading ?
            <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />{t("components.requesting")}

            </> :

            <>
                  <Bell className="mr-2 h-4 w-4" />{t("components.enable_notifications")}

            </>
            }
            </Button>
          }

          {permission === 'granted' && !subscription &&
          <Button
            onClick={handleSubscribe}
            disabled={isLoading}
            className="flex-1">

              {isLoading ?
            <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />{t("components.subscribing")}

            </> :

            <>
                  <Bell className="mr-2 h-4 w-4" />{t("components.subscribe")}

            </>
            }
            </Button>
          }

          {permission === 'granted' && subscription &&
          <Button
            onClick={sendTestNotification}
            variant="outline"
            className="flex-1">

              <Bell className="mr-2 h-4 w-4" />{t("components.test_notification")}

          </Button>
          }
        </div>

        {/* Test Notification Feedback */}
        {testNotification &&
        <Alert variant="default" className="border-blue-200 bg-blue-50">
            <Check className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-700">
              {testNotification}
            </AlertDescription>
          </Alert>
        }

        {/* Notification Categories */}
        {permission === 'granted' &&
        <div className="space-y-4">
            <h4 className="font-medium flex items-center gap-2">
              <Settings className="h-4 w-4" />{t("components.notification_categories")}

          </h4>
            
            <div className="space-y-3">
              {Object.entries(notificationSettings).map(([key, enabled]) =>
            <div key={key} className="flex items-center justify-between py-2">
                  <div>
                    <div className="font-medium text-sm capitalize">
                      {key === 'evaluations' && 'Evaluations & Tests'}
                      {key === 'appointments' && 'Appointments & Calendar'}
                      {key === 'documents' && 'Documents & Files'}
                      {key === 'general' && 'General Updates'}
                      {key === 'marketing' && 'Marketing & Promotions'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {key === 'evaluations' && 'New tests, results, and evaluation updates'}
                      {key === 'appointments' && 'Upcoming appointments and schedule changes'}
                      {key === 'documents' && 'Document shares and upload notifications'}
                      {key === 'general' && 'System updates and important announcements'}
                      {key === 'marketing' && 'Optional promotional content and tips'}
                    </div>
                  </div>
                  <Switch
                checked={enabled}
                onCheckedChange={(checked) => {
                  const newSettings = { ...notificationSettings, [key]: checked };
                  saveSettings(newSettings);
                }} />

                </div>
            )}
            </div>
          </div>
        }

        {/* Subscription Info */}
        {subscription &&
        <div className="text-xs text-gray-500 space-y-1">
            <div>{t("components.subscription_active")}</div>
            <div className="font-mono text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded">
              Endpoint: {subscription.endpoint.substring(0, 50)}...
            </div>
          </div>
        }
      </CardContent>
    </Card>);

}

/**
 * Simple Notification Permission Prompt
 * Minimal component for quick permission request
 */
export function NotificationPermissionPrompt({ onDismiss, className = '' }) {const { t } = useTranslation();
  const { permission, requestPermission, isLoading } = usePushNotifications();
  const [dismissed, setDismissed] = useState(false);

  if (permission !== 'default' || dismissed) {
    return null;
  }

  const handleAllow = async () => {
    try {
      await requestPermission();
    } catch (error) {
      console.error('Permission request failed:', error);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  return (
    <Card className={`border-blue-200 bg-blue-50 dark:bg-blue-950 dark:border-blue-800 ${className}`}>
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Bell className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1 space-y-3">
            <div>
              <div className="font-medium text-sm text-blue-900 dark:text-blue-100">{t("components.stay_updated")}

              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300">{t("components.enable_notifications_to_get_updates_about_evaluati")}

              </div>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleAllow}
                disabled={isLoading}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white">

                {isLoading ?
                <>
                    <div className="mr-1 h-3 w-3 animate-spin rounded-full border border-white border-t-transparent" />{t("components.enabling")}

                </> :

                'Allow'
                }
              </Button>
              <Button
                onClick={handleDismiss}
                size="sm"
                variant="outline"
                className="border-blue-300 text-blue-700 hover:bg-blue-100">{t("components.not_now")}


              </Button>
            </div>
          </div>
          <Button
            onClick={handleDismiss}
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800">

            <X className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>);

}

/**
 * Notification Status Badge
 * Simple badge showing notification status
 */
export function NotificationStatusBadge({ className = '' }) {const { t } = useTranslation();
  const { permission, subscription } = usePushNotifications();

  const getStatus = () => {
    if (permission === 'granted' && subscription) {
      return { icon: Bell, text: 'On', className: 'bg-green-100 text-green-800' };
    }
    if (permission === 'denied') {
      return { icon: BellOff, text: 'Off', className: 'bg-red-100 text-red-800' };
    }
    return { icon: AlertCircle, text: 'Ask', className: 'bg-yellow-100 text-yellow-800' };
  };

  const status = getStatus();
  const Icon = status.icon;

  return (
    <Badge className={`${status.className} ${className}`}>
      <Icon className="h-3 w-3 mr-1" />
      {status.text}
    </Badge>);

}

export default PushNotificationManager;