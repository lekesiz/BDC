import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../../pages/dashboard/DashboardPage';
import { useAuth } from '../../hooks/useAuth';
import api from '../../lib/api';
import { API_ENDPOINTS } from '../../lib/constants';

// Mock modules
vi.mock('../../hooks/useAuth');
vi.mock('../../lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));
vi.mock('../../lib/constants', () => ({
  API_ENDPOINTS: {
    ANALYTICS: {
      DASHBOARD: '/api/analytics/dashboard'
    },
    REPORTS: {
      RECENT: '/api/reports/recent'
    }
  }
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { id: 1, first_name: 'Test', name: 'Test User', role: 'trainer' },
      isAuthenticated: true
    });
    
    // Setup default mock responses
    api.get.mockImplementation((url) => {
      switch (url) {
        case API_ENDPOINTS.ANALYTICS.DASHBOARD:
          return Promise.resolve({
            data: {
              statistics: {
                total_beneficiaries: 50,
                total_evaluations: 10,
                upcoming_sessions: 5,
                completed_evaluations: 30,
                documents_generated: 20
              }
            }
          });
        case API_ENDPOINTS.REPORTS.RECENT:
          return Promise.resolve({ data: [] });
        case '/api/calendar/events':
          return Promise.resolve({ data: { events: [] } });
        case '/api/tests':
          return Promise.resolve({ data: { tests: [] } });
        case '/api/programs':
          return Promise.resolve({ data: [] });
        default:
          return Promise.resolve({ data: {} });
      }
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard components', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      // Check for dashboard header
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
      
      // Check for the welcome message
      expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
      
      // Check for quick actions section
      expect(screen.getByText(/quick actions/i)).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Force all API calls to hang
    api.get.mockImplementation(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('handles error state', async () => {
    // Force API to reject
    api.get.mockRejectedValue(new Error('Failed to fetch'));

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // Wait for the loading state to finish
    await waitFor(() => {
      expect(screen.queryByText(/loading dashboard data/i)).not.toBeInTheDocument();
    });
    
    // Use more specific error message to avoid duplicate matches
    expect(screen.getByText(/Error fetching dashboard data/i)).toBeInTheDocument();
  });

  it('renders different content based on user role', async () => {
    useAuth.mockReturnValue({
      user: { id: 1, first_name: 'Admin', name: 'Admin User', role: 'super_admin' },
      isAuthenticated: true
    });

    // Update API response for admin role
    api.get.mockImplementation((url) => {
      switch (url) {
        case API_ENDPOINTS.ANALYTICS.DASHBOARD:
          return Promise.resolve({
            data: {
              statistics: {
                total_users: 100,
                total_tenants: 5,
                total_beneficiaries: 500,
                total_evaluations: 50
              }
            }
          });
        case API_ENDPOINTS.REPORTS.RECENT:
          return Promise.resolve({ data: [] });
        case '/api/calendar/events':
          return Promise.resolve({ data: { events: [] } });
        case '/api/tests':
          return Promise.resolve({ data: { tests: [] } });
        case '/api/programs':
          return Promise.resolve({ data: [] });
        default:
          return Promise.resolve({ data: {} });
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // For a super_admin, check that we see their name and role-specific content
    await waitFor(() => {
      expect(screen.getByText(/admin/i)).toBeInTheDocument();
      expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
    });
  });

  it('renders recent activities', async () => {
    // Mock the API to return activities
    api.get.mockImplementation((url) => {
      switch (url) {
        case API_ENDPOINTS.ANALYTICS.DASHBOARD:
          return Promise.resolve({
            data: {
              statistics: {}
            }
          });
        case API_ENDPOINTS.REPORTS.RECENT:
          return Promise.resolve({ data: [] });
        case '/api/calendar/events':
          return Promise.resolve({ data: { events: [] } });
        case '/api/programs':
          return Promise.resolve({ data: [] });
        case '/api/tests':
          return Promise.resolve({
            data: {
              tests: [
                {
                  id: 1,
                  title: 'JavaScript Test',
                  status: 'completed',
                  score: 85,
                  date: '2024-01-15T10:00:00Z'
                }
              ]
            }
          });
        default:
          return Promise.resolve({ data: {} });
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/recent evaluations/i)).toBeInTheDocument();
      expect(screen.getByText(/javascript test/i)).toBeInTheDocument();
    });
  });

  it('renders appointment information', async () => {
    // Mock the API to return upcoming appointments
    api.get.mockImplementation((url) => {
      switch (url) {
        case API_ENDPOINTS.ANALYTICS.DASHBOARD:
          return Promise.resolve({
            data: {
              statistics: {}
            }
          });
        case API_ENDPOINTS.REPORTS.RECENT:
          return Promise.resolve({ data: [] });
        case '/api/programs':
          return Promise.resolve({ data: [] });
        case '/api/tests':
          return Promise.resolve({ data: { tests: [] } });
        case '/api/calendar/events':
          return Promise.resolve({
            data: {
              events: [
                {
                  id: 1,
                  title: 'System Update Meeting',
                  date: '2024-01-15',
                  time: '10:00 AM',
                  beneficiary: 'John Doe'
                }
              ]
            }
          });
        default:
          return Promise.resolve({ data: {} });
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      // Check for the specific meeting title which is unique in this context
      expect(screen.getByText(/system update meeting/i)).toBeInTheDocument();
      
      // Check for the meeting details
      expect(screen.getByText(/john doe/i)).toBeInTheDocument();
    });
  });

  it('fetches data on mount', async () => {
    // Reset mocks to track calls
    api.get.mockClear();
    
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      // Verify all expected endpoints were called
      expect(api.get).toHaveBeenCalledWith(API_ENDPOINTS.ANALYTICS.DASHBOARD);
      expect(api.get).toHaveBeenCalledWith(API_ENDPOINTS.REPORTS.RECENT);
      expect(api.get).toHaveBeenCalledWith('/api/calendar/events', expect.any(Object));
      expect(api.get).toHaveBeenCalledWith('/api/tests', expect.any(Object));
    });
  });
});