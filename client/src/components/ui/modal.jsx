import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';

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
  size = 'md'
}) => {
  const modalRef = useRef(null);

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden'; // Prevent body scrolling
    }
    
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'auto'; // Restore body scrolling
    };
  }, [isOpen, onClose]);

  // Handle clicking outside modal
  const handleBackdropClick = (e) => {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    full: 'max-w-full'
  };

  return createPortal(
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
      onClick={handleBackdropClick}
    >
      <div 
        ref={modalRef}
        className={cn(
          'bg-white rounded-lg shadow-xl overflow-hidden w-full',
          sizeClasses[size] || sizeClasses.md,
          className
        )}
        aria-modal="true"
        role="dialog"
      >
        {title && (
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          </div>
        )}
        <div className="p-6">{children}</div>
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
export const ModalHeader = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={cn("px-6 py-4 border-b border-gray-200", className)}
      {...props}
    >
      <h3 className="text-lg font-medium text-gray-900">{children}</h3>
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
    <div className={cn("p-6", className)} {...props}>
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
  return (
    <div 
      className={cn("px-6 py-4 border-t border-gray-200 flex justify-end space-x-2", className)}
      {...props}
    >
      {children}
    </div>
  );
};