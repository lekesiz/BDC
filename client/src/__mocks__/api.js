import { vi } from 'vitest'
const api = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  },
  defaults: {
    headers: {
      common: {}
    }
  }
}
export default api