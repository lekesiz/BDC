import '@testing-library/jest-dom';
import { vi } from 'vitest';
import apiMock from './mocks/api';

// Set React Router future flags to suppress warnings
window.__REACT_ROUTER_FUTURE__ = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
};

// Mock API globally
vi.mock('@/lib/api', () => ({
  default: apiMock
}));

// Mock jwt-decode
vi.mock('jwt-decode', () => ({
  jwtDecode: vi.fn((token) => {
    // Return a valid decoded token with future expiry
    return {
      sub: '1',
      email: 'test@example.com',
      role: 'admin',
      exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
    };
  })
}));

// Mock i18n for tests
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: {
      language: 'en',
      changeLanguage: vi.fn(),
      use: vi.fn(),
      init: vi.fn(),
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: vi.fn(),
  },
  I18nextProvider: ({ children }) => children,
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock canvas for charts
HTMLCanvasElement.prototype.getContext = vi.fn();

// Mock scrollTo
window.scrollTo = vi.fn();

// Suppress console errors in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
       args[0].includes('Warning: An update to') ||
       args[0].includes('Warning: <PieChart />'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});