import React from 'react';
import { cn } from '@/lib/utils';
/**
 * RadioGroup component for grouping radio buttons
 * 
 * @param {object} props - Component props
 * @param {string} props.value - Currently selected value
 * @param {function} props.onValueChange - Callback when value changes
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} RadioGroup component
 */
export const RadioGroup = React.forwardRef(({ 
  value,
  onValueChange,
  className,
  children,
  ...props 
}, ref) => {
  return (
    <div 
      ref={ref}
      role="radiogroup"
      className={cn("space-y-2", className)}
      {...props}
    >
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            checked: value === child.props.value,
            onChange: () => onValueChange(child.props.value),
          });
        }
        return child;
      })}
    </div>
  );
});
RadioGroup.displayName = "RadioGroup";
/**
 * RadioGroupItem component for individual radio items
 * 
 * @param {object} props - Component props
 * @param {string} props.value - Value of this radio item
 * @param {boolean} props.checked - Whether this item is checked
 * @param {function} props.onChange - Change handler
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} RadioGroupItem component
 */
export const RadioGroupItem = React.forwardRef(({ 
  value,
  checked,
  onChange,
  className,
  children,
  ...props 
}, ref) => {
  const id = props.id || `radio-${value}`;
  return (
    <div className="flex items-center space-x-2">
      <input
        ref={ref}
        type="radio"
        id={id}
        value={value}
        checked={checked}
        onChange={onChange}
        className={cn(
          "h-4 w-4 border-gray-300 text-primary focus:ring-primary",
          className
        )}
        {...props}
      />
      {children && (
        <label htmlFor={id} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {children}
        </label>
      )}
    </div>
  );
});
RadioGroupItem.displayName = "RadioGroupItem";