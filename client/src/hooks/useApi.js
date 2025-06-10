// TODO: i18n - processed
import { useState, useEffect, useCallback, useRef } from 'react';
import api from '@/lib/api';

/**
 * Custom hook for API data fetching with loading, error, and cancellation
 * @param {string} url - API endpoint URL
 * @param {Object} options - Additional options
 * @param {boolean} options.immediate - Whether to fetch immediately on mount
 * @param {Array} options.dependencies - Dependencies to trigger refetch
 * @param {Function} options.onSuccess - Success callback
 * @param {Function} options.onError - Error callback
 * @param {Object} options.config - Axios config options
 */import { useTranslation } from "react-i18next";
export const useApi = (url, options = {}) => {
  const {
    immediate = true,
    dependencies = [],
    onSuccess,
    onError,
    config = {}
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      const response = await api.get(url, {
        ...config,
        signal: abortControllerRef.current.signal
      });

      setData(response.data);
      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.response?.data?.message || err.message);
        if (onError) {
          onError(err);
        }
      }
    } finally {
      setLoading(false);
    }
  }, [url, config, onSuccess, onError]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    return () => {
      // Cleanup: cancel request on unmount
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [immediate, ...dependencies]);

  return { data, loading, error, refetch };
};

/**
 * Custom hook for API mutations (POST, PUT, DELETE)
 * @param {Function} mutationFn - Function that performs the mutation
 * @param {Object} options - Additional options
 */
export const useMutation = (mutationFn, options = {}) => {
  const { onSuccess, onError } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const mutate = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);

      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      const result = await mutationFn(...args, {
        signal: abortControllerRef.current.signal
      });

      setData(result.data || result);
      if (onSuccess) {
        onSuccess(result.data || result);
      }

      return result;
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.response?.data?.message || err.message);
        if (onError) {
          onError(err);
        }
        throw err;
      }
    } finally {
      setLoading(false);
    }
  }, [mutationFn, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    return () => {
      // Cleanup: cancel request on unmount
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { mutate, data, loading, error, reset };
};

/**
 * Custom hook for paginated API requests
 * @param {string} baseUrl - Base API endpoint URL
 * @param {Object} options - Pagination options
 */
export const usePaginatedApi = (baseUrl, options = {}) => {
  const {
    pageSize = 10,
    onSuccess,
    onError,
    config = {}
  } = options;

  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const abortControllerRef = useRef(null);

  const fetchPage = useCallback(async (pageNumber) => {
    try {
      setLoading(true);
      setError(null);

      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      const response = await api.get(baseUrl, {
        ...config,
        params: {
          page: pageNumber,
          per_page: pageSize,
          ...config.params
        },
        signal: abortControllerRef.current.signal
      });

      const { items = [], total_pages = 0, total_items = 0 } = response.data;

      setData(items);
      setTotalPages(total_pages);
      setTotalItems(total_items);
      setHasMore(pageNumber < total_pages);

      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.response?.data?.message || err.message);
        if (onError) {
          onError(err);
        }
      }
    } finally {
      setLoading(false);
    }
  }, [baseUrl, pageSize, config, onSuccess, onError]);

  const goToPage = useCallback((pageNumber) => {
    setPage(pageNumber);
    fetchPage(pageNumber);
  }, [fetchPage]);

  const nextPage = useCallback(() => {
    if (hasMore) {
      goToPage(page + 1);
    }
  }, [page, hasMore, goToPage]);

  const previousPage = useCallback(() => {
    if (page > 1) {
      goToPage(page - 1);
    }
  }, [page, goToPage]);

  useEffect(() => {
    fetchPage(1);

    return () => {
      // Cleanup: cancel request on unmount
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    data,
    page,
    totalPages,
    totalItems,
    loading,
    error,
    hasMore,
    goToPage,
    nextPage,
    previousPage,
    refetch: () => fetchPage(page)
  };
};