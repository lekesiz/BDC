// TODO: i18n - processed
/**
 * useRealtime Hook
 * 
 * Custom hook for managing real-time connections and subscriptions
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { io } from 'socket.io-client';
import RealtimeService from '../services/realtimeService';import { useTranslation } from "react-i18next";

const useRealtime = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [subscriptions, setSubscriptions] = useState([]);
  const [latestData, setLatestData] = useState(null);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState({
    totalUpdates: 0,
    totalErrors: 0,
    averageLatency: 0,
    uptime: 0
  });

  const socketRef = useRef(null);
  const serviceRef = useRef(null);
  const statisticsRef = useRef(statistics);
  const connectTimeRef = useRef(null);

  // Initialize connection
  useEffect(() => {
    initializeConnection();

    return () => {
      cleanup();
    };
  }, []);

  // Update statistics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (connectTimeRef.current) {
        const uptime = (Date.now() - connectTimeRef.current) / 1000;
        statisticsRef.current = {
          ...statisticsRef.current,
          uptime
        };
        setStatistics({ ...statisticsRef.current });
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const initializeConnection = useCallback(() => {
    try {
      setConnectionStatus('connecting');

      // Initialize Socket.IO client
      const socketUrl = process.env.REACT_APP_SOCKET_URL || 'ws://localhost:5000';
      socketRef.current = io(socketUrl, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true
      });

      // Initialize realtime service
      serviceRef.current = new RealtimeService(socketRef.current);

      // Socket event handlers
      socketRef.current.on('connect', handleConnect);
      socketRef.current.on('disconnect', handleDisconnect);
      socketRef.current.on('connect_error', handleConnectionError);
      socketRef.current.on('report_data', handleReportData);
      socketRef.current.on('report_error', handleReportError);
      socketRef.current.on('system_notification', handleSystemNotification);

    } catch (err) {
      console.error('Failed to initialize connection:', err);
      setError(err);
      setConnectionStatus('error');
    }
  }, []);

  const handleConnect = useCallback(() => {
    setIsConnected(true);
    setConnectionStatus('connected');
    setError(null);
    connectTimeRef.current = Date.now();

    console.log('Connected to real-time server');
  }, []);

  const handleDisconnect = useCallback((reason) => {
    setIsConnected(false);
    setConnectionStatus('disconnected');
    connectTimeRef.current = null;

    console.log('Disconnected from real-time server:', reason);

    // Attempt to reconnect if not intentional
    if (reason === 'io server disconnect') {
      setTimeout(() => {
        if (socketRef.current) {
          socketRef.current.connect();
        }
      }, 5000);
    }
  }, []);

  const handleConnectionError = useCallback((error) => {
    setConnectionStatus('error');
    setError(error);

    statisticsRef.current = {
      ...statisticsRef.current,
      totalErrors: statisticsRef.current.totalErrors + 1
    };
    setStatistics({ ...statisticsRef.current });

    console.error('Connection error:', error);
  }, []);

  const handleReportData = useCallback((data) => {
    setLatestData(data);
    setError(null);

    // Update statistics
    statisticsRef.current = {
      ...statisticsRef.current,
      totalUpdates: statisticsRef.current.totalUpdates + 1
    };
    setStatistics({ ...statisticsRef.current });

    console.log('Received report data:', data);
  }, []);

  const handleReportError = useCallback((errorData) => {
    const error = new Error(errorData.error || 'Report error');
    setError(error);

    statisticsRef.current = {
      ...statisticsRef.current,
      totalErrors: statisticsRef.current.totalErrors + 1
    };
    setStatistics({ ...statisticsRef.current });

    console.error('Report error:', errorData);
  }, []);

  const handleSystemNotification = useCallback((notification) => {
    console.log('System notification:', notification);

    // Handle different notification types
    switch (notification.notification_type) {
      case 'error':
        setError(new Error(notification.message));
        break;
      case 'warning':
        // Could show a toast or other warning UI
        break;
      case 'info':
        // Could show an info message
        break;
      default:
        break;
    }
  }, []);

  const subscribe = useCallback(async (subscriptionConfig) => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.subscribe(subscriptionConfig);

      if (result.success) {
        setSubscriptions((prev) => [
        ...prev,
        {
          id: result.subscription_id,
          config: subscriptionConfig,
          status: 'active',
          created_at: new Date().toISOString()
        }]
        );
      }

      return result;
    } catch (err) {
      console.error('Failed to subscribe:', err);
      throw err;
    }
  }, [isConnected]);

  const unsubscribe = useCallback(async (subscriptionId) => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.unsubscribe(subscriptionId);

      if (result) {
        setSubscriptions((prev) =>
        prev.filter((sub) => sub.id !== subscriptionId)
        );
      }

      return result;
    } catch (err) {
      console.error('Failed to unsubscribe:', err);
      throw err;
    }
  }, [isConnected]);

  const updateSubscription = useCallback(async (subscriptionId, updates) => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.updateSubscription(subscriptionId, updates);

      if (result.success) {
        setSubscriptions((prev) =>
        prev.map((sub) =>
        sub.id === subscriptionId ?
        { ...sub, config: { ...sub.config, ...updates } } :
        sub
        )
        );
      }

      return result;
    } catch (err) {
      console.error('Failed to update subscription:', err);
      throw err;
    }
  }, [isConnected]);

  const triggerManualUpdate = useCallback(async (subscriptionId) => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.triggerManualUpdate(subscriptionId);
      return result;
    } catch (err) {
      console.error('Failed to trigger manual update:', err);
      throw err;
    }
  }, [isConnected]);

  const getSubscriptionStatus = useCallback(async (subscriptionId) => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.getSubscriptionStatus(subscriptionId);
      return result;
    } catch (err) {
      console.error('Failed to get subscription status:', err);
      throw err;
    }
  }, [isConnected]);

  const getSystemStats = useCallback(async () => {
    if (!serviceRef.current || !isConnected) {
      throw new Error('Not connected to real-time server');
    }

    try {
      const result = await serviceRef.current.getSystemStats();
      return result;
    } catch (err) {
      console.error('Failed to get system stats:', err);
      throw err;
    }
  }, [isConnected]);

  const reconnect = useCallback(() => {
    if (socketRef.current) {
      setConnectionStatus('connecting');
      socketRef.current.connect();
    } else {
      initializeConnection();
    }
  }, [initializeConnection]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  }, []);

  const cleanup = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.off('connect', handleConnect);
      socketRef.current.off('disconnect', handleDisconnect);
      socketRef.current.off('connect_error', handleConnectionError);
      socketRef.current.off('report_data', handleReportData);
      socketRef.current.off('report_error', handleReportError);
      socketRef.current.off('system_notification', handleSystemNotification);

      socketRef.current.disconnect();
      socketRef.current = null;
    }

    serviceRef.current = null;
    connectTimeRef.current = null;
  }, [handleConnect, handleDisconnect, handleConnectionError, handleReportData, handleReportError, handleSystemNotification]);

  return {
    isConnected,
    connectionStatus,
    subscriptions,
    latestData,
    error,
    statistics,
    subscribe,
    unsubscribe,
    updateSubscription,
    triggerManualUpdate,
    getSubscriptionStatus,
    getSystemStats,
    reconnect,
    disconnect
  };
};

export default useRealtime;