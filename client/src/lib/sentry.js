// TODO: i18n - processed
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
/**
 * Initialize Sentry for error tracking and performance monitoring
 */import { useTranslation } from "react-i18next";
export function initSentry() {
  const environment = import.meta.env.MODE;
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn) {
    return;
  }
  Sentry.init({
    dsn,
    environment,
    integrations: [
    new BrowserTracing({
      // Set tracing origins to your frontend and backend
      tracingOrigins: [
      'localhost',
      /^https:\/\/.*\.bdc\.com/,
      /^http:\/\/localhost:\d+/],

      // Performance Monitoring
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      )
    })],

    // Performance Monitoring
    tracesSampleRate: environment === 'production' ? 0.1 : 1.0,
    // Session Replay
    replaysSessionSampleRate: environment === 'production' ? 0.1 : 0,
    replaysOnErrorSampleRate: 1.0,
    // Release tracking
    release: import.meta.env.VITE_APP_VERSION || '1.0.0',
    // User context
    beforeSend(event, hint) {
      // Don't send events in development unless explicitly enabled
      if (environment === 'development' && !import.meta.env.VITE_SENTRY_ENABLED) {
        return null;
      }
      // Filter out some common non-critical errors
      if (event.exception) {
        const error = hint.originalException;
        // Filter out network errors that are expected
        if (error?.message?.includes('Network request failed') &&
        error?.message?.includes('/api/health')) {
          return null;
        }
        // Filter out canceled requests
        if (error?.name === 'AbortError') {
          return null;
        }
      }
      return event;
    },
    // Add user context
    initialScope: {
      tags: {
        component: 'frontend'
      }
    }
  });
}
/**
 * Set user context for Sentry
 */
export function setSentryUser(user) {
  if (!user) {
    Sentry.setUser(null);
    return;
  }
  Sentry.setUser({
    id: user.id,
    email: user.email,
    username: user.username,
    role: user.role
  });
}
/**
 * Log a message to Sentry
 */
export function logToSentry(message, level = 'info', extra = {}) {
  Sentry.captureMessage(message, {
    level,
    extra,
    tags: {
      manual: true
    }
  });
}
/**
 * Capture an exception in Sentry
 */
export function captureException(error, context = {}) {
  console.error('Error captured:', error);
  Sentry.captureException(error, {
    contexts: {
      app: context
    }
  });
}
/**
 * Create a Sentry transaction for performance monitoring
 */
export function startTransaction(name, op = 'navigation') {
  return Sentry.startTransaction({ name, op });
}
/**
 * Add breadcrumb for better error context
 */
export function addBreadcrumb(message, category = 'action', data = {}) {
  Sentry.addBreadcrumb({
    message,
    category,
    level: 'info',
    data,
    timestamp: Date.now() / 1000
  });
}