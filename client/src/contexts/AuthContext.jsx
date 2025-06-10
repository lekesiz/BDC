// TODO: i18n - processed
import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import api from '@/lib/api';
// Create context
import { useTranslation } from "react-i18next";export const AuthContext = createContext();
export const AuthProvider = ({ children }) => {const { t } = useTranslation();
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // Check if user has required role
  const hasRole = useCallback((requiredRole) => {
    if (!user) return false;
    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(user.role);
    }
    return user.role === requiredRole;
  }, [user]);
  // Check if user has permission
  const hasPermission = useCallback((permission) => {
    if (!user) return false;
    // Super admin has all permissions
    if (user.role === 'super_admin') return true;
    // Check specific permissions based on role
    return user.permissions?.includes(permission) || false;
  }, [user]);
  // Refresh token
  const refreshToken = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      const response = await api.post('/api/auth/refresh', {
        refresh_token: refreshToken
      });
      const { access_token, user: userData } = response.data;
      // Update tokens
      localStorage.setItem('access_token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      // Update user state
      setUser(userData);
      setIsAuthenticated(true);
      return access_token;
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  }, []);
  // Logout function
  const logout = useCallback(() => {
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // Clear auth header
    delete api.defaults.headers.common['Authorization'];
    // Clear state
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  }, []);
  // Login function
  const login = async (email, password, remember = false) => {
    try {
      setError(null);
      setIsLoading(true);
      const response = await api.post('/api/auth/login', {
        email,
        password,
        remember
      });
      const { access_token, refresh_token, user: userData } = response.data;
      // Store tokens
      localStorage.setItem('access_token', access_token);
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token);
      }
      // Set default auth header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      // Update state
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      const errorMessage = error.response?.data?.message || 'Failed to login';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  };
  // Register function - MISSING FUNCTION ADDED
  const register = async (userData) => {
    try {
      setError(null);
      setIsLoading(true);
      const response = await api.post('/api/auth/register', userData);
      const { access_token, refresh_token, user } = response.data;
      // Store tokens
      localStorage.setItem('access_token', access_token);
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token);
      }
      // Set default auth header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      // Update state
      setUser(user);
      setIsAuthenticated(true);
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.response?.data?.message || 'Failed to register');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
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
  }, [refreshToken, logout]);
  // Request interceptor to add token
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    // Response interceptor to handle token refresh
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        // Skip refresh logic for login and refresh endpoints
        const isAuthEndpoint = originalRequest.url?.includes('/auth/login') ||
        originalRequest.url?.includes('/auth/refresh');
        if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
          originalRequest._retry = true;
          try {
            // Try to refresh token
            const newToken = await refreshToken();
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout
            logout();
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );
    // Cleanup
    return () => {
      api.interceptors.request.eject(requestInterceptor);
      api.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshToken, logout]);
  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register, // ADDED MISSING REGISTER FUNCTION
    logout,
    refreshToken,
    hasRole,
    hasPermission
  };
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>);

};