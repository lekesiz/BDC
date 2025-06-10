// Mobile Types Index

/**
 * Device and capability types
 */
export interface DeviceCapabilities {
  hasTouch: boolean;
  hasGyroscope: boolean;
  hasAccelerometer: boolean;
  hasGeolocation: boolean;
  hasCamera: boolean;
  hasVibration: boolean;
  hasShare: boolean;
  hasNotifications: boolean;
  hasInstallPrompt: boolean;
  isStandalone: boolean;
  hasServiceWorker: boolean;
}

export interface NetworkStatus {
  isOnline: boolean;
  connectionType: string;
  effectiveType: string;
  downlink: number;
  rtt: number;
  saveData: boolean;
}

export interface PerformanceMetrics {
  isSlowDevice: boolean;
  memoryStatus: 'low' | 'medium' | 'high';
  batteryLevel: number;
  isCharging: boolean;
}

export interface AccessibilitySettings {
  reducedMotion: boolean;
  highContrast: boolean;
  textSize: 'small' | 'normal' | 'large';
  darkMode: boolean;
  hapticFeedback: boolean;
  autoRotate: boolean;
}

/**
 * Touch and gesture types
 */
export interface TouchPoint {
  x: number;
  y: number;
  id?: number;
  pageX?: number;
  pageY?: number;
}

export interface SwipeGestureConfig {
  onSwipeLeft?: (event: TouchEvent, data: SwipeData) => void;
  onSwipeRight?: (event: TouchEvent, data: SwipeData) => void;
  onSwipeUp?: (event: TouchEvent, data: SwipeData) => void;
  onSwipeDown?: (event: TouchEvent, data: SwipeData) => void;
  onSwipeStart?: (event: TouchEvent, data: TouchPoint) => void;
  onSwipeEnd?: (event: TouchEvent, data: SwipeEndData) => void;
  threshold?: number;
  velocityThreshold?: number;
  timeThreshold?: number;
  maxDuration?: number;
  direction?: 'horizontal' | 'vertical' | 'all';
  enabled?: boolean;
}

export interface SwipeData {
  distance: number;
  velocity: number;
  duration: number;
}

export interface SwipeEndData extends SwipeData {
  direction: 'left' | 'right' | 'up' | 'down' | null;
  isValid: boolean;
  isCancelled: boolean;
}

export interface PinchGestureConfig {
  minZoom?: number;
  maxZoom?: number;
  initialZoom?: number;
  zoomSpeed?: number;
  doubleTapZoom?: number;
  onZoomChange?: (zoom: ZoomData) => void;
  onZoomStart?: () => void;
  onZoomEnd?: (zoom: ZoomData) => void;
  enabled?: boolean;
}

export interface ZoomData {
  scale: number;
  translateX: number;
  translateY: number;
}

/**
 * Navigation types
 */
export interface NavigationTab {
  id: string;
  label: string;
  icon?: React.ComponentType<any>;
  path: string;
  badge?: string | number;
  matchPaths?: string[];
  disabled?: boolean;
}

export interface NavigationItem {
  id: string;
  title: string;
  path?: string;
  icon?: React.ComponentType<any>;
  description?: string;
  badge?: string | number;
  type?: 'item' | 'group' | 'divider';
  children?: NavigationItem[];
  disabled?: boolean;
  exact?: boolean;
  onClick?: () => void;
}

export interface BreadcrumbItem {
  id: string;
  label: string;
  path?: string;
  icon?: React.ComponentType<any>;
  description?: string;
  onClick?: () => void;
}

/**
 * Layout types
 */
export interface ResponsiveBreakpoints {
  mobile?: number;
  tablet?: number;
  desktop?: number;
}

export interface ResponsiveColumns {
  mobile?: number;
  tablet?: number;
  desktop?: number;
}

export interface SafeAreaInsets {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

/**
 * PWA types
 */
export interface SyncQueueItem {
  id: string | number;
  type: string;
  data: any;
  operation: 'upload' | 'download' | 'bidirectional';
  priority: 'high' | 'normal' | 'low';
  retries: number;
  timestamp: number;
  endpoint?: string;
  method?: string;
  headers?: Record<string, string>;
}

export interface OfflineData {
  data: any;
  timestamp: number;
  key: string;
}

export interface NotificationData {
  id: string | number;
  title: string;
  body?: string;
  icon?: string;
  badge?: string;
  image?: string;
  tag?: string;
  timestamp: number;
  read: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  action: string;
  title: string;
  icon?: string;
}

/**
 * Performance types
 */
export interface ImageOptimizationConfig {
  quality?: number;
  formats?: string[];
  breakpoints?: Record<string, number>;
  loading?: 'lazy' | 'eager';
  priority?: boolean;
  placeholder?: 'blur' | 'empty' | 'none';
  blurDataURL?: string;
}

export interface LazyLoadingConfig {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
  preload?: boolean;
}

export interface VirtualListConfig {
  itemHeight?: number;
  overscanCount?: number;
  estimatedItemHeight?: number;
  enableVirtualization?: boolean;
}

/**
 * Component prop types
 */
export interface MobileProviderProps {
  children: React.ReactNode;
}

export interface ResponsiveContainerProps {
  children: React.ReactNode;
  variant?: 'default' | 'card' | 'elevated' | 'glass' | 'sidebar' | 'modal' | 'fullscreen' | 'section';
  padding?: 'none' | 'responsive' | string;
  maxWidth?: 'responsive' | 'full' | string;
  safeArea?: boolean;
  fullHeight?: boolean;
  centerContent?: boolean;
  scrollable?: boolean;
  maintainAspectRatio?: '16:9' | '4:3' | '1:1' | '3:2' | '21:9';
  backgroundBlur?: boolean;
  className?: string;
}

export interface TouchOptimizedButtonProps {
  children: React.ReactNode;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'xl' | 'icon';
  hapticFeedback?: boolean;
  hapticType?: 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning';
  touchOptimized?: boolean;
  pressAnimation?: boolean;
  rippleEffect?: boolean;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  onClick?: (event: React.MouseEvent) => void;
}

export interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  size?: 'sm' | 'md' | 'lg' | 'full' | 'auto';
  backdrop?: boolean;
  backdropBlur?: boolean;
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  swipeToClose?: boolean;
  className?: string;
}

/**
 * Hook return types
 */
export interface UseMobileReturn {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isTouchDevice: boolean;
  orientation: 'portrait' | 'landscape';
  screenSize: { width: number; height: number };
  capabilities: DeviceCapabilities;
  networkStatus: NetworkStatus;
  performance: PerformanceMetrics;
  settings: AccessibilitySettings;
  hapticFeedback: (type?: string) => void;
  shareContent: (data: ShareData) => Promise<boolean>;
  requestPermission: (permission: string) => Promise<boolean>;
  isLandscape: boolean;
  isPortrait: boolean;
  isSmallScreen: boolean;
  isMediumScreen: boolean;
  isLargeScreen: boolean;
  isSlowConnection: boolean;
  isOffline: boolean;
  shouldReduceAnimations: boolean;
}

export interface UseSwipeReturn extends SwipeGestureConfig {
  isSwiping: boolean;
  direction: 'left' | 'right' | 'up' | 'down' | null;
  distance: number;
  velocity: number;
  progress: number;
  onTouchStart: (event: TouchEvent) => void;
  onTouchMove: (event: TouchEvent) => void;
  onTouchEnd: (event: TouchEvent) => void;
}

export interface UseOfflineReturn {
  isOnline: boolean;
  networkStatus: NetworkStatus;
  hasCachedData: boolean;
  offlineData: any;
  syncQueue: SyncQueueItem[];
  syncStatus: 'idle' | 'syncing' | 'success' | 'error';
  lastSyncTime: number | null;
  cacheData: (data: any, key?: string) => Promise<void>;
  queueOfflineAction: (action: any) => string | number;
  removeFromSyncQueue: (id: string | number) => void;
  syncOfflineActions: () => Promise<any[]>;
  retrySyncQueue: () => void;
  clearOfflineCache: () => void;
}

/**
 * Event types
 */
export interface ShareData {
  title?: string;
  text?: string;
  url?: string;
  files?: File[];
}

export interface DeviceMotionData {
  acceleration: { x: number; y: number; z: number };
  rotationRate: { alpha: number; beta: number; gamma: number };
  orientation: { alpha: number; beta: number; gamma: number };
}

/**
 * Utility types
 */
export type Orientation = 'portrait' | 'landscape';
export type DeviceType = 'mobile' | 'tablet' | 'desktop';
export type ConnectionQuality = 'poor' | 'fair' | 'good' | 'excellent' | 'offline' | 'unknown';
export type HapticFeedbackType = 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning';
export type NotificationPermission = 'default' | 'granted' | 'denied';