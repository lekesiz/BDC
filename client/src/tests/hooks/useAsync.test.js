import { renderHook, act, waitFor } from '@testing-library/react';
import useAsync from '../../hooks/useAsync';
import { describe, it, expect, vi, beforeEach } from 'vitest';
describe('useAsync', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });
  it('should initialize with loading=false and no data or error', () => {
    const { result } = renderHook(() => useAsync());
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });
  it('should set loading=true when execute is called', async () => {
    const mockAsyncFn = vi.fn(() => new Promise(resolve => setTimeout(() => resolve('data'), 100)));
    const { result } = renderHook(() => useAsync(mockAsyncFn));
    act(() => {
      result.current.execute();
    });
    expect(result.current.loading).toBe(true);
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
  it('should set data when async function resolves', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockAsyncFn = vi.fn(() => Promise.resolve(mockData));
    const { result } = renderHook(() => useAsync(mockAsyncFn));
    act(() => {
      result.current.execute();
    });
    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });
  it('should set error when async function rejects', async () => {
    const mockError = new Error('Test error');
    const mockAsyncFn = vi.fn(() => Promise.reject(mockError));
    const { result } = renderHook(() => useAsync(mockAsyncFn));
    let executionError;
    act(() => {
      // We need to catch the error here to prevent unhandled promise rejection
      result.current.execute().catch(err => {
        executionError = err;
      });
    });
    await waitFor(() => {
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeNull();
      expect(executionError).toEqual(mockError);
    });
  });
  it('should pass arguments to the async function', async () => {
    const mockAsyncFn = vi.fn((a, b) => Promise.resolve(a + b));
    const { result } = renderHook(() => useAsync(mockAsyncFn));
    act(() => {
      result.current.execute(2, 3);
    });
    await waitFor(() => {
      expect(mockAsyncFn).toHaveBeenCalledWith(2, 3);
      expect(result.current.data).toBe(5);
    });
  });
  it('should reset state when reset is called', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockAsyncFn = vi.fn(() => Promise.resolve(mockData));
    const { result } = renderHook(() => useAsync(mockAsyncFn));
    // First load some data
    act(() => {
      result.current.execute();
    });
    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });
    // Then reset
    act(() => {
      result.current.reset();
    });
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });
  it('should auto-execute if executeOnMount is true', async () => {
    const mockAsyncFn = vi.fn(() => Promise.resolve('data'));
    let { result } = renderHook(() => useAsync(mockAsyncFn, [], true));
    expect(mockAsyncFn).toHaveBeenCalledTimes(1);
    await waitFor(() => {
      expect(result.current.data).toBe('data');
    });
  });
  it('should re-execute when dependencies change', async () => {
    const mockAsyncFn = vi.fn(() => Promise.resolve('data'));
    const { rerender, result } = renderHook(
      ({ deps }) => useAsync(mockAsyncFn, deps, true),
      { initialProps: { deps: [1] } }
    );
    expect(mockAsyncFn).toHaveBeenCalledTimes(1);
    await waitFor(() => {
      expect(result.current.data).toBe('data');
    });
    // Change dependencies
    rerender({ deps: [2] });
    expect(mockAsyncFn).toHaveBeenCalledTimes(2);
    await waitFor(() => {
      expect(result.current.data).toBe('data');
    });
  });
});