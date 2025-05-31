import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';
import { useBreakpoint } from '@/hooks/useMediaQuery';

/**
 * Modal component using React Portal
 * 
 * @param {object} props - Component props
 * @param {boolean} props.isOpen - Whether the modal is open
 * @param {function} props.onClose - Function to close the modal
 * @param {React.ReactNode} props.title - Modal title
 * @param {React.ReactNode} props.children - Modal content
 * @param {string} props.className - Additional CSS classes for the modal
 * @param {string} props.size - Modal size: 'sm', 'md', 'lg', 'xl', 'full'
 * @returns {JSX.Element|null} Modal component
 */
export const Modal = ({ 
  isOpen, 
  onClose, 
  title,
  children,
  className = '',
  size = 'md',
  closeOnEscape = true,
  closeOnOutsideClick = true,
  initialFocus = null,
  returnFocus = true,
  fullScreenOnMobile = true
}) => {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);
  const { isMobile } = useBreakpoint();

  // Handle ESC key and focus management
  useEffect(() => {
    if (isOpen) {
      // Save current focus
      previousActiveElement.current = document.activeElement;
      
      // Prevent body scrolling
      document.body.style.overflow = 'hidden';
      
      // Focus management
      setTimeout(() => {
        if (initialFocus && modalRef.current) {
          const focusElement = modalRef.current.querySelector(initialFocus);
          if (focusElement) {
            focusElement.focus();
          }
        } else if (modalRef.current) {
          // Focus the modal itself if no initial focus specified
          modalRef.current.focus();
        }
      }, 0);
      
      // Handle escape key
      const handleEsc = (event) => {
        if (closeOnEscape && event.key === 'Escape') {
          onClose();
        }
      };
      
      // Trap focus within modal
      const handleTab = (event) => {
        if (event.key === 'Tab' && modalRef.current) {
          const focusableElements = modalRef.current.querySelectorAll(
            'a[href], button:not([disabled]), textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
          );
          
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];
          
          if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      };
      
      document.addEventListener('keydown', handleEsc);
      document.addEventListener('keydown', handleTab);
      
      return () => {
        document.removeEventListener('keydown', handleEsc);
        document.removeEventListener('keydown', handleTab);
      };
    } else {
      // Restore body scrolling and focus
      document.body.style.overflow = 'auto';
      
      if (returnFocus && previousActiveElement.current && previousActiveElement.current.focus) {
        previousActiveElement.current.focus();
      }
    }
  }, [isOpen, onClose, closeOnEscape, initialFocus, returnFocus]);

  // Handle clicking outside modal
  const handleBackdropClick = (e) => {
    if (closeOnOutsideClick && modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'sm:max-w-sm',
    md: 'sm:max-w-md',
    lg: 'sm:max-w-lg',
    xl: 'sm:max-w-xl',
    '2xl': 'sm:max-w-2xl',
    '3xl': 'sm:max-w-3xl',
    '4xl': 'sm:max-w-4xl',
    '5xl': 'sm:max-w-5xl',
    full: 'max-w-full'
  };

  return createPortal(
    <div 
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center sm:p-4 bg-black bg-opacity-50 transition-opacity"
      onClick={handleBackdropClick}
      aria-modal="true"
      aria-hidden={!isOpen}
    >
      <div 
        ref={modalRef}
        className={cn(
          'bg-white dark:bg-gray-800 shadow-xl overflow-hidden w-full transition-all transform',
          fullScreenOnMobile && isMobile 
            ? 'h-full rounded-none' 
            : 'rounded-t-xl sm:rounded-lg max-h-[90vh] sm:max-h-[85vh]',
          sizeClasses[size] || sizeClasses.md,
          'focus:outline-none',
          'animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-10 sm:slide-in-from-bottom-0',
          className
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        tabIndex="-1"
      >
        {title && (
          <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 id="modal-title" className="text-base sm:text-lg font-medium text-gray-900 dark:text-gray-100">{title}</h3>
            <button
              onClick={onClose}
              className="sm:hidden p-2 -mr-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary rounded-full"
              aria-label="Close modal"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        <div className={cn(
          "overflow-y-auto",
          fullScreenOnMobile && isMobile ? "flex-1" : "max-h-[calc(90vh-8rem)] sm:max-h-[calc(85vh-8rem)]"
        )} role="document">
          <div className="p-4 sm:p-6">{children}</div>
        </div>
      </div>
    </div>,
    document.body
  );
};

/**
 * Modal Header component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Header content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Modal header component
 */
export const ModalHeader = ({ children, className = '', onClose, ...props }) => {
  return (
    <div 
      className={cn("px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between", className)}
      {...props}
    >
      <h3 className="text-base sm:text-lg font-medium text-gray-900 dark:text-gray-100">{children}</h3>
      {onClose && (
        <button
          onClick={onClose}
          className="sm:hidden p-2 -mr-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary rounded-full"
          aria-label="Close modal"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
};

/**
 * Modal Body component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Body content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Modal body component
 */
export const ModalBody = ({ children, className = '', ...props }) => {
  return (
    <div className={cn("p-4 sm:p-6", className)} {...props}>
      {children}
    </div>
  );
};

/**
 * Modal Footer component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Footer content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Modal footer component
 */
export const ModalFooter = ({ children, className = '', ...props }) => {
  const { isMobile } = useBreakpoint();
  
  return (
    <div 
      className={cn(
        "px-4 sm:px-6 py-3 sm:py-4 border-t border-gray-200 dark:border-gray-700",
        isMobile ? "flex flex-col-reverse gap-2" : "flex justify-end space-x-2",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};