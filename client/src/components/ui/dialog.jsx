import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { trapFocus, handleEscapeKey, createFocusManager } from '@/utils/accessibility';

/**
 * Dialog component for modal dialogs
 * 
 * @param {object} props - Component props
 * @param {boolean} props.open - Whether the dialog is open
 * @param {function} props.onOpenChange - Callback when open state changes
 * @param {React.ReactNode} props.children - Dialog content
 * @returns {JSX.Element} Dialog component
 */
export const Dialog = ({ open, onOpenChange, children }) => {
  const dialogRef = useRef(null);
  const focusManager = useRef(createFocusManager());
  
  useEffect(() => {
    if (open) {
      // Save current focus
      focusManager.current.saveFocus();
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
      
      // Set up focus trap and escape handler
      const cleanup = [];
      
      if (dialogRef.current) {
        // Trap focus
        cleanup.push(trapFocus(dialogRef.current));
        
        // Focus the dialog
        setTimeout(() => {
          dialogRef.current?.focus();
        }, 0);
      }
      
      // Handle escape key
      cleanup.push(handleEscapeKey(() => onOpenChange?.(false)));
      
      return () => {
        cleanup.forEach(fn => fn());
      };
    } else {
      // Restore body scroll and focus
      document.body.style.overflow = '';
      focusManager.current.restoreFocus();
    }
  }, [open, onOpenChange]);
  
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50" role="presentation">
      <div 
        className="fixed inset-0 bg-black/50"
        aria-hidden="true"
        onClick={() => onOpenChange && onOpenChange(false)}
      />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <div 
          ref={dialogRef}
          className="relative bg-background rounded-lg shadow-lg w-full max-w-lg focus:outline-none"
          role="dialog"
          aria-modal="true"
          aria-labelledby="dialog-title"
          aria-describedby="dialog-description"
          tabIndex={-1}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

export const DialogHeader = ({ children, className, ...props }) => (
  <div className={cn("px-6 py-4 border-b", className)} {...props}>
    {children}
  </div>
);

export const DialogTitle = ({ children, className, ...props }) => (
  <h2 
    id="dialog-title"
    className={cn("text-lg font-semibold", className)} 
    {...props}
  >
    {children}
  </h2>
);

export const DialogDescription = ({ children, className, ...props }) => (
  <p 
    id="dialog-description"
    className={cn("text-sm text-muted-foreground", className)} 
    {...props}
  >
    {children}
  </p>
);

export const DialogContent = ({ children, className, ...props }) => (
  <div className={cn("px-6 py-4", className)} {...props}>
    {children}
  </div>
);

export const DialogFooter = ({ children, className, ...props }) => (
  <div className={cn("px-6 py-4 border-t flex justify-end space-x-2", className)} {...props}>
    {children}
  </div>
);

export const DialogClose = ({ children, onClick, className, ...props }) => (
  <button
    onClick={onClick}
    className={cn(
      "absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background",
      "hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
      className
    )}
    aria-label="Close dialog"
    {...props}
  >
    {children || <X className="h-4 w-4" aria-hidden="true" />}
  </button>
);