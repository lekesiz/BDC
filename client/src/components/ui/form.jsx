import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Form component
 * 
 * @param {object} props - Component props
 * @param {function} props.onSubmit - Form submission handler
 * @param {React.ReactNode} props.children - Form content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Form component
 */
export const Form = ({ onSubmit, children, className = '', ...props }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit && onSubmit(e);
  };

  return (
    <form
      className={cn('space-y-4', className)}
      onSubmit={handleSubmit}
      {...props}
    >
      {children}
    </form>
  );
};

/**
 * FormGroup component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Form group content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Form group component
 */
export const FormGroup = ({ children, className = '', ...props }) => {
  return (
    <div className={cn('space-y-2', className)} {...props}>
      {children}
    </div>
  );
};

/**
 * FormLabel component
 * 
 * @param {object} props - Component props
 * @param {string} props.htmlFor - ID of the associated form control
 * @param {React.ReactNode} props.children - Label content
 * @param {boolean} props.required - Whether the associated field is required
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Form label component
 */
export const FormLabel = ({ 
  htmlFor, 
  children, 
  required = false,
  className = '', 
  ...props 
}) => {
  return (
    <label
      htmlFor={htmlFor}
      className={cn('block text-sm font-medium text-gray-700', className)}
      {...props}
    >
      {children}
      {required && <span className="ml-1 text-red-500">*</span>}
    </label>
  );
};

/**
 * FormControl component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Form control content
 * @param {string} props.id - ID of the form control
 * @param {string} props.name - Name of the form control
 * @param {boolean} props.invalid - Whether the form control has an error
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Form control component
 */
export const FormControl = ({ 
  children, 
  id, 
  name, 
  invalid = false,
  className = '', 
  ...props 
}) => {
  return React.cloneElement(React.Children.only(children), {
    id,
    name,
    className: cn(
      className,
      invalid && 'border-red-500 focus:ring-red-500 focus:border-red-500'
    ),
    'aria-invalid': invalid,
    ...props
  });
};

/**
 * FormHelper component for help text or error messages
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Helper content
 * @param {string} props.id - ID of the associated form control
 * @param {boolean} props.error - Whether this is an error message
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Form helper component
 */
export const FormHelper = ({ 
  children, 
  id, 
  error = false, 
  className = '',
  ...props 
}) => {
  return (
    <p
      id={id ? `${id}-helper` : undefined}
      className={cn(
        'text-sm',
        error ? 'text-red-600' : 'text-gray-500',
        className
      )}
      {...props}
    >
      {children}
    </p>
  );
};

/**
 * Checkbox component
 * 
 * @param {object} props - Component props
 * @param {string} props.id - ID of the checkbox
 * @param {string} props.name - Name of the checkbox
 * @param {boolean} props.checked - Whether the checkbox is checked
 * @param {function} props.onChange - Change handler
 * @param {string} props.label - Checkbox label
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Checkbox component
 */
export const Checkbox = ({ 
  id, 
  name, 
  checked, 
  onChange, 
  label,
  className = '', 
  ...props 
}) => {
  return (
    <div className="flex items-center">
      <input
        type="checkbox"
        id={id}
        name={name}
        checked={checked}
        onChange={onChange}
        className={cn(
          'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary',
          className
        )}
        {...props}
      />
      {label && (
        <label
          htmlFor={id}
          className="ml-2 block text-sm text-gray-700"
        >
          {label}
        </label>
      )}
    </div>
  );
};

/**
 * Radio component
 * 
 * @param {object} props - Component props
 * @param {string} props.id - ID of the radio button
 * @param {string} props.name - Name of the radio button
 * @param {boolean} props.checked - Whether the radio button is checked
 * @param {function} props.onChange - Change handler
 * @param {string} props.label - Radio button label
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Radio component
 */
export const Radio = ({ 
  id, 
  name, 
  checked, 
  onChange, 
  label,
  className = '', 
  ...props 
}) => {
  return (
    <div className="flex items-center">
      <input
        type="radio"
        id={id}
        name={name}
        checked={checked}
        onChange={onChange}
        className={cn(
          'h-4 w-4 border-gray-300 text-primary focus:ring-primary',
          className
        )}
        {...props}
      />
      {label && (
        <label
          htmlFor={id}
          className="ml-2 block text-sm text-gray-700"
        >
          {label}
        </label>
      )}
    </div>
  );
};

/**
 * Select component
 * 
 * @param {object} props - Component props
 * @param {string} props.id - ID of the select
 * @param {string} props.name - Name of the select
 * @param {function} props.onChange - Change handler
 * @param {array} props.options - Array of options
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Select component
 */
export const Select = ({ 
  id, 
  name, 
  onChange, 
  options = [], 
  placeholder = 'Select an option',
  className = '', 
  ...props 
}) => {
  return (
    <select
      id={id}
      name={name}
      onChange={onChange}
      className={cn(
        'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm',
        className
      )}
      {...props}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};