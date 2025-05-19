import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Reusable spinner component with different sizes and variants
 */
export const Spinner = ({ 
  size = 'default', 
  variant = 'default',
  className = '',
  ...props 
}) => {
  const sizes = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    default: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  const variants = {
    default: 'text-primary',
    secondary: 'text-secondary',
    white: 'text-white',
    muted: 'text-muted-foreground'
  };

  return (
    <Loader2 
      className={cn(
        'animate-spin',
        sizes[size],
        variants[variant],
        className
      )}
      {...props}
    />
  );
};

/**
 * Full page spinner for page transitions
 */
export const PageSpinner = ({ message = 'Loading...', className = '' }) => {
  return (
    <div className={cn('min-h-screen flex items-center justify-center', className)}>
      <div className="text-center">
        <Spinner size="xl" className="mx-auto" />
        {message && (
          <p className="mt-4 text-sm text-muted-foreground">{message}</p>
        )}
      </div>
    </div>
  );
};

/**
 * Inline spinner for buttons and small sections
 */
export const InlineSpinner = ({ 
  text = 'Loading...', 
  size = 'sm',
  className = '' 
}) => {
  return (
    <span className={cn('inline-flex items-center gap-2', className)}>
      <Spinner size={size} />
      {text && <span>{text}</span>}
    </span>
  );
};

/**
 * Overlay spinner for covering content while loading
 */
export const OverlaySpinner = ({ 
  show = false, 
  message = 'Loading...',
  className = '' 
}) => {
  if (!show) return null;

  return (
    <div className={cn(
      'absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50',
      className
    )}>
      <div className="text-center">
        <Spinner size="lg" />
        {message && (
          <p className="mt-3 text-sm text-muted-foreground">{message}</p>
        )}
      </div>
    </div>
  );
};

export default Spinner;