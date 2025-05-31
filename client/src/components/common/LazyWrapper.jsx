import { Suspense } from 'react';
import ErrorBoundary from './ErrorBoundary';
import LoadingSpinner from '../ui/LoadingSpinner';

/**
 * Wrapper component for lazy-loaded components
 * Provides error boundary and loading state
 */
const LazyWrapper = ({ children, fallback = <LoadingSpinner /> }) => {
  return (
    <ErrorBoundary>
      <Suspense fallback={fallback}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
};

export default LazyWrapper;