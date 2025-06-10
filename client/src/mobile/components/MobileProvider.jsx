// TODO: i18n - processed
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useMediaQuery } from '@/hooks/useMediaQuery';import { useTranslation } from "react-i18next";

const MobileContext = createContext({});

/**
 * MobileProvider - Comprehensive mobile context provider
 * Manages mobile-specific state, device capabilities, and responsive behavior
 */
export const MobileProvider = ({ children }) => {const { t } = useTranslation();
  // Device detection
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
  const isDesktop = useMediaQuery('(min-width: 1025px)');
  const isTouchDevice = useMediaQuery('(pointer: coarse)');

  // Screen orientation
  const [orientation, setOrientation] = useState('portrait');
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0
  });

  // Mobile capabilities
  const [capabilities, setCapabilities] = useState({
    hasTouch: false,
    hasGyroscope: false,
    hasAccelerometer: false,
    hasGeolocation: false,
    hasCamera: false,
    hasVibration: false,
    hasShare: false,
    hasNotifications: false,
    hasInstallPrompt: false,
    isStandalone: false,
    hasServiceWorker: false
  });

  // Network status
  const [networkStatus, setNetworkStatus] = useState({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    connectionType: 'unknown',
    effectiveType: 'unknown',
    downlink: 0,
    rtt: 0,
    saveData: false
  });

  // Performance metrics
  const [performance, setPerformance] = useState({
    isSlowDevice: false,
    memoryStatus: 'good',
    batteryLevel: 1,
    isCharging: true
  });

  // Mobile settings
  const [settings, setSettings] = useState({
    reducedMotion: false,
    highContrast: false,
    textSize: 'normal',
    darkMode: false,
    hapticFeedback: true,
    autoRotate: true
  });

  // Device capabilities detection
  const detectCapabilities = useCallback(async () => {
    const newCapabilities = { ...capabilities };

    // Touch support
    newCapabilities.hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Gyroscope and accelerometer
    if ('DeviceOrientationEvent' in window) {
      newCapabilities.hasGyroscope = true;
    }
    if ('DeviceMotionEvent' in window) {
      newCapabilities.hasAccelerometer = true;
    }

    // Geolocation
    newCapabilities.hasGeolocation = 'geolocation' in navigator;

    // Camera/Media
    newCapabilities.hasCamera = 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices;

    // Vibration
    newCapabilities.hasVibration = 'vibrate' in navigator;

    // Web Share API
    newCapabilities.hasShare = 'share' in navigator;

    // Notifications
    newCapabilities.hasNotifications = 'Notification' in window;

    // PWA capabilities
    newCapabilities.isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    newCapabilities.hasServiceWorker = 'serviceWorker' in navigator;

    setCapabilities(newCapabilities);
  }, []);

  // Network information detection
  const updateNetworkStatus = useCallback(() => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

    setNetworkStatus((prev) => ({
      ...prev,
      isOnline: navigator.onLine,
      connectionType: connection?.type || 'unknown',
      effectiveType: connection?.effectiveType || 'unknown',
      downlink: connection?.downlink || 0,
      rtt: connection?.rtt || 0,
      saveData: connection?.saveData || false
    }));
  }, []);

  // Performance detection
  const detectPerformance = useCallback(async () => {
    const newPerformance = { ...performance };

    // Device memory (if available)
    if ('deviceMemory' in navigator) {
      newPerformance.isSlowDevice = navigator.deviceMemory <= 2;
      newPerformance.memoryStatus = navigator.deviceMemory <= 2 ? 'low' :
      navigator.deviceMemory <= 4 ? 'medium' : 'high';
    }

    // Battery API (if available)
    if ('getBattery' in navigator) {
      try {
        const battery = await navigator.getBattery();
        newPerformance.batteryLevel = battery.level;
        newPerformance.isCharging = battery.charging;
      } catch (error) {
        console.warn('Battery API not available:', error);
      }
    }

    setPerformance(newPerformance);
  }, []);

  // Accessibility preferences detection
  const detectAccessibilityPreferences = useCallback(() => {
    const newSettings = { ...settings };

    // Reduced motion
    newSettings.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // High contrast
    newSettings.highContrast = window.matchMedia('(prefers-contrast: high)').matches;

    // Color scheme
    newSettings.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

    setSettings(newSettings);
  }, []);

  // Screen size and orientation tracking
  useEffect(() => {
    const updateScreenInfo = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight
      });

      // Update orientation
      if (screen.orientation) {
        setOrientation(screen.orientation.type.includes('portrait') ? 'portrait' : 'landscape');
      } else {
        setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
      }
    };

    updateScreenInfo();
    window.addEventListener('resize', updateScreenInfo);
    window.addEventListener('orientationchange', updateScreenInfo);

    return () => {
      window.removeEventListener('resize', updateScreenInfo);
      window.removeEventListener('orientationchange', updateScreenInfo);
    };
  }, []);

  // Network status tracking
  useEffect(() => {
    updateNetworkStatus();

    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);

    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      connection.addEventListener('change', updateNetworkStatus);
    }

    return () => {
      window.removeEventListener('online', updateNetworkStatus);
      window.removeEventListener('offline', updateNetworkStatus);
      if (connection) {
        connection.removeEventListener('change', updateNetworkStatus);
      }
    };
  }, [updateNetworkStatus]);

  // Initialize capabilities and preferences
  useEffect(() => {
    detectCapabilities();
    detectPerformance();
    detectAccessibilityPreferences();

    // Listen for preference changes
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handlePreferenceChange = () => {
      detectAccessibilityPreferences();
    };

    reducedMotionQuery.addListener(handlePreferenceChange);
    highContrastQuery.addListener(handlePreferenceChange);
    darkModeQuery.addListener(handlePreferenceChange);

    return () => {
      reducedMotionQuery.removeListener(handlePreferenceChange);
      highContrastQuery.removeListener(handlePreferenceChange);
      darkModeQuery.removeListener(handlePreferenceChange);
    };
  }, [detectCapabilities, detectPerformance, detectAccessibilityPreferences]);

  // Utility functions
  const hapticFeedback = useCallback((type = 'light') => {
    if (capabilities.hasVibration && settings.hapticFeedback) {
      const patterns = {
        light: [10],
        medium: [20],
        heavy: [30],
        success: [10, 50, 10],
        error: [50, 100, 50],
        warning: [20, 50, 20]
      };
      navigator.vibrate(patterns[type] || patterns.light);
    }
  }, [capabilities.hasVibration, settings.hapticFeedback]);

  const shareContent = useCallback(async (shareData) => {
    if (capabilities.hasShare) {
      try {
        await navigator.share(shareData);
        return true;
      } catch (error) {
        console.warn('Share failed:', error);
        return false;
      }
    }
    return false;
  }, [capabilities.hasShare]);

  const requestPermission = useCallback(async (permission) => {
    try {
      if (permission === 'notifications' && capabilities.hasNotifications) {
        const result = await Notification.requestPermission();
        return result === 'granted';
      }
      // Add other permission types as needed
      return false;
    } catch (error) {
      console.warn(`Permission request failed for ${permission}:`, error);
      return false;
    }
  }, [capabilities]);

  const contextValue = {
    // Device information
    isMobile,
    isTablet,
    isDesktop,
    isTouchDevice,
    orientation,
    screenSize,

    // Capabilities
    capabilities,

    // Network status
    networkStatus,

    // Performance
    performance,

    // Settings
    settings,
    updateSettings: setSettings,

    // Utility functions
    hapticFeedback,
    shareContent,
    requestPermission,

    // Helper functions
    isLandscape: orientation === 'landscape',
    isPortrait: orientation === 'portrait',
    isSmallScreen: screenSize.width < 375,
    isMediumScreen: screenSize.width >= 375 && screenSize.width < 768,
    isLargeScreen: screenSize.width >= 768,
    isSlowConnection: networkStatus.effectiveType === 'slow-2g' || networkStatus.effectiveType === '2g',
    isOffline: !networkStatus.isOnline,
    shouldReduceAnimations: settings.reducedMotion || performance.isSlowDevice || networkStatus.saveData
  };

  return (
    <MobileContext.Provider value={contextValue}>
      {children}
    </MobileContext.Provider>);

};

/**
 * Hook to access mobile context
 */
export const useMobile = () => {
  const context = useContext(MobileContext);
  if (!context) {
    throw new Error('useMobile must be used within a MobileProvider');
  }
  return context;
};

export default MobileProvider;