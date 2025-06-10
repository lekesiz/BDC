/**
 * Test Setup for i18n Tests
 * Global configuration and mocks for internationalization testing
 */

import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { initTestI18n, mockLocalStorage } from './utils.js';

// Configure testing library
configure({
  testIdAttribute: 'data-testid',
  asyncUtilTimeout: 5000
});

// Mock i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options) => {
      // Simple mock implementation
      if (options && typeof options === 'object') {
        let result = key;
        Object.entries(options).forEach(([k, v]) => {
          result = result.replace(`{{${k}}}`, v);
        });
        return result;
      }
      return key;
    },
    i18n: {
      language: 'en',
      changeLanguage: jest.fn().mockResolvedValue(undefined),
      on: jest.fn(),
      off: jest.fn(),
      exists: jest.fn().mockReturnValue(true)
    }
  }),
  I18nextProvider: ({ children }) => children,
  Trans: ({ children, i18nKey }) => children || i18nKey
}));

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage(),
  writable: true
});

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: mockLocalStorage(),
  writable: true
});

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }))
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock console methods to reduce noise in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeEach(() => {
  // Suppress specific warnings/errors in tests
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
       args[0].includes('Warning: React does not recognize'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('componentWillReceiveProps has been renamed')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterEach(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Global test utilities
global.testUtils = {
  // Helper to wait for async operations
  waitFor: (fn, timeout = 1000) => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const check = () => {
        try {
          const result = fn();
          if (result) {
            resolve(result);
          } else if (Date.now() - startTime > timeout) {
            reject(new Error('Timeout waiting for condition'));
          } else {
            setTimeout(check, 10);
          }
        } catch (error) {
          if (Date.now() - startTime > timeout) {
            reject(error);
          } else {
            setTimeout(check, 10);
          }
        }
      };
      check();
    });
  },

  // Helper to create test i18n instance
  createTestI18n: initTestI18n,

  // Helper to simulate language change
  simulateLanguageChange: (language) => {
    const event = new CustomEvent('languageChanged', {
      detail: { language }
    });
    window.dispatchEvent(event);
  },

  // Helper to get computed styles
  getComputedStyle: (element, property) => {
    return window.getComputedStyle(element).getPropertyValue(property);
  },

  // Helper to simulate RTL
  simulateRTL: () => {
    document.documentElement.setAttribute('dir', 'rtl');
    document.documentElement.setAttribute('lang', 'ar');
  },

  // Helper to simulate LTR
  simulateLTR: () => {
    document.documentElement.setAttribute('dir', 'ltr');
    document.documentElement.setAttribute('lang', 'en');
  }
};

// Mock API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve('')
  })
);

// Setup global beforeEach and afterEach
beforeEach(() => {
  // Clear all mocks
  jest.clearAllMocks();
  
  // Reset DOM
  document.documentElement.setAttribute('lang', 'en');
  document.documentElement.setAttribute('dir', 'ltr');
  
  // Clear localStorage and sessionStorage
  localStorage.clear();
  sessionStorage.clear();
  
  // Reset any global state
  if (window.i18n) {
    window.i18n.language = 'en';
  }
});

afterEach(() => {
  // Cleanup after each test
  jest.clearAllTimers();
  jest.useRealTimers();
});

// Custom matchers for i18n testing
expect.extend({
  toBeTranslated(received, language) {
    const pass = received && typeof received === 'string' && received.length > 0;
    
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be a valid translation for language ${language}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be a valid translation for language ${language}`,
        pass: false,
      };
    }
  },

  toHaveDirection(received, direction) {
    const actualDirection = window.getComputedStyle(received).direction;
    const pass = actualDirection === direction;
    
    if (pass) {
      return {
        message: () =>
          `expected element not to have direction ${direction}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected element to have direction ${direction} but was ${actualDirection}`,
        pass: false,
      };
    }
  },

  toBeRTL(received) {
    const direction = window.getComputedStyle(received).direction;
    const pass = direction === 'rtl';
    
    if (pass) {
      return {
        message: () => `expected element not to be RTL`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to be RTL but direction was ${direction}`,
        pass: false,
      };
    }
  },

  toBeLTR(received) {
    const direction = window.getComputedStyle(received).direction;
    const pass = direction === 'ltr';
    
    if (pass) {
      return {
        message: () => `expected element not to be LTR`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to be LTR but direction was ${direction}`,
        pass: false,
      };
    }
  }
});

// Export test utilities
export { initTestI18n, mockLocalStorage } from './utils.js';