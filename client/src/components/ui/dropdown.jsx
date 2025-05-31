import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

/**
 * Dropdown component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.trigger - Element that triggers the dropdown
 * @param {React.ReactNode} props.children - Dropdown content
 * @param {string} props.align - Dropdown alignment: left, right
 * @param {string} props.className - Additional CSS classes for the dropdown
 * @param {string} props.triggerClassName - Additional CSS classes for the trigger
 * @returns {JSX.Element} Dropdown component
 */
export const Dropdown = ({ 
  trigger, 
  children, 
  align = 'left',
  className = '',
  triggerClassName = '',
  'aria-label': ariaLabel,
  closeOnSelect = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const triggerRef = useRef(null);
  const itemRefs = useRef([]);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  // Close dropdown when clicking outside and handle keyboard navigation
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setFocusedIndex(-1);
      }
    };

    const handleKeyDown = (event) => {
      if (!isOpen) return;
      
      switch (event.key) {
        case 'Escape':
          setIsOpen(false);
          setFocusedIndex(-1);
          triggerRef.current?.focus();
          break;
        case 'ArrowDown':
          event.preventDefault();
          setFocusedIndex(prev => {
            const nextIndex = prev < itemRefs.current.length - 1 ? prev + 1 : 0;
            itemRefs.current[nextIndex]?.focus();
            return nextIndex;
          });
          break;
        case 'ArrowUp':
          event.preventDefault();
          setFocusedIndex(prev => {
            const nextIndex = prev > 0 ? prev - 1 : itemRefs.current.length - 1;
            itemRefs.current[nextIndex]?.focus();
            return nextIndex;
          });
          break;
        case 'Home':
          event.preventDefault();
          setFocusedIndex(0);
          itemRefs.current[0]?.focus();
          break;
        case 'End':
          event.preventDefault();
          const lastIndex = itemRefs.current.length - 1;
          setFocusedIndex(lastIndex);
          itemRefs.current[lastIndex]?.focus();
          break;
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      // Reset focus when opening
      setFocusedIndex(-1);
      setTimeout(() => {
        itemRefs.current[0]?.focus();
        setFocusedIndex(0);
      }, 0);
    }
  };

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button 
        ref={triggerRef}
        className={cn("cursor-pointer", triggerClassName)}
        onClick={toggleDropdown}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label={ariaLabel}
        type="button"
      >
        {trigger}
      </button>
      
      {isOpen && (
        <div 
          className={cn(
            "absolute z-50 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5",
            {
              "right-0": align === 'right',
              "left-0": align === 'left',
            },
            className
          )}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby={ariaLabel}
        >
          <div className="py-1 rounded-md bg-white shadow-xs">
            {React.Children.map(children, (child, index) => {
              if (React.isValidElement(child) && child.type === DropdownItem) {
                return React.cloneElement(child, {
                  ref: (el) => itemRefs.current[index] = el,
                  tabIndex: focusedIndex === index ? 0 : -1,
                  onClose: closeOnSelect ? () => setIsOpen(false) : undefined,
                  role: "menuitem"
                });
              }
              return child;
            })}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Dropdown Item component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Item content
 * @param {function} props.onClick - Click handler
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Dropdown item component
 */
export const DropdownItem = React.forwardRef(({ 
  children, 
  onClick, 
  className = '',
  onClose,
  disabled = false,
  ...props 
}, ref) => {
  const handleClick = (e) => {
    e.preventDefault();
    if (!disabled) {
      onClick && onClick();
      onClose && onClose();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick(e);
    }
  };

  return (
    <a
      ref={ref}
      href="#"
      className={cn(
        "block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:bg-gray-100 focus:outline-none",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-disabled={disabled}
      {...props}
    >
      {children}
    </a>
  );
});

DropdownItem.displayName = 'DropdownItem';

/**
 * Dropdown Divider component
 * 
 * @param {object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Dropdown divider component
 */
export const DropdownDivider = ({ className = '', ...props }) => {
  return (
    <div 
      className={cn("border-t border-gray-100 my-1", className)}
      role="separator"
      aria-orientation="horizontal"
      {...props}
    />
  );
};