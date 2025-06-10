# Progressive Web App (PWA) Implementation

This comprehensive PWA implementation provides advanced features for the BDC application, including offline functionality, push notifications, background sync, and app installation capabilities.

## Features

### ✅ Core PWA Features
- **Service Worker**: Advanced caching strategies with IndexedDB integration
- **Web App Manifest**: Complete manifest with advanced features
- **App Installation**: Cross-platform installation prompts and management
- **Offline Support**: Comprehensive offline functionality with error handling
- **Background Sync**: Automatic data synchronization when connection is restored
- **Push Notifications**: Real-time notifications with permission management
- **Performance Monitoring**: PWA metrics tracking and optimization
- **Cache Management**: Intelligent caching with quota enforcement

### 🎯 Advanced Features
- **IndexedDB Integration**: Persistent storage for offline data
- **Performance Monitoring**: Real-time PWA metrics and optimization suggestions
- **Connection Quality Detection**: Adaptive behavior based on network conditions
- **Offline Error Boundary**: Context-aware error handling for offline scenarios
- **PWA Dashboard**: Comprehensive management interface
- **Widget Support**: Home screen widgets (where supported)
- **File Handling**: Associate file types with the PWA

## Components

### Core Components

#### PWAProvider
Central provider component that manages PWA state and provides context to child components.

```jsx
import { PWAProvider } from './components/pwa';

function App() {
  return (
    <PWAProvider
      showInstallPrompt={true}
      showUpdateNotifications={true}
      showOfflineIndicators={true}
      showNotificationPrompts={true}
      installPromptDelay={5000}
    >
      {/* Your app content */}
    </PWAProvider>
  );
}
```

#### PWADashboard
Comprehensive dashboard for managing all PWA features.

```jsx
import { PWADashboard } from './components/pwa';

function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <PWADashboard />
    </div>
  );
}
```

### Installation Components

#### InstallPrompt
Rich installation prompt with benefits and platform-specific instructions.

```jsx
import { InstallPrompt } from './components/pwa';

function HomePage() {
  return (
    <div>
      <InstallPrompt onDismiss={() => console.log('Install prompt dismissed')} />
    </div>
  );
}
```

#### FloatingInstallButton
Minimal floating action button for app installation.

```jsx
import { FloatingInstallButton } from './components/pwa';

function Layout() {
  return (
    <div>
      {/* Your layout content */}
      <FloatingInstallButton />
    </div>
  );
}
```

### Background Sync Components

#### BackgroundSyncManager
Manages offline actions and background synchronization.

```jsx
import { BackgroundSyncManager } from './components/pwa';

function SyncPage() {
  return <BackgroundSyncManager />;
}
```

### Push Notification Components

#### PushNotificationManager
Complete push notification management with permission handling.

```jsx
import { PushNotificationManager } from './components/pwa';

function NotificationSettings() {
  return <PushNotificationManager />;
}
```

### Performance Monitoring

#### PWAPerformanceMonitor
Real-time PWA performance metrics and optimization suggestions.

```jsx
import { PWAPerformanceMonitor } from './components/pwa';

function PerformancePage() {
  return <PWAPerformanceMonitor />;
}
```

### Error Handling

#### OfflineErrorBoundary
Context-aware error boundary for offline scenarios.

```jsx
import { OfflineErrorBoundary } from './components/pwa';

function App() {
  return (
    <OfflineErrorBoundary>
      {/* Your app content */}
    </OfflineErrorBoundary>
  );
}
```

## Hooks

### usePWA
Main PWA hook providing comprehensive functionality.

```jsx
import { usePWA } from './hooks/usePWA';

function MyComponent() {
  const {
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
    clearError
  } = usePWA();

  return (
    <div>
      <p>Status: {isOnline ? 'Online' : 'Offline'}</p>
      {canInstall && <button onClick={install}>Install App</button>}
      {hasUpdate && <button onClick={update}>Update App</button>}
    </div>
  );
}
```

### useInstallPrompt
Focused hook for app installation management.

```jsx
import { useInstallPrompt } from './hooks/usePWA';

function InstallButton() {
  const { canInstall, isInstalled, isLoading, promptInstall } = useInstallPrompt();

  if (isInstalled || !canInstall) return null;

  return (
    <button onClick={promptInstall} disabled={isLoading}>
      {isLoading ? 'Installing...' : 'Install App'}
    </button>
  );
}
```

### useBackgroundSync
Manage background synchronization.

```jsx
import { useBackgroundSync } from './hooks/usePWA';

function DataComponent() {
  const { syncQueue, isSyncing, addToSyncQueue } = useBackgroundSync();

  const saveData = async (data) => {
    try {
      // Try to save online first
      await fetch('/api/data', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      // Queue for background sync if offline
      await addToSyncQueue('data-save', data);
    }
  };

  return (
    <div>
      <p>Pending sync items: {syncQueue.length}</p>
      {isSyncing && <p>Syncing...</p>}
    </div>
  );
}
```

### usePushNotifications
Manage push notifications.

```jsx
import { usePushNotifications } from './hooks/usePWA';

function NotificationButton() {
  const {
    permission,
    subscription,
    isLoading,
    requestPermission,
    subscribe
  } = usePushNotifications();

  const handleEnable = async () => {
    if (permission === 'default') {
      await requestPermission();
    }
    if (permission === 'granted' && !subscription) {
      await subscribe();
    }
  };

  return (
    <button onClick={handleEnable} disabled={isLoading}>
      {permission === 'granted' ? 'Subscribe' : 'Enable Notifications'}
    </button>
  );
}
```

## Service Worker Features

### Advanced Caching Strategies

The service worker implements multiple caching strategies:

- **Cache First**: Static assets (CSS, JS, images)
- **Network First**: API endpoints with cache fallback
- **Stale While Revalidate**: HTML pages for fast loading

### IndexedDB Integration

Persistent storage for:
- Background sync queue
- Offline user actions
- Performance metrics
- Error logs

### Performance Monitoring

Automatic tracking of:
- Cache hit rates
- Network response times
- Offline usage patterns
- Storage consumption

## Configuration

### Environment Variables

```env
# PWA Configuration
VITE_PWA_ENABLED=true
VITE_PWA_CACHE_SIZE_LIMIT=100
VITE_PWA_OFFLINE_FALLBACK=true
VITE_PWA_BACKGROUND_SYNC=true
VITE_PWA_PUSH_NOTIFICATIONS=true
VITE_PWA_PERFORMANCE_MONITORING=true

# Push Notification Configuration
VITE_VAPID_PUBLIC_KEY=your_vapid_public_key
VITE_PUSH_NOTIFICATION_ENDPOINT=https://your-server.com/api/push
```

### Manifest Configuration

The web app manifest includes:
- App metadata and branding
- Icon sets (including maskable icons)
- Display modes and orientations
- Shortcuts and widgets
- File handlers
- Protocol handlers
- Share targets

## Best Practices

### Performance
- Use appropriate caching strategies for different content types
- Implement cache size limits and cleanup
- Monitor cache hit rates and storage usage
- Preload critical resources

### Offline Experience
- Provide meaningful offline pages
- Show clear offline indicators
- Queue user actions for background sync
- Handle network errors gracefully

### Installation
- Use platform-appropriate install prompts
- Provide clear installation benefits
- Handle installation state changes
- Track installation metrics

### Notifications
- Request permissions contextually
- Provide notification categories
- Handle permission denied gracefully
- Respect user preferences

### Background Sync
- Queue failed requests automatically
- Implement retry logic with exponential backoff
- Handle sync failures gracefully
- Show sync status to users

## Browser Support

### Full Support
- Chrome/Chromium 67+
- Edge 79+
- Firefox 72+
- Safari 14+ (limited)

### Feature Support Matrix

| Feature | Chrome | Edge | Firefox | Safari |
|---------|--------|------|---------|---------|
| Service Worker | ✅ | ✅ | ✅ | ✅ |
| Web App Manifest | ✅ | ✅ | ✅ | ✅ |
| App Installation | ✅ | ✅ | ❌ | ❌ |
| Push Notifications | ✅ | ✅ | ✅ | ❌ |
| Background Sync | ✅ | ✅ | ❌ | ❌ |
| Badge API | ✅ | ✅ | ❌ | ❌ |
| Web Share | ✅ | ✅ | ❌ | ✅ |

## Testing

### Manual Testing
1. Test offline functionality
2. Verify installation on different platforms
3. Test push notifications
4. Verify background sync
5. Check performance metrics

### Automated Testing
```bash
# Run PWA tests
npm run test:pwa

# Run Lighthouse PWA audit
npm run audit:pwa

# Test service worker
npm run test:sw
```

### Testing Checklist
- [ ] Service worker registers successfully
- [ ] App works offline
- [ ] Installation prompt appears
- [ ] Push notifications work
- [ ] Background sync functions
- [ ] Performance metrics track correctly
- [ ] Error boundaries handle offline errors
- [ ] Cache management works properly

## Deployment

### Build Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 1 day
              }
            }
          }
        ]
      }
    })
  ]
});
```

### Server Configuration
- Serve manifest.json with correct MIME type
- Configure HTTPS (required for PWA features)
- Set up push notification endpoints
- Configure caching headers

## Troubleshooting

### Common Issues

#### Service Worker Not Registering
- Check browser support
- Verify HTTPS is enabled
- Check console for errors
- Ensure service worker file is accessible

#### Installation Prompt Not Showing
- Verify PWA criteria are met
- Check if user has dismissed prompt
- Ensure app is not already installed
- Test beforeinstallprompt event

#### Push Notifications Not Working
- Verify permissions are granted
- Check VAPID keys configuration
- Ensure service worker is active
- Test notification payload

#### Background Sync Failing
- Check network connectivity
- Verify service worker registration
- Inspect sync queue in DevTools
- Check for JavaScript errors

### Debug Tools
- Chrome DevTools > Application > Service Workers
- Chrome DevTools > Application > Storage
- Lighthouse PWA audit
- PWA Dashboard component

## Migration Guide

### From Basic PWA
1. Replace existing service worker with enhanced version
2. Update manifest.json with new features
3. Integrate PWA provider in your app
4. Replace basic install prompt with new components
5. Add background sync and push notifications

### From No PWA
1. Add web app manifest
2. Implement service worker
3. Add PWA provider to app root
4. Integrate PWA components where needed
5. Configure build tools for PWA

## Contributing

### Development Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

### Adding New Features
1. Create component in appropriate directory
2. Add TypeScript types if applicable
3. Write comprehensive tests
4. Update documentation
5. Add to index.js exports

### Code Style
- Follow existing component patterns
- Use TypeScript for type safety
- Write comprehensive tests
- Document props and usage
- Follow accessibility guidelines

## License

This PWA implementation is part of the BDC project and follows the same license terms.