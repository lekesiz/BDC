// TODO: i18n - processed
// Accessibility Hook
import { useEffect, useRef, useCallback } from 'react';
import { a11yUtils } from '../accessibility/a11yUtils';
import { useDesignSystem } from '../DesignSystemProvider';import { useTranslation } from "react-i18next";

export const useAccessibility = () => {
  const { config } = useDesignSystem();

  return {
    announce: useCallback((message, priority = 'polite') => {
      a11yUtils.aria.announce(message, priority);
    }, []),

    trapFocus: useCallback((containerRef) => {
      if (!containerRef.current) return;
      return a11yUtils.focusManagement.trapFocus(containerRef.current);
    }, []),

    restoreFocus: useCallback((elementRef) => {
      if (!elementRef.current) return;
      a11yUtils.focusManagement.restoreFocus(elementRef.current);
    }, []),

    setAriaAttributes: useCallback((elementRef, attributes) => {
      if (!elementRef.current) return;
      a11yUtils.aria.setAttributes(elementRef.current, attributes);
    }, []),

    generateId: useCallback((prefix) => {
      return a11yUtils.generateId(prefix);
    }, []),

    prefersReducedMotion: config.reducedMotion,
    prefersHighContrast: config.highContrast,
    isRTL: config.rtl
  };
};

// Focus management hook
export const useFocusTrap = (isActive = true) => {
  const containerRef = useRef(null);
  const previousActiveElement = useRef(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    // Store current active element
    previousActiveElement.current = document.activeElement;

    // Trap focus
    const cleanup = a11yUtils.focusManagement.trapFocus(containerRef.current);

    // Focus first focusable element
    const focusableElements = a11yUtils.focusManagement.getFocusableElements(containerRef.current);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    return () => {
      cleanup?.();
      // Restore focus
      if (previousActiveElement.current) {
        a11yUtils.focusManagement.restoreFocus(previousActiveElement.current);
      }
    };
  }, [isActive]);

  return containerRef;
};

// Keyboard navigation hook
export const useKeyboardNavigation = (options = {}) => {
  const {
    orientation = 'vertical',
    loop = true,
    onNavigate,
    onSelect,
    onEscape
  } = options;

  const itemsRef = useRef([]);
  const containerRef = useRef(null);

  const handleKeyDown = useCallback((event) => {
    const items = itemsRef.current.filter(Boolean);

    if (items.length === 0) return;

    switch (event.key) {
      case 'ArrowUp':
      case 'ArrowDown':
      case 'ArrowLeft':
      case 'ArrowRight':
      case 'Home':
      case 'End':
        event.preventDefault();
        a11yUtils.keyboard.handleArrowNavigation(event, items, {
          orientation,
          loop
        });
        onNavigate?.(event);
        break;

      case 'Enter':
      case ' ':
        event.preventDefault();
        onSelect?.(event);
        break;

      case 'Escape':
        event.preventDefault();
        onEscape?.(event);
        break;
    }
  }, [orientation, loop, onNavigate, onSelect, onEscape]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('keydown', handleKeyDown);
    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const registerItem = useCallback((element, index) => {
    itemsRef.current[index] = element;
  }, []);

  return {
    containerRef,
    registerItem,
    handleKeyDown
  };
};

// Live region hook for screen reader announcements
export const useLiveRegion = (ariaLive = 'polite') => {
  const regionRef = useRef(null);

  const announce = useCallback((message) => {
    if (!regionRef.current) return;

    // Clear and set message for screen readers
    regionRef.current.textContent = '';
    setTimeout(() => {
      if (regionRef.current) {
        regionRef.current.textContent = message;
      }
    }, 100);
  }, []);

  return {
    regionRef,
    announce,
    regionProps: {
      role: 'status',
      'aria-live': ariaLive,
      'aria-atomic': 'true',
      className: 'sr-only'
    }
  };
};