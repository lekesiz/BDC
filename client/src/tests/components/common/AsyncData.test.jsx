import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '../../../test/test-utils';
// Mock the module with an absolute path
vi.mock('../../../hooks/useAsyncOperation', () => {
  // Create a mock function that we can control in tests
  const useAsyncOperationMock = vi.fn();
  return {
    useAsyncOperation: useAsyncOperationMock
  };
});
// Import the mocked module
import { useAsyncOperation } from '../../../hooks/useAsyncOperation';
// Import the component
import { AsyncData } from '../../../components/common/AsyncData.jsx';
describe('AsyncData', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
  });
  it('shows loading state while fetching data', () => {
    // Mock the hook to return loading state
    useAsyncOperation.mockReturnValue({
      loading: true,
      error: null,
      data: null,
      execute: vi.fn(),
      retry: vi.fn()
    });
    const mockFetch = vi.fn(() => new Promise(() => {})); // Never resolves
    render(
      <AsyncData
        fetchData={mockFetch}
        loadingComponent={<div>Loading...</div>}
        render={() => <div>Data loaded</div>}
      />
    );
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  it('renders data when fetch resolves', async () => {
    const mockData = { id: 1, name: 'Test Item' };
    const mockFetch = vi.fn(() => Promise.resolve(mockData));
    // First show loading state
    useAsyncOperation.mockReturnValueOnce({
      loading: true,
      error: null,
      data: null,
      execute: vi.fn(),
      retry: vi.fn()
    });
    const { rerender } = render(
      <AsyncData
        fetchData={mockFetch}
        loadingComponent={<div>Loading...</div>}
        render={(data) => <div>Data: {data.name}</div>}
      />
    );
    // Initially shows loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    // Then simulate data being loaded
    useAsyncOperation.mockReturnValue({
      loading: false,
      error: null,
      data: mockData,
      execute: vi.fn(),
      retry: vi.fn()
    });
    await act(async () => {
      rerender(
        <AsyncData
          fetchData={mockFetch}
          loadingComponent={<div>Loading...</div>}
          render={(data) => <div>Data: {data.name}</div>}
        />
      );
    });
    // Then shows the data
    expect(screen.getByText('Data: Test Item')).toBeInTheDocument();
  });
  it('shows error state when fetch rejects', async () => {
    const mockError = new Error('Failed to load data');
    const mockFetch = vi.fn(() => Promise.reject(mockError));
    // First show loading state
    useAsyncOperation.mockReturnValueOnce({
      loading: true,
      error: null,
      data: null,
      execute: vi.fn(),
      retry: vi.fn()
    });
    const { rerender } = render(
      <AsyncData
        fetchData={mockFetch}
        loadingComponent={<div>Loading...</div>}
        errorComponent={<div>Error occurred</div>}
        render={(data) => <div>Data loaded</div>}
      />
    );
    // Initially shows loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    // Then simulate error state
    useAsyncOperation.mockReturnValue({
      loading: false,
      error: mockError,
      data: null,
      execute: vi.fn(),
      retry: vi.fn()
    });
    await act(async () => {
      rerender(
        <AsyncData
          fetchData={mockFetch}
          loadingComponent={<div>Loading...</div>}
          errorComponent={<div>Error occurred</div>}
          render={(data) => <div>Data loaded</div>}
        />
      );
    });
    // Then shows the error state
    expect(screen.getByText('Error occurred')).toBeInTheDocument();
  });
  it('shows empty state when fetch returns empty data', async () => {
    const mockFetch = vi.fn(() => Promise.resolve(null));
    // First show loading state
    useAsyncOperation.mockReturnValueOnce({
      loading: true,
      error: null,
      data: null,
      execute: vi.fn(),
      retry: vi.fn()
    });
    const { rerender } = render(
      <AsyncData
        fetchData={mockFetch}
        loadingComponent={<div>Loading...</div>}
        emptyComponent={<div>No data available</div>}
        render={(data) => <div>Data loaded</div>}
      />
    );
    // Initially shows loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    // Then simulate empty data
    useAsyncOperation.mockReturnValue({
      loading: false,
      error: null,
      data: null, // Empty data
      execute: vi.fn(),
      retry: vi.fn()
    });
    await act(async () => {
      rerender(
        <AsyncData
          fetchData={mockFetch}
          loadingComponent={<div>Loading...</div>}
          emptyComponent={<div>No data available</div>}
          render={(data) => <div>Data loaded</div>}
        />
      );
    });
    // Then shows the empty state
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });
  it('refetches data when dependencies change', async () => {
    const mockData = { id: 1, name: 'Test Item' };
    const mockFetch = vi.fn(() => Promise.resolve(mockData));
    const mockExecute = vi.fn(() => Promise.resolve(mockData));
    // Set up the mock hook with a trackable execute function
    useAsyncOperation.mockReturnValue({
      loading: false,
      error: null,
      data: mockData,
      execute: mockExecute,
      retry: vi.fn()
    });
    const { rerender } = render(
      <AsyncData
        fetchData={mockFetch}
        dependencies={[1]}
        loadingComponent={<div>Loading...</div>}
        render={(data) => <div>Data: {data.name}</div>}
      />
    );
    // Initial render should show data and call execute
    expect(screen.getByText('Data: Test Item')).toBeInTheDocument();
    // Reset mock counts
    mockExecute.mockClear();
    // Change dependencies to trigger useEffect
    await act(async () => {
      rerender(
        <AsyncData
          fetchData={mockFetch}
          dependencies={[2]} // Changed dependency
          loadingComponent={<div>Loading...</div>}
          render={(data) => <div>Data: {data.name}</div>}
        />
      );
    });
    // The useEffect should be triggered because dependencies changed,
    // so execute should be called again
    expect(mockExecute).toHaveBeenCalled();
  });
});