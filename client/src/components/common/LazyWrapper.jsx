// TODO: i18n - processed
import { Suspense } from 'react';
import ErrorBoundary from './ErrorBoundary';
import LoadingSpinner from '../ui/LoadingSpinner';
/**
 * Wrapper component for lazy-loaded components
 * Provides error boundary and loading state
 */import { useTranslation } from "react-i18next";
const LazyWrapper = ({ children, fallback = <LoadingSpinner /> }) => {const { t } = useTranslation();
  return (
    <ErrorBoundary>
      <Suspense fallback={fallback}>
        {children}
      </Suspense>
    </ErrorBoundary>);

};
export default LazyWrapper;