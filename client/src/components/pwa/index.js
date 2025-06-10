// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // PWA Components Export Index

// Core PWA Provider and Hooks
export { default as PWAProvider, usePWAContext, PWAStatus, PWAControls } from './PWAProvider';

// Installation Components
export { InstallPrompt, FloatingInstallButton, InstallBanner } from './InstallPrompt';

// Update Management
export { UpdateNotification, UpdateBanner, UpdateStatus } from './UpdateNotification';

// Offline & Connection Management
export {
  OfflineIndicator,
  OfflineBanner,
  ConnectionQualityIndicator,
  SyncQueueStatus } from
'./OfflineIndicator';

// Background Sync Components
export {
  default as BackgroundSyncManager,
  SyncStatusIndicator,
  SyncQueueItem } from
'./BackgroundSyncManager';

// Push Notifications
export {
  default as PushNotificationManager,
  NotificationPermissionPrompt,
  NotificationStatusBadge } from
'./PushNotificationManager';

// Performance Monitoring
export { default as PWAPerformanceMonitor } from './PWAPerformanceMonitor';

// Error Handling
export {
  default as OfflineErrorBoundary,
  OfflineErrorBoundaryWrapper,
  withOfflineErrorBoundary } from
'./OfflineErrorBoundary';

// Legacy exports for backward compatibility
export {
  PushNotificationManager as NotificationManager,
  NotificationPermissionPrompt,
  NotificationStatusBadge } from
'./PushNotificationManager';

// Re-export hooks for convenience
export {
  usePWA,
  useInstallPrompt,
  useAppUpdate,
  useOnlineStatus,
  useBackgroundSync,
  usePushNotifications,
  useStorageManager } from
'../../hooks/usePWA';

// Re-export service for advanced usage
export { default as pwaService } from '../../services/pwa.service';