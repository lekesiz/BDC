import axios from 'axios';
import { setupMockApi } from '@/lib/setupMockApi';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Get the token from localStorage
    const token = localStorage.getItem('access_token');
    
    // If token exists, add it to the request header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 (Unauthorized) and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          // Try to refresh the token with correct base URL
          const response = await api.post('/api/auth/refresh', {}, {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          });
          
          const { access_token } = response.data;
          
          // Store new token
          localStorage.setItem('access_token', access_token);
          
          // Update default header
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, handle logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // If your app has global events, dispatch a logout event
        // window.dispatchEvent(new CustomEvent('auth:logout'));
        
        // Redirect to login (you might want to use a more elegant solution)
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Enable mock API for demo data
console.log('🚀 API backend at:', api.defaults.baseURL);
if (import.meta.env.VITE_USE_MOCK_API === 'true') {
  console.log('🔧 Mock API enabled for demo data');
  setupMockApi(api);
} else {
  console.log('🔧 Using real backend');
}

export default api;