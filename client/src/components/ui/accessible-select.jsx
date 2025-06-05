import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { generateId } from '@/utils/accessibility';
/**
 * Accessible Select component with proper ARIA attributes and keyboard navigation
 * 
 * @param {object} props - Component props
 * @param {array} props.options - Array of options {value, label, disabled}
 * @param {string} props.value - Currently selected value
 * @param {function} props.onValueChange - Callback when value changes
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.label - Label for the select
 * @param {string} props.error - Error message
 * @param {boolean} props.required - Whether the select is required
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Accessible Select component
 */
export const AccessibleSelect = React.forwardRef(({ 
  options = [],
  value,
  onValueChange,
  placeholder = 'Select an option',
  label,
  error,
  required = false,
  disabled = false,
  className,
  ...props 
}, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchTimeout, setSearchTimeout] = useState(null);
  const buttonRef = useRef(null);
  const listRef = useRef(null);
  const optionRefs = useRef([]);
  const id = props.id || generateId('select');
  const labelId = `${id}-label`;
  const listboxId = `${id}-listbox`;
  const errorId = error ? `${id}-error` : undefined;
  const selectedOption = options.find(opt => opt.value === value);
  const selectedIndex = options.findIndex(opt => opt.value === value);
  // Filter options based on search
  const filteredOptions = options.filter(option => 
    option.label.toLowerCase().includes(searchQuery.toLowerCase())
  );
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        buttonRef.current && 
        !buttonRef.current.contains(event.target) &&
        listRef.current && 
        !listRef.current.contains(event.target)
      ) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);
  // Focus management
  useEffect(() => {
    if (isOpen && focusedIndex >= 0 && optionRefs.current[focusedIndex]) {
      optionRefs.current[focusedIndex].focus();
    }
  }, [focusedIndex, isOpen]);
  // Keyboard navigation
  const handleKeyDown = (event) => {
    if (!isOpen && (event.key === 'ArrowDown' || event.key === 'ArrowUp' || event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      setIsOpen(true);
      setFocusedIndex(selectedIndex >= 0 ? selectedIndex : 0);
      return;
    }
    if (!isOpen) return;
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev < filteredOptions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Home':
        event.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        event.preventDefault();
        setFocusedIndex(filteredOptions.length - 1);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0 && filteredOptions[focusedIndex]) {
          selectOption(filteredOptions[focusedIndex]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        setIsOpen(false);
        setSearchQuery('');
        buttonRef.current?.focus();
        break;
      case 'Tab':
        setIsOpen(false);
        setSearchQuery('');
        break;
      default:
        // Type-ahead search
        if (event.key.length === 1) {
          clearTimeout(searchTimeout);
          const newQuery = searchQuery + event.key;
          setSearchQuery(newQuery);
          // Find first matching option
          const matchIndex = options.findIndex(opt => 
            opt.label.toLowerCase().startsWith(newQuery.toLowerCase())
          );
          if (matchIndex >= 0) {
            setFocusedIndex(matchIndex);
          }
          // Clear search after delay
          const timeout = setTimeout(() => setSearchQuery(''), 1000);
          setSearchTimeout(timeout);
        }
    }
  };
  const selectOption = (option) => {
    if (!option.disabled) {
      onValueChange(option.value);
      setIsOpen(false);
      setSearchQuery('');
      buttonRef.current?.focus();
    }
  };
  const toggleOpen = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
      if (!isOpen) {
        setFocusedIndex(selectedIndex >= 0 ? selectedIndex : 0);
      } else {
        setSearchQuery('');
      }
    }
  };
  return (
    <div className="w-full space-y-2">
      {label && (
        <label 
          id={labelId}
          htmlFor={id}
          className={cn(
            "block text-sm font-medium text-gray-700",
            error && "text-red-500"
          )}
        >
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      )}
      <div className="relative" ref={ref}>
        <button
          ref={buttonRef}
          id={id}
          type="button"
          role="combobox"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-controls={listboxId}
          aria-labelledby={label ? labelId : undefined}
          aria-describedby={errorId}
          aria-invalid={error ? 'true' : 'false'}
          aria-required={required}
          disabled={disabled}
          onClick={toggleOpen}
          onKeyDown={handleKeyDown}
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
            "placeholder:text-muted-foreground",
            "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500 focus:ring-red-500",
            className
          )}
          {...props}
        >
          <span className={!selectedOption ? 'text-muted-foreground' : ''}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <ChevronDown 
            className={cn(
              "h-4 w-4 opacity-50 transition-transform",
              isOpen && "transform rotate-180"
            )} 
            aria-hidden="true"
          />
        </button>
        {isOpen && (
          <ul
            ref={listRef}
            id={listboxId}
            role="listbox"
            aria-labelledby={label ? labelId : undefined}
            aria-activedescendant={
              focusedIndex >= 0 ? `${id}-option-${focusedIndex}` : undefined
            }
            className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-background shadow-lg focus:outline-none"
          >
            {filteredOptions.length === 0 ? (
              <li className="px-2 py-1.5 text-sm text-muted-foreground">
                No options found
              </li>
            ) : (
              filteredOptions.map((option, index) => (
                <li
                  key={option.value}
                  id={`${id}-option-${index}`}
                  ref={el => optionRefs.current[index] = el}
                  role="option"
                  aria-selected={value === option.value}
                  aria-disabled={option.disabled}
                  tabIndex={-1}
                  onClick={() => selectOption(option)}
                  onMouseEnter={() => setFocusedIndex(index)}
                  className={cn(
                    "relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none",
                    "hover:bg-accent hover:text-accent-foreground",
                    "focus:bg-accent focus:text-accent-foreground",
                    value === option.value && "bg-accent text-accent-foreground",
                    option.disabled && "opacity-50 cursor-not-allowed",
                    focusedIndex === index && "bg-accent text-accent-foreground"
                  )}
                >
                  <span className="flex-1">{option.label}</span>
                  {value === option.value && (
                    <Check className="h-4 w-4" aria-hidden="true" />
                  )}
                </li>
              ))
            )}
          </ul>
        )}
      </div>
      {error && (
        <p id={errorId} className="text-sm text-red-500 mt-1" role="alert">
          {error}
        </p>
      )}
      {/* Screen reader only live region for search */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {searchQuery && `Searching for ${searchQuery}`}
      </div>
    </div>
  );
});
AccessibleSelect.displayName = "AccessibleSelect";
export default AccessibleSelect;