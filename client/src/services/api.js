import axios from 'axios';
/**
 * Base API configuration with default settings
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
});
/**
 * Add authorization header with JWT token
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
/**
 * Handle token expiration and other common API errors
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response && error.response.status === 401) {
      // Clear tokens if they exist
      if (localStorage.getItem('access_token')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // Reload the page to reset application state
        window.location.reload();
      }
    }
    // Handle 403 Forbidden - insufficient permissions
    if (error.response && error.response.status === 403) {
      console.error('Permission denied:', error.response.data);
    }
    // Handle 500 server errors
    if (error.response && error.response.status >= 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);
export default api;