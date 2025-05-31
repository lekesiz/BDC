/**
 * Accessibility utility functions and helpers
 */

/**
 * Trap focus within a container element
 * @param {HTMLElement} container - The container element to trap focus within
 * @returns {Function} Cleanup function to remove event listeners
 */
export function trapFocus(container) {
  const focusableElements = container.querySelectorAll(
    'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstFocusableElement = focusableElements[0];
  const lastFocusableElement = focusableElements[focusableElements.length - 1];

  function handleKeyDown(e) {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstFocusableElement) {
          lastFocusableElement.focus();
          e.preventDefault();
        }
      } else {
        // Tab
        if (document.activeElement === lastFocusableElement) {
          firstFocusableElement.focus();
          e.preventDefault();
        }
      }
    }
  }

  container.addEventListener('keydown', handleKeyDown);
  
  // Focus first element
  if (firstFocusableElement) {
    firstFocusableElement.focus();
  }

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Announce message to screen readers
 * @param {string} message - Message to announce
 * @param {string} priority - Priority level: 'polite' or 'assertive'
 */
export function announceToScreenReader(message, priority = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.classList.add('sr-only');
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Generate unique ID for form elements
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
export function generateId(prefix = 'element') {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Handle escape key for closing modals/dropdowns
 * @param {Function} onClose - Function to call when escape is pressed
 * @returns {Function} Cleanup function to remove event listener
 */
export function handleEscapeKey(onClose) {
  function handleKeyDown(e) {
    if (e.key === 'Escape') {
      onClose();
    }
  }
  
  document.addEventListener('keydown', handleKeyDown);
  
  return () => {
    document.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Manage focus restoration after modal/dialog closes
 * @returns {Object} Object with saveFocus and restoreFocus methods
 */
export function createFocusManager() {
  let previouslyFocusedElement = null;
  
  return {
    saveFocus() {
      previouslyFocusedElement = document.activeElement;
    },
    restoreFocus() {
      if (previouslyFocusedElement && previouslyFocusedElement.focus) {
        previouslyFocusedElement.focus();
      }
    }
  };
}

/**
 * Check if user prefers reduced motion
 * @returns {boolean} True if user prefers reduced motion
 */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Add keyboard navigation to list items
 * @param {HTMLElement} container - Container element with list items
 * @param {string} itemSelector - CSS selector for list items
 * @param {Function} onSelect - Function to call when item is selected
 * @returns {Function} Cleanup function
 */
export function addListKeyboardNavigation(container, itemSelector, onSelect) {
  const items = container.querySelectorAll(itemSelector);
  let currentIndex = -1;

  function handleKeyDown(e) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        currentIndex = Math.min(currentIndex + 1, items.length - 1);
        focusItem(currentIndex);
        break;
      case 'ArrowUp':
        e.preventDefault();
        currentIndex = Math.max(currentIndex - 1, 0);
        focusItem(currentIndex);
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (currentIndex >= 0 && items[currentIndex]) {
          onSelect(items[currentIndex], currentIndex);
        }
        break;
      case 'Home':
        e.preventDefault();
        currentIndex = 0;
        focusItem(currentIndex);
        break;
      case 'End':
        e.preventDefault();
        currentIndex = items.length - 1;
        focusItem(currentIndex);
        break;
    }
  }

  function focusItem(index) {
    items.forEach((item, i) => {
      item.setAttribute('tabindex', i === index ? '0' : '-1');
      if (i === index) {
        item.focus();
      }
    });
  }

  container.addEventListener('keydown', handleKeyDown);

  // Initialize first item as focusable
  if (items.length > 0) {
    items[0].setAttribute('tabindex', '0');
  }

  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Debounce function for live regions
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounceAnnouncement(func, wait = 500) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Create skip navigation link
 * @param {string} targetId - ID of the main content element
 * @returns {HTMLElement} Skip link element
 */
export function createSkipLink(targetId = 'main-content') {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.className = 'skip-link';
  skipLink.textContent = 'Skip to main content';
  skipLink.setAttribute('aria-label', 'Skip to main content');
  
  skipLink.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView();
    }
  });
  
  return skipLink;
}

/**
 * Format text for screen readers
 * @param {string} visualText - Text shown visually
 * @param {string} screenReaderText - Text for screen readers
 * @returns {Object} Object with visual and sr-only text
 */
export function formatForScreenReader(visualText, screenReaderText) {
  return {
    visual: visualText,
    srOnly: screenReaderText || visualText
  };
}