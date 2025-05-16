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
  triggerClassName = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleDropdown = () => setIsOpen(!isOpen);

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <div 
        className={cn("cursor-pointer", triggerClassName)}
        onClick={toggleDropdown}
      >
        {trigger}
      </div>
      
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
        >
          <div className="py-1 rounded-md bg-white shadow-xs">
            {children}
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
export const DropdownItem = ({ 
  children, 
  onClick, 
  className = '',
  ...props 
}) => {
  return (
    <a
      href="#"
      className={cn(
        "block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900",
        className
      )}
      onClick={(e) => {
        e.preventDefault();
        onClick && onClick();
      }}
      {...props}
    >
      {children}
    </a>
  );
};

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
      {...props}
    />
  );
};