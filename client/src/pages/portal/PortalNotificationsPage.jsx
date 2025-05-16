import { useState, useEffect } from 'react';
import { 
  Bell, 
  Calendar, 
  MessageSquare, 
  BarChart, 
  AlertCircle, 
  CheckCircle,
  AlertTriangle,
  Info,
  X,
  Clock,
  Loader,
  Settings,
  Filter,
  ChevronDown,
  ChevronUp,
  MoreVertical
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';

/**
 * PortalNotificationsPage displays system notifications, announcements,
 * and updates for the beneficiary student
 */
const PortalNotificationsPage = () => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState({
    unreadCount: 0,
    notifications: []
  });
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  
  // Fetch notifications data
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/notifications');
        setNotifications(response.data);
      } catch (error) {
        console.error('Error fetching notifications:', error);
        toast({
          title: 'Error',
          description: 'Failed to load notifications',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchNotifications();
  }, [toast]);
  
  // Filter notifications based on filter value and search term
  const getFilteredNotifications = () => {
    let filtered = [...notifications.notifications];
    
    // Apply type filter
    if (filter !== 'all') {
      filtered = filtered.filter(notification => notification.type === filter);
    }
    
    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(notification => 
        notification.message.toLowerCase().includes(term) || 
        notification.title?.toLowerCase().includes(term)
      );
    }
    
    return filtered;
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    // If it's today, show only time
    if (date.toDateString() === now.toDateString()) {
      return `Today at ${formatTime(date)}`;
    }
    
    // If it's yesterday, show "Yesterday"
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
      return `Yesterday at ${formatTime(date)}`;
    }
    
    // If it's within the last 7 days, show the day of week
    const oneWeekAgo = new Date(now);
    oneWeekAgo.setDate(now.getDate() - 7);
    if (date > oneWeekAgo) {
      return `${date.toLocaleDateString(undefined, { weekday: 'long' })} at ${formatTime(date)}`;
    }
    
    // Otherwise, show the full date
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
  };
  
  // Format time
  const formatTime = (date) => {
    return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  };
  
  // Get icon for notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'schedule':
        return <Calendar className="h-5 w-5" />;
      case 'message':
        return <MessageSquare className="h-5 w-5" />;
      case 'progress':
        return <BarChart className="h-5 w-5" />;
      case 'alert':
        return <AlertCircle className="h-5 w-5" />;
      case 'reminder':
        return <Clock className="h-5 w-5" />;
      case 'success':
        return <CheckCircle className="h-5 w-5" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5" />;
      default:
        return <Info className="h-5 w-5" />;
    }
  };
  
  // Get color classes for notification type
  const getNotificationColorClass = (type) => {
    switch (type) {
      case 'schedule':
        return 'bg-blue-50 text-blue-500 border-blue-200';
      case 'message':
        return 'bg-purple-50 text-purple-500 border-purple-200';
      case 'progress':
        return 'bg-green-50 text-green-500 border-green-200';
      case 'alert':
        return 'bg-red-50 text-red-500 border-red-200';
      case 'reminder':
        return 'bg-yellow-50 text-yellow-500 border-yellow-200';
      case 'success':
        return 'bg-emerald-50 text-emerald-500 border-emerald-200';
      case 'warning':
        return 'bg-amber-50 text-amber-500 border-amber-200';
      default:
        return 'bg-gray-50 text-gray-500 border-gray-200';
    }
  };
  
  // Mark a notification as read
  const handleMarkAsRead = async (id) => {
    try {
      await api.put(`/api/portal/notifications/${id}/read`);
      
      // Update local state
      setNotifications(prev => {
        const updatedNotifications = prev.notifications.map(notif => 
          notif.id === id ? { ...notif, isRead: true } : notif
        );
        
        const newUnreadCount = prev.unreadCount > 0 ? prev.unreadCount - 1 : 0;
        
        return {
          unreadCount: newUnreadCount,
          notifications: updatedNotifications
        };
      });
    } catch (error) {
      console.error('Error marking notification as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to mark notification as read',
        type: 'error',
      });
    }
  };
  
  // Mark all notifications as read
  const handleMarkAllAsRead = async () => {
    try {
      await api.put('/api/portal/notifications/mark-all-read');
      
      // Update local state
      setNotifications(prev => ({
        unreadCount: 0,
        notifications: prev.notifications.map(notif => ({ ...notif, isRead: true }))
      }));
      
      toast({
        title: 'Success',
        description: 'All notifications marked as read',
        type: 'success',
      });
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to mark all notifications as read',
        type: 'error',
      });
    }
  };
  
  // Delete a notification
  const handleDeleteNotification = async (id) => {
    try {
      await api.delete(`/api/portal/notifications/${id}`);
      
      // Update local state
      setNotifications(prev => {
        const isUnread = prev.notifications.find(n => n.id === id)?.isRead === false;
        const updatedNotifications = prev.notifications.filter(notif => notif.id !== id);
        
        return {
          unreadCount: isUnread ? prev.unreadCount - 1 : prev.unreadCount,
          notifications: updatedNotifications
        };
      });
      
      toast({
        title: 'Success',
        description: 'Notification deleted',
        type: 'success',
      });
    } catch (error) {
      console.error('Error deleting notification:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete notification',
        type: 'error',
      });
    }
  };
  
  // Save notification settings
  const handleSaveSettings = async () => {
    try {
      // In a real implementation, this would update the notification settings
      await api.put('/api/portal/notifications/settings', {
        emailEnabled: true,
        pushEnabled: true,
        categories: {
          schedule: true,
          message: true,
          progress: true,
          reminder: true,
          alert: true
        }
      });
      
      setShowSettings(false);
      
      toast({
        title: 'Success',
        description: 'Notification settings updated',
        type: 'success',
      });
    } catch (error) {
      console.error('Error updating notification settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to update notification settings',
        type: 'error',
      });
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  const filteredNotifications = getFilteredNotifications();
  
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-2">Notifications</h1>
          <p className="text-gray-600">
            Stay updated with important announcements and notifications
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          
          {notifications.unreadCount > 0 && (
            <Button
              onClick={handleMarkAllAsRead}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Mark All as Read
            </Button>
          )}
        </div>
      </div>
      
      {/* Notification settings panel */}
      {showSettings && (
        <Card className="mb-8 overflow-hidden">
          <div className="p-6 bg-gray-50 border-b flex justify-between items-center">
            <h2 className="text-lg font-medium">Notification Settings</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-base font-medium mb-3">Delivery Methods</h3>
              <div className="space-y-2 pl-2">
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Email notifications</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Push notifications (browser)</span>
                </label>
              </div>
            </div>
            
            <div>
              <h3 className="text-base font-medium mb-3">Notification Categories</h3>
              <div className="space-y-2 pl-2">
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Schedule updates</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Messages from instructors</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Progress updates</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Reminders</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    defaultChecked={true}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>Alerts and important announcements</span>
                </label>
              </div>
            </div>
            
            <div className="pt-4 border-t flex justify-end">
              <Button onClick={handleSaveSettings}>
                Save Settings
              </Button>
            </div>
          </div>
        </Card>
      )}
      
      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search notifications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        
        <div className="flex space-x-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            All
          </Button>
          <Button
            variant={filter === 'schedule' ? 'default' : 'outline'}
            onClick={() => setFilter('schedule')}
          >
            <Calendar className="h-4 w-4 mr-1" />
            Schedule
          </Button>
          <Button
            variant={filter === 'message' ? 'default' : 'outline'}
            onClick={() => setFilter('message')}
          >
            <MessageSquare className="h-4 w-4 mr-1" />
            Messages
          </Button>
          <Button
            variant={filter === 'progress' ? 'default' : 'outline'}
            onClick={() => setFilter('progress')}
          >
            <BarChart className="h-4 w-4 mr-1" />
            Progress
          </Button>
        </div>
      </div>
      
      {/* Notifications list */}
      {filteredNotifications.length === 0 ? (
        <Card className="p-8 text-center">
          <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No notifications found</h3>
          <p className="text-gray-500">
            {searchTerm || filter !== 'all' 
              ? 'Try adjusting your search or filter to find what you\'re looking for' 
              : 'You don\'t have any notifications yet'
            }
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredNotifications.map(notification => (
            <Card 
              key={notification.id} 
              className={`overflow-hidden ${!notification.isRead ? 'border-l-4 border-primary' : ''}`}
            >
              <div className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    <div className={`p-2 rounded-full mr-3 ${getNotificationColorClass(notification.type)}`}>
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div>
                      {notification.title && (
                        <h3 className="font-medium mb-1">{notification.title}</h3>
                      )}
                      <p className={`${notification.isRead ? 'text-gray-500' : 'text-gray-900'}`}>
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(notification.timestamp)}
                      </p>
                      
                      {notification.link && (
                        <Button
                          variant="link"
                          className="p-0 h-auto mt-2 text-sm"
                          onClick={() => window.location.href = notification.link}
                        >
                          {notification.linkText || 'View Details'}
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    {!notification.isRead && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMarkAsRead(notification.id)}
                        className="mr-1"
                      >
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    )}
                    
                    <div className="relative">
                      <Dropdown 
                        trigger={(
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        )}
                        items={[
                          {
                            label: notification.isRead ? 'Mark as unread' : 'Mark as read',
                            onClick: () => handleMarkAsRead(notification.id)
                          },
                          { 
                            label: 'Delete', 
                            onClick: () => handleDeleteNotification(notification.id)
                          }
                        ]}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// Search component (to fix missing definition)
const Search = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={props.className || ''}
  >
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.3-4.3" />
  </svg>
);

// Simple Dropdown component
const Dropdown = ({ trigger, items }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="relative">
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>
      
      {isOpen && (
        <div 
          className="absolute right-0 mt-1 w-40 bg-white border rounded-md shadow-lg z-10"
          onBlur={() => setIsOpen(false)}
        >
          <ul className="py-1">
            {items.map((item, index) => (
              <li key={index}>
                <button
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                  onClick={() => {
                    item.onClick();
                    setIsOpen(false);
                  }}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PortalNotificationsPage;