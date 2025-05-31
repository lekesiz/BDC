import { useEffect, useRef } from 'react';

/**
 * Custom hook for managing focus in accessible web applications
 */
export const useFocusManagement = () => {
  const previousElementRef = useRef(null);

  /**
   * Store the currently focused element
   */
  const storeFocus = () => {
    previousElementRef.current = document.activeElement;
  };

  /**
   * Restore focus to the previously stored element
   */
  const restoreFocus = () => {
    if (previousElementRef.current && typeof previousElementRef.current.focus === 'function') {
      previousElementRef.current.focus();
    }
  };

  /**
   * Focus the first focusable element within a container
   */
  const focusFirst = (container) => {
    const focusableElements = getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  };

  /**
   * Focus the last focusable element within a container
   */
  const focusLast = (container) => {
    const focusableElements = getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusableElements[focusableElements.length - 1].focus();
    }
  };

  /**
   * Get all focusable elements within a container
   */
  const getFocusableElements = (container) => {
    if (!container) return [];
    
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors))
      .filter(element => !element.hasAttribute('disabled') && isVisible(element));
  };

  /**
   * Check if an element is visible
   */
  const isVisible = (element) => {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0';
  };

  /**
   * Trap focus within a container (useful for modals)
   */
  const trapFocus = (container, event) => {
    if (!container) return;

    const focusableElements = getFocusableElements(container);
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        // Shift + Tab: moving backwards
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab: moving forwards
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  };

  return {
    storeFocus,
    restoreFocus,
    focusFirst,
    focusLast,
    getFocusableElements,
    trapFocus
  };
};

/**
 * Hook for managing modal focus
 */
export const useModalFocus = (isOpen, modalRef) => {
  const { storeFocus, restoreFocus, focusFirst, trapFocus } = useFocusManagement();

  useEffect(() => {
    if (isOpen) {
      storeFocus();
      // Focus the modal container after a short delay
      setTimeout(() => {
        if (modalRef.current) {
          focusFirst(modalRef.current);
        }
      }, 100);

      // Handle escape key
      const handleEscape = (event) => {
        if (event.key === 'Escape') {
          restoreFocus();
        }
      };

      // Handle focus trap
      const handleKeyDown = (event) => {
        if (modalRef.current) {
          trapFocus(modalRef.current, event);
        }
      };

      document.addEventListener('keydown', handleEscape);
      document.addEventListener('keydown', handleKeyDown);

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      restoreFocus();
    }
  }, [isOpen, modalRef, storeFocus, restoreFocus, focusFirst, trapFocus]);
};

export default useFocusManagement;