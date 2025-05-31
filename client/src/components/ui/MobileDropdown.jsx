import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';
import { useBreakpoint } from '@/hooks/useMediaQuery';
import { ChevronDown, Check } from 'lucide-react';

/**
 * Mobile-optimized dropdown component
 * Shows as bottom sheet on mobile, regular dropdown on desktop
 */
export const MobileDropdown = ({
  trigger,
  children,
  value,
  onChange,
  options = [],
  placeholder = 'Select an option',
  label,
  className,
  disabled = false,
  error = false,
  helperText,
  fullWidth = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value);
  const { isMobile } = useBreakpoint();
  const triggerRef = useRef(null);

  useEffect(() => {
    setSelectedValue(value);
  }, [value]);

  const handleSelect = (optionValue) => {
    setSelectedValue(optionValue);
    onChange && onChange(optionValue);
    setIsOpen(false);
  };

  const selectedOption = options.find(opt => opt.value === selectedValue);

  // Custom trigger element
  if (trigger) {
    return (
      <>
        <div onClick={() => !disabled && setIsOpen(true)}>
          {trigger}
        </div>
        {isOpen && isMobile && (
          <MobileBottomSheet
            isOpen={isOpen}
            onClose={() => setIsOpen(false)}
            title={label || placeholder}
            options={options}
            selectedValue={selectedValue}
            onSelect={handleSelect}
          />
        )}
      </>
    );
  }

  // Default dropdown trigger
  return (
    <div className={cn('relative', fullWidth && 'w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
        </label>
      )}
      
      <button
        ref={triggerRef}
        type="button"
        onClick={() => !disabled && setIsOpen(true)}
        disabled={disabled}
        className={cn(
          'flex items-center justify-between w-full px-3 py-2 text-left',
          'bg-white dark:bg-gray-800 border rounded-md shadow-sm',
          'min-h-[44px] text-base sm:text-sm',
          'transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary',
          error 
            ? 'border-red-500 focus:ring-red-500' 
            : 'border-gray-300 dark:border-gray-600',
          disabled 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer',
          className
        )}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={label}
      >
        <span className={cn(
          'block truncate',
          !selectedOption && 'text-gray-500 dark:text-gray-400'
        )}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown className={cn(
          'h-4 w-4 text-gray-400 transition-transform',
          isOpen && 'transform rotate-180'
        )} />
      </button>

      {helperText && (
        <p className={cn(
          'mt-1 text-sm',
          error ? 'text-red-600' : 'text-gray-500'
        )}>
          {helperText}
        </p>
      )}

      {/* Desktop dropdown */}
      {isOpen && !isMobile && (
        <DesktopDropdown
          options={options}
          selectedValue={selectedValue}
          onSelect={handleSelect}
          onClose={() => setIsOpen(false)}
          triggerRef={triggerRef}
        />
      )}

      {/* Mobile bottom sheet */}
      {isOpen && isMobile && (
        <MobileBottomSheet
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          title={label || placeholder}
          options={options}
          selectedValue={selectedValue}
          onSelect={handleSelect}
        />
      )}
    </div>
  );
};

/**
 * Desktop dropdown menu
 */
const DesktopDropdown = ({ 
  options, 
  selectedValue, 
  onSelect, 
  onClose,
  triggerRef 
}) => {
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target)
      ) {
        onClose();
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose, triggerRef]);

  return (
    <div
      ref={dropdownRef}
      className="absolute z-50 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto focus:outline-none"
      role="listbox"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onSelect(option.value)}
          className={cn(
            'w-full px-3 py-2 text-left flex items-center justify-between',
            'hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors',
            'focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none',
            selectedValue === option.value && 'bg-gray-50 dark:bg-gray-700'
          )}
          role="option"
          aria-selected={selectedValue === option.value}
        >
          <span className="block truncate text-sm">
            {option.label}
          </span>
          {selectedValue === option.value && (
            <Check className="h-4 w-4 text-primary" />
          )}
        </button>
      ))}
    </div>
  );
};

/**
 * Mobile bottom sheet for dropdown
 */
const MobileBottomSheet = ({ 
  isOpen, 
  onClose, 
  title,
  options, 
  selectedValue, 
  onSelect 
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-end">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Bottom sheet */}
      <div className="relative w-full bg-white dark:bg-gray-800 rounded-t-xl max-h-[80vh] animate-in slide-in-from-bottom-full duration-300">
        {/* Handle bar */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-10 h-1 bg-gray-300 dark:bg-gray-600 rounded-full" />
        </div>
        
        {/* Header */}
        <div className="px-4 pb-3 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            {title}
          </h3>
        </div>
        
        {/* Options list */}
        <div className="overflow-y-auto max-h-[60vh] pb-safe">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onSelect(option.value)}
              className={cn(
                'w-full px-4 py-4 text-left flex items-center justify-between',
                'hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors',
                'border-b border-gray-100 dark:border-gray-700',
                selectedValue === option.value && 'bg-gray-50 dark:bg-gray-700'
              )}
            >
              <span className="text-base">
                {option.label}
              </span>
              {selectedValue === option.value && (
                <Check className="h-5 w-5 text-primary" />
              )}
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
};