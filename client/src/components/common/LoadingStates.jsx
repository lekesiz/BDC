// TODO: i18n - processed
import React from 'react';
import { Loader2 } from 'lucide-react';
/**
 * Different types of loading states for various use cases
 */
// Full page loading state
import { useTranslation } from "react-i18next";export const FullPageLoader = ({ message = "Loading..." }) =>
<div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
      <p className="mt-4 text-lg text-gray-600">{message}</p>
    </div>
  </div>;

// Card/Section loading state
export const CardLoader = ({ message = "Loading content..." }) =>
<div className="flex items-center justify-center py-12">
    <div className="text-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
      <p className="mt-3 text-sm text-gray-600">{message}</p>
    </div>
  </div>;

// Inline loading state (for buttons, small sections)
export const InlineLoader = ({ size = "sm", className = "" }) => {const { t } = useTranslation();
  const sizeClasses = {
    xs: "h-3 w-3",
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
    xl: "h-8 w-8"
  };
  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />);

};
// Button loading state
export const ButtonLoader = ({ text = "Loading...", size = "sm" }) =>
<div className="flex items-center gap-2">
    <InlineLoader size={size} />
    <span>{text}</span>
  </div>;

// Skeleton loaders for different content types
export const SkeletonTable = ({ rows = 5, columns = 4 }) =>
<div className="animate-pulse">
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {Array.from({ length: columns }).map((_, i) =>
          <th key={i} className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded" />
              </th>
          )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {Array.from({ length: rows }).map((_, rowIndex) =>
        <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) =>
          <td key={colIndex} className="px-6 py-4">
                  <div className="h-4 bg-gray-200 rounded" />
                </td>
          )}
            </tr>
        )}
        </tbody>
      </table>
    </div>
  </div>;

export const SkeletonCard = ({ height = "h-48" }) =>
<div className="animate-pulse">
    <div className={`bg-gray-200 rounded-lg ${height}`} />
  </div>;

export const SkeletonList = ({ items = 3 }) =>
<div className="animate-pulse space-y-4">
    {Array.from({ length: items }).map((_, i) =>
  <div key={i} className="flex items-center space-x-4">
        <div className="h-12 w-12 bg-gray-200 rounded-full" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
  )}
  </div>;

export const SkeletonForm = ({ fields = 4 }) =>
<div className="animate-pulse space-y-6">
    {Array.from({ length: fields }).map((_, i) =>
  <div key={i}>
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
        <div className="h-10 bg-gray-200 rounded" />
      </div>
  )}
    <div className="flex gap-4">
      <div className="h-10 bg-gray-200 rounded w-24" />
      <div className="h-10 bg-gray-200 rounded w-24" />
    </div>
  </div>;

// Loading container with customizable content
export const LoadingContainer = ({
  loading,
  error,
  children,
  loader = <CardLoader />,
  errorComponent = null,
  className = ""
}) => {const { t } = useTranslation();
  if (loading) {
    return <div className={className}>{loader}</div>;
  }
  if (error) {
    if (errorComponent) {
      return <div className={className}>{errorComponent}</div>;
    }
    return (
      <div className={`text-center py-12 ${className}`}>
        <p className="text-red-600">Error: {error.message || "Something went wrong"}</p>
      </div>);

  }
  return <div className={className}>{children}</div>;
};
// Data fetching state component
export const DataState = ({
  loading,
  error,
  data,
  loadingComponent = <CardLoader />,
  errorComponent = null,
  emptyComponent = null,
  children
}) => {
  const { t } = useTranslation();
  if (loading) return loadingComponent;
  if (error) {
    return errorComponent ||
    <div className="text-center py-12">
        <p className="text-red-600">Error: {error.message || "Failed to load data"}</p>
      </div>;

  }
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return emptyComponent || (
      <p className="text-gray-500 text-center py-8">
        {t("components.loading_states.no_data_available")}
      </p>
    );
  }
  return children;
};
export default {
  FullPageLoader,
  CardLoader,
  InlineLoader,
  ButtonLoader,
  SkeletonTable,
  SkeletonCard,
  SkeletonList,
  SkeletonForm,
  LoadingContainer,
  DataState
};