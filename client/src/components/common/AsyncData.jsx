import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ErrorState } from './ErrorStates';
import { CardSkeleton, TableSkeleton, ContentLoader } from './LoadingAnimations';
import { useAsyncOperation } from '@/hooks/useAsyncOperation';
/**
 * Comprehensive async data component with loading, error, and empty states
 */
export const AsyncData = ({
  // Data fetching
  fetchData,
  params = {},
  dependencies = [],
  // State components
  loadingComponent,
  errorComponent,
  emptyComponent,
  // Display options
  showRetry = true,
  skeletonType = 'card',
  skeletonProps = {},
  errorProps = {},
  emptyMessage = "No data available",
  // Animation
  animate = true,
  animationDuration = 0.3,
  // Render function
  children,
  render,
  // Callbacks
  onSuccess,
  onError,
  className = ""
}) => {
  const {
    loading,
    error,
    data,
    execute,
    retry
  } = useAsyncOperation({
    onSuccess,
    onError,
    showErrorToast: false
  });
  React.useEffect(() => {
    execute(() => fetchData(params));
  }, dependencies);
  // Loading state
  if (loading && !data) {
    if (loadingComponent) {
      return loadingComponent;
    }
    const SkeletonComponent = {
      card: CardSkeleton,
      table: TableSkeleton,
      content: ContentLoader
    }[skeletonType] || CardSkeleton;
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: animationDuration }}
        className={className}
      >
        <SkeletonComponent {...skeletonProps} />
      </motion.div>
    );
  }
  // Error state
  if (error && !data) {
    if (errorComponent) {
      return errorComponent;
    }
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: animationDuration }}
        className={className}
      >
        <ErrorState
          error={error}
          onRetry={showRetry ? retry : undefined}
          {...errorProps}
        />
      </motion.div>
    );
  }
  // Empty state
  if (!data || (Array.isArray(data) && data.length === 0)) {
    if (emptyComponent) {
      return emptyComponent;
    }
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: animationDuration }}
        className={`text-center py-12 ${className}`}
      >
        <p className="text-gray-500">{emptyMessage}</p>
      </motion.div>
    );
  }
  // Success state with data
  const content = render ? render(data) : children(data);
  if (!animate) {
    return <div className={className}>{content}</div>;
  }
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="content"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: animationDuration }}
        className={className}
      >
        {content}
      </motion.div>
    </AnimatePresence>
  );
};
/**
 * Paginated async data component
 */
export const AsyncPaginatedData = ({
  fetchData,
  initialPage = 1,
  pageSize = 10,
  // Components
  loadingComponent,
  errorComponent,
  emptyComponent,
  paginationComponent,
  // Options
  showPageSizeSelector = true,
  pageSizeOptions = [10, 25, 50, 100],
  // Render
  children,
  render,
  className = ""
}) => {
  const [page, setPage] = React.useState(initialPage);
  const [perPage, setPerPage] = React.useState(pageSize);
  const {
    loading,
    error,
    data,
    execute,
    retry
  } = useAsyncOperation();
  const fetchPageData = React.useCallback(() => {
    return execute(() => fetchData({ page, per_page: perPage }));
  }, [page, perPage, fetchData, execute]);
  React.useEffect(() => {
    fetchPageData();
  }, [fetchPageData]);
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };
  const handlePageSizeChange = (newSize) => {
    setPerPage(newSize);
    setPage(1); // Reset to first page when changing page size
  };
  if (loading && !data) {
    return loadingComponent || <TableSkeleton />;
  }
  if (error && !data) {
    return errorComponent || <ErrorState error={error} onRetry={retry} />;
  }
  if (!data || data.items?.length === 0) {
    return emptyComponent || (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }
  const content = render ? render(data.items) : children(data.items);
  const defaultPagination = (
    <div className="mt-6 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {showPageSizeSelector && (
          <>
            <span className="text-sm text-gray-700">Show</span>
            <select
              value={perPage}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="rounded border-gray-300 text-sm"
            >
              {pageSizeOptions.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
            <span className="text-sm text-gray-700">per page</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 1}
          className="px-3 py-1 text-sm border rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-sm text-gray-700">
          Page {page} of {data.total_pages}
        </span>
        <button
          onClick={() => handlePageChange(page + 1)}
          disabled={page === data.total_pages}
          className="px-3 py-1 text-sm border rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
  return (
    <div className={className}>
      {content}
      {paginationComponent || defaultPagination}
    </div>
  );
};
/**
 * Infinite scroll async data component
 */
export const AsyncInfiniteData = ({
  fetchData,
  pageSize = 20,
  threshold = 100,
  // Components
  loadingComponent,
  errorComponent,
  emptyComponent,
  loadMoreComponent,
  // Render
  children,
  render,
  className = ""
}) => {
  const [page, setPage] = React.useState(1);
  const [items, setItems] = React.useState([]);
  const [hasMore, setHasMore] = React.useState(true);
  const observerRef = React.useRef();
  const loadMoreRef = React.useRef();
  const {
    loading,
    error,
    execute
  } = useAsyncOperation();
  const loadMore = React.useCallback(async () => {
    if (loading || !hasMore) return;
    const result = await execute(() => fetchData({ page, per_page: pageSize }));
    if (result) {
      setItems(prev => [...prev, ...result.items]);
      setHasMore(result.has_next);
      setPage(prev => prev + 1);
    }
  }, [page, pageSize, loading, hasMore, fetchData, execute]);
  React.useEffect(() => {
    loadMore();
  }, []);
  React.useEffect(() => {
    if (loading) return;
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore) {
          loadMore();
        }
      },
      { threshold: 0.1, rootMargin: `${threshold}px` }
    );
    observerRef.current = observer;
    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loading, hasMore, loadMore, threshold]);
  if (loading && items.length === 0) {
    return loadingComponent || <CardSkeleton />;
  }
  if (error && items.length === 0) {
    return errorComponent || <ErrorState error={error} />;
  }
  if (items.length === 0) {
    return emptyComponent || (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }
  const content = render ? render(items) : children(items);
  return (
    <div className={className}>
      {content}
      {hasMore && (
        <div ref={loadMoreRef} className="py-4">
          {loading ? (
            loadMoreComponent || (
              <div className="text-center">
                <div className="inline-flex items-center gap-2 text-gray-500">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500" />
                  Loading more...
                </div>
              </div>
            )
          ) : (
            <div className="h-4" /> // Invisible trigger element
          )}
        </div>
      )}
      {!hasMore && items.length > 0 && (
        <div className="text-center py-4 text-gray-500 text-sm">
          No more items to load
        </div>
      )}
    </div>
  );
};