import React from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

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
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div 
        className="fixed inset-0 bg-black/50"
        onClick={() => onOpenChange && onOpenChange(false)}
      />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <div className="relative bg-background rounded-lg shadow-lg w-full max-w-lg">
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
  <h2 className={cn("text-lg font-semibold", className)} {...props}>
    {children}
  </h2>
);

export const DialogDescription = ({ children, className, ...props }) => (
  <p className={cn("text-sm text-muted-foreground", className)} {...props}>
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
    {...props}
  >
    {children || <X className="h-4 w-4" />}
  </button>
);