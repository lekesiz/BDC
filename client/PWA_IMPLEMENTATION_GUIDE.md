# BDC Progressive Web App (PWA) Implementation Guide

## Overview

The BDC client application has been enhanced with comprehensive Progressive Web App (PWA) features to provide a native app-like experience while maintaining web accessibility. This implementation includes offline functionality, push notifications, app installation, performance optimizations, and automatic updates.

## 🚀 Features Implemented

### 1. Service Worker (`/public/sw.js`)
- **Caching Strategies**: Cache-first for static assets, network-first for API calls
- **Offline Support**: Automatic fallback to cached content when offline
- **Background Sync**: Queue actions while offline and sync when connection returns
- **Update Management**: Automatic detection and installation of new versions
- **Push Notifications**: Handle incoming push notifications with actions

### 2. Web App Manifest (`/public/manifest.json`)
- **Native App Experience**: Standalone display mode with custom theme colors
- **App Icons**: Multiple sizes including maskable icons for adaptive displays
- **Shortcuts**: Quick access to main app sections (Dashboard, Beneficiaries, etc.)
- **File Handling**: Support for PDF, DOCX, and XLSX files
- **Screenshots**: App store-ready screenshots for installation prompts

### 3. PWA Components (`/src/components/pwa/`)

#### Installation Components
- `InstallPrompt`: Rich installation prompt with benefits and step-by-step guide
- `FloatingInstallButton`: Minimalist floating install button
- `InstallBanner`: Full-width installation banner

#### Update Components
- `UpdateNotification`: Detailed update notification with version info
- `UpdateBanner`: Minimal update banner for quick updates
- `UpdateStatus`: Status indicator for update availability

#### Offline Components
- `OfflineIndicator`: Connection status with sync queue information
- `OfflineBanner`: Full-width offline notification with pending count
- `ConnectionQualityIndicator`: Visual connection quality indicator

#### Notification Components
- `NotificationManager`: Complete push notification management interface
- `NotificationPermissionPrompt`: Permission request with benefits explanation
- `NotificationStatusBadge`: Simple notification status indicator

### 4. PWA Hooks (`/src/hooks/usePWA.js`)
- `usePWA`: Main PWA hook with all functionality
- `useInstallPrompt`: Installation management
- `useAppUpdate`: Update detection and application
- `useOnlineStatus`: Connection monitoring
- `useBackgroundSync`: Offline action queuing
- `usePushNotifications`: Push notification management
- `useStorageManager`: Cache and storage management

### 5. Performance Optimizations (`/src/utils/pwaOptimizations.js`)
- **Resource Preloader**: Intelligent preloading of critical resources
- **Lazy Loader**: Intersection Observer-based lazy loading
- **Code Splitter**: Dynamic imports with error handling and retry logic
- **Resource Prioritizer**: Automatic identification of critical resources

### 6. Backend Push Notifications (`/server/`)
- **Push Service**: Complete web push implementation with VAPID keys
- **API Routes**: RESTful endpoints for subscription management
- **Templates**: Pre-defined notification templates for common scenarios
- **Analytics**: Subscription statistics and delivery tracking

## 📱 Installation

### Client Setup

1. **Install Dependencies**
   ```bash
   cd client
   npm install
   # All PWA dependencies are already included in package.json
   ```

2. **Configure Environment Variables**
   ```bash
   # Add to .env.local
   VITE_VAPID_PUBLIC_KEY=your_vapid_public_key
   VITE_API_BASE_URL=your_api_base_url
   ```

3. **Generate App Icons**
   ```bash
   # Create icons in /public/icons/ directory
   # Use PWA Icon Generator: https://www.pwabuilder.com/imageGenerator
   # Required sizes: 72, 96, 128, 144, 152, 192, 384, 512
   ```

### Server Setup

1. **Install Dependencies**
   ```bash
   cd server
   pip install pywebpush cryptography
   ```

2. **Generate VAPID Keys**
   ```python
   from pywebpush import webpush
   vapid_private_key = webpush.generate_vapid_keys()
   print("Private Key:", vapid_private_key['private_key'])
   print("Public Key:", vapid_private_key['public_key'])
   ```

3. **Configure Environment Variables**
   ```bash
   # Add to .env
   VAPID_PRIVATE_KEY=your_vapid_private_key
   VAPID_PUBLIC_KEY=your_vapid_public_key
   VAPID_CLAIM_EMAIL=admin@yourdomain.com
   ```

4. **Run Database Migration**
   ```bash
   flask db upgrade
   # This adds push notification support to the database
   ```

## 🎯 Usage

### Basic Integration

```jsx
import React from 'react';
import { PWAProvider } from './components/pwa';

function App() {
  return (
    <PWAProvider
      showInstallPrompt={true}
      showUpdateNotifications={true}
      showOfflineIndicators={true}
      showNotificationPrompts={true}
    >
      {/* Your app content */}
    </PWAProvider>
  );
}
```

### Advanced Usage

#### Custom Installation Flow
```jsx
import { useInstallPrompt } from './hooks/usePWA';

function CustomInstallButton() {
  const { canInstall, promptInstall, isLoading } = useInstallPrompt();
  
  if (!canInstall) return null;
  
  return (
    <button onClick={promptInstall} disabled={isLoading}>
      {isLoading ? 'Installing...' : 'Install App'}
    </button>
  );
}
```

#### Offline Data Management
```jsx
import { useBackgroundSync } from './hooks/usePWA';

function OfflineForm() {
  const { addToSyncQueue, syncQueue } = useBackgroundSync();
  
  const handleSubmit = async (data) => {
    try {
      // Try to submit online first
      await submitData(data);
    } catch (error) {
      // Queue for offline sync
      await addToSyncQueue('form-submissions', data);
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Form fields */}
      </form>
      {syncQueue.length > 0 && (
        <p>{syncQueue.length} items waiting to sync</p>
      )}
    </div>
  );
}
```

#### Performance Optimization
```jsx
import { OptimizedImage, RoutePreloader } from './components/pwa';

function OptimizedPage() {
  return (
    <RoutePreloader routes={appRoutes}>
      <div>
        <OptimizedImage
          src="/images/hero.jpg"
          alt="Hero image"
          priority={true}
          sizes="(max-width: 768px) 100vw, 50vw"
        />
        {/* Other content */}
      </div>
    </RoutePreloader>
  );
}
```

#### Push Notifications
```jsx
import { usePushNotifications } from './hooks/usePWA';

function NotificationSettings() {
  const { permission, subscribe, isLoading } = usePushNotifications();
  
  const handleSubscribe = async () => {
    try {
      const subscription = await subscribe();
      // Send subscription to server
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('Subscription failed:', error);
    }
  };
  
  return (
    <div>
      <p>Notification permission: {permission}</p>
      {permission === 'default' && (
        <button onClick={handleSubscribe} disabled={isLoading}>
          Enable Notifications
        </button>
      )}
    </div>
  );
}
```

## 🔧 Configuration

### Service Worker Configuration
```javascript
// In /public/sw.js
const CACHE_NAME = 'bdc-pwa-v1.0.0';
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/src/main.jsx',
  // Add your critical assets
];
```

### Manifest Configuration
```json
{
  "name": "BDC - Beneficiary Development Center",
  "short_name": "BDC",
  "theme_color": "#3b82f6",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

### Push Notification Templates
```python
# Server-side templates
templates = {
    'evaluation_available': {
        'title': 'New Evaluation Available',
        'body': 'A new evaluation "{evaluation_title}" is available',
        'data': {'type': 'evaluation', 'url': '/evaluations'}
    }
}
```

## 📊 Monitoring and Analytics

### Performance Monitoring
```javascript
import { PWAOptimizations } from './utils/pwaOptimizations';

// Get performance metrics
const metrics = PWAOptimizations.getPerformanceInfo();
console.log('PWA Performance:', metrics);
```

### Storage Management
```javascript
import { useStorageManager } from './hooks/usePWA';

function StorageStatus() {
  const { storageEstimate, clearCache } = useStorageManager();
  
  return (
    <div>
      <p>Used: {storageEstimate?.usage} / {storageEstimate?.quota}</p>
      <button onClick={() => clearCache('api-cache')}>
        Clear API Cache
      </button>
    </div>
  );
}
```

### Push Notification Analytics
```bash
# API endpoint for statistics
GET /api/push/stats
{
  "total_users": 1000,
  "subscribed_users": 750,
  "subscription_rate": 75.0,
  "notifications_today": 45
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Service Worker Not Registering**
   - Ensure HTTPS is enabled (required for PWA)
   - Check browser console for registration errors
   - Verify sw.js is accessible at the root

2. **Push Notifications Not Working**
   - Verify VAPID keys are correctly configured
   - Check notification permissions in browser
   - Ensure valid subscription endpoint

3. **Install Prompt Not Showing**
   - PWA criteria must be met (manifest, service worker, HTTPS)
   - Install prompt is limited by browser policies
   - Check manifest.json for validation errors

4. **Offline Functionality Issues**
   - Verify service worker is caching required resources
   - Check network tab in dev tools for cache hits
   - Ensure offline.html page exists

### Debug Tools
```javascript
import { PWADevTools } from './utils/pwaIntegration';

// Debug PWA state
PWADevTools.debug();

// Test PWA features
PWADevTools.test();

// Simulate offline mode
PWADevTools.simulateOffline();
```

### Browser DevTools
1. **Application Tab**
   - Check Service Workers status
   - Inspect Cache Storage
   - View Manifest

2. **Network Tab**
   - Monitor cache hits/misses
   - Check offline behavior
   - Verify resource loading

3. **Console**
   - Service Worker logs
   - PWA initialization messages
   - Error debugging

## 🔮 Future Enhancements

### Planned Features
- **Web Share API**: Share content from the app
- **Background Fetch**: Large file downloads while offline
- **Contact Picker**: Native contact selection
- **Web Bluetooth**: IoT device integration
- **Badging API**: App icon badges for notifications

### Performance Improvements
- **Critical Resource Hints**: Preload/prefetch optimization
- **Image Optimization**: WebP format with fallbacks
- **Bundle Splitting**: Route-based code splitting
- **Service Worker Streaming**: Faster response times

## 📚 Resources

### Documentation
- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google PWA Checklist](https://web.dev/pwa-checklist/)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)

### Tools
- [PWA Builder](https://www.pwabuilder.com/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Workbox](https://developers.google.com/web/tools/workbox)

### Testing
- [PWA Testing Guide](https://web.dev/pwa-testing/)
- [Chrome DevTools PWA](https://developers.google.com/web/tools/chrome-devtools/progressive-web-apps)

## 🤝 Contributing

When contributing to PWA features:

1. **Test across browsers**: Chrome, Firefox, Safari, Edge
2. **Verify offline functionality**: Test with throttled/offline network
3. **Check performance impact**: Monitor bundle size and load times
4. **Update documentation**: Keep this guide current with changes
5. **Follow PWA best practices**: Refer to web.dev guidelines

## 📄 License

This PWA implementation is part of the BDC project and follows the same licensing terms.