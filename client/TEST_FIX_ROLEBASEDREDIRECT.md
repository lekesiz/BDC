# RoleBasedRedirect Test Fix Documentation

## Issue Overview

The `RoleBasedRedirect.test.jsx` test was failing because it was not properly handling the React Router v6 `Navigate` component in a test environment. The test was trying to check for a redirect by looking for a string in the HTML output, which is not a reliable approach for testing React Router redirects.

## Testing Challenges

1. **React Router Navigation Testing**: Testing components that use `Navigate` from React Router requires special setup, as navigation doesn't work the same way in test environments as it does in browsers.

2. **Router Future Flag Warnings**: The test was showing warnings about React Router future flags, but these warnings don't affect test functionality.

3. **Component Dependencies**: The RoleBasedRedirect component depends on both the auth context and a dashboard component, which needed to be properly mocked.

## Solution Approach

1. **Proper Router Setup**: Instead of just rendering the component within a `MemoryRouter`, we set up a complete routing structure with `Routes` and `Route` components to properly handle navigation.

2. **Mock Component Dependencies**: We mocked both the useAuth hook and the DashboardPageEnhanced component to control their behavior in tests.

3. **Flexible Hook Mocking**: We changed the useAuth mock to use `vi.fn()` so we could easily set different return values for different test cases.

4. **Comprehensive Test Cases**: We added tests for all three main component states:
   - Student redirect to portal
   - Non-student showing dashboard
   - Loading state

5. **Better Testing Assertions**: Instead of checking HTML content, we used proper testing-library assertions with test IDs to verify component rendering.

## Code Changes

### Before:

```jsx
import { render } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import RoleBasedRedirect from '@/components/common/RoleBasedRedirect'

vi.mock('@/hooks/useAuth', () => {
  return {
    useAuth: () => ({ user: { role: 'student' }, isLoading: false }),
  }
})

describe('RoleBasedRedirect', () => {
  it('redirects students to /portal', () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/"]}>
        <RoleBasedRedirect />
      </MemoryRouter>
    )
    // Navigate renders <a href="/portal"> fallback in test DOM
    expect(container.innerHTML).toContain('/portal')
  })
})
```

### After:

```jsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import RoleBasedRedirect from '@/components/common/RoleBasedRedirect'

// Mock the DashboardPageEnhanced component
vi.mock('@/pages/dashboard/DashboardPageEnhanced', () => ({
  default: () => <div data-testid="dashboard">Dashboard</div>
}))

// Mock the useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn()
}))

import { useAuth } from '@/hooks/useAuth'

describe('RoleBasedRedirect', () => {
  it('redirects students to /portal', () => {
    // Set up the mock to return student role
    useAuth.mockReturnValue({ user: { role: 'student' }, isLoading: false })
    
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<RoleBasedRedirect />} />
          <Route path="/portal" element={<div data-testid="portal">Portal</div>} />
        </Routes>
      </MemoryRouter>
    )
    
    // Verify that we've been redirected to the portal
    expect(screen.getByTestId('portal')).toBeInTheDocument()
  })
  
  it('shows dashboard for non-student roles', () => {
    // Set up the mock to return admin role
    useAuth.mockReturnValue({ user: { role: 'admin' }, isLoading: false })
    
    render(
      <MemoryRouter initialEntries={["/"]}>
        <RoleBasedRedirect />
      </MemoryRouter>
    )
    
    // Verify that the dashboard is shown
    expect(screen.getByTestId('dashboard')).toBeInTheDocument()
  })
  
  it('shows loading state when isLoading is true', () => {
    // Set up the mock to return loading state
    useAuth.mockReturnValue({ user: null, isLoading: true })
    
    const { container } = render(
      <MemoryRouter initialEntries={["/"]}>
        <RoleBasedRedirect />
      </MemoryRouter>
    )
    
    // Verify that the loading spinner is shown
    expect(container.querySelector('.animate-spin')).toBeInTheDocument()
  })
})
```

## Key Lessons

1. **Testing Router Navigation**: When testing components that use React Router's `Navigate` component, you need to set up proper route handling with `Routes` and `Route` components.

2. **Flexible Mocking**: Using `vi.fn()` for hook mocks allows easy adjustment of return values for different test cases.

3. **Component Coverage**: It's important to test all possible states of a component (in this case: redirect, dashboard, and loading).

4. **Warning vs Error**: React Router future flags show warnings but don't affect test functionality - they're informational for future React Router versions.

5. **Test ID Selectors**: Using data-testid attributes makes tests more reliable than checking HTML content directly.

## Benefits of Fix

1. **More Robust Tests**: The tests now properly verify all component states and behaviors.
2. **Better Coverage**: We added tests for additional states, improving coverage.
3. **More Maintainable**: The tests are now more resilient to UI changes.
4. **Pattern for Router Testing**: This establishes a pattern for testing redirects in React Router v6.