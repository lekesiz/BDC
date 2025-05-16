import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Checkbox component
 * 
 * @param {object} props - Component props
 * @param {boolean} props.checked - Whether the checkbox is checked
 * @param {function} props.onCheckedChange - Callback when checked state changes
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Checkbox component
 */
export const Checkbox = React.forwardRef(({ 
  checked = false,
  onCheckedChange,
  className,
  ...props 
}, ref) => {
  return (
    <button
      ref={ref}
      type="button"
      role="checkbox"
      aria-checked={checked}
      onClick={() => onCheckedChange && onCheckedChange(!checked)}
      className={cn(
        "h-4 w-4 shrink-0 rounded-sm border border-primary",
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50",
        checked && "bg-primary text-primary-foreground",
        className
      )}
      {...props}
    >
      {checked && (
        <svg
          className="h-3 w-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={3}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
          />
        </svg>
      )}
    </button>
  );
});

Checkbox.displayName = "Checkbox";