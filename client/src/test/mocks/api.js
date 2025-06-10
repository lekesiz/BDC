import { vi } from 'vitest';

// Complete API mock with all required properties
export const createApiMock = () => ({
  get: vi.fn(),
  post: vi.fn(), 
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  request: vi.fn(),
  defaults: {
    headers: {
      common: {}
    }
  },
  interceptors: {
    request: {
      use: vi.fn((onFulfilled, onRejected) => {
        // Return a unique ID for the interceptor
        return Math.random();
      }),
      eject: vi.fn()
    },
    response: {
      use: vi.fn((onFulfilled, onRejected) => {
        // Return a unique ID for the interceptor
        return Math.random();
      }),
      eject: vi.fn()
    }
  }
});

// Default mock implementation
const apiMock = createApiMock();

export default apiMock;