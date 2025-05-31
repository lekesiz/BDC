import React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

/**
 * Button variants using class-variance-authority
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background active:scale-95",
  {
    variants: {
      variant: {
        default: "bg-primary text-white hover:bg-primary-dark dark:bg-primary-dark dark:hover:bg-primary shadow-sm",
        destructive: "bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800 shadow-sm",
        outline: "border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200",
        secondary: "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-600",
        ghost: "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200",
        link: "underline-offset-4 hover:underline text-primary dark:text-primary-light p-0 h-auto",
      },
      size: {
        default: "h-10 sm:h-10 py-2 px-4 text-base sm:text-sm",
        sm: "h-8 sm:h-9 px-3 text-sm rounded-md",
        lg: "h-12 sm:h-11 px-6 sm:px-8 text-base sm:text-base rounded-md",
        icon: "h-10 w-10 p-0",
        // Mobile-optimized sizes
        mobile: "min-h-[44px] px-4 py-3 text-base",
        mobileSm: "min-h-[40px] px-3 py-2 text-sm",
        mobileLg: "min-h-[48px] px-6 py-3 text-base",
      },
      fullWidth: {
        true: "w-full",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      fullWidth: false,
    },
  }
);

/**
 * Button component with support for different variants and sizes
 * 
 * @param {object} props - Component props
 * @param {string} props.variant - Button variant: default, destructive, outline, secondary, ghost, link
 * @param {string} props.size - Button size: default, sm, lg, icon
 * @param {boolean} props.isLoading - Whether the button is in a loading state
 * @param {React.ReactNode} props.children - Button content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Button component
 */
const Button = ({ 
  children, 
  variant, 
  size, 
  isLoading = false,
  className,
  leftIcon,
  rightIcon,
  loadingText = 'Loading...',
  fullWidth = false,
  mobileSize,
  'aria-label': ariaLabel,
  ...props 
}) => {
  // Use mobile size on small screens if specified
  const effectiveSize = mobileSize && typeof window !== 'undefined' && window.innerWidth < 640 ? mobileSize : size;
  
  return (
    <button
      className={cn(
        buttonVariants({ variant, size: effectiveSize, fullWidth }),
        // Ensure minimum touch target size on mobile
        "min-h-[44px] sm:min-h-0",
        className
      )}
      disabled={isLoading || props.disabled}
      aria-disabled={isLoading || props.disabled}
      aria-busy={isLoading}
      aria-label={ariaLabel || (isLoading ? loadingText : undefined)}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center">
          <svg 
            className="animate-spin -ml-1 mr-2 h-4 w-4 sm:h-4 sm:w-4 text-current" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
            aria-hidden="true"
            role="img"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            ></circle>
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span className="sr-only" aria-live="polite">{loadingText}</span>
          {loadingText}
        </span>
      ) : (
        <span className="flex items-center justify-center">
          {leftIcon && <span className="mr-2 flex-shrink-0" aria-hidden="true">{leftIcon}</span>}
          <span className="truncate">{children}</span>
          {rightIcon && <span className="ml-2 flex-shrink-0" aria-hidden="true">{rightIcon}</span>}
        </span>
      )}
    </button>
  );
};

export { Button, buttonVariants };