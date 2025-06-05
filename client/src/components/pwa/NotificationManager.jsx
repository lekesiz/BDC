import React, { useState, useEffect } from 'react';
import { Bell, BellOff, Settings, Check, X, AlertCircle } from 'lucide-react';
import { usePushNotifications } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Switch } from '../ui/switch';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
/**
 * Push Notification Manager Component
 * Handles push notification permissions and subscription
 */
export function NotificationManager({ className = '' }) {
  const { permission, subscription, isLoading, requestPermission, subscribe, isSupported } = usePushNotifications();
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState({
    evaluations: true,
    appointments: true,
    messages: true,
    updates: false
  });
  const isEnabled = permission === 'granted' && subscription;
  const canEnable = permission !== 'denied' && isSupported;
  useEffect(() => {
    // Load saved preferences
    const saved = localStorage.getItem('notification-preferences');
    if (saved) {
      try {
        setPreferences(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load notification preferences:', error);
      }
    }
  }, []);
  const savePreferences = (newPreferences) => {
    setPreferences(newPreferences);
    localStorage.setItem('notification-preferences', JSON.stringify(newPreferences));
  };
  const handleEnable = async () => {
    try {
      if (permission !== 'granted') {
        await requestPermission();
      }
      if (permission === 'granted' && !subscription) {
        await subscribe();
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
    }
  };
  const handlePreferenceChange = (key, value) => {
    const newPreferences = { ...preferences, [key]: value };
    savePreferences(newPreferences);
  };
  if (!isSupported) {
    return (
      <Alert className={className}>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Push notifications are not supported in this browser.
        </AlertDescription>
      </Alert>
    );
  }
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isEnabled ? (
              <Bell className="h-5 w-5 text-green-600" />
            ) : (
              <BellOff className="h-5 w-5 text-gray-400" />
            )}
            <CardTitle className="text-lg">Push Notifications</CardTitle>
            <Badge variant={isEnabled ? 'default' : 'secondary'}>
              {isEnabled ? 'Enabled' : 'Disabled'}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription>
          {isEnabled 
            ? 'You\'ll receive notifications for important updates and activities.'
            : 'Enable notifications to stay updated with important information.'
          }
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Permission status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Permission Status:</span>
            <Badge variant={permission === 'granted' ? 'default' : permission === 'denied' ? 'destructive' : 'secondary'}>
              {permission === 'granted' ? 'Granted' : permission === 'denied' ? 'Denied' : 'Not requested'}
            </Badge>
          </div>
          {subscription && (
            <div className="flex items-center justify-between text-sm">
              <span>Subscription Status:</span>
              <Badge variant="default">Active</Badge>
            </div>
          )}
        </div>
        {/* Enable/disable notifications */}
        {!isEnabled && canEnable && (
          <Button
            onClick={handleEnable}
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Enabling...
              </>
            ) : (
              <>
                <Bell className="mr-2 h-4 w-4" />
                Enable Notifications
              </>
            )}
          </Button>
        )}
        {permission === 'denied' && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Notifications are blocked. To enable them, click the lock icon in your address bar and allow notifications.
            </AlertDescription>
          </Alert>
        )}
        {/* Notification preferences */}
        {showSettings && isEnabled && (
          <div className="border-t pt-4 space-y-3">
            <h4 className="font-medium text-sm">Notification Preferences</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Evaluations</label>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    New evaluations and test results
                  </p>
                </div>
                <Switch
                  checked={preferences.evaluations}
                  onCheckedChange={(checked) => handlePreferenceChange('evaluations', checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Appointments</label>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Appointment reminders and updates
                  </p>
                </div>
                <Switch
                  checked={preferences.appointments}
                  onCheckedChange={(checked) => handlePreferenceChange('appointments', checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Messages</label>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    New messages and communications
                  </p>
                </div>
                <Switch
                  checked={preferences.messages}
                  onCheckedChange={(checked) => handlePreferenceChange('messages', checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">App Updates</label>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    New features and important updates
                  </p>
                </div>
                <Switch
                  checked={preferences.updates}
                  onCheckedChange={(checked) => handlePreferenceChange('updates', checked)}
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
/**
 * Notification Permission Prompt
 * Simple prompt to request notification permission
 */
export function NotificationPermissionPrompt({ onDismiss, className = '' }) {
  const { permission, isLoading, requestPermission, isSupported } = usePushNotifications();
  const [dismissed, setDismissed] = useState(false);
  if (!isSupported || permission === 'granted' || permission === 'denied' || dismissed) {
    return null;
  }
  const handleRequest = async () => {
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
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <CardTitle className="text-lg text-blue-900 dark:text-blue-100">
              Stay Updated
            </CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800 dark:text-blue-400"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription className="text-blue-700 dark:text-blue-300">
          Get notified about important updates, new evaluations, and appointment reminders.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Button
            onClick={handleRequest}
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Requesting...
              </>
            ) : (
              <>
                <Bell className="mr-2 h-4 w-4" />
                Enable Notifications
              </>
            )}
          </Button>
          <Button variant="outline" onClick={handleDismiss}>
            Not now
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
/**
 * Notification Status Badge
 * Simple status indicator for notifications
 */
export function NotificationStatusBadge({ className = '' }) {
  const { permission, subscription, isSupported } = usePushNotifications();
  if (!isSupported) {
    return null;
  }
  const isEnabled = permission === 'granted' && subscription;
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {isEnabled ? (
        <>
          <Bell className="h-3 w-3 text-green-500" />
          <span className="text-xs text-green-600 dark:text-green-400">Notifications On</span>
        </>
      ) : (
        <>
          <BellOff className="h-3 w-3 text-gray-400" />
          <span className="text-xs text-gray-500">Notifications Off</span>
        </>
      )}
    </div>
  );
}
export default NotificationManager;