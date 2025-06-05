import React, { useState, useEffect } from 'react';
import { useSocket } from '../../contexts/SocketContext';
import { Bell, Check, X } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../../lib/api';
const RealTimeNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const { on, off } = useSocket();
  useEffect(() => {
    // Load initial notifications
    loadNotifications();
    // Subscribe to real-time notifications
    const unsubscribeNotification = on('notification', handleNewNotification);
    const unsubscribeUpdate = on('notification_update', handleNotificationUpdate);
    return () => {
      unsubscribeNotification();
      unsubscribeUpdate();
    };
  }, []);
  const loadNotifications = async () => {
    try {
      const response = await api.get('/api/notifications');
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };
  const handleNewNotification = (data) => {
    setNotifications(prev => [data, ...prev]);
    setUnreadCount(prev => prev + 1);
    // Show toast notification
    toast(data.message, {
      type: data.type || 'info',
      position: 'top-right',
      autoClose: 5000
    });
  };
  const handleNotificationUpdate = (data) => {
    if (data.action === 'mark_read') {
      setNotifications(prev => 
        prev.map(n => ({
          ...n,
          read: data.notification_ids.includes(n.id) ? true : n.read
        }))
      );
      setUnreadCount(prev => Math.max(0, prev - data.notification_ids.length));
    }
  };
  const markAsRead = async (notificationId) => {
    try {
      await api.patch(`/notifications/${notificationId}/read`);
      setNotifications(prev =>
        prev.map(n => ({
          ...n,
          read: n.id === notificationId ? true : n.read
        }))
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };
  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark-all-read');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };
  const dismissNotification = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to dismiss notification:', error);
    }
  };
  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50">
          <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Mark all as read
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                No notifications
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`px-4 py-3 border-b border-gray-100 hover:bg-gray-50 ${
                    !notification.read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">
                        {notification.title}
                      </h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-400 mt-2">
                        {new Date(notification.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="text-blue-600 hover:text-blue-800"
                          title="Mark as read"
                        >
                          <Check className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => dismissNotification(notification.id)}
                        className="text-gray-400 hover:text-gray-600"
                        title="Dismiss"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          {notifications.length > 0 && (
            <div className="px-4 py-3 text-center">
              <a
                href="/notifications/v2"
                className="text-sm text-blue-600 hover:text-blue-800"
                onClick={() => setShowDropdown(false)}
              >
                View all notifications
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default RealTimeNotifications;