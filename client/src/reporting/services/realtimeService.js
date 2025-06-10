// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Real-time Service
 * 
 * Handles real-time communication with the server via WebSockets
 */

class RealtimeService {
  constructor(socket) {
    this.socket = socket;
    this.subscriptions = new Map();
    this.eventHandlers = new Map();

    // Set up socket event handlers
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Connected to real-time server');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from real-time server:', reason);
    });

    this.socket.on('report_data', (data) => {
      this.handleReportData(data);
    });

    this.socket.on('report_error', (error) => {
      this.handleReportError(error);
    });

    this.socket.on('subscription_status', (status) => {
      this.handleSubscriptionStatus(status);
    });

    this.socket.on('system_notification', (notification) => {
      this.handleSystemNotification(notification);
    });
  }

  handleReportData(data) {
    const subscriptionId = data.subscription_id;

    if (this.subscriptions.has(subscriptionId)) {
      const subscription = this.subscriptions.get(subscriptionId);
      subscription.lastUpdate = Date.now();
      subscription.updateCount = (subscription.updateCount || 0) + 1;
    }

    // Emit to registered event handlers
    this.emit('data', data);
  }

  handleReportError(error) {
    const subscriptionId = error.subscription_id;

    if (this.subscriptions.has(subscriptionId)) {
      const subscription = this.subscriptions.get(subscriptionId);
      subscription.errorCount = (subscription.errorCount || 0) + 1;
      subscription.lastError = error.error;
    }

    // Emit to registered event handlers
    this.emit('error', error);
  }

  handleSubscriptionStatus(status) {
    const subscriptionId = status.subscription_id;

    if (this.subscriptions.has(subscriptionId)) {
      const subscription = this.subscriptions.get(subscriptionId);
      subscription.status = status.status;
    }

    // Emit to registered event handlers
    this.emit('status', status);
  }

  handleSystemNotification(notification) {
    // Emit to registered event handlers
    this.emit('notification', notification);
  }

  async subscribe(config) {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`subscribe_response_${requestId}`, responseHandler);

        if (response.success) {
          // Store subscription locally
          this.subscriptions.set(response.subscription_id, {
            id: response.subscription_id,
            config,
            status: 'active',
            createdAt: Date.now(),
            updateCount: 0,
            errorCount: 0
          });

          resolve(response);
        } else {
          reject(new Error(response.error || 'Failed to subscribe'));
        }
      };

      // Listen for response
      this.socket.on(`subscribe_response_${requestId}`, responseHandler);

      // Send subscription request
      this.socket.emit('subscribe', {
        request_id: requestId,
        ...config
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`subscribe_response_${requestId}`, responseHandler);
        reject(new Error('Subscription request timeout'));
      }, 10000);
    });
  }

  async unsubscribe(subscriptionId) {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`unsubscribe_response_${requestId}`, responseHandler);

        if (response.success) {
          // Remove subscription locally
          this.subscriptions.delete(subscriptionId);
          resolve(true);
        } else {
          reject(new Error(response.error || 'Failed to unsubscribe'));
        }
      };

      // Listen for response
      this.socket.on(`unsubscribe_response_${requestId}`, responseHandler);

      // Send unsubscribe request
      this.socket.emit('unsubscribe', {
        request_id: requestId,
        subscription_id: subscriptionId
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`unsubscribe_response_${requestId}`, responseHandler);
        reject(new Error('Unsubscribe request timeout'));
      }, 5000);
    });
  }

  async updateSubscription(subscriptionId, updates) {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`update_subscription_response_${requestId}`, responseHandler);

        if (response.success) {
          // Update subscription locally
          if (this.subscriptions.has(subscriptionId)) {
            const subscription = this.subscriptions.get(subscriptionId);
            subscription.config = { ...subscription.config, ...updates };
          }

          resolve(response);
        } else {
          reject(new Error(response.error || 'Failed to update subscription'));
        }
      };

      // Listen for response
      this.socket.on(`update_subscription_response_${requestId}`, responseHandler);

      // Send update request
      this.socket.emit('update_subscription', {
        request_id: requestId,
        subscription_id: subscriptionId,
        updates
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`update_subscription_response_${requestId}`, responseHandler);
        reject(new Error('Update subscription request timeout'));
      }, 5000);
    });
  }

  async triggerManualUpdate(subscriptionId) {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`manual_update_response_${requestId}`, responseHandler);

        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error || 'Failed to trigger manual update'));
        }
      };

      // Listen for response
      this.socket.on(`manual_update_response_${requestId}`, responseHandler);

      // Send manual update request
      this.socket.emit('manual_update', {
        request_id: requestId,
        subscription_id: subscriptionId
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`manual_update_response_${requestId}`, responseHandler);
        reject(new Error('Manual update request timeout'));
      }, 10000);
    });
  }

  async getSubscriptionStatus(subscriptionId) {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`subscription_status_response_${requestId}`, responseHandler);

        if (response.success) {
          resolve(response.status);
        } else {
          reject(new Error(response.error || 'Failed to get subscription status'));
        }
      };

      // Listen for response
      this.socket.on(`subscription_status_response_${requestId}`, responseHandler);

      // Send status request
      this.socket.emit('get_subscription_status', {
        request_id: requestId,
        subscription_id: subscriptionId
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`subscription_status_response_${requestId}`, responseHandler);
        reject(new Error('Subscription status request timeout'));
      }, 5000);
    });
  }

  async getSystemStats() {
    return new Promise((resolve, reject) => {
      if (!this.socket || !this.socket.connected) {
        reject(new Error('Not connected to real-time server'));
        return;
      }

      const requestId = this.generateRequestId();

      // Set up response handler
      const responseHandler = (response) => {
        this.socket.off(`system_stats_response_${requestId}`, responseHandler);

        if (response.success) {
          resolve(response.stats);
        } else {
          reject(new Error(response.error || 'Failed to get system stats'));
        }
      };

      // Listen for response
      this.socket.on(`system_stats_response_${requestId}`, responseHandler);

      // Send stats request
      this.socket.emit('get_system_stats', {
        request_id: requestId
      });

      // Set timeout for response
      setTimeout(() => {
        this.socket.off(`system_stats_response_${requestId}`, responseHandler);
        reject(new Error('System stats request timeout'));
      }, 5000);
    });
  }

  // Event handler registration
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event).add(handler);
  }

  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).delete(handler);
    }
  }

  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  // Get local subscription info
  getSubscription(subscriptionId) {
    return this.subscriptions.get(subscriptionId);
  }

  getSubscriptions() {
    return Array.from(this.subscriptions.values());
  }

  // Utility methods
  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  isConnected() {
    return this.socket && this.socket.connected;
  }

  // Clean up
  destroy() {
    if (this.socket) {
      // Remove all listeners
      this.socket.removeAllListeners();
    }

    // Clear local state
    this.subscriptions.clear();
    this.eventHandlers.clear();
  }

  // Connection management
  connect() {
    if (this.socket) {
      this.socket.connect();
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  // Subscription management helpers
  async subscribeToReport(reportConfig, options = {}) {
    return this.subscribe({
      type: 'report',
      report_config: reportConfig,
      update_frequency: options.updateFrequency || 30,
      auto_refresh: options.autoRefresh !== false,
      filters: options.filters || []
    });
  }

  async subscribeToDashboard(dashboardId, options = {}) {
    return this.subscribe({
      type: 'dashboard',
      dashboard_id: dashboardId,
      update_frequency: options.updateFrequency || 60,
      auto_refresh: options.autoRefresh !== false
    });
  }

  async subscribeToWidget(widgetConfig, options = {}) {
    return this.subscribe({
      type: 'widget',
      widget_config: widgetConfig,
      update_frequency: options.updateFrequency || 30,
      auto_refresh: options.autoRefresh !== false
    });
  }

  async subscribeToChart(chartConfig, dataConfig, options = {}) {
    return this.subscribe({
      type: 'chart',
      chart_config: chartConfig,
      data_config: dataConfig,
      update_frequency: options.updateFrequency || 30,
      auto_refresh: options.autoRefresh !== false
    });
  }

  // Bulk operations
  async unsubscribeAll() {
    const subscriptionIds = Array.from(this.subscriptions.keys());
    const results = [];

    for (const subscriptionId of subscriptionIds) {
      try {
        await this.unsubscribe(subscriptionId);
        results.push({ subscriptionId, success: true });
      } catch (error) {
        results.push({ subscriptionId, success: false, error: error.message });
      }
    }

    return results;
  }

  // Statistics
  getLocalStats() {
    const subscriptions = Array.from(this.subscriptions.values());

    return {
      total_subscriptions: subscriptions.length,
      active_subscriptions: subscriptions.filter((s) => s.status === 'active').length,
      total_updates: subscriptions.reduce((sum, s) => sum + (s.updateCount || 0), 0),
      total_errors: subscriptions.reduce((sum, s) => sum + (s.errorCount || 0), 0),
      oldest_subscription: subscriptions.length > 0 ?
      Math.min(...subscriptions.map((s) => s.createdAt)) :
      null,
      connection_status: this.isConnected() ? 'connected' : 'disconnected'
    };
  }
}

export default RealtimeService;