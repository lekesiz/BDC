import React, { useState, useEffect } from 'react';
import { Download, Smartphone, Monitor, X, Check, Info, Settings } from 'lucide-react';
import { useInstallPrompt, useAppUpdate } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
/**
 * Comprehensive PWA Installation and Update Manager
 */
export function PWAInstallManager({ className = '' }) {
  const [activeTab, setActiveTab] = useState('install');
  const [settings, setSettings] = useState({
    autoUpdate: true,
    updateNotifications: true,
    installReminders: true,
    backgroundSync: true
  });
  useEffect(() => {
    // Load saved settings
    const saved = localStorage.getItem('pwa-settings');
    if (saved) {
      try {
        setSettings(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load PWA settings:', error);
      }
    }
  }, []);
  const saveSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('pwa-settings', JSON.stringify(newSettings));
  };
  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    saveSettings(newSettings);
  };
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          PWA Manager
        </CardTitle>
        <CardDescription>
          Manage app installation, updates, and PWA features
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="install">Install</TabsTrigger>
            <TabsTrigger value="updates">Updates</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>
          <TabsContent value="install" className="space-y-4">
            <InstallTab />
          </TabsContent>
          <TabsContent value="updates" className="space-y-4">
            <UpdatesTab />
          </TabsContent>
          <TabsContent value="settings" className="space-y-4">
            <SettingsTab 
              settings={settings} 
              onSettingChange={handleSettingChange} 
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
/**
 * Installation Tab Component
 */
function InstallTab() {
  const { canInstall, isInstalled, isLoading, promptInstall } = useInstallPrompt();
  const [installStep, setInstallStep] = useState(0);
  const handleInstall = async () => {
    try {
      setInstallStep(1);
      await promptInstall();
      setInstallStep(2);
    } catch (error) {
      console.error('Installation failed:', error);
      setInstallStep(0);
    }
  };
  if (isInstalled) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        <h3 className="text-lg font-semibold mb-2">App Installed</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          BDC is installed and ready to use as a native app.
        </p>
        <Badge variant="default" className="bg-green-600">
          <Check className="w-3 h-3 mr-1" />
          Installed
        </Badge>
      </div>
    );
  }
  if (!canInstall) {
    return (
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          This app is not currently installable. Install prompts are only available 
          when accessing the app from a supported browser and meeting PWA criteria.
        </AlertDescription>
      </Alert>
    );
  }
  return (
    <div className="space-y-6">
      {/* Installation benefits */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-start gap-3">
          <Smartphone className="h-5 w-5 text-blue-600 mt-1" />
          <div>
            <h4 className="font-medium">Native Experience</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Works like a native app with app icons and window controls
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Monitor className="h-5 w-5 text-blue-600 mt-1" />
          <div>
            <h4 className="font-medium">Offline Access</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Continue working even when you're offline
            </p>
          </div>
        </div>
      </div>
      {/* Installation steps */}
      <div className="space-y-3">
        <h4 className="font-medium">Installation Process:</h4>
        <div className="space-y-2">
          {[
            'Click "Install App" button',
            'Confirm installation in browser prompt',
            'App will be added to your device'
          ].map((step, index) => (
            <div key={index} className="flex items-center gap-2">
              <div className={`
                w-6 h-6 rounded-full flex items-center justify-center text-xs
                ${installStep > index 
                  ? 'bg-green-600 text-white' 
                  : installStep === index
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }
              `}>
                {installStep > index ? <Check className="w-3 h-3" /> : index + 1}
              </div>
              <span className={installStep > index ? 'line-through text-gray-500' : ''}>
                {step}
              </span>
            </div>
          ))}
        </div>
      </div>
      {/* Install button */}
      <Button
        onClick={handleInstall}
        disabled={isLoading}
        className="w-full"
        size="lg"
      >
        {isLoading ? (
          <>
            <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Installing...
          </>
        ) : (
          <>
            <Download className="mr-2 h-4 w-4" />
            Install App
          </>
        )}
      </Button>
    </div>
  );
}
/**
 * Updates Tab Component
 */
function UpdatesTab() {
  const { hasUpdate, isUpdating, applyUpdate } = useAppUpdate();
  const [updateHistory, setUpdateHistory] = useState([]);
  useEffect(() => {
    // Load update history
    const history = localStorage.getItem('pwa-update-history');
    if (history) {
      try {
        setUpdateHistory(JSON.parse(history));
      } catch (error) {
        console.error('Failed to load update history:', error);
      }
    }
  }, []);
  const handleUpdate = async () => {
    try {
      await applyUpdate();
      // Record update in history
      const newUpdate = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        version: 'Latest',
        status: 'completed'
      };
      const newHistory = [newUpdate, ...updateHistory.slice(0, 9)]; // Keep last 10
      setUpdateHistory(newHistory);
      localStorage.setItem('pwa-update-history', JSON.stringify(newHistory));
    } catch (error) {
      console.error('Update failed:', error);
    }
  };
  return (
    <div className="space-y-6">
      {/* Update status */}
      <div className="text-center">
        {hasUpdate ? (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center mx-auto">
              <Download className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Update Available</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                A new version of BDC is ready to install with improvements and bug fixes.
              </p>
              <Button onClick={handleUpdate} disabled={isUpdating} size="lg">
                {isUpdating ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Updating...
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Update Now
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto">
              <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Up to Date</h3>
              <p className="text-gray-600 dark:text-gray-400">
                You're running the latest version of BDC.
              </p>
            </div>
          </div>
        )}
      </div>
      {/* Update history */}
      {updateHistory.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium">Recent Updates</h4>
          <div className="space-y-2">
            {updateHistory.slice(0, 5).map((update) => (
              <div key={update.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="text-sm font-medium">Version {update.version}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(update.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <Badge variant={update.status === 'completed' ? 'default' : 'secondary'}>
                  {update.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Manual check */}
      <div className="border-t pt-4">
        <Button
          variant="outline"
          onClick={() => window.location.reload()}
          className="w-full"
        >
          Check for Updates
        </Button>
      </div>
    </div>
  );
}
/**
 * Settings Tab Component
 */
function SettingsTab({ settings, onSettingChange }) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Auto Updates</label>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Automatically install updates when available
            </p>
          </div>
          <Switch
            checked={settings.autoUpdate}
            onCheckedChange={(checked) => onSettingChange('autoUpdate', checked)}
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Update Notifications</label>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Show notifications when updates are available
            </p>
          </div>
          <Switch
            checked={settings.updateNotifications}
            onCheckedChange={(checked) => onSettingChange('updateNotifications', checked)}
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Install Reminders</label>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Show reminders to install the app
            </p>
          </div>
          <Switch
            checked={settings.installReminders}
            onCheckedChange={(checked) => onSettingChange('installReminders', checked)}
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Background Sync</label>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Sync data in the background when offline
            </p>
          </div>
          <Switch
            checked={settings.backgroundSync}
            onCheckedChange={(checked) => onSettingChange('backgroundSync', checked)}
          />
        </div>
      </div>
      {/* Storage info */}
      <div className="border-t pt-4">
        <h4 className="font-medium mb-3">Storage Information</h4>
        <StorageInfo />
      </div>
    </div>
  );
}
/**
 * Storage Information Component
 */
function StorageInfo() {
  const [storageInfo, setStorageInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    const getStorageInfo = async () => {
      try {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
          const estimate = await navigator.storage.estimate();
          setStorageInfo(estimate);
        }
      } catch (error) {
        console.error('Failed to get storage info:', error);
      } finally {
        setIsLoading(false);
      }
    };
    getStorageInfo();
  }, []);
  const clearCaches = async () => {
    try {
      const cacheNames = await caches.keys();
      await Promise.all(cacheNames.map(name => caches.delete(name)));
      // Refresh storage info
      const estimate = await navigator.storage.estimate();
      setStorageInfo(estimate);
      alert('Caches cleared successfully');
    } catch (error) {
      console.error('Failed to clear caches:', error);
      alert('Failed to clear caches');
    }
  };
  if (isLoading) {
    return <div className="text-sm text-gray-600">Loading storage info...</div>;
  }
  if (!storageInfo) {
    return <div className="text-sm text-gray-600">Storage info not available</div>;
  }
  const usedMB = Math.round((storageInfo.usage || 0) / 1024 / 1024);
  const quotaMB = Math.round((storageInfo.quota || 0) / 1024 / 1024);
  const usagePercent = quotaMB > 0 ? (usedMB / quotaMB) * 100 : 0;
  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm">
        <span>Used Storage:</span>
        <span>{usedMB} MB / {quotaMB} MB</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(usagePercent, 100)}%` }}
        />
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={clearCaches}
        className="w-full"
      >
        Clear Cache
      </Button>
    </div>
  );
}
export default PWAInstallManager;