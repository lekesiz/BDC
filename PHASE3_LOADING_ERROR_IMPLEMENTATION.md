# Phase 3: Loading States & Error Handling Implementation Guide

## Overview
This document outlines the implementation of comprehensive loading states and error handling for the BDC application.

## New Components and Utilities

### 1. Loading States
- **LoadingAnimations.jsx**: Enhanced loading components with animations
  - `PulsingDots`: Animated dots loader
  - `SpinningCircle`: Circular spinner
  - `ProgressBar`: Progress indicator
  - `SkeletonPulse`: Skeleton loading animation
  - `CardSkeleton`, `TableSkeleton`, `FormSkeleton`: Specific skeleton loaders
  - `LoadingOverlay`: Full-screen loading overlay
  - `ButtonLoading`: Button with loading state

### 2. Error States
- **ErrorStates.jsx**: Comprehensive error components
  - `NetworkError`: Network connection issues
  - `PermissionError`: Authorization errors
  - `NotFoundError`: 404 errors
  - `ServerError`: Server-side errors
  - `ErrorState`: Generic error with smart detection
  - `InlineError`: Inline error messages
  - `FieldError`: Form field errors
  - `ErrorList`: Multiple error display

### 3. Async Data Handling
- **AsyncData.jsx**: Smart data fetching components
  - `AsyncData`: Basic async data with loading/error states
  - `AsyncPaginatedData`: Paginated data fetching
  - `AsyncInfiniteData`: Infinite scroll implementation

### 4. Custom Hooks
- **useAsyncOperation.js**: Centralized async operation handling
  - `useAsyncOperation`: Base hook for async operations
  - `useApiCall`: API-specific async handling
  - `useFormSubmit`: Form submission handler
  - `useCachedData`: Data fetching with caching

### 5. Error Utilities
- **errorHandling.js**: Error handling utilities
  - Error type detection
  - User-friendly error messages
  - Error logging
  - Retry with exponential backoff
  - Validation error formatting

### 6. Global Error Context
- **ErrorContext.jsx**: Centralized error management
  - Global error notifications
  - Error queue management
  - Error boundary integration

## Implementation Examples

### 1. Basic Page with Loading/Error States

```jsx
import { useState, useEffect } from 'react';
import { useApiCall } from '@/hooks/useAsyncOperation';
import { AsyncData } from '@/components/common/AsyncData';
import { CardSkeleton } from '@/components/common/LoadingAnimations';
import api from '@/lib/api';

function UsersPage() {
  const { data, loading, error, refetch } = useApiCall(
    () => api.get('/users'),
    { immediate: true }
  );

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-6">Users</h1>
      
      <AsyncData
        loading={loading}
        error={error}
        data={data}
        loadingComponent={<CardSkeleton />}
        render={(users) => (
          <div className="grid gap-4">
            {users.map(user => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>
        )}
      />
    </div>
  );
}
```

### 2. Form with Loading States

```jsx
import { useFormSubmit } from '@/hooks/useAsyncOperation';
import { ButtonLoading } from '@/components/common/LoadingAnimations';
import { FieldError } from '@/components/common/ErrorStates';
import api from '@/lib/api';

function CreateUserForm() {
  const { handleSubmit, isSubmitting, error } = useFormSubmit(
    async (data) => {
      return api.post('/users', data);
    },
    {
      successMessage: 'User created successfully',
      onSuccess: () => {
        router.push('/users');
      }
    }
  );

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <input
          type="text"
          name="name"
          placeholder="Name"
          className="w-full p-2 border rounded"
        />
        <FieldError error={error?.fields?.name} />
      </div>
      
      <ButtonLoading
        type="submit"
        loading={isSubmitting}
        loadingText="Creating..."
        className="btn btn-primary"
      >
        Create User
      </ButtonLoading>
    </form>
  );
}
```

### 3. Paginated Data Table

```jsx
import { AsyncPaginatedData } from '@/components/common/AsyncData';
import { TableSkeleton } from '@/components/common/LoadingAnimations';
import api from '@/lib/api';

function BeneficiariesTable() {
  const fetchBeneficiaries = ({ page, per_page }) => {
    return api.get('/beneficiaries', { params: { page, per_page } });
  };

  return (
    <AsyncPaginatedData
      fetchData={fetchBeneficiaries}
      pageSize={20}
      loadingComponent={<TableSkeleton rows={5} columns={6} />}
      render={(beneficiaries) => (
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {beneficiaries.map(beneficiary => (
              <tr key={beneficiary.id}>
                <td>{beneficiary.name}</td>
                <td>{beneficiary.email}</td>
                <td>{beneficiary.status}</td>
                <td>
                  <button>Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    />
  );
}
```

### 4. Global Error Handling Setup

```jsx
// In App.jsx
import { ErrorProvider, ContextErrorBoundary } from '@/contexts/ErrorContext';

function App() {
  return (
    <ErrorProvider options={{ position: 'top-right' }}>
      <ContextErrorBoundary>
        <Router>
          <Routes>
            {/* Your routes */}
          </Routes>
        </Router>
      </ContextErrorBoundary>
    </ErrorProvider>
  );
}
```

### 5. Using Error Context

```jsx
import { useError } from '@/contexts/ErrorContext';

function SomeComponent() {
  const { showError, showSuccess } = useError();
  
  const handleAction = async () => {
    try {
      const result = await someAsyncOperation();
      showSuccess('Operation completed successfully');
    } catch (error) {
      showError(error.message, {
        title: 'Operation Failed',
        details: error
      });
    }
  };
  
  return (
    <button onClick={handleAction}>
      Perform Action
    </button>
  );
}
```

## Best Practices

### 1. Choose the Right Loading Component
- Use `SkeletonLoaders` for content that has a known structure
- Use `SpinningCircle` or `PulsingDots` for indeterminate loading
- Use `ProgressBar` when you can track progress
- Use `LoadingOverlay` for full-page operations

### 2. Handle Errors Appropriately
- Use specific error components (`NetworkError`, `PermissionError`) when possible
- Provide retry options for transient errors
- Show helpful error messages with actionable steps
- Log errors for debugging but show user-friendly messages

### 3. Async Operations
- Use `useAsyncOperation` for all async operations
- Implement retry logic for network failures
- Cache data when appropriate with `useCachedData`
- Handle loading states at the appropriate level

### 4. Form Handling
- Use `useFormSubmit` for form submissions
- Show field-level errors with `FieldError`
- Disable submit button during submission
- Show success messages after successful submission

### 5. Performance Considerations
- Implement proper caching strategies
- Use pagination or infinite scroll for large datasets
- Show skeleton loaders that match actual content structure
- Minimize layout shifts during loading

## Migration Guide

### 1. Update Existing Pages
Replace basic loading/error handling with new components:

```jsx
// Before
if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error.message}</div>;

// After
return (
  <AsyncData
    loading={loading}
    error={error}
    data={data}
    loadingComponent={<CardSkeleton />}
    render={(data) => <YourContent data={data} />}
  />
);
```

### 2. Update API Calls
Replace manual async handling with hooks:

```jsx
// Before
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);

useEffect(() => {
  setLoading(true);
  api.get('/endpoint')
    .then(res => setData(res.data))
    .catch(err => setError(err))
    .finally(() => setLoading(false));
}, []);

// After
const { data, loading, error } = useApiCall(
  () => api.get('/endpoint'),
  { immediate: true }
);
```

### 3. Update Forms
Use form submission hook:

```jsx
// Before
const [submitting, setSubmitting] = useState(false);
const handleSubmit = async (e) => {
  e.preventDefault();
  setSubmitting(true);
  try {
    await api.post('/endpoint', data);
  } catch (error) {
    console.error(error);
  } finally {
    setSubmitting(false);
  }
};

// After
const { handleSubmit, isSubmitting } = useFormSubmit(
  (data) => api.post('/endpoint', data),
  { successMessage: 'Saved successfully' }
);
```

## Testing

### 1. Test Loading States
```jsx
it('shows loading state', () => {
  const { getByTestId } = render(
    <AsyncData loading={true} data={null} error={null}>
      {(data) => <div>Content</div>}
    </AsyncData>
  );
  
  expect(getByTestId('loading-spinner')).toBeInTheDocument();
});
```

### 2. Test Error States
```jsx
it('shows error state with retry', () => {
  const mockRetry = jest.fn();
  const error = new Error('Test error');
  
  const { getByText } = render(
    <ErrorState error={error} onRetry={mockRetry} />
  );
  
  expect(getByText('Test error')).toBeInTheDocument();
  fireEvent.click(getByText('Try Again'));
  expect(mockRetry).toHaveBeenCalled();
});
```

## Conclusion

This implementation provides a robust foundation for handling loading states and errors throughout the application. The modular approach allows for easy customization while maintaining consistency across the app.