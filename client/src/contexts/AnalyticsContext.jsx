// Real-time Analytics Context
// Provides real-time analytics data with WebSocket integration

import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from 'react';
import { useSocket } from './SocketContext';
import analyticsService from '@/services/analytics.service';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'react-toastify';

const AnalyticsContext = createContext();

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

export const AnalyticsProvider = ({ children }) => {
  const { user } = useAuth();
  const { socket, connected, on, emit } = useSocket();
  
  // Real-time data state
  const [realtimeMetrics, setRealtimeMetrics] = useState({});
  const [liveUpdates, setLiveUpdates] = useState([]);
  const [systemHealth, setSystemHealth] = useState({});
  const [activeUsers, setActiveUsers] = useState(0);
  const [activeSessions, setActiveSessions] = useState(0);
  
  // Analytics state
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Subscription management
  const [subscriptions, setSubscriptions] = useState(new Set());
  const updateInterval = useRef(null);
  const metricsInterval = useRef(null);
  
  // Initialize real-time analytics
  useEffect(() => {
    if (connected && socket && user) {
      // Join analytics room
      emit('join_analytics_room', { userId: user.id });
      
      // Set up real-time event listeners
      const cleanupFunctions = [
        on('analytics_update', handleAnalyticsUpdate),
        on('metrics_update', handleMetricsUpdate),
        on('system_health_update', handleSystemHealthUpdate),
        on('user_activity_update', handleUserActivityUpdate),
        on('alert_notification', handleAlertNotification)
      ];
      
      // Start periodic updates
      startPeriodicUpdates();
      
      return () => {
        cleanupFunctions.forEach(cleanup => cleanup && cleanup());
        stopPeriodicUpdates();
        emit('leave_analytics_room', { userId: user.id });
      };
    }
  }, [connected, socket, user]);

  // Handle real-time analytics updates
  const handleAnalyticsUpdate = useCallback((data) => {
    setLiveUpdates(prev => [
      {
        id: Date.now(),
        timestamp: new Date(),
        type: data.type,
        data: data.payload,
        message: data.message
      },
      ...prev.slice(0, 99) // Keep last 100 updates
    ]);
    
    // Update specific metrics based on update type
    switch (data.type) {
      case 'beneficiary_progress':
        updateBeneficiaryMetrics(data.payload);
        break;
      case 'trainer_activity':
        updateTrainerMetrics(data.payload);
        break;
      case 'system_performance':
        updateSystemMetrics(data.payload);
        break;
      default:
        break;
    }
    
    setLastUpdate(new Date());
  }, []);

  // Handle metrics updates
  const handleMetricsUpdate = useCallback((data) => {
    setRealtimeMetrics(prev => ({
      ...prev,
      ...data.metrics
    }));
  }, []);

  // Handle system health updates
  const handleSystemHealthUpdate = useCallback((data) => {
    setSystemHealth(data.health);
    
    // Show alerts for critical issues
    if (data.health.status === 'critical') {
      toast.error(`System Alert: ${data.health.message}`, {
        position: "top-right",
        autoClose: false,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    }
  }, []);

  // Handle user activity updates
  const handleUserActivityUpdate = useCallback((data) => {
    setActiveUsers(data.activeUsers);
    setActiveSessions(data.activeSessions);
  }, []);

  // Handle alert notifications
  const handleAlertNotification = useCallback((data) => {
    const alertType = data.severity === 'high' ? 'error' : 
                     data.severity === 'medium' ? 'warning' : 'info';
    
    toast[alertType](`Analytics Alert: ${data.message}`, {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  }, []);

  // Update specific metric types
  const updateBeneficiaryMetrics = (data) => {
    setRealtimeMetrics(prev => ({
      ...prev,
      beneficiaryMetrics: {
        ...prev.beneficiaryMetrics,
        ...data
      }
    }));
  };

  const updateTrainerMetrics = (data) => {
    setRealtimeMetrics(prev => ({
      ...prev,
      trainerMetrics: {
        ...prev.trainerMetrics,
        ...data
      }
    }));
  };

  const updateSystemMetrics = (data) => {
    setRealtimeMetrics(prev => ({
      ...prev,
      systemMetrics: {
        ...prev.systemMetrics,
        ...data
      }
    }));
  };

  // Start periodic updates
  const startPeriodicUpdates = () => {
    // Update dashboard data every 30 seconds
    updateInterval.current = setInterval(async () => {
      try {
        const data = await analyticsService.getDashboardOverview();
        setDashboardData(data);
      } catch (error) {
        console.error('Error updating dashboard data:', error);
      }
    }, 30000);

    // Update real-time metrics every 10 seconds
    metricsInterval.current = setInterval(async () => {
      try {
        const metrics = await analyticsService.getRealtimeMetrics();
        setRealtimeMetrics(prev => ({ ...prev, ...metrics }));
      } catch (error) {
        console.error('Error updating real-time metrics:', error);
      }
    }, 10000);
  };

  // Stop periodic updates
  const stopPeriodicUpdates = () => {
    if (updateInterval.current) {
      clearInterval(updateInterval.current);
      updateInterval.current = null;
    }
    if (metricsInterval.current) {
      clearInterval(metricsInterval.current);
      metricsInterval.current = null;
    }
  };

  // Subscribe to specific analytics updates
  const subscribe = (eventType, callback) => {
    const subscription = { eventType, callback, id: Date.now() };
    setSubscriptions(prev => new Set([...prev, subscription]));
    
    if (socket) {
      socket.on(`analytics_${eventType}`, callback);
    }
    
    return () => {
      setSubscriptions(prev => {
        const newSet = new Set(prev);
        newSet.delete(subscription);
        return newSet;
      });
      
      if (socket) {
        socket.off(`analytics_${eventType}`, callback);
      }
    };
  };

  // Unsubscribe from all events
  const unsubscribeAll = () => {
    subscriptions.forEach(subscription => {
      if (socket) {
        socket.off(`analytics_${subscription.eventType}`, subscription.callback);
      }
    });
    setSubscriptions(new Set());
  };

  // Request specific analytics data
  const requestAnalyticsData = async (type, params = {}) => {
    setIsLoading(true);
    try {
      let data;
      switch (type) {
        case 'dashboard':
          data = await analyticsService.getDashboardOverview(params);
          setDashboardData(data);
          break;
        case 'beneficiaries':
          data = await analyticsService.getBeneficiaryAnalytics(params);
          break;
        case 'trainers':
          data = await analyticsService.getTrainerAnalytics(params);
          break;
        case 'programs':
          data = await analyticsService.getProgramAnalytics(params);
          break;
        case 'performance':
          data = await analyticsService.getPerformanceMetrics(params);
          break;
        default:
          throw new Error(`Unknown analytics type: ${type}`);
      }
      return data;
    } catch (error) {
      console.error(`Error requesting ${type} analytics:`, error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Export analytics data
  const exportAnalytics = async (format, dataType, params = {}) => {
    try {
      await analyticsService.exportData(format, dataType, params);
      toast.success(`Analytics exported successfully as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Error exporting analytics:', error);
      toast.error('Failed to export analytics data');
      throw error;
    }
  };

  // Get analytics insights
  const getInsights = (data, type) => {
    const insights = [];
    
    if (!data) return insights;
    
    switch (type) {
      case 'beneficiaries':
        if (data.growthRate > 10) {
          insights.push({
            type: 'positive',
            message: `Beneficiary enrollment is growing at ${data.growthRate}% - excellent progress!`
          });
        }
        if (data.completionRate < 70) {
          insights.push({
            type: 'warning',
            message: `Completion rate is ${data.completionRate}% - consider program optimization`
          });
        }
        break;
        
      case 'trainers':
        if (data.averageRating > 4.5) {
          insights.push({
            type: 'positive',
            message: `High trainer satisfaction with ${data.averageRating}/5 rating`
          });
        }
        if (data.workload > 80) {
          insights.push({
            type: 'warning',
            message: `High trainer workload detected - consider load balancing`
          });
        }
        break;
        
      case 'system':
        if (data.uptime > 99.9) {
          insights.push({
            type: 'positive',
            message: `Excellent system reliability with ${data.uptime}% uptime`
          });
        }
        if (data.responseTime > 500) {
          insights.push({
            type: 'warning',
            message: `System response time is ${data.responseTime}ms - optimization needed`
          });
        }
        break;
        
      default:
        break;
    }
    
    return insights;
  };

  // Clear live updates
  const clearLiveUpdates = () => {
    setLiveUpdates([]);
  };

  // Refresh all data
  const refreshAll = async () => {
    setIsLoading(true);
    try {
      const [dashboard, metrics] = await Promise.all([
        analyticsService.getDashboardOverview(),
        analyticsService.getRealtimeMetrics()
      ]);
      
      setDashboardData(dashboard);
      setRealtimeMetrics(prev => ({ ...prev, ...metrics }));
      setLastUpdate(new Date());
      
      toast.success('Analytics data refreshed successfully');
    } catch (error) {
      console.error('Error refreshing analytics data:', error);
      toast.error('Failed to refresh analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    // Real-time data
    realtimeMetrics,
    liveUpdates,
    systemHealth,
    activeUsers,
    activeSessions,
    
    // Analytics data
    dashboardData,
    isLoading,
    lastUpdate,
    
    // Subscription management
    subscribe,
    unsubscribeAll,
    
    // Data operations
    requestAnalyticsData,
    exportAnalytics,
    refreshAll,
    
    // Utilities
    getInsights,
    clearLiveUpdates,
    
    // Service access
    analyticsService
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};