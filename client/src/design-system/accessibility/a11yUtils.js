// TODO: i18n - processed
// Accessibility Utilities
import { a11yConfig } from './a11yConfig';import { useTranslation } from "react-i18next";

export const a11yUtils = {
  // Generate unique IDs for accessibility
  generateId: (prefix = 'a11y') => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },

  // Check color contrast ratio
  getContrastRatio: (color1, color2) => {
    const getLuminance = (color) => {
      const rgb = color.match(/\d+/g).map(Number);
      const [r, g, b] = rgb.map((val) => {
        val = val / 255;
        return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const l1 = getLuminance(color1);
    const l2 = getLuminance(color2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);

    return (lighter + 0.05) / (darker + 0.05);
  },

  // Check if contrast meets WCAG standards
  meetsContrastRequirements: (ratio, size = 'normal', level = 'AA') => {
    const requirement = a11yConfig.contrast[size][level];
    return ratio >= requirement;
  },

  // Focus management
  focusManagement: {
    // Trap focus within a container
    trapFocus: (container) => {
      const focusableElements = container.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
      );

      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];

      const handleTabKey = (e) => {
        if (e.key !== 'Tab') return;

        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
          }
        }
      };

      container.addEventListener('keydown', handleTabKey);

      return () => {
        container.removeEventListener('keydown', handleTabKey);
      };
    },

    // Restore focus to a previous element
    restoreFocus: (element) => {
      if (element && typeof element.focus === 'function') {
        element.focus();
      }
    },

    // Get all focusable elements
    getFocusableElements: (container = document) => {
      return container.querySelectorAll(
        'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
    }
  },

  // ARIA helpers
  aria: {
    // Set multiple ARIA attributes
    setAttributes: (element, attributes) => {
      Object.entries(attributes).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          element.setAttribute(key, value.toString());
        }
      });
    },

    // Toggle ARIA boolean attributes
    toggleBoolean: (element, attribute) => {
      const current = element.getAttribute(attribute) === 'true';
      element.setAttribute(attribute, (!current).toString());
    },

    // Announce to screen readers
    announce: (message, priority = 'polite') => {
      const announcement = document.createElement('div');
      announcement.setAttribute('role', 'status');
      announcement.setAttribute('aria-live', priority);
      announcement.style.position = 'absolute';
      announcement.style.left = '-10000px';
      announcement.style.width = '1px';
      announcement.style.height = '1px';
      announcement.style.overflow = 'hidden';

      document.body.appendChild(announcement);
      announcement.textContent = message;

      setTimeout(() => {
        document.body.removeChild(announcement);
      }, 1000);
    }
  },

  // Keyboard navigation helpers
  keyboard: {
    // Handle arrow key navigation
    handleArrowNavigation: (event, elements, options = {}) => {
      const { orientation = 'vertical', loop = true } = options;
      const currentIndex = elements.indexOf(document.activeElement);

      if (currentIndex === -1) return;

      let nextIndex;

      switch (event.key) {
        case 'ArrowUp':
          if (orientation === 'vertical') {
            nextIndex = loop ?
            (currentIndex - 1 + elements.length) % elements.length :
            Math.max(0, currentIndex - 1);
          }
          break;
        case 'ArrowDown':
          if (orientation === 'vertical') {
            nextIndex = loop ?
            (currentIndex + 1) % elements.length :
            Math.min(elements.length - 1, currentIndex + 1);
          }
          break;
        case 'ArrowLeft':
          if (orientation === 'horizontal') {
            nextIndex = loop ?
            (currentIndex - 1 + elements.length) % elements.length :
            Math.max(0, currentIndex - 1);
          }
          break;
        case 'ArrowRight':
          if (orientation === 'horizontal') {
            nextIndex = loop ?
            (currentIndex + 1) % elements.length :
            Math.min(elements.length - 1, currentIndex + 1);
          }
          break;
        case 'Home':
          nextIndex = 0;
          break;
        case 'End':
          nextIndex = elements.length - 1;
          break;
        default:
          return;
      }

      if (nextIndex !== undefined && nextIndex !== currentIndex) {
        event.preventDefault();
        elements[nextIndex].focus();
      }
    },

    // Check if key is printable character
    isPrintableKey: (key) => {
      return key.length === 1 && !key.match(/[\x00-\x1F\x7F]/);
    }
  },

  // Form accessibility
  form: {
    // Associate error messages with form fields
    associateError: (fieldId, errorId) => {
      const field = document.getElementById(fieldId);
      const error = document.getElementById(errorId);

      if (field && error) {
        field.setAttribute('aria-describedby', errorId);
        field.setAttribute('aria-invalid', 'true');
        error.setAttribute('role', 'alert');
      }
    },

    // Clear error associations
    clearError: (fieldId) => {
      const field = document.getElementById(fieldId);

      if (field) {
        field.removeAttribute('aria-describedby');
        field.setAttribute('aria-invalid', 'false');
      }
    },

    // Mark required fields
    markRequired: (field) => {
      field.setAttribute('aria-required', 'true');
      field.setAttribute('required', '');
    }
  },

  // Text alternatives
  textAlternatives: {
    // Generate descriptive text for icons
    getIconDescription: (iconName) => {
      const descriptions = {
        close: 'Close',
        menu: 'Menu',
        search: 'Search',
        filter: 'Filter',
        sort: 'Sort',
        edit: 'Edit',
        delete: 'Delete',
        save: 'Save',
        cancel: 'Cancel',
        info: 'Information',
        warning: 'Warning',
        error: 'Error',
        success: 'Success',
        loading: 'Loading',
        refresh: 'Refresh',
        settings: 'Settings',
        user: 'User profile',
        logout: 'Log out',
        home: 'Home',
        back: 'Go back',
        forward: 'Go forward'
      };

      return descriptions[iconName] || iconName;
    }
  },

  // Responsive design helpers
  responsive: {
    // Check if touch device
    isTouchDevice: () => {
      return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },

    // Check if reduced motion is preferred
    prefersReducedMotion: () => {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    // Check if high contrast mode
    prefersHighContrast: () => {
      return window.matchMedia('(prefers-contrast: high)').matches;
    },

    // Check if dark mode is preferred
    prefersDarkMode: () => {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
  }
};