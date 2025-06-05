import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, 
  CheckCheck, 
  Calendar, 
  FileText, 
  MessageSquare, 
  User, 
  AlertCircle,
  Activity,
  Check,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';
/**
 * NotificationsPage displays user notifications with filtering and management options
 */
const NotificationsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [filteredNotifications, setFilteredNotifications] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;
  // Filter options
  const filters = [
    { id: 'all', label: 'All', icon: Bell },
    { id: 'unread', label: 'Unread', icon: AlertCircle },
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'system', label: 'System', icon: Activity },
  ];
  // Fetch notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/notifications', {
          params: {
            page: currentPage,
            limit: itemsPerPage,
            filter: activeFilter !== 'all' ? activeFilter : undefined
          }
        });
        setNotifications(response.data.notifications);
        setFilteredNotifications(response.data.notifications);
        setTotalPages(Math.ceil(response.data.total / itemsPerPage));
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
  }, [activeFilter, currentPage]); // Remove toast dependency to prevent infinite loop
  // Get icon for notification type
  const getNotificationIcon = (notification) => {
    switch (notification.type) {
      case 'appointment':
        return <Calendar className="w-5 h-5 text-blue-500" />;
      case 'document':
        return <FileText className="w-5 h-5 text-green-500" />;
      case 'message':
        return <MessageSquare className="w-5 h-5 text-purple-500" />;
      case 'user':
        return <User className="w-5 h-5 text-orange-500" />;
      case 'system':
        return <Activity className="w-5 h-5 text-gray-500" />;
      default:
        return <Bell className="w-5 h-5 text-primary" />;
    }
  };
  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/api/notifications/${notificationId}/mark-read`);
      // Update notification in the list
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, is_read: true } 
            : notif
        )
      );
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
  const markAllAsRead = async () => {
    try {
      await api.post('/api/notifications/mark-all-read');
      // Update all notifications in the list
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
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
  // Handle notification click
  const handleNotificationClick = (notification) => {
    // Mark as read if unread
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    // Navigate based on notification type and data
    if (notification.link) {
      navigate(notification.link);
    }
  };
  // Navigate to previous page
  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };
  // Navigate to next page
  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Notifications</h1>
        <Button
          variant="outline"
          onClick={markAllAsRead}
          className="flex items-center"
        >
          <CheckCheck className="w-4 h-4 mr-2" />
          Mark All as Read
        </Button>
      </div>
      {/* Filters */}
      <div className="flex overflow-x-auto mb-6 pb-2">
        {filters.map(filter => (
          <Button
            key={filter.id}
            variant={activeFilter === filter.id ? 'default' : 'outline'}
            className="mr-2 flex items-center whitespace-nowrap"
            onClick={() => {
              setActiveFilter(filter.id);
              setCurrentPage(1);
            }}
          >
            <filter.icon className="w-4 h-4 mr-2" />
            {filter.label}
            {filter.id === 'unread' && (
              <span className="ml-2 bg-primary text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {notifications.filter(n => !n.is_read).length}
              </span>
            )}
          </Button>
        ))}
      </div>
      {/* Notifications List */}
      <Card className="divide-y">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-gray-500">
            <Bell className="w-12 h-12 text-gray-300 mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No notifications</h3>
            <p>You're all caught up!</p>
          </div>
        ) : (
          <>
            {notifications.map(notification => (
              <div 
                key={notification.id}
                className={`flex p-4 cursor-pointer hover:bg-gray-50 ${!notification.is_read ? 'bg-blue-50' : ''}`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex-shrink-0 mr-4">
                  <div className={`p-2 rounded-full ${!notification.is_read ? 'bg-blue-100' : 'bg-gray-100'}`}>
                    {getNotificationIcon(notification)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className={`text-sm ${!notification.is_read ? 'font-medium' : 'text-gray-900'}`}>
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.content}
                      </p>
                    </div>
                    <div className="ml-4 flex-shrink-0 flex flex-col items-end">
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(notification.created_at), {
                          addSuffix: true,
                          locale: tr
                        })}
                      </span>
                      {!notification.is_read && (
                        <span className="mt-1 bg-primary w-2 h-2 rounded-full"></span>
                      )}
                    </div>
                  </div>
                  {notification.action_text && (
                    <div className="mt-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleNotificationClick(notification);
                        }}
                      >
                        {notification.action_text}
                      </Button>
                    </div>
                  )}
                </div>
                <div className="ml-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-gray-400 hover:text-gray-500"
                    onClick={(e) => {
                      e.stopPropagation();
                      // In a real app, this would show a dropdown menu
                    }}
                  >
                    <MoreHorizontal className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            ))}
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-between items-center p-4">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * itemsPerPage, (currentPage - 1) * itemsPerPage + notifications.length)}
                  </span> of{' '}
                  <span className="font-medium">{totalPages * itemsPerPage}</span> results
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={goToPreviousPage}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={goToNextPage}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>
      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <Info className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Notification Settings</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                You can customize your notification preferences in the{' '}
                <Button 
                  variant="link" 
                  className="p-0 h-auto text-blue-600 font-medium"
                  onClick={() => navigate('/settings/notifications')}
                >
                  Settings
                </Button>{' '}
                page.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
// Info icon component
const Info = ({ className }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 20 20"
    fill="currentColor"
    className={className}
  >
    <path
      fillRule="evenodd"
      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
      clipRule="evenodd"
    />
  </svg>
);
export default NotificationsPage;