import axios from 'axios';
import { setupMockApi } from '@/lib/setupMockApi';
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // withCredentials: true, // Temporarily disabled for testing
});
// NOTE: Auth interceptors are handled by AuthContext.jsx
// This prevents duplicate interceptor conflicts and infinite loops
// Enable mock API for demo data
if (import.meta.env.VITE_USE_MOCK_API === 'true') {
  setupMockApi(api);
}
export default api;