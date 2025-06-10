# Mobile Responsiveness System for BDC

A comprehensive mobile responsiveness system that provides touch-optimized components, advanced gesture support, PWA features, and performance optimizations for the BDC application.

## Features

### 📱 Responsive Design Components
- **ResponsiveContainer**: Adaptive container that adjusts based on device type
- **ResponsiveGrid**: Grid that adapts columns based on screen size
- **ResponsiveFlex**: Flexible container with responsive direction and alignment
- **MobileSafeArea**: Handles safe areas for devices with notches and home indicators

### 👆 Touch Gesture Support
- **Advanced Swipe Detection**: Multi-directional swipe support with velocity tracking
- **Touch Gestures**: Comprehensive touch handling (tap, double-tap, long press, pinch, pan)
- **Pinch-to-Zoom**: Smooth zoom functionality with constraints and animations
- **Haptic Feedback**: Native device vibration integration

### 🧭 Mobile Navigation Patterns
- **MobileTabNavigation**: Bottom/top tab navigation with swipe support
- **MobileSidebar**: Responsive sidebar with search and collapsible groups
- **BreadcrumbNavigation**: Mobile-optimized breadcrumbs with overflow handling
- **Touch-Optimized Components**: All navigation elements optimized for thumb interaction

### 📴 Progressive Web App (PWA) Features
- **Offline Capability**: Intelligent caching and offline data management
- **Background Sync**: Automatic synchronization when connection is restored
- **Push Notifications**: Complete notification management system
- **Install Prompts**: Native app installation experience

### ⚡ Performance Optimizations
- **Lazy Loading**: Smart component and image lazy loading
- **Image Optimization**: Responsive images with format detection
- **Virtual Lists**: High-performance lists for large datasets
- **Network-Aware Loading**: Adapts quality based on connection speed

## Quick Start

### 1. Wrap your app with MobileProvider

```jsx
import { MobileProvider } from '@/mobile';

function App() {
  return (
    <MobileProvider>
      {/* Your app content */}
    </MobileProvider>
  );
}
```

### 2. Use responsive components

```jsx
import { 
  ResponsiveContainer, 
  TouchOptimizedButton,
  MobileTabNavigation 
} from '@/mobile';

function HomePage() {
  return (
    <ResponsiveContainer variant="card" safeArea>
      <h1>Welcome to BDC</h1>
      <TouchOptimizedButton 
        hapticFeedback 
        onClick={() => console.log('Button pressed!')}
      >
        Get Started
      </TouchOptimizedButton>
    </ResponsiveContainer>
  );
}
```

### 3. Add navigation

```jsx
import { MobileTabNavigation } from '@/mobile';
import { Home, User, Settings } from 'lucide-react';

const tabs = [
  { id: 'home', label: 'Home', icon: Home, path: '/' },
  { id: 'profile', label: 'Profile', icon: User, path: '/profile' },
  { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' }
];

function Layout() {
  return (
    <div>
      {/* Your content */}
      <MobileTabNavigation tabs={tabs} />
    </div>
  );
}
```

### 4. Add gesture support

```jsx
import { useAdvancedSwipe } from '@/mobile';

function SwipeableCard() {
  const swipeHandlers = useAdvancedSwipe({
    onSwipeLeft: () => console.log('Swiped left!'),
    onSwipeRight: () => console.log('Swiped right!'),
    threshold: 50
  });

  return (
    <div {...swipeHandlers}>
      Swipe me!
    </div>
  );
}
```

### 5. Enable PWA features

```jsx
import { OfflineCapable, PushNotificationManager } from '@/mobile';

function App() {
  return (
    <OfflineCapable enableOfflineActions syncOnReconnect>
      <PushNotificationManager vapidKey="your-vapid-key">
        {/* Your app */}
      </PushNotificationManager>
    </OfflineCapable>
  );
}
```

## Components

### Core Components

#### MobileProvider
The main context provider that manages mobile state and capabilities.

```jsx
<MobileProvider>
  {/* Your app */}
</MobileProvider>
```

#### ResponsiveContainer
Adaptive container with responsive padding, max-width, and safe area support.

```jsx
<ResponsiveContainer 
  variant="card" 
  safeArea 
  centerContent
  maxWidth="responsive"
>
  Content
</ResponsiveContainer>
```

#### TouchOptimizedButton
Button component optimized for touch interactions with haptic feedback.

```jsx
<TouchOptimizedButton
  variant="default"
  size="lg"
  hapticFeedback
  hapticType="medium"
  rippleEffect
>
  Click me
</TouchOptimizedButton>
```

### Navigation Components

#### MobileTabNavigation
Bottom or top tab navigation with swipe support and badges.

```jsx
<MobileTabNavigation
  tabs={tabs}
  variant="bottom"
  showLabels
  allowSwipeNavigation
  hapticFeedback
/>
```

#### MobileSidebar
Responsive sidebar navigation with search and collapsible groups.

```jsx
<MobileSidebar
  navigation={navigationItems}
  showSearch
  allowGroupCollapse
  showUserProfile
  userProfile={{ name: 'John Doe', email: 'john@example.com' }}
/>
```

### Layout Components

#### MobileLayout
Comprehensive layout with header, navigation, and safe area support.

```jsx
<MobileLayout
  header={<Header />}
  navigation={{ tabs }}
  showTabNavigation
  variant="standard"
>
  <PageContent />
</MobileLayout>
```

#### MobilePageLayout
Layout for individual pages with title, actions, and back button support.

```jsx
<MobilePageLayout
  title="Page Title"
  subtitle="Page description"
  backButton={<BackButton />}
  actions={[<ActionButton key="1" />]}
>
  Page content
</MobilePageLayout>
```

### Performance Components

#### LazyMobileComponent
Optimized lazy loading with intersection observer and preloading.

```jsx
<LazyMobileComponent
  component={() => import('./HeavyComponent')}
  fallback={<LoadingSpinner />}
  preload={false}
  threshold={0.1}
/>
```

#### MobileImageOptimizer
Responsive image optimization with format detection and lazy loading.

```jsx
<MobileImageOptimizer
  src="/image.jpg"
  alt="Description"
  aspectRatio="16:9"
  quality={75}
  formats={['webp', 'jpg']}
  priority={false}
/>
```

#### TouchOptimizedList
High-performance virtualized list with swipe actions and pull-to-refresh.

```jsx
<TouchOptimizedList
  items={data}
  renderItem={(item, index) => <ListItem item={item} />}
  itemHeight={60}
  enableVirtualization
  enableInfiniteScroll
  onLoadMore={loadMore}
  onPullToRefresh={refresh}
/>
```

## Hooks

### Core Hooks

#### useMobile
Access mobile context and device capabilities.

```jsx
const { 
  isMobile, 
  orientation, 
  capabilities, 
  networkStatus,
  hapticFeedback 
} = useMobile();
```

#### useAdvancedSwipe
Advanced swipe gesture detection with velocity tracking.

```jsx
const swipeHandlers = useAdvancedSwipe({
  onSwipeLeft: handleSwipeLeft,
  onSwipeRight: handleSwipeRight,
  threshold: 50,
  velocityThreshold: 0.3,
  direction: 'horizontal'
});
```

#### useTouchGestures
Comprehensive touch gesture support (tap, double-tap, long press, pinch, pan).

```jsx
const gestureHandlers = useTouchGestures({
  onTap: handleTap,
  onDoubleTap: handleDoubleTap,
  onLongPress: handleLongPress,
  onPinch: handlePinch,
  onPan: handlePan
});
```

### Device Hooks

#### useOrientation
Monitor device orientation changes.

```jsx
const { orientation, isLandscape, isPortrait } = useOrientation();
```

#### useNetworkStatus
Monitor network connection status and quality.

```jsx
const { 
  isOnline, 
  effectiveType, 
  downlink, 
  isStable 
} = useNetworkStatus();
```

#### useBattery
Monitor device battery status.

```jsx
const { 
  level, 
  charging, 
  chargingTime, 
  supported 
} = useBattery();
```

#### useVibration
Control device vibration.

```jsx
const { vibrate, vibratePattern, isSupported } = useVibration();

// Usage
vibratePattern('success');
vibrate([100, 50, 100]);
```

### PWA Hooks

#### useOffline
Manage offline functionality and sync queue.

```jsx
const {
  isOnline,
  syncQueue,
  cacheData,
  queueOfflineAction,
  syncOfflineActions
} = useOffline();
```

#### useInstallPrompt
Handle PWA installation prompts.

```jsx
const { 
  isInstallable, 
  isInstalled, 
  promptInstall 
} = useInstallPrompt();
```

#### useShare
Web Share API integration.

```jsx
const { share, canShare, isSupported } = useShare();

// Usage
share({
  title: 'Check this out!',
  text: 'Amazing content',
  url: 'https://example.com'
});
```

## PWA Features

### Offline Capability
Wrap components to provide offline functionality:

```jsx
<OfflineCapable
  enableOfflineActions
  syncOnReconnect
  showOfflineIndicator
  onSyncComplete={handleSyncComplete}
>
  <YourComponent />
</OfflineCapable>
```

### Background Sync
Manage background synchronization:

```jsx
<BackgroundSync
  syncInterval={30000}
  autoSync
  syncOnNetworkChange
  onSyncComplete={handleSyncComplete}
>
  <YourApp />
</BackgroundSync>
```

### Push Notifications
Complete notification management:

```jsx
<PushNotificationManager
  vapidKey="your-vapid-key"
  autoRequestPermission
  onNotificationReceived={handleNotification}
>
  <YourApp />
</PushNotificationManager>
```

## Best Practices

### 1. Always Use MobileProvider
Wrap your app with MobileProvider to access mobile context throughout your application.

### 2. Optimize Touch Targets
Ensure interactive elements are at least 44px in height and width for optimal touch interaction.

### 3. Implement Safe Areas
Use MobileSafeArea or the safeArea prop to handle device notches and home indicators.

### 4. Add Haptic Feedback
Enhance user experience with haptic feedback for touch interactions.

### 5. Handle Network Conditions
Adapt content quality and loading strategies based on network conditions.

### 6. Implement Progressive Enhancement
Start with basic functionality and enhance based on device capabilities.

### 7. Use Lazy Loading
Implement lazy loading for images and components to improve performance.

### 8. Add Offline Support
Provide offline functionality for critical features using the PWA components.

## Performance Considerations

### Image Optimization
- Use responsive images with appropriate breakpoints
- Implement lazy loading for images below the fold
- Choose optimal image formats based on browser support
- Adjust quality based on network conditions

### List Performance
- Use virtualization for lists with more than 50 items
- Implement infinite scrolling for large datasets
- Use TouchOptimizedList for optimal mobile performance

### Bundle Optimization
- Implement code splitting for large components
- Use lazy loading for non-critical features
- Optimize bundle size for slower connections

### Memory Management
- Monitor memory usage on low-end devices
- Implement proper cleanup in useEffect hooks
- Use React.memo for expensive re-renders

## Browser Support

### Modern Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Mobile Browsers
- iOS Safari 13+
- Chrome Mobile 80+
- Samsung Internet 12+
- Firefox Mobile 75+

### PWA Features
- Service Workers: Most modern browsers
- Push Notifications: Chrome, Firefox, Edge
- Install Prompts: Chrome, Edge, Samsung Internet
- Background Sync: Chrome, Edge

## Migration Guide

### From Basic Mobile Support

1. **Install Dependencies**
   ```bash
   npm install react-intersection-observer react-window
   ```

2. **Add MobileProvider**
   ```jsx
   import { MobileProvider } from '@/mobile';
   
   // Wrap your App component
   <MobileProvider>
     <App />
   </MobileProvider>
   ```

3. **Replace Standard Components**
   ```jsx
   // Before
   <button onClick={handleClick}>Click me</button>
   
   // After
   <TouchOptimizedButton onClick={handleClick} hapticFeedback>
     Click me
   </TouchOptimizedButton>
   ```

4. **Add Navigation**
   ```jsx
   // Replace your existing navigation
   <MobileTabNavigation tabs={tabs} />
   ```

5. **Implement PWA Features**
   ```jsx
   <OfflineCapable>
     <PushNotificationManager vapidKey="your-key">
       <YourApp />
     </PushNotificationManager>
   </OfflineCapable>
   ```

## Contributing

When contributing to the mobile system:

1. Follow the existing component patterns
2. Include TypeScript types for new components
3. Add comprehensive JSDoc documentation
4. Test on multiple devices and browsers
5. Consider performance implications
6. Follow accessibility guidelines
7. Include examples in documentation

## Testing

### Component Testing
```jsx
import { render, screen } from '@testing-library/react';
import { MobileProvider } from '@/mobile';

test('renders mobile component', () => {
  render(
    <MobileProvider>
      <YourComponent />
    </MobileProvider>
  );
  
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

### Gesture Testing
```jsx
import { fireEvent } from '@testing-library/react';

test('handles swipe gesture', () => {
  const handleSwipe = jest.fn();
  render(<SwipeableComponent onSwipe={handleSwipe} />);
  
  // Simulate touch events
  fireEvent.touchStart(element, { touches: [{ clientX: 0, clientY: 0 }] });
  fireEvent.touchMove(element, { touches: [{ clientX: 100, clientY: 0 }] });
  fireEvent.touchEnd(element);
  
  expect(handleSwipe).toHaveBeenCalled();
});
```

### PWA Testing
```jsx
test('handles offline state', async () => {
  // Mock navigator.onLine
  Object.defineProperty(navigator, 'onLine', {
    writable: true,
    value: false
  });
  
  render(
    <OfflineCapable>
      <YourComponent />
    </OfflineCapable>
  );
  
  expect(screen.getByText(/offline/i)).toBeInTheDocument();
});
```

This comprehensive mobile system provides everything needed to create responsive, touch-optimized, and PWA-ready mobile experiences for the BDC application.