import React, { memo } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

/**
 * Optimized Button component with React.memo
 * Only re-renders when props actually change
 */
const OptimizedButton = memo(({
  children,
  onClick,
  variant = 'default',
  size = 'default',
  disabled = false,
  loading = false,
  className,
  type = 'button',
  ...props
}) => {
  return (
    <Button
      type={type}
      variant={variant}
      size={size}
      disabled={disabled || loading}
      onClick={onClick}
      className={cn(className, loading && 'opacity-70 cursor-wait')}
      {...props}
    >
      {loading ? (
        <>
          <span className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full inline-block" />
          {children}
        </>
      ) : (
        children
      )}
    </Button>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for better performance
  return (
    prevProps.children === nextProps.children &&
    prevProps.onClick === nextProps.onClick &&
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.loading === nextProps.loading &&
    prevProps.className === nextProps.className &&
    prevProps.type === nextProps.type
  );
});

OptimizedButton.displayName = 'OptimizedButton';

export default OptimizedButton;