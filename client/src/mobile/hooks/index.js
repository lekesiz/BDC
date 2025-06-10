// TODO: i18n - processed
// Mobile Hooks Index
import { useState, useEffect, useCallback, useRef } from 'react';
import { useMobile } from '../components/MobileProvider';

/**
 * useOrientation - Hook for handling device orientation changes
 */import { useTranslation } from "react-i18next";
export const useOrientation = () => {
  const { orientation } = useMobile();
  const [isLandscape, setIsLandscape] = useState(orientation === 'landscape');

  useEffect(() => {
    setIsLandscape(orientation === 'landscape');
  }, [orientation]);

  return {
    orientation,
    isLandscape,
    isPortrait: !isLandscape
  };
};

/**
 * useDeviceMotion - Hook for device motion and orientation events
 */
export const useDeviceMotion = (options = {}) => {
  const { enabled = true, threshold = 10 } = options;
  const [motion, setMotion] = useState({
    acceleration: { x: 0, y: 0, z: 0 },
    rotationRate: { alpha: 0, beta: 0, gamma: 0 },
    orientation: { alpha: 0, beta: 0, gamma: 0 }
  });

  useEffect(() => {
    if (!enabled) return;

    const handleDeviceMotion = (event) => {
      const { acceleration, rotationRate } = event;
      if (acceleration && rotationRate) {
        setMotion((prev) => ({
          ...prev,
          acceleration: {
            x: Math.abs(acceleration.x) > threshold ? acceleration.x : 0,
            y: Math.abs(acceleration.y) > threshold ? acceleration.y : 0,
            z: Math.abs(acceleration.z) > threshold ? acceleration.z : 0
          },
          rotationRate: {
            alpha: rotationRate.alpha || 0,
            beta: rotationRate.beta || 0,
            gamma: rotationRate.gamma || 0
          }
        }));
      }
    };

    const handleDeviceOrientation = (event) => {
      setMotion((prev) => ({
        ...prev,
        orientation: {
          alpha: event.alpha || 0,
          beta: event.beta || 0,
          gamma: event.gamma || 0
        }
      }));
    };

    window.addEventListener('devicemotion', handleDeviceMotion);
    window.addEventListener('deviceorientation', handleDeviceOrientation);

    return () => {
      window.removeEventListener('devicemotion', handleDeviceMotion);
      window.removeEventListener('deviceorientation', handleDeviceOrientation);
    };
  }, [enabled, threshold]);

  return motion;
};

/**
 * useVibration - Hook for device vibration
 */
export const useVibration = () => {
  const { capabilities } = useMobile();

  const vibrate = useCallback((pattern) => {
    if (capabilities.hasVibration && navigator.vibrate) {
      navigator.vibrate(pattern);
    }
  }, [capabilities.hasVibration]);

  const vibratePattern = useCallback((type) => {
    const patterns = {
      tap: [10],
      double: [10, 50, 10],
      long: [200],
      error: [100, 50, 100],
      success: [10, 50, 10, 50, 10],
      notification: [50, 100, 50]
    };
    vibrate(patterns[type] || patterns.tap);
  }, [vibrate]);

  return {
    vibrate,
    vibratePattern,
    isSupported: capabilities.hasVibration
  };
};

/**
 * useNetworkStatus - Hook for network status monitoring
 */
export const useNetworkStatus = () => {
  const { networkStatus } = useMobile();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory((prev) => [...prev.slice(-9), {
      ...networkStatus,
      timestamp: Date.now()
    }]);
  }, [networkStatus.isOnline, networkStatus.effectiveType]);

  const getAverageSpeed = useCallback(() => {
    if (history.length < 2) return 0;
    const speeds = history.map((h) => h.downlink || 0).filter((s) => s > 0);
    return speeds.length > 0 ? speeds.reduce((a, b) => a + b) / speeds.length : 0;
  }, [history]);

  return {
    ...networkStatus,
    history,
    averageSpeed: getAverageSpeed(),
    isStable: history.length >= 5 && history.slice(-5).every((h) => h.isOnline)
  };
};

/**
 * useBattery - Hook for battery status
 */
export const useBattery = () => {
  const [battery, setBattery] = useState({
    level: 1,
    charging: true,
    chargingTime: Infinity,
    dischargingTime: Infinity,
    supported: false
  });

  useEffect(() => {
    if ('getBattery' in navigator) {
      navigator.getBattery().then((batteryManager) => {
        const updateBattery = () => {
          setBattery({
            level: batteryManager.level,
            charging: batteryManager.charging,
            chargingTime: batteryManager.chargingTime,
            dischargingTime: batteryManager.dischargingTime,
            supported: true
          });
        };

        updateBattery();

        batteryManager.addEventListener('chargingchange', updateBattery);
        batteryManager.addEventListener('levelchange', updateBattery);
        batteryManager.addEventListener('chargingtimechange', updateBattery);
        batteryManager.addEventListener('dischargingtimechange', updateBattery);

        return () => {
          batteryManager.removeEventListener('chargingchange', updateBattery);
          batteryManager.removeEventListener('levelchange', updateBattery);
          batteryManager.removeEventListener('chargingtimechange', updateBattery);
          batteryManager.removeEventListener('dischargingtimechange', updateBattery);
        };
      });
    }
  }, []);

  return battery;
};

/**
 * useWakeLock - Hook for screen wake lock
 */
export const useWakeLock = () => {
  const [wakeLock, setWakeLock] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported('wakeLock' in navigator);
  }, []);

  const requestWakeLock = useCallback(async () => {
    if (!isSupported) return false;

    try {
      const lock = await navigator.wakeLock.request('screen');
      setWakeLock(lock);
      return true;
    } catch (error) {
      console.warn('Wake lock request failed:', error);
      return false;
    }
  }, [isSupported]);

  const releaseWakeLock = useCallback(async () => {
    if (wakeLock) {
      await wakeLock.release();
      setWakeLock(null);
    }
  }, [wakeLock]);

  // Auto-release on page visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && wakeLock) {
        releaseWakeLock();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [wakeLock, releaseWakeLock]);

  return {
    isSupported,
    isActive: !!wakeLock,
    requestWakeLock,
    releaseWakeLock
  };
};

/**
 * useInstallPrompt - Hook for PWA install prompt
 */
export const useInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    setIsInstalled(window.matchMedia('(display-mode: standalone)').matches);

    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const promptInstall = useCallback(async () => {
    if (!deferredPrompt) return false;

    try {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      setDeferredPrompt(null);
      setIsInstallable(false);
      return outcome === 'accepted';
    } catch (error) {
      console.warn('Install prompt failed:', error);
      return false;
    }
  }, [deferredPrompt]);

  return {
    isInstallable,
    isInstalled,
    promptInstall
  };
};

/**
 * useShare - Hook for Web Share API
 */
export const useShare = () => {
  const { capabilities } = useMobile();

  const share = useCallback(async (data) => {
    if (capabilities.hasShare && navigator.share) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.warn('Share failed:', error);
        }
        return false;
      }
    }
    return false;
  }, [capabilities.hasShare]);

  const canShare = useCallback((data) => {
    return capabilities.hasShare && navigator.canShare && navigator.canShare(data);
  }, [capabilities.hasShare]);

  return {
    share,
    canShare,
    isSupported: capabilities.hasShare
  };
};

/**
 * useVisibility - Hook for page visibility
 */
export const useVisibility = () => {
  const [isVisible, setIsVisible] = useState(!document.hidden);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return isVisible;
};

/**
 * useKeyboard - Hook for virtual keyboard detection
 */
export const useKeyboard = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [height, setHeight] = useState(0);
  const initialViewportHeight = useRef(window.innerHeight);

  useEffect(() => {
    const handleResize = () => {
      const currentHeight = window.innerHeight;
      const heightDifference = initialViewportHeight.current - currentHeight;

      // Consider keyboard open if viewport shrunk significantly
      const keyboardOpen = heightDifference > 150;

      setIsOpen(keyboardOpen);
      setHeight(keyboardOpen ? heightDifference : 0);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return { isOpen, height };
};

/**
 * useConnectionQuality - Hook for connection quality assessment
 */
export const useConnectionQuality = () => {
  const { networkStatus } = useMobile();
  const [quality, setQuality] = useState('unknown');

  useEffect(() => {
    const assessQuality = () => {
      if (!networkStatus.isOnline) {
        setQuality('offline');
        return;
      }

      const { effectiveType, downlink, rtt, saveData } = networkStatus;

      if (saveData) {
        setQuality('poor');
        return;
      }

      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        setQuality('poor');
      } else if (effectiveType === '3g' || downlink && downlink < 1.5 || rtt && rtt > 300) {
        setQuality('fair');
      } else if (effectiveType === '4g' || downlink && downlink >= 1.5) {
        setQuality('good');
      } else {
        setQuality('unknown');
      }
    };

    assessQuality();
  }, [networkStatus]);

  return quality;
};