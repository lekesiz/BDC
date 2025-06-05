import api from './api';
/**
 * Log in a user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} User data and token
 */
export const login = async (email, password) => {
  try {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Login failed');
  }
};
/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @returns {Promise<Object>} User data and token
 */
export const register = async (userData) => {
  try {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Registration failed');
  }
};
/**
 * Get the current user data
 * @returns {Promise<Object>} User data
 */
export const getCurrentUser = async () => {
  try {
    const response = await api.get('/api/auth/me');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Failed to get user data');
  }
};
/**
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>} Updated user data
 */
export const updateProfile = async (profileData) => {
  try {
    const response = await api.put('/api/auth/profile', profileData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Failed to update profile');
  }
};
/**
 * Request password reset
 * @param {string} email - User email
 * @returns {Promise<Object>} Success message
 */
export const requestPasswordReset = async (email) => {
  try {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Failed to request password reset');
  }
};
/**
 * Reset password with token
 * @param {string} token - Reset token
 * @param {string} password - New password
 * @returns {Promise<Object>} Success message
 */
export const resetPassword = async (token, password) => {
  try {
    const response = await api.post('/api/auth/reset-password', { token, password });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Failed to reset password');
  }
};
/**
 * Change password
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} Success message
 */
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const response = await api.post('/api/auth/change-password', { 
      currentPassword, 
      newPassword 
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Failed to change password');
  }
};