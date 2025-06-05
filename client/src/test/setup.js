import '@testing-library/jest-dom';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
// Cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});
// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});
// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;
// Suppress console warnings for tests
const originalWarn = console.warn;
console.warn = (...args) => {
  // Suppress React Router future flag warnings in tests
  if (args[0]?.includes?.('React Router Future Flag Warning')) {
    return;
  }
  originalWarn(...args);
};
// Set test environment
import.meta.env.DEV = false;
import.meta.env.VITE_USE_MOCK_API = 'false';
// Mock the api module
vi.mock('@/lib/api', () => ({
  default: {
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
}));