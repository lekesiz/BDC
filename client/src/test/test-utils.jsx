import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '../components/ui/toast';
import { AuthContext } from '../contexts/AuthContext';
import { vi } from 'vitest';
// Create a custom render function that includes providers
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});
// Mock auth context
export const mockAuthContext = {
  user: {
    id: 1,
    email: 'test@example.com',
    role: 'tenant_admin',
    tenant_id: 1,
  },
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  isAuthenticated: true,
  refreshToken: vi.fn(),
  hasRole: vi.fn(() => true),
  hasPermission: vi.fn(() => true),
  theme: 'light',
  toggleTheme: vi.fn(),
  isDark: false
};
export const AllTheProviders = ({ children }) => {
  const testQueryClient = createTestQueryClient()
  return (
    <BrowserRouter>
      <QueryClientProvider client={testQueryClient}>
        <AuthContext.Provider value={mockAuthContext}>
          <ToastProvider>
            {children}
          </ToastProvider>
        </AuthContext.Provider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};
export const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options });
// This is now defined above with the updated version
// Mock navigation
export const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
});
// re-export everything
export * from '@testing-library/react';
// Override render method
export { customRender as render };