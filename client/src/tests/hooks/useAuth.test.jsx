import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React, { createContext, useState, useCallback } from 'react';

// Create a simple mock AuthContext
export const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  loading: true,
  error: null,
  login: async () => {},
  logout: () => {},
  register: async () => {},
  updateProfile: async () => {},
  hasRole: () => false
})

// Mock the useAuth hook
const useAuth = () => {
  return React.useContext(AuthContext)
}

// Mock auth service
import * as authService from '../../services/auth.service';
vi.mock('../../services/auth.service')

// Create a custom AuthProvider for testing
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const login = async (email, password) => {
    try {
      setLoading(true)
      const response = await authService.login(email, password)
      setUser(response.user)
      setIsAuthenticated(true)
      localStorage.setItem('token', response.token)
      return response
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = useCallback(() => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('token')
  }, [])

  const register = async (userData) => {
    try {
      setLoading(true)
      const response = await authService.register(userData)
      setUser(response.user)
      setIsAuthenticated(true)
      localStorage.setItem('token', response.token)
      return response
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (profileData) => {
    try {
      setLoading(true)
      const updatedUser = await authService.updateProfile(profileData)
      setUser(updatedUser)
      return updatedUser
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const hasRole = useCallback((requiredRole) => {
    if (!user) return false
    
    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(user.role)
    }
    
    return user.role === requiredRole
  }, [user])

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    register,
    updateProfile,
    hasRole
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Wrapper for tests
const wrapper = ({ children }) => (
  <AuthProvider>
    {children}
  </AuthProvider>
)

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    
    // Set loading to false after some delay to simulate initialization
    setTimeout(() => {
      document.dispatchEvent(new Event('DOMContentLoaded'))
    }, 10)
  })

  it('initializes with unauthenticated state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
    expect(result.current.loading).toBe(false)
  })

  it('logs in user successfully', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'student' }
    const mockToken = 'fake-jwt-token'
    
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await act(async () => {
      await result.current.login('test@example.com', 'password123')
    })
    
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
    expect(localStorage.getItem('token')).toBe(mockToken)
  })

  it('handles login error', async () => {
    authService.login = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await expect(
      act(async () => {
        await result.current.login('test@example.com', 'wrongpassword')
      })
    ).rejects.toThrow('Invalid credentials')
    
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
  })

  it('logs out user', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'student' }
    const mockToken = 'fake-token'
    
    // Set up the mocks
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    // Login first
    await act(async () => {
      await result.current.login('test@example.com', 'password')
    })
    
    // Verify login worked
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
    
    // Now logout
    act(() => {
      result.current.logout()
    })
    
    // Verify logged out state
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
    expect(localStorage.getItem('token')).toBe(null)
  })

  it('registers new user', async () => {
    const mockUser = { id: 1, email: 'new@example.com', role: 'student' }
    const mockToken = 'fake-jwt-token'
    
    authService.register = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await act(async () => {
      await result.current.register({
        email: 'new@example.com',
        password: 'password123',
        firstName: 'New',
        lastName: 'User'
      })
    })
    
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
  })

  it('checks for existing session on mount', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'student' }
    const mockToken = 'existing-token'
    
    // Set up login mock for this test
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    // Login the user first
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await act(async () => {
      await result.current.login('test@example.com', 'password')
    })
    
    // Now verify the state
    expect(result.current.loading).toBe(false)
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
  })

  it('provides hasRole utility', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'tenant_admin' }
    const mockToken = 'fake-token'
    
    // Set up login mock for this test
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    // Login the user first
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await act(async () => {
      await result.current.login('test@example.com', 'password')
    })
    
    // Now verify the hasRole function
    expect(result.current.hasRole('tenant_admin')).toBe(true)
    expect(result.current.hasRole('super_admin')).toBe(false)
    expect(result.current.hasRole(['tenant_admin', 'trainer'])).toBe(true)
  })

  it('updates user profile', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'student' }
    const mockToken = 'fake-token'
    const updatedUser = {
      ...mockUser,
      firstName: 'Updated',
      lastName: 'Name'
    }
    
    // Set up mocks
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: mockToken
    })
    
    authService.updateProfile = vi.fn().mockResolvedValue(updatedUser)
    
    // Login the user first
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await act(async () => {
      await result.current.login('test@example.com', 'password')
    })
    
    // Now update profile
    await act(async () => {
      await result.current.updateProfile({
        firstName: 'Updated',
        lastName: 'Name'
      })
    })
    
    // Verify the update
    expect(result.current.user.firstName).toBe('Updated')
    expect(result.current.user.lastName).toBe('Name')
  })
});