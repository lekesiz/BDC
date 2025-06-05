import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import InputSanitizer from './InputSanitizer';
import XSSProtection from './XSSProtection';
import SecurityMonitor from './SecurityMonitor';
import CSPHelper from './CSPHelper';
const SecurityContext = createContext(null);
/**
 * Security Provider component that wraps the application with comprehensive security features
 */
const SecurityProvider = ({ children, config = {} }) => {
  const [securityState, setSecurityState] = useState({
    isInitialized: false,
    threats: [],
    securityLevel: 'medium',
    csrfToken: null,
    sessionValid: true,
    lastActivity: Date.now(),
  });
  const defaultConfig = {
    enableXSSProtection: true,
    enableCSRFProtection: true,
    enableInputSanitization: true,
    enableSecurityMonitoring: true,
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    maxIdleTime: 15 * 60 * 1000, // 15 minutes
    securityHeaders: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-Content-Type-Options': 'nosniff',
    },
    ...config,
  };
  // Initialize security components
  useEffect(() => {
    const initializeSecurity = async () => {
      try {
        // Initialize XSS Protection
        if (defaultConfig.enableXSSProtection) {
          XSSProtection.initialize();
        }
        // Initialize CSP Helper
        CSPHelper.initialize();
        // Initialize Security Monitor
        if (defaultConfig.enableSecurityMonitoring) {
          SecurityMonitor.initialize({
            onThreatDetected: handleThreatDetected,
            onSecurityViolation: handleSecurityViolation,
          });
        }
        // Setup session monitoring
        setupSessionMonitoring();
        // Setup CSRF protection
        if (defaultConfig.enableCSRFProtection) {
          await setupCSRFProtection();
        }
        setSecurityState(prev => ({
          ...prev,
          isInitialized: true,
        }));
      } catch (error) {
        console.error('Security initialization failed:', error);
        handleSecurityError(error);
      }
    };
    initializeSecurity();
  }, []);
  // CSRF Token management
  const setupCSRFProtection = async () => {
    try {
      const response = await fetch('/api/csrf-token', {
        method: 'GET',
        credentials: 'include',
        headers: defaultConfig.securityHeaders,
      });
      if (response.ok) {
        const data = await response.json();
        setSecurityState(prev => ({
          ...prev,
          csrfToken: data.token,
        }));
      }
    } catch (error) {
      console.error('CSRF token setup failed:', error);
    }
  };
  // Session monitoring
  const setupSessionMonitoring = () => {
    // Track user activity
    const activityEvents = ['mousedown', 'keypress', 'scroll', 'touchstart'];
    const updateActivity = () => {
      setSecurityState(prev => ({
        ...prev,
        lastActivity: Date.now(),
      }));
    };
    activityEvents.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true });
    });
    // Check session validity periodically
    const sessionCheck = setInterval(() => {
      const now = Date.now();
      const timeSinceActivity = now - securityState.lastActivity;
      if (timeSinceActivity > defaultConfig.maxIdleTime) {
        handleSessionTimeout();
      }
    }, 60000); // Check every minute
    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, updateActivity);
      });
      clearInterval(sessionCheck);
    };
  };
  // Security event handlers
  const handleThreatDetected = useCallback((threat) => {
    setSecurityState(prev => ({
      ...prev,
      threats: [...prev.threats, {
        ...threat,
        timestamp: Date.now(),
        id: Math.random().toString(36).substr(2, 9),
      }],
    }));
    // Log security threat
    console.warn('Security threat detected:', threat);
    // Send to security monitoring endpoint
    if (defaultConfig.enableSecurityMonitoring) {
      fetch('/api/security/threat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...defaultConfig.securityHeaders,
          ...(securityState.csrfToken && { 'X-CSRF-Token': securityState.csrfToken }),
        },
        credentials: 'include',
        body: JSON.stringify(threat),
      }).catch(error => {
        console.error('Failed to report security threat:', error);
      });
    }
  }, [securityState.csrfToken, defaultConfig]);
  const handleSecurityViolation = useCallback((violation) => {
    console.error('Security violation:', violation);
    // Increase security level based on violation severity
    if (violation.severity === 'high') {
      setSecurityState(prev => ({
        ...prev,
        securityLevel: 'high',
      }));
    }
  }, []);
  const handleSecurityError = useCallback((error) => {
    console.error('Security error:', error);
    setSecurityState(prev => ({
      ...prev,
      threats: [...prev.threats, {
        type: 'security_error',
        message: error.message,
        timestamp: Date.now(),
        severity: 'medium',
      }],
    }));
  }, []);
  const handleSessionTimeout = useCallback(() => {
    setSecurityState(prev => ({
      ...prev,
      sessionValid: false,
    }));
    // Redirect to login or show session expired modal
    if (typeof window !== 'undefined') {
      window.location.href = '/login?reason=session_expired';
    }
  }, []);
  // Security utility functions
  const sanitizeInput = useCallback((input, options = {}) => {
    if (!defaultConfig.enableInputSanitization) {
      return input;
    }
    return InputSanitizer.sanitize(input, options);
  }, [defaultConfig.enableInputSanitization]);
  const validateInput = useCallback((input, rules = []) => {
    return InputSanitizer.validate(input, rules);
  }, []);
  const checkXSS = useCallback((content) => {
    if (!defaultConfig.enableXSSProtection) {
      return { safe: true };
    }
    return XSSProtection.scan(content);
  }, [defaultConfig.enableXSSProtection]);
  const reportSecurityIncident = useCallback((incident) => {
    handleThreatDetected({
      type: 'user_reported',
      ...incident,
      severity: incident.severity || 'medium',
    });
  }, [handleThreatDetected]);
  const getSecureHeaders = useCallback(() => {
    const headers = { ...defaultConfig.securityHeaders };
    if (securityState.csrfToken) {
      headers['X-CSRF-Token'] = securityState.csrfToken;
    }
    return headers;
  }, [securityState.csrfToken, defaultConfig.securityHeaders]);
  const secureApiCall = useCallback(async (url, options = {}) => {
    const secureOptions = {
      ...options,
      credentials: 'include',
      headers: {
        ...getSecureHeaders(),
        ...options.headers,
      },
    };
    // Input validation for request body
    if (secureOptions.body && typeof secureOptions.body === 'string') {
      try {
        const bodyData = JSON.parse(secureOptions.body);
        const sanitizedData = {};
        for (const [key, value] of Object.entries(bodyData)) {
          if (typeof value === 'string') {
            sanitizedData[key] = sanitizeInput(value);
          } else {
            sanitizedData[key] = value;
          }
        }
        secureOptions.body = JSON.stringify(sanitizedData);
      } catch (error) {
        console.warn('Failed to sanitize request body:', error);
      }
    }
    try {
      const response = await fetch(url, secureOptions);
      // Check for security headers in response
      const securityHeaders = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Strict-Transport-Security',
      ];
      securityHeaders.forEach(header => {
        if (!response.headers.get(header)) {
          console.warn(`Missing security header: ${header}`);
        }
      });
      return response;
    } catch (error) {
      handleSecurityError(error);
      throw error;
    }
  }, [getSecureHeaders, sanitizeInput, handleSecurityError]);
  const contextValue = {
    // State
    ...securityState,
    config: defaultConfig,
    // Security utilities
    sanitizeInput,
    validateInput,
    checkXSS,
    secureApiCall,
    getSecureHeaders,
    // Event handlers
    reportSecurityIncident,
    // Security components
    InputSanitizer,
    XSSProtection,
    SecurityMonitor,
    CSPHelper,
  };
  // Render security warning if not initialized
  if (!securityState.isInitialized) {
    return (
      <div className="security-initializing">
        <div>Initializing security components...</div>
      </div>
    );
  }
  // Render session expired notice
  if (!securityState.sessionValid) {
    return (
      <div className="security-session-expired">
        <div>Session expired. Redirecting to login...</div>
      </div>
    );
  }
  return (
    <SecurityContext.Provider value={contextValue}>
      {children}
    </SecurityContext.Provider>
  );
};
export const useSecurityContext = () => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurityContext must be used within SecurityProvider');
  }
  return context;
};
export default SecurityProvider;