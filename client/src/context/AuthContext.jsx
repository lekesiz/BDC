import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '@/lib/api';

// Create context
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          // Set default auth header
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Check if token is expired
          const decoded = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp < currentTime) {
            // Token is expired, try to refresh
            await refreshToken();
          } else {
            // Token is valid, fetch user data
            const response = await api.get('/api/users/me');
            setUser(response.data);
            setIsAuthenticated(true);
          }
        } catch (error) {
          console.error('Authentication error:', error);
          logout();
        }
      }
      
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  // Login function
  const login = async (email, password, remember = false) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.post('/api/auth/login', { email, password, remember_me: remember });
      
      const { access_token, refresh_token } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', access_token);
      if (remember) {
        localStorage.setItem('refresh_token', refresh_token);
      }
      
      // Set default auth header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data
      const userResponse = await api.get('/api/users/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      
      return userResponse.data;
    } catch (error) {
      console.error('Login error:', error);
      setError(error.response?.data?.message || 'An unexpected error occurred');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.post('/api/auth/register', userData);
      
      const { access_token, refresh_token } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Set default auth header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data
      const userResponse = await api.get('/api/users/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      
      return userResponse.data;
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.response?.data?.message || 'An unexpected error occurred');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = useCallback(async () => {
    try {
      // Call logout API if authenticated
      if (isAuthenticated) {
        await api.post('/api/auth/logout');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear auth state regardless of API call success
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
      setIsAuthenticated(false);
    }
  }, [isAuthenticated]);

  // Refresh token function
  const refreshToken = async () => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }
      
      const response = await api.post('/api/auth/refresh', { refresh_token });
      
      const { access_token } = response.data;
      
      // Store new access token
      localStorage.setItem('access_token', access_token);
      
      // Set default auth header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      throw error;
    }
  };

  // Check if user has a specific role
  const hasRole = (role) => {
    if (!user) return false;
    return user.role === role || (Array.isArray(role) && role.includes(user.role));
  };

  // Context value
  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshToken,
    hasRole
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};