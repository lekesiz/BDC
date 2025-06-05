import { 
  generateNotificationsData, 
  generateNotificationPreferences,
  generateNotificationStats,
  generateNotificationTemplates 
} from './mockNotificationsData';
export const setupNotificationsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // Notification endpoints
  api.get = function(url, ...args) {
    // List notifications
    if (url === '/api/notifications' || url.startsWith('/api/notifications?')) {
      const userRole = localStorage.getItem('userRole') || 'student';
      const notifications = generateNotificationsData(userRole);
      // Parse query parameters
      const urlObj = new URL(url, 'http://localhost');
      const category = urlObj.searchParams.get('category');
      const priority = urlObj.searchParams.get('priority');
      const read = urlObj.searchParams.get('read');
      const limit = parseInt(urlObj.searchParams.get('limit') || '50');
      const offset = parseInt(urlObj.searchParams.get('offset') || '0');
      let filteredNotifications = [...notifications];
      // Filter by category
      if (category) {
        filteredNotifications = filteredNotifications.filter(n => n.category === category);
      }
      // Filter by priority
      if (priority) {
        filteredNotifications = filteredNotifications.filter(n => n.priority === priority);
      }
      // Filter by read status
      if (read !== null) {
        const isRead = read === 'true';
        filteredNotifications = filteredNotifications.filter(n => n.read === isRead);
      }
      // Apply pagination
      const paginatedNotifications = filteredNotifications.slice(offset, offset + limit);
      return Promise.resolve({
        status: 200,
        data: {
          notifications: paginatedNotifications,
          total: filteredNotifications.length,
          unread: filteredNotifications.filter(n => !n.read).length,
          hasMore: offset + limit < filteredNotifications.length
        }
      });
    }
    // Unread notifications count
    if (url === '/api/notifications/unread-count') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const notifications = generateNotificationsData(userRole);
      const unreadCount = notifications.filter(n => !n.read).length;
      return Promise.resolve({
        status: 200,
        data: {
          count: unreadCount,
          byCategory: {
            academic: notifications.filter(n => n.category === 'academic' && !n.read).length,
            reminder: notifications.filter(n => n.category === 'reminder' && !n.read).length,
            system: notifications.filter(n => n.category === 'system' && !n.read).length,
            communication: notifications.filter(n => n.category === 'communication' && !n.read).length,
            achievement: notifications.filter(n => n.category === 'achievement' && !n.read).length,
            event: notifications.filter(n => n.category === 'event' && !n.read).length
          }
        }
      });
    }
    // Specific notification
    if (url.match(/^\/api\/notifications\/\d+$/)) {
      const notificationId = parseInt(url.split('/').pop());
      const userRole = localStorage.getItem('userRole') || 'student';
      const notifications = generateNotificationsData(userRole);
      const notification = notifications.find(n => n.id === notificationId);
      if (notification) {
        return Promise.resolve({
          status: 200,
          data: notification
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Notification not found' }
        });
      }
    }
    // Notification preferences
    if (url === '/api/notifications/preferences') {
      const preferences = generateNotificationPreferences();
      return Promise.resolve({
        status: 200,
        data: preferences
      });
    }
    // Notification statistics
    if (url === '/api/notifications/statistics') {
      const stats = generateNotificationStats();
      return Promise.resolve({
        status: 200,
        data: stats
      });
    }
    // Notification templates
    if (url === '/api/notifications/templates') {
      const templates = generateNotificationTemplates();
      return Promise.resolve({
        status: 200,
        data: {
          templates,
          total: templates.length
        }
      });
    }
    // Notification history
    if (url === '/api/notifications/history') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const notifications = generateNotificationsData(userRole);
      // Include read notifications from the past 30 days
      const historicalNotifications = notifications.map(n => ({
        ...n,
        read: true,
        timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
      }));
      return Promise.resolve({
        status: 200,
        data: {
          notifications: historicalNotifications,
          total: historicalNotifications.length
        }
      });
    }
    // Notification categories
    if (url === '/api/notifications/categories') {
      const categories = [
        { id: 'academic', name: 'Academic', icon: 'graduation-cap', color: 'blue' },
        { id: 'reminder', name: 'Reminders', icon: 'clock', color: 'orange' },
        { id: 'system', name: 'System', icon: 'cog', color: 'gray' },
        { id: 'communication', name: 'Messages', icon: 'message', color: 'green' },
        { id: 'achievement', name: 'Achievements', icon: 'trophy', color: 'yellow' },
        { id: 'event', name: 'Events', icon: 'calendar', color: 'purple' }
      ];
      return Promise.resolve({
        status: 200,
        data: categories
      });
    }
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  // Notification POST endpoints
  api.post = function(url, data, ...args) {
    // Mark notification as read
    if (url.match(/^\/api\/notifications\/\d+\/read$/)) {
      const notificationId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          id: notificationId,
          read: true,
          readAt: new Date().toISOString()
        }
      });
    }
    // Mark all notifications as read
    if (url === '/api/notifications/mark-all-read') {
      return Promise.resolve({
        status: 200,
        data: {
          updated: 23,
          message: 'All notifications marked as read'
        }
      });
    }
    // Snooze notification
    if (url.match(/^\/api\/notifications\/\d+\/snooze$/)) {
      const notificationId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          id: notificationId,
          snoozedUntil: new Date(Date.now() + (data.duration || 3600000)).toISOString()
        }
      });
    }
    // Execute notification action
    if (url.match(/^\/api\/notifications\/\d+\/action$/)) {
      const notificationId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          id: notificationId,
          action: data.action,
          executed: true,
          executedAt: new Date().toISOString()
        }
      });
    }
    // Create notification (admin)
    if (url === '/api/notifications/send') {
      const newNotification = {
        id: Date.now(),
        ...data,
        timestamp: new Date().toISOString(),
        read: false,
        sent: true
      };
      return Promise.resolve({
        status: 201,
        data: newNotification
      });
    }
    // Subscribe to notifications
    if (url === '/api/notifications/subscribe') {
      return Promise.resolve({
        status: 200,
        data: {
          subscribed: true,
          endpoint: data.endpoint,
          subscribedAt: new Date().toISOString()
        }
      });
    }
    // Test notification
    if (url === '/api/notifications/test') {
      return Promise.resolve({
        status: 200,
        data: {
          sent: true,
          channel: data.channel,
          message: 'Test notification sent successfully'
        }
      });
    }
    return originalFunctions.post.call(api, url, data, ...args);
  };
  // Notification PUT endpoints
  api.put = function(url, data, ...args) {
    // Update notification preferences
    if (url === '/api/notifications/preferences') {
      return Promise.resolve({
        status: 200,
        data: {
          ...data,
          updatedAt: new Date().toISOString(),
          message: 'Notification preferences updated successfully'
        }
      });
    }
    // Update notification template
    if (url.match(/^\/api\/notifications\/templates\/\d+$/)) {
      const templateId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: templateId,
          ...data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    // Update notification settings
    if (url === '/api/notifications/settings') {
      return Promise.resolve({
        status: 200,
        data: {
          settings: data,
          updatedAt: new Date().toISOString(),
          message: 'Notification settings updated successfully'
        }
      });
    }
    // Batch update notifications
    if (url === '/api/notifications/batch-update') {
      return Promise.resolve({
        status: 200,
        data: {
          updated: data.notificationIds.length,
          action: data.action,
          message: `${data.notificationIds.length} notifications updated`
        }
      });
    }
    return originalFunctions.put.call(api, url, data, ...args);
  };
  // Notification DELETE endpoints
  api.delete = function(url, ...args) {
    // Delete notification
    if (url.match(/^\/api\/notifications\/\d+$/)) {
      const notificationId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: notificationId,
          deleted: true
        }
      });
    }
    // Delete old notifications
    if (url === '/api/notifications/old') {
      return Promise.resolve({
        status: 200,
        data: {
          deleted: 45,
          message: 'Old notifications deleted successfully'
        }
      });
    }
    // Unsubscribe from notifications
    if (url === '/api/notifications/unsubscribe') {
      return Promise.resolve({
        status: 200,
        data: {
          unsubscribed: true,
          message: 'Successfully unsubscribed from notifications'
        }
      });
    }
    // Delete notification template
    if (url.match(/^\/api\/notifications\/templates\/\d+$/)) {
      const templateId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: templateId,
          deleted: true
        }
      });
    }
    // Clear all notifications
    if (url === '/api/notifications/clear-all') {
      return Promise.resolve({
        status: 200,
        data: {
          cleared: true,
          message: 'All notifications cleared'
        }
      });
    }
    return originalFunctions.delete.call(api, url, ...args);
  };
};