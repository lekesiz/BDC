import { useNavigate } from 'react-router-dom';
import { 
  Bell, 
  CalendarCheck, 
  BarChart, 
  MessageSquare, 
  AlertCircle,
  Clock,
  CheckCircle,
  AlertTriangle,
  Info,
  Loader 
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

/**
 * Displays recent notifications for the student
 */
const RecentNotificationsWidget = ({ data, isLoading, error }) => {
  const navigate = useNavigate();
  
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
    
    // Otherwise, show the day
    return date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  };
  
  // Format time
  const formatTime = (date) => {
    return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  };
  
  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'schedule':
        return <CalendarCheck className="h-4 w-4" />;
      case 'message':
        return <MessageSquare className="h-4 w-4" />;
      case 'progress':
        return <BarChart className="h-4 w-4" />;
      case 'alert':
        return <AlertCircle className="h-4 w-4" />;
      case 'reminder':
        return <Clock className="h-4 w-4" />;
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };
  
  // Get color class based on notification type
  const getNotificationColorClass = (type) => {
    switch (type) {
      case 'schedule':
        return 'bg-blue-50 text-blue-500';
      case 'message':
        return 'bg-purple-50 text-purple-500';
      case 'progress':
        return 'bg-green-50 text-green-500';
      case 'alert':
        return 'bg-red-50 text-red-500';
      case 'reminder':
        return 'bg-yellow-50 text-yellow-500';
      case 'success':
        return 'bg-emerald-50 text-emerald-500';
      case 'warning':
        return 'bg-amber-50 text-amber-500';
      default:
        return 'bg-gray-50 text-gray-500';
    }
  };
  
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">Recent Notifications</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">Recent Notifications</h2>
        </div>
        <div className="p-6 text-center text-red-500">
          Failed to load notifications
        </div>
      </Card>
    );
  }
  
  // Get notifications to display (limit to 5)
  const notifications = data?.notifications?.slice(0, 5) || [];
  
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <div className="flex items-center">
          <h2 className="text-lg font-medium">Recent Notifications</h2>
          {data?.unreadCount > 0 && (
            <span className="ml-2 bg-primary text-white text-xs rounded-full px-2 py-0.5">
              {data.unreadCount} new
            </span>
          )}
        </div>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/portal/notifications')}
        >
          View All
        </Button>
      </div>
      
      {notifications.length > 0 ? (
        <div className="divide-y max-h-80 overflow-auto">
          {notifications.map(notification => (
            <div key={notification.id} className={`p-4 hover:bg-gray-50 ${!notification.isRead ? 'bg-blue-50/20' : ''}`}>
              <div className="flex items-start">
                <div className={`p-2 rounded-full mr-3 ${getNotificationColorClass(notification.type)}`}>
                  {getNotificationIcon(notification.type)}
                </div>
                <div>
                  {notification.title && (
                    <h4 className="text-sm font-medium">{notification.title}</h4>
                  )}
                  <p className="text-sm">{notification.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDate(notification.timestamp)}
                  </p>
                  
                  {notification.link && (
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 h-auto mt-1 text-xs"
                      onClick={() => navigate(notification.link)}
                    >
                      {notification.linkText || 'View Details'}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-8 text-center">
          <Bell className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No notifications</p>
        </div>
      )}
      
      <div className="bg-gray-50 p-4 text-center border-t">
        <Button
          variant="link"
          onClick={() => navigate('/portal/notifications')}
        >
          View All Notifications
        </Button>
      </div>
    </Card>
  );
};

export default RecentNotificationsWidget;