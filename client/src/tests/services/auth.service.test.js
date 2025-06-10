import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import {
  login,
  register,
  getCurrentUser,
  updateProfile,
  requestPasswordReset,
  resetPassword,
  changePassword
} from '@/services/auth.service';
import api from '@/services/api';

// Mock api module
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn()
  }
}));

describe('Auth Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('login', () => {
    it('successfully logs in user', async () => {
      const mockResponse = {
        data: {
          user: { id: '1', email: 'test@example.com' },
          token: 'mock-token'
        }
      };
      
      api.post.mockResolvedValueOnce(mockResponse);

      const result = await login('test@example.com', 'password123');

      expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
        email: 'test@example.com',
        password: 'password123'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error on login failure', async () => {
      api.post.mockRejectedValueOnce({
        response: { data: { message: 'Invalid credentials' } }
      });

      await expect(login('test@example.com', 'wrongpassword')).rejects.toThrow('Invalid credentials');
    });

    it('throws generic error when no specific message', async () => {
      api.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(login('test@example.com', 'password')).rejects.toThrow('Login failed');
    });
  });

  describe('register', () => {
    it('successfully registers user', async () => {
      const userData = {
        email: 'newuser@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe'
      };

      const mockResponse = {
        data: {
          user: { id: '1', ...userData },
          token: 'mock-token'
        }
      };
      
      api.post.mockResolvedValueOnce(mockResponse);

      const result = await register(userData);

      expect(api.post).toHaveBeenCalledWith('/api/auth/register', userData);
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error on registration failure', async () => {
      api.post.mockRejectedValueOnce({
        response: { data: { message: 'Email already exists' } }
      });

      await expect(register({ email: 'existing@example.com' })).rejects.toThrow('Email already exists');
    });
  });

  describe('getCurrentUser', () => {
    it('successfully fetches current user', async () => {
      const mockUser = {
        id: '1',
        email: 'user@example.com',
        role: 'student'
      };
      
      api.get.mockResolvedValueOnce({ data: mockUser });

      const result = await getCurrentUser();

      expect(api.get).toHaveBeenCalledWith('/api/auth/me');
      expect(result).toEqual(mockUser);
    });

    it('throws error when fetching user fails', async () => {
      api.get.mockRejectedValueOnce({
        response: { data: { message: 'Unauthorized' } }
      });

      await expect(getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateProfile', () => {
    it('successfully updates profile', async () => {
      const profileData = {
        firstName: 'Jane',
        lastName: 'Smith'
      };

      const mockResponse = {
        data: {
          id: '1',
          email: 'user@example.com',
          ...profileData
        }
      };
      
      api.put.mockResolvedValueOnce(mockResponse);

      const result = await updateProfile(profileData);

      expect(api.put).toHaveBeenCalledWith('/api/auth/profile', profileData);
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error on profile update failure', async () => {
      api.put.mockRejectedValueOnce({
        response: { data: { message: 'Validation error' } }
      });

      await expect(updateProfile({})).rejects.toThrow('Validation error');
    });
  });

  describe('requestPasswordReset', () => {
    it('successfully requests password reset', async () => {
      const mockResponse = {
        data: { message: 'Password reset email sent' }
      };
      
      api.post.mockResolvedValueOnce(mockResponse);

      const result = await requestPasswordReset('user@example.com');

      expect(api.post).toHaveBeenCalledWith('/api/auth/forgot-password', {
        email: 'user@example.com'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when password reset request fails', async () => {
      api.post.mockRejectedValueOnce({
        response: { data: { message: 'User not found' } }
      });

      await expect(requestPasswordReset('nonexistent@example.com')).rejects.toThrow('User not found');
    });

    it('throws generic error when no specific message', async () => {
      api.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(requestPasswordReset('user@example.com')).rejects.toThrow('Failed to request password reset');
    });
  });

  describe('resetPassword', () => {
    it('successfully resets password', async () => {
      const mockResponse = {
        data: { message: 'Password reset successful' }
      };
      
      api.post.mockResolvedValueOnce(mockResponse);

      const result = await resetPassword('reset-token', 'newpassword123');

      expect(api.post).toHaveBeenCalledWith('/api/auth/reset-password', {
        token: 'reset-token',
        password: 'newpassword123'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when password reset fails', async () => {
      api.post.mockRejectedValueOnce({
        response: { data: { message: 'Invalid or expired token' } }
      });

      await expect(resetPassword('invalid-token', 'newpassword')).rejects.toThrow('Invalid or expired token');
    });
  });

  describe('changePassword', () => {
    it('successfully changes password', async () => {
      const mockResponse = {
        data: { message: 'Password changed successfully' }
      };
      
      api.post.mockResolvedValueOnce(mockResponse);

      const result = await changePassword('oldpassword', 'newpassword');

      expect(api.post).toHaveBeenCalledWith('/api/auth/change-password', {
        currentPassword: 'oldpassword',
        newPassword: 'newpassword'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when password change fails', async () => {
      api.post.mockRejectedValueOnce({
        response: { data: { message: 'Current password is incorrect' } }
      });

      await expect(changePassword('wrongpassword', 'newpassword')).rejects.toThrow('Current password is incorrect');
    });

    it('throws generic error when no specific message', async () => {
      api.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(changePassword('oldpassword', 'newpassword')).rejects.toThrow('Failed to change password');
    });
  });
});