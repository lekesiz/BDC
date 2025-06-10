// TODO: i18n - processed
import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import { DataState } from './LoadingStates';
/**
 * Combined component that handles both error boundaries and loading states
 * Simplifies the pattern of wrapping components with both error and loading handling
 */import { useTranslation } from "react-i18next";
const AsyncBoundary = ({
  children,
  loading = false,
  error = null,
  data = null,
  // Error boundary props
  errorBoundaryProps = {},
  // Loading state props
  loadingComponent,
  errorComponent,
  emptyComponent,
  // Callbacks
  onError,
  onRetry,
  // Display options
  showErrorDetails = process.env.NODE_ENV === 'development',
  errorTitle = "Something went wrong",
  errorMessage = "An unexpected error occurred. Please try again.",
  ...props
}) => {const { t } = useTranslation();
  return (
    <ErrorBoundary
      onError={onError}
      showDetails={showErrorDetails}
      errorTitle={errorTitle}
      errorMessage={errorMessage}
      {...errorBoundaryProps}>

      <DataState
        loading={loading}
        error={error}
        data={data}
        loadingComponent={loadingComponent}
        errorComponent={errorComponent}
        emptyComponent={emptyComponent}>

        {children}
      </DataState>
    </ErrorBoundary>);

};
/**
 * Hook to manage async boundary state
 */
export const useAsyncBoundary = () => {
  const [state, setState] = React.useState({
    loading: false,
    error: null,
    data: null
  });
  const setLoading = (loading) => {
    setState((prev) => ({ ...prev, loading }));
  };
  const setError = (error) => {
    setState((prev) => ({ ...prev, error, loading: false }));
  };
  const setData = (data) => {
    setState((prev) => ({ ...prev, data, loading: false, error: null }));
  };
  const reset = () => {
    setState({ loading: false, error: null, data: null });
  };
  return {
    ...state,
    setLoading,
    setError,
    setData,
    reset
  };
};
/**
 * HOC to wrap any component with async boundary
 */
export const withAsyncBoundary = (Component, boundaryProps = {}) => {
  return (props) =>
  <AsyncBoundary {...boundaryProps}>
      <Component {...props} />
    </AsyncBoundary>;

};
export default AsyncBoundary;