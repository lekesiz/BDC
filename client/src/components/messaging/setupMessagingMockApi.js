import {
  fetchConversations,
  fetchMessages,
  sendMessage,
  markConversationAsRead,
  createConversation,
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  fetchNotificationSettings,
  updateNotificationSettings
} from './mockMessagingData';

// This function sets up mock API handlers for messaging and notification endpoints
export const setupMessagingMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  
  // Override GET requests for messaging and notification endpoints
  api.get = function(url, config) {
    // Fetch conversations
    if (url === '/api/conversations') {
      return Promise.resolve(fetchConversations());
    }
    
    // Fetch messages for a conversation
    const messagesMatch = url.match(/\/api\/conversations\/(\d+)\/messages$/);
    if (messagesMatch) {
      return Promise.resolve(fetchMessages(messagesMatch[1]));
    }
    
    // Fetch notifications
    if (url === '/api/notifications') {
      // Extract query parameters
      const urlObj = new URL(url, window.location.origin);
      const page = urlObj.searchParams.get('page');
      const limit = urlObj.searchParams.get('limit');
      const filter = urlObj.searchParams.get('filter');
      
      return Promise.resolve(fetchNotifications({
        page: page ? parseInt(page) : 1,
        limit: limit ? parseInt(limit) : 10,
        filter
      }));
    }
    
    // Fetch notification settings
    if (url === '/api/settings/notifications') {
      return Promise.resolve(fetchNotificationSettings());
    }
    
    // Fallback to original implementation
    return originalGet.call(this, url, config);
  };
  
  // Override POST requests for messaging and notification endpoints
  api.post = function(url, data, config) {
    // Send a message
    const sendMessageMatch = url.match(/\/api\/conversations\/(\d+)\/messages$/);
    if (sendMessageMatch) {
      return Promise.resolve(sendMessage(sendMessageMatch[1], data));
    }
    
    // Mark conversation as read
    const markReadMatch = url.match(/\/api\/conversations\/(\d+)\/mark-read$/);
    if (markReadMatch) {
      return Promise.resolve(markConversationAsRead(markReadMatch[1]));
    }
    
    // Create a new conversation
    if (url === '/api/conversations') {
      return Promise.resolve(createConversation(data));
    }
    
    // Mark notification as read
    const notificationReadMatch = url.match(/\/api\/notifications\/(\d+)\/mark-read$/);
    if (notificationReadMatch) {
      return Promise.resolve(markNotificationAsRead(notificationReadMatch[1]));
    }
    
    // Mark all notifications as read
    if (url === '/api/notifications/mark-all-read') {
      return Promise.resolve(markAllNotificationsAsRead());
    }
    
    // Fallback to original implementation
    return originalPost.call(this, url, data, config);
  };
  
  // Override PUT requests for messaging and notification endpoints
  api.put = function(url, data, config) {
    // Update notification settings
    if (url === '/api/settings/notifications') {
      return Promise.resolve(updateNotificationSettings(data));
    }
    
    // Fallback to original implementation
    return originalPut.call(this, url, data, config);
  };
};