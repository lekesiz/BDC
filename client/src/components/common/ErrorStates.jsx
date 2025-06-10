// TODO: i18n - processed
import React from 'react';
import {
  AlertTriangle,
  RefreshCw,
  WifiOff,
  Lock,
  FileX,
  ServerCrash,
  Home,
  ArrowLeft } from
'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
/**
 * Different types of error states for various use cases
 */
// Network error state
import { useTranslation } from "react-i18next";export const NetworkError = ({
  onRetry,
  message = "Unable to connect to the server"
}) =>
<div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="bg-yellow-50 rounded-full p-3 mb-4">
      <WifiOff className="h-8 w-8 text-yellow-600" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t("components.connection_error")}</h3>
    <p className="text-sm text-gray-600 text-center max-w-sm mb-6">{message}</p>
    {onRetry &&
  <Button onClick={onRetry} variant="outline" size="sm">
        <RefreshCw className="h-4 w-4 mr-2" />{t("components.try_again")}

  </Button>
  }
  </div>;

// Permission error state
export const PermissionError = ({
  message = "You don't have permission to view this content"
}) => {const { t } = useTranslation();
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="bg-red-50 rounded-full p-3 mb-4">
        <Lock className="h-8 w-8 text-red-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{t("components.access_denied")}</h3>
      <p className="text-sm text-gray-600 text-center max-w-sm mb-6">{message}</p>
      <div className="flex gap-3">
        <Button onClick={() => navigate(-1)} variant="outline" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />{t("components.go_back")}

        </Button>
        <Button onClick={() => navigate('/')} size="sm">
          <Home className="h-4 w-4 mr-2" />{t("components.home")}

        </Button>
      </div>
    </div>);

};
// Not found error state
export const NotFoundError = ({
  title = "Page Not Found",
  message = "The page you're looking for doesn't exist or has been moved"
}) => {const { t } = useTranslation();
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="bg-gray-100 rounded-full p-3 mb-4">
        <FileX className="h-8 w-8 text-gray-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 text-center max-w-sm mb-6">{message}</p>
      <div className="flex gap-3">
        <Button onClick={() => navigate(-1)} variant="outline" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />{t("components.go_back")}

        </Button>
        <Button onClick={() => navigate('/')} size="sm">
          <Home className="h-4 w-4 mr-2" />{t("components.home")}

        </Button>
      </div>
    </div>);

};
// Server error state
export const ServerError = ({
  onRetry,
  message = "Something went wrong on our end. Please try again later"
}) =>
<div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="bg-red-50 rounded-full p-3 mb-4">
      <ServerCrash className="h-8 w-8 text-red-600" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t("components.server_error")}</h3>
    <p className="text-sm text-gray-600 text-center max-w-sm mb-6">{message}</p>
    {onRetry &&
  <Button onClick={onRetry} variant="outline" size="sm">
        <RefreshCw className="h-4 w-4 mr-2" />{t("components.try_again")}

  </Button>
  }
  </div>;

// Generic error state with customization
export const ErrorState = ({
  error,
  onRetry,
  title = "Error",
  icon: Icon = AlertTriangle,
  showDetails = process.env.NODE_ENV === 'development',
  className = "",
  children
}) => {const { t } = useTranslation();
  const navigate = useNavigate();
  // Determine error type and appropriate display
  const is404 = error?.response?.status === 404;
  const is403 = error?.response?.status === 403;
  const is401 = error?.response?.status === 401;
  const isNetwork = error?.code === 'ERR_NETWORK' || !navigator.onLine;
  const isServer = error?.response?.status >= 500;
  if (is404) {
    return <NotFoundError />;
  }
  if (is403 || is401) {
    return <PermissionError />;
  }
  if (isNetwork) {
    return <NetworkError onRetry={onRetry} />;
  }
  if (isServer) {
    return <ServerError onRetry={onRetry} />;
  }
  const errorMessage = error?.response?.data?.message || error?.message || "An unexpected error occurred";
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      <div className="bg-red-50 rounded-full p-3 mb-4">
        <Icon className="h-8 w-8 text-red-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 text-center max-w-sm mb-6">{errorMessage}</p>
      {showDetails && error &&
      <details className="mb-6 w-full max-w-md">
          <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">{t("components.error_details")}

        </summary>
          <div className="mt-2 p-3 bg-gray-50 rounded text-xs text-gray-700 font-mono overflow-auto">
            <pre className="whitespace-pre-wrap">
              {JSON.stringify(error, null, 2)}
            </pre>
          </div>
        </details>
      }
      {children}
      <div className="flex gap-3">
        {onRetry &&
        <Button onClick={onRetry} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />{t("components.try_again")}

        </Button>
        }
        <Button onClick={() => navigate(-1)} variant="outline" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />{t("components.go_back")}

        </Button>
      </div>
    </div>);

};
// Inline error message component
export const InlineError = ({
  error,
  className = "",
  showIcon = true
}) => {const { t } = useTranslation();
  const message = error?.response?.data?.message || error?.message || "An error occurred";
  return (
    <div className={`bg-red-50 border-l-4 border-red-400 p-4 ${className}`}>
      <div className="flex items-start">
        {showIcon &&
        <div className="flex-shrink-0">
            <AlertTriangle className="h-5 w-5 text-red-400" />
          </div>
        }
        <div className={showIcon ? "ml-3" : ""}>
          <p className="text-sm text-red-700">{message}</p>
        </div>
      </div>
    </div>);

};
// Form field error component
export const FieldError = ({ error, className = "" }) => {const { t } = useTranslation();
  if (!error) return null;
  return (
    <p className={`mt-1 text-sm text-red-600 ${className}`}>
      {error}
    </p>);

};
// Error list component for multiple errors
export const ErrorList = ({ errors, title = "Please fix the following errors:", className = "" }) => {const { t } = useTranslation();
  if (!errors || errors.length === 0) return null;
  return (
    <div className={`bg-red-50 border-l-4 border-red-400 p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <div className="mt-2 text-sm text-red-700">
            <ul className="list-disc pl-5 space-y-1">
              {errors.map((error, index) =>
              <li key={index}>{error}</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>);

};
export default {
  NetworkError,
  PermissionError,
  NotFoundError,
  ServerError,
  ErrorState,
  InlineError,
  FieldError,
  ErrorList
};