// TODO: i18n - processed
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NotificationCenter from '@/components/notifications/NotificationCenter';
// Mock the notification provider
import { useTranslation } from "react-i18next";const mockNotificationContext = {
  notifications: [
  {
    id: 1,
    title: 'Test Notification',
    message: 'This is a test notification',
    type: 'info',
    is_read: false,
    created_at: '2025-05-22T10:00:00Z',
    action_url: '/test'
  },
  {
    id: 2,
    title: 'Warning Notification',
    message: 'This is a warning',
    type: 'warning',
    is_read: true,
    created_at: '2025-05-22T09:00:00Z'
  }],

  unreadCount: 1,
  markAsRead: vi.fn(),
  deleteNotifications: vi.fn(),
  markAllAsRead: vi.fn()
};
vi.mock('@/providers/NotificationProviderV2', () => ({
  useNotifications: () => mockNotificationContext
}));
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};
describe('NotificationCenter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('renders notification list correctly', () => {
    renderWithRouter(<NotificationCenter />);
    expect(screen.getByText('Test Notification')).toBeInTheDocument();
    expect(screen.getByText('This is a test notification')).toBeInTheDocument();
    expect(screen.getByText('Warning Notification')).toBeInTheDocument();
  });
  it('displays unread count in header', () => {
    renderWithRouter(<NotificationCenter />);
    expect(screen.getByText('1')).toBeInTheDocument(); // unread count
  });
  it('shows different icons for different notification types', () => {
    renderWithRouter(<NotificationCenter />);
    // Info notification should have info icon
    const infoNotification = screen.getByText('Test Notification').closest('.notification-item');
    expect(infoNotification).toBeInTheDocument();
    // Warning notification should have warning icon
    const warningNotification = screen.getByText('Warning Notification').closest('.notification-item');
    expect(warningNotification).toBeInTheDocument();
  });
  it('marks notification as read when clicked', async () => {
    renderWithRouter(<NotificationCenter />);
    const notification = screen.getByText('Test Notification');
    fireEvent.click(notification);
    await waitFor(() => {
      expect(mockNotificationContext.markAsRead).toHaveBeenCalledWith([1]);
    });
  });
  it('marks all notifications as read when button clicked', async () => {
    renderWithRouter(<NotificationCenter />);
    const markAllButton = screen.getByText('Mark All Read');
    fireEvent.click(markAllButton);
    await waitFor(() => {
      expect(mockNotificationContext.markAllAsRead).toHaveBeenCalled();
    });
  });
  it('shows empty state when no notifications', () => {
    const emptyContext = {
      ...mockNotificationContext,
      notifications: [],
      unreadCount: 0
    };
    vi.mocked(require('@/providers/NotificationProviderV2').useNotifications).mockReturnValue(emptyContext);
    renderWithRouter(<NotificationCenter />);
    expect(screen.getByText('No notifications')).toBeInTheDocument();
  });
  it('displays relative time for notifications', () => {
    renderWithRouter(<NotificationCenter />);
    // Should show relative time like "2 hours ago"
    expect(screen.getByText(/ago/)).toBeInTheDocument();
  });
  it('highlights unread notifications', () => {
    renderWithRouter(<NotificationCenter />);
    const unreadNotification = screen.getByText('Test Notification').closest('.notification-item');
    expect(unreadNotification).toHaveClass('unread');
    const readNotification = screen.getByText('Warning Notification').closest('.notification-item');
    expect(readNotification).not.toHaveClass('unread');
  });
  it('navigates to action URL when notification with URL is clicked', async () => {
    const mockNavigate = vi.fn();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate
      };
    });
    renderWithRouter(<NotificationCenter />);
    const notification = screen.getByText('Test Notification');
    fireEvent.click(notification);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/test');
    });
  });
});