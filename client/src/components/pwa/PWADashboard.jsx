import React, { useState } from 'react';
import { 
  Smartphone, 
  Settings, 
  Activity, 
  Bell, 
  RefreshCw, 
  Wifi,
  HardDrive,
  Shield,
  Zap,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Switch } from '../ui/switch';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';

// Import PWA components
import { PWAStatus, PWAControls } from './PWAProvider';
import { InstallPrompt, FloatingInstallButton } from './InstallPrompt';
import { UpdateNotification } from './UpdateNotification';
import { OfflineIndicator, SyncQueueStatus } from './OfflineIndicator';
import BackgroundSyncManager from './BackgroundSyncManager';
import PushNotificationManager from './PushNotificationManager';
import PWAPerformanceMonitor from './PWAPerformanceMonitor';

// Import hooks
import { usePWA, useOnlineStatus, useStorageManager } from '../../hooks/usePWA';

/**
 * Comprehensive PWA Dashboard Component
 * Provides a centralized interface for all PWA features and management
 */
export function PWADashboard({ className = '' }) {
  const { isOnline, canInstall, isInstalled, hasUpdate, isLoading, error } = usePWA();
  const { connectionInfo } = useOnlineStatus();
  const { storageEstimate } = useStorageManager();
  
  const [expandedSections, setExpandedSections] = useState({
    overview: true,
    installation: false,
    notifications: false,
    sync: false,
    performance: false,
    storage: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getPWAScore = () => {
    let score = 0;
    let maxScore = 5;

    // Service Worker
    if ('serviceWorker' in navigator) score += 1;
    
    // Installable
    if (canInstall || isInstalled) score += 1;
    
    // Online/Offline capable
    if (isOnline || 'serviceWorker' in navigator) score += 1;
    
    // Notifications supported
    if ('Notification' in window) score += 1;
    
    // Storage available
    if ('caches' in window) score += 1;

    return Math.round((score / maxScore) * 100);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const getStoragePercentage = () => {
    if (!storageEstimate?.quota || !storageEstimate?.usage) return 0;
    return (storageEstimate.usage / storageEstimate.quota) * 100;
  };

  const pwaScore = getPWAScore();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">PWA Dashboard</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Monitor and manage Progressive Web App features
          </p>
        </div>
        <Badge className={getScoreBadgeColor(pwaScore)}>
          PWA Score: {pwaScore}%
        </Badge>
      </div>

      {/* Quick Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${isOnline ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                <Wifi className="h-4 w-4" />
              </div>
              <div>
                <div className="font-medium text-sm">Connection</div>
                <div className="text-xs text-gray-500">
                  {isOnline ? 'Online' : 'Offline'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${isInstalled ? 'bg-green-100 text-green-600' : canInstall ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'}`}>
                <Smartphone className="h-4 w-4" />
              </div>
              <div>
                <div className="font-medium text-sm">Installation</div>
                <div className="text-xs text-gray-500">
                  {isInstalled ? 'Installed' : canInstall ? 'Available' : 'Not Available'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${Notification.permission === 'granted' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}>
                <Bell className="h-4 w-4" />
              </div>
              <div>
                <div className="font-medium text-sm">Notifications</div>
                <div className="text-xs text-gray-500">
                  {Notification.permission === 'granted' ? 'Enabled' : 'Disabled'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                <HardDrive className="h-4 w-4" />
              </div>
              <div>
                <div className="font-medium text-sm">Storage</div>
                <div className="text-xs text-gray-500">
                  {formatBytes(storageEstimate?.usage)} used
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="installation">Install</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="sync">Sync</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </Tabs>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* PWA Status */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  <CardTitle>PWA Status</CardTitle>
                </div>
                <CardDescription>
                  Current status of Progressive Web App features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PWAStatus />
                <div className="mt-4">
                  <PWAControls />
                </div>
              </CardContent>
            </Card>

            {/* Connection Status */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Wifi className="h-5 w-5" />
                  <CardTitle>Connection Status</CardTitle>
                </div>
                <CardDescription>
                  Network connectivity and quality information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <OfflineIndicator showDetails />
                {connectionInfo && (
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Connection Type:</span>
                      <span className="font-medium capitalize">
                        {connectionInfo.effectiveType || 'Unknown'}
                      </span>
                    </div>
                    {connectionInfo.downlink && (
                      <div className="flex justify-between text-sm">
                        <span>Downlink Speed:</span>
                        <span className="font-medium">
                          {connectionInfo.downlink} Mbps
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Storage Overview */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5" />
                  <CardTitle>Storage Usage</CardTitle>
                </div>
                <CardDescription>
                  Current storage consumption and availability
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Used Storage</span>
                      <span>{formatBytes(storageEstimate?.usage)} / {formatBytes(storageEstimate?.quota)}</span>
                    </div>
                    <Progress value={getStoragePercentage()} className="h-2" />
                    <div className="text-xs text-gray-500">
                      {getStoragePercentage().toFixed(1)}% of available storage
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* PWA Features */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  <CardTitle>PWA Features</CardTitle>
                </div>
                <CardDescription>
                  Available Progressive Web App capabilities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Service Worker</span>
                    <Badge className={'serviceWorker' in navigator ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'serviceWorker' in navigator ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Push Notifications</span>
                    <Badge className={'Notification' in window ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'Notification' in window ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Background Sync</span>
                    <Badge className={'serviceWorker' in navigator ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'serviceWorker' in navigator ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cache Storage</span>
                    <Badge className={'caches' in window ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'caches' in window ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Installation Tab */}
        <TabsContent value="installation">
          <div className="space-y-6">
            <InstallPrompt />
            <Card>
              <CardHeader>
                <CardTitle>Installation Status</CardTitle>
                <CardDescription>
                  Manage app installation and display options
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>App Installation Status</span>
                    <Badge className={isInstalled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}>
                      {isInstalled ? 'Installed' : 'Not Installed'}
                    </Badge>
                  </div>
                  
                  {canInstall && (
                    <div className="flex items-center justify-between">
                      <span>Installation Available</span>
                      <Badge className="bg-blue-100 text-blue-800">
                        Ready to Install
                      </Badge>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <span>Display Mode</span>
                    <Badge className="bg-gray-100 text-gray-600">
                      {window.matchMedia('(display-mode: standalone)').matches ? 'Standalone' : 'Browser'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <PushNotificationManager />
        </TabsContent>

        {/* Sync Tab */}
        <TabsContent value="sync">
          <div className="space-y-6">
            <BackgroundSyncManager />
            <SyncQueueStatus />
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance">
          <PWAPerformanceMonitor />
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>PWA Settings</CardTitle>
              <CardDescription>
                Configure Progressive Web App behavior and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* General Settings */}
              <div className="space-y-4">
                <h4 className="font-medium">General Settings</h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Auto-update</div>
                    <div className="text-xs text-gray-500">
                      Automatically apply updates when available
                    </div>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Background sync</div>
                    <div className="text-xs text-gray-500">
                      Sync data automatically when online
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Offline mode</div>
                    <div className="text-xs text-gray-500">
                      Enable offline functionality
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              {/* Cache Settings */}
              <div className="space-y-4">
                <h4 className="font-medium">Cache Settings</h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Aggressive caching</div>
                    <div className="text-xs text-gray-500">
                      Cache more content for better offline experience
                    </div>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Cache images</div>
                    <div className="text-xs text-gray-500">
                      Store images for offline viewing
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              {/* Debug Settings */}
              <div className="space-y-4">
                <h4 className="font-medium">Debug Settings</h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Debug logging</div>
                    <div className="text-xs text-gray-500">
                      Enable detailed logging for troubleshooting
                    </div>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Performance monitoring</div>
                    <div className="text-xs text-gray-500">
                      Track performance metrics
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-950">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
              <Shield className="h-4 w-4" />
              <span className="font-medium">PWA Error</span>
            </div>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default PWADashboard;