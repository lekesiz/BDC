import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../../pages/dashboard/DashboardPage';
import { useAuth } from '../../hooks/useAuth';
import axios from 'axios';

vi.mock('../../hooks/useAuth');
vi.mock('axios');

describe('DashboardPage', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { id: 1, name: 'Test User', role: 'trainer' },
      isAuthenticated: true
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard components', async () => {
    axios.get.mockResolvedValue({
      data: {
        stats: {
          totalBeneficiaries: 50,
          activeEvaluations: 10,
          upcomingAppointments: 5,
          completedEvaluations: 30
        },
        recentActivities: [],
        notifications: []
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      expect(screen.getByText(/50/)).toBeInTheDocument();
      expect(screen.getByText(/10/)).toBeInTheDocument();
      expect(screen.getByText(/5/)).toBeInTheDocument();
      expect(screen.getByText(/30/)).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    axios.get.mockReturnValue(new Promise(() => {}));

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    axios.get.mockRejectedValue(new Error('Failed to fetch'));

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/error loading dashboard/i)).toBeInTheDocument();
    });
  });

  it('renders different content based on user role', async () => {
    useAuth.mockReturnValue({
      user: { id: 1, name: 'Admin User', role: 'super_admin' },
      isAuthenticated: true
    });

    axios.get.mockResolvedValue({
      data: {
        stats: {
          totalUsers: 100,
          totalTenants: 5,
          totalBeneficiaries: 500,
          activeEvaluations: 50
        },
        recentActivities: [],
        notifications: []
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/total users/i)).toBeInTheDocument();
      expect(screen.getByText(/total tenants/i)).toBeInTheDocument();
    });
  });

  it('renders recent activities', async () => {
    axios.get.mockResolvedValue({
      data: {
        stats: {},
        recentActivities: [
          {
            id: 1,
            type: 'evaluation_completed',
            title: 'Evaluation Completed',
            description: 'John Doe completed JavaScript Test',
            timestamp: '2024-01-15T10:00:00Z'
          }
        ],
        notifications: []
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/recent activities/i)).toBeInTheDocument();
      expect(screen.getByText(/john doe completed javascript test/i)).toBeInTheDocument();
    });
  });

  it('renders notifications', async () => {
    axios.get.mockResolvedValue({
      data: {
        stats: {},
        recentActivities: [],
        notifications: [
          {
            id: 1,
            type: 'info',
            title: 'System Update',
            message: 'System will be updated tonight',
            timestamp: '2024-01-15T10:00:00Z'
          }
        ]
      }
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/notifications/i)).toBeInTheDocument();
      expect(screen.getByText(/system will be updated tonight/i)).toBeInTheDocument();
    });
  });

  it('refreshes data on interval', async () => {
    axios.get.mockResolvedValue({
      data: {
        stats: {},
        recentActivities: [],
        notifications: []
      }
    });

    vi.useFakeTimers();

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(axios.get).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(60000); // 1 minute

    expect(axios.get).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });
});