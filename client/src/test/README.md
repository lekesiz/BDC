# BDC Frontend Test Suite

This directory contains the comprehensive test suite for the BDC frontend React application.

## Test Structure

```
src/
├── test/
│   ├── setup.js           # Test environment setup
│   ├── test-utils.jsx     # Custom render utilities
│   └── README.md          # This file
├── pages/
│   ├── auth/__tests__/    # Authentication page tests
│   └── beneficiaries/__tests__/  # Beneficiary page tests
├── components/
│   └── ui/__tests__/      # UI component tests
├── hooks/
│   └── __tests__/         # Custom hook tests
└── services/
    └── __tests__/         # Service/API tests
```

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install test dependencies:
   ```bash
   npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
   ```

### Test Commands

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui

# Use the test runner script
./run_tests.sh [watch|coverage|ui]
```

## Test Configuration

Tests are configured in `vitest.config.js`:
- Environment: jsdom
- Framework: Vitest
- Testing Library: React Testing Library
- Coverage: V8

## Writing Tests

### Component Tests

```jsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '../test/test-utils'
import userEvent from '@testing-library/user-event'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  const user = userEvent.setup()

  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('handles user interaction', async () => {
    render(<MyComponent />)
    
    const button = screen.getByRole('button')
    await user.click(button)
    
    expect(screen.getByText('After Click')).toBeInTheDocument()
  })
})
```

### Hook Tests

```jsx
import { renderHook, act } from '@testing-library/react'
import { useCustomHook } from './useCustomHook'

describe('useCustomHook', () => {
  it('returns expected value', () => {
    const { result } = renderHook(() => useCustomHook())
    
    expect(result.current.value).toBe('expected')
    
    act(() => {
      result.current.setValue('new value')
    })
    
    expect(result.current.value).toBe('new value')
  })
})
```

### API/Service Tests

```jsx
import { describe, it, expect, vi } from 'vitest'
import api from './api'
import { fetchData } from './dataService'

vi.mock('./api')

describe('dataService', () => {
  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }
    api.get.mockResolvedValue({ data: mockData })
    
    const result = await fetchData()
    
    expect(api.get).toHaveBeenCalledWith('/data')
    expect(result).toEqual(mockData)
  })
})
```

## Test Utilities

### Custom Render

The `test-utils.jsx` file provides a custom render function that includes all necessary providers:

```jsx
import { render } from './test/test-utils'

// This automatically wraps components with:
// - BrowserRouter
// - QueryClient
// - AuthProvider
// - ToastProvider
```

### Mock Utilities

Common mocks are available in test-utils:
- `mockAuthContext`: Mock authentication context
- `mockNavigate`: Mock navigation function

## Best Practices

1. **Use descriptive test names**
   ```jsx
   it('displays error message when form submission fails')
   ```

2. **Follow AAA pattern**
   - Arrange: Set up test data
   - Act: Perform the action
   - Assert: Check the result

3. **Test user behavior, not implementation**
   ```jsx
   // Good
   await user.click(screen.getByRole('button', { name: /submit/i }))
   
   // Avoid
   await user.click(wrapper.find('.submit-btn'))
   ```

4. **Use proper queries**
   - Prefer: `getByRole`, `getByLabelText`, `getByText`
   - Avoid: `getByTestId`, `querySelector`

5. **Mock external dependencies**
   ```jsx
   vi.mock('../services/api')
   ```

6. **Test accessibility**
   ```jsx
   expect(screen.getByRole('button')).toHaveAttribute('aria-label')
   ```

## Test Coverage

Aim for:
- Statements: >80%
- Branches: >75%
- Functions: >80%
- Lines: >80%

View coverage report:
```bash
npm run test:coverage
open coverage/index.html
```

## Common Patterns

### Testing Forms

```jsx
const user = userEvent.setup()

// Fill form
await user.type(screen.getByLabelText(/email/i), 'test@example.com')
await user.type(screen.getByLabelText(/password/i), 'password123')

// Submit
await user.click(screen.getByRole('button', { name: /submit/i }))

// Check result
await waitFor(() => {
  expect(screen.getByText(/success/i)).toBeInTheDocument()
})
```

### Testing Loading States

```jsx
render(<DataComponent />)

// Check loading
expect(screen.getByText(/loading/i)).toBeInTheDocument()

// Wait for data
await waitFor(() => {
  expect(screen.getByText(/data loaded/i)).toBeInTheDocument()
})
```

### Testing Error States

```jsx
// Mock error
api.get.mockRejectedValue(new Error('Failed'))

render(<DataComponent />)

await waitFor(() => {
  expect(screen.getByText(/error occurred/i)).toBeInTheDocument()
})
```

## Debugging Tests

1. **Use screen.debug()**
   ```jsx
   screen.debug() // Prints current DOM
   ```

2. **Use console.log in tests**
   ```jsx
   console.log(result.current)
   ```

3. **Run specific test**
   ```bash
   npm run test -- LoginPage.test.jsx
   ```

4. **Use test.only**
   ```jsx
   it.only('runs only this test', () => {})
   ```

## Continuous Integration

Tests are automatically run:
- On pull requests
- Before deployment
- On main branch commits

## Troubleshooting

### Common Issues

1. **Module not found**
   - Check import paths
   - Ensure aliases are configured

2. **React state updates**
   - Use `waitFor` for async updates
   - Use `act` for synchronous updates

3. **Navigation errors**
   - Mock `useNavigate` properly
   - Check router setup

4. **Provider errors**
   - Use custom render function
   - Check provider hierarchy

## Contributing

1. Write tests for new features
2. Update tests for modified features
3. Ensure all tests pass
4. Maintain or improve coverage
5. Follow testing best practices