import { renderHook, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useApi, useMutation } from '@/hooks/useApi';
import api from '@/lib/api';

// Mock api module
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

describe('useApi Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('useApi (GET requests)', () => {
    it('fetches data successfully', async () => {
      const mockData = { id: 1, name: 'Test Item' };
      api.get.mockResolvedValueOnce({ data: mockData });

      const { result } = renderHook(() => useApi('/api/test'));

      // Initial state
      expect(result.current.loading).toBe(true);
      expect(result.current.data).toBe(null);
      expect(result.current.error).toBe(null);

      // Wait for fetch to complete
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.data).toEqual(mockData);
        expect(result.current.error).toBe(null);
      });

      expect(api.get).toHaveBeenCalledWith('/api/test', expect.objectContaining({
        signal: expect.any(AbortSignal)
      }));
    });

    it('handles fetch errors', async () => {
      const errorMessage = 'Network error';
      api.get.mockRejectedValueOnce({
        response: { data: { message: errorMessage } }
      });

      const { result } = renderHook(() => useApi('/api/test'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.data).toBe(null);
        expect(result.current.error).toBe(errorMessage);
      });
    });

    it('does not fetch immediately when immediate is false', () => {
      const mockData = { id: 1, name: 'Test Item' };
      api.get.mockResolvedValueOnce({ data: mockData });

      const { result } = renderHook(() => 
        useApi('/api/test', { immediate: false })
      );

      expect(result.current.loading).toBe(false);
      expect(api.get).not.toHaveBeenCalled();
    });

    it('refetches data when refetch is called', async () => {
      const mockData1 = { id: 1, name: 'Test Item 1' };
      const mockData2 = { id: 2, name: 'Test Item 2' };
      
      api.get
        .mockResolvedValueOnce({ data: mockData1 })
        .mockResolvedValueOnce({ data: mockData2 });

      const { result } = renderHook(() => useApi('/api/test'));

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.data).toEqual(mockData1);
      });

      // Refetch
      act(() => {
        result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData2);
      });

      expect(api.get).toHaveBeenCalledTimes(2);
    });

    it('calls success callback when provided', async () => {
      const mockData = { id: 1, name: 'Test Item' };
      const onSuccess = vi.fn();
      
      api.get.mockResolvedValueOnce({ data: mockData });

      renderHook(() => useApi('/api/test', { onSuccess }));

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(mockData);
      });
    });

    it('calls error callback when provided', async () => {
      const error = new Error('Network error');
      const onError = vi.fn();
      
      api.get.mockRejectedValueOnce(error);

      renderHook(() => useApi('/api/test', { onError }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(error);
      });
    });

    it('cancels previous request when new request is made', async () => {
      const mockData1 = { id: 1, name: 'Test Item 1' };
      const mockData2 = { id: 2, name: 'Test Item 2' };
      
      let resolveFirst;
      const firstPromise = new Promise(resolve => {
        resolveFirst = resolve;
      });
      
      api.get
        .mockReturnValueOnce(firstPromise)
        .mockResolvedValueOnce({ data: mockData2 });

      const { result } = renderHook(() => useApi('/api/test'));

      // Start first request
      expect(result.current.loading).toBe(true);

      // Trigger refetch before first completes
      act(() => {
        result.current.refetch();
      });

      // Complete first request
      act(() => {
        resolveFirst({ data: mockData1 });
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData2);
      });
    });

    it('refetches when dependencies change', async () => {
      const mockData1 = { id: 1, name: 'Test Item 1' };
      const mockData2 = { id: 2, name: 'Test Item 2' };
      
      api.get
        .mockResolvedValueOnce({ data: mockData1 })
        .mockResolvedValueOnce({ data: mockData2 });

      const { result, rerender } = renderHook(
        ({ dep }) => useApi('/api/test', { dependencies: [dep] }),
        { initialProps: { dep: 1 } }
      );

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData1);
      });

      // Change dependency
      rerender({ dep: 2 });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData2);
      });

      expect(api.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('useMutation', () => {
    it('performs mutation successfully', async () => {
      const mockData = { id: 1, name: 'Created Item' };
      const mutationFn = vi.fn().mockResolvedValueOnce({ data: mockData });

      const { result } = renderHook(() => useMutation(mutationFn));

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBe(null);
      expect(result.current.error).toBe(null);

      // Perform mutation
      act(() => {
        result.current.mutate({ name: 'New Item' });
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.data).toEqual(mockData);
        expect(result.current.error).toBe(null);
      });

      expect(mutationFn).toHaveBeenCalledWith({ name: 'New Item' });
    });

    it('handles mutation errors', async () => {
      const errorMessage = 'Mutation failed';
      const mutationFn = vi.fn().mockRejectedValueOnce({
        response: { data: { message: errorMessage } }
      });

      const { result } = renderHook(() => useMutation(mutationFn));

      // Catch the thrown error
      await expect(async () => {
        await act(async () => {
          await result.current.mutate({ name: 'New Item' });
        });
      }).rejects.toThrow();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.data).toBe(null);
        expect(result.current.error).toBe(errorMessage);
      });
    });

    it('calls success callback', async () => {
      const mockData = { id: 1, name: 'Created Item' };
      const mutationFn = vi.fn().mockResolvedValueOnce({ data: mockData });
      const onSuccess = vi.fn();

      const { result } = renderHook(() => 
        useMutation(mutationFn, { onSuccess })
      );

      act(() => {
        result.current.mutate({ name: 'New Item' });
      });

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(mockData);
      });
    });

    it('calls error callback', async () => {
      const error = new Error('Mutation failed');
      const mutationFn = vi.fn().mockRejectedValueOnce(error);
      const onError = vi.fn();

      const { result } = renderHook(() => 
        useMutation(mutationFn, { onError })
      );

      // Catch the thrown error
      await expect(async () => {
        await act(async () => {
          await result.current.mutate({ name: 'New Item' });
        });
      }).rejects.toThrow('Mutation failed');

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(error);
      });
    });

    it('resets state on reset', async () => {
      const mockData = { id: 1, name: 'Created Item' };
      const mutationFn = vi.fn().mockResolvedValueOnce({ data: mockData });

      const { result } = renderHook(() => useMutation(mutationFn));

      // Perform mutation
      act(() => {
        result.current.mutate({ name: 'New Item' });
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });

      // Reset
      act(() => {
        result.current.reset();
      });

      expect(result.current.data).toBe(null);
      expect(result.current.error).toBe(null);
      expect(result.current.loading).toBe(false);
    });

    it('handles AbortError gracefully', async () => {
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';
      
      const mutationFn = vi.fn().mockRejectedValueOnce(abortError);

      const { result } = renderHook(() => useMutation(mutationFn));

      act(() => {
        result.current.mutate({ name: 'New Item' });
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.error).toBe(null); // AbortError should not set error
      });
    });
  });
});