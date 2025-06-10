// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mobile Module Entry Point
// Comprehensive mobile responsiveness system for BDC

// Components
export * from './components';

// Hooks
export * from './hooks';

// Utilities
export * from './utils';

// Layouts
export * from './layouts';

// Gestures
export * from './gestures';

// Navigation
export * from './navigation';

// PWA Features
export * from './pwa';

// Performance
export * from './performance';

// Types (if using TypeScript)
export * from './types';

// Main mobile provider
export { MobileProvider, useMobile } from './components/MobileProvider';

// Quick exports for commonly used components
export { ResponsiveContainer, ResponsiveGrid, ResponsiveFlex } from './components/ResponsiveContainer';
export { TouchOptimizedButton, FloatingActionButton, TouchOptimizedIconButton } from './components/TouchOptimizedButton';
export { MobileDrawer, MobileBottomSheet, MobileSidebar as MobileDrawerSidebar } from './components/MobileDrawer';
export { SwipeableCard, SwipeableListItem } from './components/SwipeableCard';
export { MobileSafeArea, SafeAreaProvider, SafeAreaView, useSafeAreaInsets } from './components/MobileSafeArea';
export { PullToRefresh, SimplePullToRefresh, useRefreshControl } from './components/PullToRefresh';

// Navigation exports
export {
  MobileTabNavigation,
  MobileTopTabs,
  MobileBottomTabs,
  FloatingTabs,
  ScrollableTabs,
  TabContent } from
'./navigation/MobileTabNavigation';
export { MobileSidebar, SidebarTrigger } from './navigation/MobileSidebar';
export {
  BreadcrumbNavigation,
  CompactBreadcrumb,
  ScrollableBreadcrumb,
  useBreadcrumbs } from
'./navigation/BreadcrumbNavigation';

// Gesture exports
export { useAdvancedSwipe, useSimpleSwipe, useVerticalSwipe } from './gestures/useAdvancedSwipe';
export { useTouchGestures } from './gestures/useTouchGestures';
export { usePinchZoom } from './gestures/usePinchZoom';

// PWA exports
export { OfflineCapable, useOffline, withOfflineCapability } from './pwa/OfflineCapable';
export { BackgroundSync, useBackgroundSync, withBackgroundSync } from './pwa/BackgroundSync';
export { PushNotificationManager, NotificationBell, usePushNotification } from './pwa/PushNotificationManager';

// Performance exports
export {
  LazyMobileComponent,
  LazyImage,
  LazyList,
  withLazyLoading,
  useLazyLoading } from
'./performance/LazyMobileComponent';
export {
  MobileImageOptimizer,
  OptimizedAvatar,
  ResponsiveImage,
  ImageGallery,
  useImagePreloader } from
'./performance/MobileImageOptimizer';
export { TouchOptimizedList, TouchOptimizedVariableList } from './performance/TouchOptimizedList';

// Layout exports
export {
  MobileLayout,
  MobilePageLayout,
  MobileCardLayout,
  MobileListLayout,
  MobileFormLayout } from
'./layouts/MobileLayout';

// Hook exports
export {
  useOrientation,
  useDeviceMotion,
  useVibration,
  useNetworkStatus,
  useBattery,
  useWakeLock,
  useInstallPrompt,
  useShare,
  useVisibility,
  useKeyboard,
  useConnectionQuality } from
'./hooks';