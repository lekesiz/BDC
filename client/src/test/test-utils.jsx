import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '../components/ui/toast'
import { AuthProvider } from '../contexts/AuthContext'
import { vi } from 'vitest'

// Create a custom render function that includes providers
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

export const AllTheProviders = ({ children }) => {
  const testQueryClient = createTestQueryClient()
  
  return (
    <BrowserRouter>
      <QueryClientProvider client={testQueryClient}>
        <AuthProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  )
}

export const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options })

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
}

// Mock navigation
export const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// re-export everything
export * from '@testing-library/react'

// Override render method
export { customRender as render }