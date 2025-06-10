/**
 * Jest Configuration for i18n Tests
 */

module.exports = {
  displayName: 'i18n Tests',
  testMatch: [
    '<rootDir>/tests/i18n/**/*.test.{js,jsx}',
    '<rootDir>/tests/i18n/**/*.spec.{js,jsx}'
  ],
  
  // Setup files
  setupFilesAfterEnv: [
    '<rootDir>/tests/i18n/setup.js'
  ],
  
  // Module mapping
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/client/src/$1',
    '^@components/(.*)$': '<rootDir>/client/src/components/$1',
    '^@i18n/(.*)$': '<rootDir>/client/src/i18n/$1',
    '^@utils/(.*)$': '<rootDir>/client/src/utils/$1'
  },
  
  // Transform files
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
    '^.+\\.css$': 'jest-transform-css'
  },
  
  // Test environment
  testEnvironment: 'jsdom',
  
  // Coverage configuration
  collectCoverageFrom: [
    'client/src/i18n/**/*.{js,jsx}',
    'client/src/components/**/*.{js,jsx}',
    'client/src/hooks/useTranslations.js',
    '!client/src/**/*.test.{js,jsx}',
    '!client/src/**/*.spec.{js,jsx}',
    '!client/src/**/__tests__/**',
    '!client/src/**/__mocks__/**'
  ],
  
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  
  // Module directories
  moduleDirectories: [
    'node_modules',
    '<rootDir>/client/src',
    '<rootDir>/tests'
  ],
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/build/',
    '/dist/'
  ],
  
  // Mock modules
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/tests/i18n/__mocks__/fileMock.js'
  },
  
  // Global variables
  globals: {
    'process.env.NODE_ENV': 'test'
  },
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Timeout for tests
  testTimeout: 10000
};