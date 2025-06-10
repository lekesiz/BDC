import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { AuthContext, AuthProvider } from '@/contexts/AuthContext';
import api from '@/lib/api';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Test component to access context
const TestComponent = () => {
  const context = React.useContext(AuthContext);
  
  return (
    <div>
      <div data-testid="is-authenticated">{String(context.isAuthenticated)}</div>
      <div data-testid="is-loading">{String(context.isLoading)}</div>
      <div data-testid="user">{JSON.stringify(context.user)}</div>
      <div data-testid="error">{context.error}</div>
      <button onClick={() => context.login('test@example.com', 'password')}>Login</button>
      <button onClick={() => context.logout()}>Logout</button>
      <button onClick={() => context.refreshToken()}>Refresh</button>
      <div data-testid="has-admin-role">{String(context.hasRole('admin'))}</div>
      <div data-testid="has-permission">{String(context.hasPermission('view_users'))}</div>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('provides initial auth state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
    expect(screen.getByTestId('user')).toHaveTextContent('null');
    expect(screen.getByTestId('error')).toBeEmptyDOMElement();
  });

  it('handles successful login', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      role: 'admin',
      permissions: ['view_users', 'edit_users']
    };

    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
    expect(api.defaults.headers.common['Authorization']).toBe('Bearer mock-access-token');
  });

  it('handles login failure', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        data: { message: 'Invalid credentials' },
        status: 401
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Invalid credentials');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });
  });

  it('handles logout correctly', async () => {
    // Set initial authenticated state
    const mockUser = { id: '1', email: 'test@example.com', role: 'admin' };
    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-access-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Login first
    await user.click(screen.getByText('Login'));
    await waitFor(() => {
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
    });

    // Then logout
    await user.click(screen.getByText('Logout'));

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    expect(api.defaults.headers.common['Authorization']).toBeUndefined();
    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('user')).toHaveTextContent('null');
  });

  it('handles token refresh', async () => {
    localStorageMock.getItem.mockReturnValue('mock-refresh-token');
    
    const mockUser = { id: '1', email: 'test@example.com', role: 'admin' };
    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'new-access-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Refresh'));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/auth/refresh', {
        refresh_token: 'mock-refresh-token'
      });
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new-access-token');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
    });
  });

  it('checks user roles correctly', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      role: 'admin',
      permissions: ['view_users']
    };

    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-access-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('has-admin-role')).toHaveTextContent('true');
    });
  });

  it('checks permissions correctly', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      role: 'trainer',
      permissions: ['view_users', 'create_assessments']
    };

    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-access-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('has-permission')).toHaveTextContent('true');
    });
  });

  it('super admin has all permissions', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@example.com',
      role: 'super_admin',
      permissions: []
    };

    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-access-token',
        user: mockUser
      }
    });

    const user = userEvent.setup();
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('has-permission')).toHaveTextContent('true');
    });
  });

  it('loads user from token on mount', async () => {
    localStorageMock.getItem.mockReturnValue('existing-token');
    
    const mockUser = {
      id: '1', 
      email: 'test@example.com',
      role: 'admin'
    };

    // Mock successful user fetch
    api.get.mockResolvedValueOnce({
      data: mockUser
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
    });
  });
});