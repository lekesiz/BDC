import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '@/lib/api';
import { toast } from 'react-toastify';
import io from 'socket.io-client';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProviderV2 = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [permission, setPermission] = useState(Notification.permission);

  useEffect(() => {
    requestNotificationPermission();
    fetchUnreadCount();
    connectWebSocket();

    return () => {
      if (ws) {
        ws.disconnect();
      }
    };
  }, []);

  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      setPermission(permission);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return;
      }
      
      const response = await api.get('/api/notifications/unread-count');
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  const connectWebSocket = () => {
    // Enable WebSocket notifications
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return;
      }
      
      const websocket = io('http://localhost:5001/ws/notifications', {
        auth: { token },
        transports: ['websocket', 'polling']
      });

      websocket.on('connect', () => {
        setIsConnected(true);
      });

      websocket.on('new_notification', (data) => {
        // data is already parsed by Socket.IO
        handleNotificationMessage(data);
      });

      websocket.on('error', (error) => {
        console.error('WebSocket error:', error);
      });

      websocket.on('disconnect', () => {
        setIsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      });

      setWs(websocket);
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const handleNotificationMessage = (data) => {
    switch (data.type) {
      case 'new_notification':
        const notification = data.notification;
        setNotifications(prev => [notification, ...prev]);
        setUnreadCount(prev => prev + 1);
        showNotification(notification);
        break;
      
      case 'notification_read':
        setNotifications(prev =>
          prev.map(n => n.id === data.notificationId ? { ...n, is_read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
        break;
      
      case 'notification_deleted':
        setNotifications(prev => prev.filter(n => n.id !== data.notificationId));
        if (!data.wasRead) {
          setUnreadCount(prev => Math.max(0, prev - 1));
        }
        break;
      
      case 'unread_count':
        setUnreadCount(data.count);
        break;
      
      default:
    }
  };

  const showNotification = (notification) => {
    // Show toast notification
    const toastContent = (
      <div>
        <strong>{notification.title}</strong>
        <p>{notification.message}</p>
      </div>
    );

    switch (notification.type) {
      case 'error':
        toast.error(toastContent, { autoClose: false });
        break;
      case 'warning':
        toast.warning(toastContent);
        break;
      case 'success':
        toast.success(toastContent);
        break;
      default:
        toast.info(toastContent);
    }

    // Show browser notification if permission granted
    if (permission === 'granted' && document.hidden) {
      const browserNotification = new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/badge.png',
        tag: notification.id,
        requireInteraction: notification.type === 'error'
      });

      browserNotification.onclick = () => {
        window.focus();
        if (notification.action_url) {
          window.location.href = notification.action_url;
        }
      };
    }
  };

  const markAsRead = async (notificationIds) => {
    try {
      await axios.put('/api/notifications/read', { notification_ids: notificationIds });
      
      setNotifications(prev =>
        prev.map(n => notificationIds.includes(n.id) ? { ...n, is_read: true } : n)
      );
      
      const readCount = notifications.filter(n => 
        notificationIds.includes(n.id) && !n.is_read
      ).length;
      
      setUnreadCount(prev => Math.max(0, prev - readCount));
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
      throw error;
    }
  };

  const deleteNotifications = async (notificationIds) => {
    try {
      await axios.delete('/api/notifications', { data: { notification_ids: notificationIds } });
      
      const deletedUnreadCount = notifications.filter(n => 
        notificationIds.includes(n.id) && !n.is_read
      ).length;
      
      setNotifications(prev => prev.filter(n => !notificationIds.includes(n.id)));
      setUnreadCount(prev => Math.max(0, prev - deletedUnreadCount));
    } catch (error) {
      console.error('Failed to delete notifications:', error);
      throw error;
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.put('/api/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      throw error;
    }
  };

  const sendNotification = (data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  };

  const value = {
    notifications,
    unreadCount,
    isConnected,
    permission,
    markAsRead,
    deleteNotifications,
    markAllAsRead,
    sendNotification,
    requestNotificationPermission
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationProviderV2;