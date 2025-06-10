import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import LoginPage from '@/pages/auth/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import api from '@/lib/api';

// Mock API
vi.mock('@/lib/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = React.useContext(AuthContext);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Test App Component
const TestApp = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('completes full login flow successfully', async () => {
      const user = userEvent.setup();
      
      // Mock successful login response
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe',
        role: 'admin'
      };
      
      api.post.mockResolvedValueOnce({
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: mockUser
        }
      });

      // Mock successful user fetch
      api.get.mockResolvedValueOnce({
        data: mockUser
      });

      render(<TestApp />);

      // Should redirect to login
      expect(window.location.pathname).toBe('/login');

      // Fill login form
      const emailInput = await screen.findByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /login/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      // Verify API calls
      expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
        email: 'test@example.com',
        password: 'password123'
      });

      // Verify tokens stored
      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
      });

      // Verify auth header set
      expect(api.defaults.headers.common['Authorization']).toBe('Bearer mock-access-token');

      // Should redirect to dashboard
      await waitFor(() => {
        expect(window.location.pathname).toBe('/dashboard');
      });
    });

    it('handles login failure with invalid credentials', async () => {
      const user = userEvent.setup();
      
      // Mock failed login response
      api.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { message: 'Invalid email or password' }
        }
      });

      render(<TestApp />);

      // Fill login form
      const emailInput = await screen.findByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /login/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(loginButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
      });

      // Should not store tokens
      expect(localStorageMock.setItem).not.toHaveBeenCalled();

      // Should remain on login page
      expect(window.location.pathname).toBe('/login');
    });
  });

  describe('Token Management', () => {
    it('uses existing token on page load', async () => {
      // Mock existing token
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'existing-token';
        return null;
      });

      // Mock successful user fetch
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        role: 'admin'
      };
      
      api.get.mockResolvedValueOnce({
        data: mockUser
      });

      render(<TestApp />);

      // Should set auth header with existing token
      await waitFor(() => {
        expect(api.defaults.headers.common['Authorization']).toBe('Bearer existing-token');
      });

      // Should fetch user data
      expect(api.get).toHaveBeenCalledWith('/api/auth/me');

      // Should navigate to dashboard
      await waitFor(() => {
        expect(window.location.pathname).toBe('/dashboard');
      });
    });

    it('handles token refresh when access token expires', async () => {
      const user = userEvent.setup();
      
      // Mock initial login
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        role: 'admin'
      };
      
      api.post.mockResolvedValueOnce({
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: mockUser
        }
      });

      // Mock token refresh
      api.post.mockResolvedValueOnce({
        data: {
          access_token: 'new-access-token',
          user: mockUser
        }
      });

      render(<TestApp />);

      // Login first
      const emailInput = await screen.findByLabelText(/email/i);
      await user.type(emailInput, 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      // Wait for login to complete
      await waitFor(() => {
        expect(window.location.pathname).toBe('/dashboard');
      });

      // Simulate token refresh
      const authContext = screen.getByTestId('auth-context');
      await user.click(screen.getByText('Refresh Token'));

      // Verify refresh API call
      expect(api.post).toHaveBeenCalledWith('/api/auth/refresh', {
        refresh_token: 'mock-refresh-token'
      });

      // Verify new token stored
      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new-access-token');
      });
    });
  });

  describe('Logout Flow', () => {
    it('completes logout flow and cleans up', async () => {
      const user = userEvent.setup();
      
      // Setup authenticated state
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'existing-token';
        if (key === 'refresh_token') return 'existing-refresh-token';
        return null;
      });

      const mockUser = {
        id: '1',
        email: 'test@example.com',
        role: 'admin'
      };
      
      api.get.mockResolvedValueOnce({
        data: mockUser
      });

      render(<TestApp />);

      // Wait for authentication
      await waitFor(() => {
        expect(window.location.pathname).toBe('/dashboard');
      });

      // Click logout button
      const logoutButton = await screen.findByRole('button', { name: /logout/i });
      await user.click(logoutButton);

      // Verify tokens removed
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');

      // Verify auth header cleared
      expect(api.defaults.headers.common['Authorization']).toBeUndefined();

      // Should redirect to login
      await waitFor(() => {
        expect(window.location.pathname).toBe('/login');
      });
    });
  });

  describe('Protected Routes', () => {
    it('redirects to login when accessing protected route without auth', async () => {
      render(<TestApp />);

      // Try to access dashboard directly
      window.history.pushState({}, '', '/dashboard');

      // Should redirect to login
      await waitFor(() => {
        expect(window.location.pathname).toBe('/login');
      });
    });

    it('allows access to protected route when authenticated', async () => {
      // Setup authenticated state
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'existing-token';
        return null;
      });

      const mockUser = {
        id: '1',
        email: 'test@example.com',
        role: 'admin'
      };
      
      api.get.mockResolvedValueOnce({
        data: mockUser
      });

      render(<TestApp />);

      // Should stay on dashboard
      await waitFor(() => {
        expect(window.location.pathname).toBe('/dashboard');
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });
  });

  describe('Role-Based Access', () => {
    it('grants access based on user role', async () => {
      const checkAccess = (user, requiredRole) => {
        if (Array.isArray(requiredRole)) {
          return requiredRole.includes(user.role);
        }
        return user.role === requiredRole || user.role === 'super_admin';
      };

      // Test different role scenarios
      const scenarios = [
        { userRole: 'admin', requiredRole: 'admin', expected: true },
        { userRole: 'trainer', requiredRole: 'admin', expected: false },
        { userRole: 'student', requiredRole: ['trainer', 'admin'], expected: false },
        { userRole: 'trainer', requiredRole: ['trainer', 'admin'], expected: true },
        { userRole: 'super_admin', requiredRole: 'admin', expected: true }
      ];

      scenarios.forEach(({ userRole, requiredRole, expected }) => {
        const user = { role: userRole };
        expect(checkAccess(user, requiredRole)).toBe(expected);
      });
    });
  });
});