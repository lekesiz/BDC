import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { act } from 'react-dom/test-utils'
import { useAuth } from '../useAuth'
import { AuthProvider } from '../../contexts/AuthContext'
import * as authService from '../../services/auth.service'

vi.mock('../../services/auth.service')

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('initializes with unauthenticated state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
    expect(result.current.loading).toBe(true)
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
    localStorage.setItem('token', 'fake-token')
    
    authService.getCurrentUser = vi.fn().mockResolvedValue(mockUser)
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })
    
    act(() => {
      result.current.logout()
    })
    
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
    localStorage.setItem('token', 'existing-token')
    
    authService.getCurrentUser = vi.fn().mockResolvedValue(mockUser)
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
  })

  it('handles expired token', async () => {
    localStorage.setItem('token', 'expired-token')
    
    authService.getCurrentUser = vi.fn().mockRejectedValue(new Error('Token expired'))
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
    expect(localStorage.getItem('token')).toBe(null)
  })

  it('provides hasRole utility', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'tenant_admin' }
    localStorage.setItem('token', 'fake-token')
    
    authService.getCurrentUser = vi.fn().mockResolvedValue(mockUser)
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    
    expect(result.current.hasRole('tenant_admin')).toBe(true)
    expect(result.current.hasRole('super_admin')).toBe(false)
    expect(result.current.hasRole(['tenant_admin', 'trainer'])).toBe(true)
  })

  it('updates user profile', async () => {
    const mockUser = { id: 1, email: 'test@example.com', role: 'student' }
    localStorage.setItem('token', 'fake-token')
    
    authService.getCurrentUser = vi.fn().mockResolvedValue(mockUser)
    authService.updateProfile = vi.fn().mockResolvedValue({
      ...mockUser,
      firstName: 'Updated',
      lastName: 'Name'
    })
    
    const { result } = renderHook(() => useAuth(), { wrapper })
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    
    await act(async () => {
      await result.current.updateProfile({
        firstName: 'Updated',
        lastName: 'Name'
      })
    })
    
    expect(result.current.user.firstName).toBe('Updated')
    expect(result.current.user.lastName).toBe('Name')
  })
})