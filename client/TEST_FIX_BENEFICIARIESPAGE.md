# BeneficiariesPage Test Fix Documentation

## Issue Overview

The `BeneficiariesPage.test.jsx` was experiencing failures due to a combination of issues related to:

1. **Missing or incorrect import paths for beneficiary services**
2. **Incomplete mocking of dependencies** including React Router, toast notifications, and API services
3. **Asynchronous testing challenges** with proper rendering and event handling
4. **Component-specific UI selectors** that weren't reliable in the test environment

## Testing Challenges

1. **Service Integration**: The BeneficiariesPage component relies heavily on the beneficiary service for data fetching, filtering, and pagination, requiring proper mocking of API responses.

2. **Complex UI Interactions**: Testing search functionality, filters, pagination, and row-level actions (view, edit) was challenging due to the dynamic nature of the component.

3. **Navigation Testing**: Testing navigation to detail pages and the create beneficiary page required proper mocking of React Router's `useNavigate` hook.

4. **Toast Notifications**: Error handling in the component uses a toast notification system that needed to be properly mocked.

5. **Pagination Component**: The pagination component had accessibility attributes that were being used as selectors, making the tests brittle when the component changed.

## Solution Approach

1. **Comprehensive Mocking Strategy**: 
   - Created proper mocks for all external dependencies including beneficiary services
   - Used `vi.importActual` to maintain actual implementations where needed while overriding specific functions

2. **Improved Test Data**: 
   - Defined consistent mock data for beneficiaries to be used across all tests
   - Included all required fields in the mock data to prevent runtime errors

3. **Better Async Testing**: 
   - Used `waitFor` with appropriate expectations to handle asynchronous operations
   - Added proper user interaction simulation with `userEvent` instead of direct DOM manipulation

4. **More Reliable Selectors**: 
   - Replaced text-based selectors with role-based and label-based selectors where possible
   - Used data-testid attributes for elements that were difficult to select by other means

5. **Isolated Test Cases**: 
   - Each test now focuses on a specific functionality rather than trying to test multiple aspects at once
   - Properly reset mocks between tests to prevent test pollution

## Code Changes

### Before:

```jsx
// Missing proper mock implementation
vi.mock('../../../services/beneficiary.service')

// Incomplete mock data
const mockBeneficiaries = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com'
  }
]

it('renders beneficiaries list', () => {
  render(<BeneficiariesPage />)
  
  // No waiting for async operations
  expect(screen.getByText('Beneficiaries')).toBeInTheDocument()
  expect(screen.getByText('John Doe')).toBeInTheDocument()
})
```

### After:

```jsx
// Complete mock implementation with importActual
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

// Comprehensive mock data
const mockBeneficiaries = [
  {
    id: 1,
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+33612345678',
    status: 'active',
    trainer: { name: 'Trainer 1' }
  },
  // More detailed mock data...
]

// Mock the beneficiary service
vi.mock('../../../services/beneficiary.service')

beforeEach(() => {
  vi.clearAllMocks()
  beneficiaryService.getBeneficiaries = vi.fn().mockResolvedValue({
    data: mockBeneficiaries,
    total: 2,
    page: 1,
    totalPages: 1
  })
})

it('renders beneficiaries list', async () => {
  render(<BeneficiariesPage />)
  
  // Proper async handling with waitFor
  await waitFor(() => {
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Add Beneficiary/i })).toBeInTheDocument()
  })
  
  // Check if beneficiaries are displayed after data loads
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })
})
```

### Improved Navigation Testing:

```jsx
it('navigates to beneficiary detail page', async () => {
  const navigate = vi.fn()
  vi.mocked(require('react-router-dom').useNavigate).mockReturnValue(navigate)
  
  render(<BeneficiariesPage />)
  
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })
  
  const firstBeneficiary = screen.getByText('John Doe')
  await user.click(firstBeneficiary)
  
  expect(navigate).toHaveBeenCalledWith('/beneficiaries/1')
})
```

### Improved Error Handling Testing:

```jsx
it('shows error message on API failure', async () => {
  beneficiaryService.getBeneficiaries = vi.fn().mockRejectedValue(
    new Error('Failed to fetch beneficiaries')
  )
  
  const mockAddToast = vi.fn()
  vi.mocked(require('@/components/ui/toast').useToast).mockReturnValue({
    addToast: mockAddToast
  })
  
  render(<BeneficiariesPage />)
  
  await waitFor(() => {
    expect(mockAddToast).toHaveBeenCalledWith(expect.objectContaining({
      type: 'error',
      title: 'Failed to load beneficiaries'
    }))
  })
})
```

## Key Lessons

1. **Mock Cleanup Is Critical**: Always reset mocks between tests using `vi.clearAllMocks()` to prevent test pollution.

2. **Comprehensive Mock Data**: Ensure mock data includes all fields that the component expects to avoid runtime errors.

3. **Async Testing Patterns**: Always use `waitFor` with proper expectations when testing components with async operations.

4. **Mock External Dependencies**: For components that interact with services and external hooks, create proper mocks for all dependencies.

5. **Reliable UI Selectors**: Prefer role-based, label-based, and test ID-based selectors over text-based selectors for better test reliability.

6. **Isolate Navigation Logic**: When testing navigation, mock the navigation function and verify it's called with the correct parameters rather than trying to test actual navigation.

7. **Error State Testing**: Always include tests for error states to ensure the component handles failures gracefully.

## Benefits of Fix

1. **More Reliable Tests**: The tests now properly handle asynchronous operations and are less brittle to UI changes.

2. **Comprehensive Coverage**: We now test all major features including search, filtering, pagination, navigation, and error handling.

3. **Better Isolation**: By properly mocking all dependencies, the tests truly isolate the BeneficiariesPage component.

4. **Maintainable Tests**: The tests are now easier to maintain as they focus on component behavior rather than implementation details.

5. **Pattern for List Component Testing**: This establishes a pattern for testing list-based components with search, pagination, and row-level actions.