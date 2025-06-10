// Error States Components
import React from 'react';
import { motion } from 'framer-motion';
import { animations } from '../animations/animations';
import './states.css';

// Error Icon Component
const ErrorIcon = ({ size = 48, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`ds-error-icon ${className}`}
  >
    <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="2" />
    <path
      d="M24 16V26"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <circle cx="24" cy="32" r="1.5" fill="currentColor" />
  </svg>
);

// Warning Icon Component
const WarningIcon = ({ size = 48, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`ds-warning-icon ${className}`}
  >
    <path
      d="M24 4L45 40H3L24 4Z"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path
      d="M24 18V28"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <circle cx="24" cy="34" r="1.5" fill="currentColor" />
  </svg>
);

// Generic Error State
export const ErrorState = ({
  type = 'error',
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  icon = true,
  actions,
  className = '',
  ...props
}) => {
  const icons = {
    error: ErrorIcon,
    warning: WarningIcon,
    404: () => (
      <div className="ds-error-state__404">404</div>
    ),
    500: () => (
      <div className="ds-error-state__500">500</div>
    )
  };

  const Icon = icons[type] || ErrorIcon;

  return (
    <motion.div
      className={`ds-error-state ds-error-state--${type} ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="alert"
      aria-live="polite"
      {...props}
    >
      {icon && (
        <motion.div
          className="ds-error-state__icon"
          animate={type === 'error' ? animations.attention.shake.animate : {}}
        >
          <Icon size={64} />
        </motion.div>
      )}
      
      <h3 className="ds-error-state__title">{title}</h3>
      
      {message && (
        <p className="ds-error-state__message">{message}</p>
      )}
      
      {actions && (
        <div className="ds-error-state__actions">
          {actions}
        </div>
      )}
    </motion.div>
  );
};

// 404 Error State
export const Error404 = ({
  title = 'Page not found',
  message = 'The page you are looking for might have been removed or is temporarily unavailable.',
  homeLink = '/',
  ...props
}) => {
  return (
    <ErrorState
      type="404"
      title={title}
      message={message}
      actions={
        <>
          <button
            className="ds-button ds-button--primary"
            onClick={() => window.location.href = homeLink}
          >
            Go to Homepage
          </button>
          <button
            className="ds-button ds-button--ghost"
            onClick={() => window.history.back()}
          >
            Go Back
          </button>
        </>
      }
      {...props}
    />
  );
};

// 500 Error State
export const Error500 = ({
  title = 'Server error',
  message = 'We are experiencing technical difficulties. Please try again later.',
  onRetry,
  ...props
}) => {
  return (
    <ErrorState
      type="500"
      title={title}
      message={message}
      actions={
        <>
          {onRetry && (
            <button
              className="ds-button ds-button--primary"
              onClick={onRetry}
            >
              Try Again
            </button>
          )}
          <button
            className="ds-button ds-button--ghost"
            onClick={() => window.location.reload()}
          >
            Refresh Page
          </button>
        </>
      }
      {...props}
    />
  );
};

// Network Error State
export const NetworkError = ({
  title = 'No internet connection',
  message = 'Please check your internet connection and try again.',
  onRetry,
  ...props
}) => {
  return (
    <motion.div
      className="ds-network-error"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="alert"
      {...props}
    >
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        className="ds-network-error__icon"
      >
        <path
          d="M32 8C18.745 8 8 18.745 8 32s10.745 24 24 24 24-10.745 24-24S45.255 8 32 8z"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M32 8c-8 0-14.5 16-14.5 24s6.5 24 14.5 24 14.5-16 14.5-24S40 8 32 8z"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M8 32h48"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M45 45L19 19"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      
      <h3 className="ds-network-error__title">{title}</h3>
      <p className="ds-network-error__message">{message}</p>
      
      {onRetry && (
        <button
          className="ds-button ds-button--primary"
          onClick={onRetry}
        >
          Try Again
        </button>
      )}
    </motion.div>
  );
};

// Permission Error State
export const PermissionError = ({
  title = 'Access denied',
  message = 'You do not have permission to view this content.',
  onRequestAccess,
  ...props
}) => {
  return (
    <motion.div
      className="ds-permission-error"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      role="alert"
      {...props}
    >
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        className="ds-permission-error__icon"
      >
        <rect
          x="16"
          y="24"
          width="32"
          height="32"
          rx="4"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M24 24V20a8 8 0 1 1 16 0v4"
          stroke="currentColor"
          strokeWidth="2"
        />
        <circle cx="32" cy="36" r="2" fill="currentColor" />
        <path
          d="M32 38v8"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
      
      <h3 className="ds-permission-error__title">{title}</h3>
      <p className="ds-permission-error__message">{message}</p>
      
      <div className="ds-permission-error__actions">
        {onRequestAccess && (
          <button
            className="ds-button ds-button--primary"
            onClick={onRequestAccess}
          >
            Request Access
          </button>
        )}
        <button
          className="ds-button ds-button--ghost"
          onClick={() => window.history.back()}
        >
          Go Back
        </button>
      </div>
    </motion.div>
  );
};

// Form Error Message
export const FormError = ({
  message,
  fieldId,
  className = '',
  ...props
}) => {
  return (
    <motion.div
      className={`ds-form-error ${className}`}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      role="alert"
      id={fieldId ? `${fieldId}-error` : undefined}
      aria-live="polite"
      {...props}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        className="ds-form-error__icon"
      >
        <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
        <path
          d="M8 5v4"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <circle cx="8" cy="11" r="0.5" fill="currentColor" />
      </svg>
      <span className="ds-form-error__message">{message}</span>
    </motion.div>
  );
};

// Inline Error
export const InlineError = ({
  message,
  variant = 'error',
  dismissible = false,
  onDismiss,
  className = '',
  ...props
}) => {
  return (
    <motion.div
      className={`ds-inline-error ds-inline-error--${variant} ${className}`}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 10 }}
      transition={{ duration: 0.2 }}
      role="alert"
      {...props}
    >
      <span className="ds-inline-error__message">{message}</span>
      {dismissible && (
        <button
          className="ds-inline-error__dismiss"
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </motion.div>
  );
};

// Export all error states
export const ErrorStates = {
  ErrorState,
  Error404,
  Error500,
  NetworkError,
  PermissionError,
  FormError,
  InlineError
};