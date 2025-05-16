import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Tooltip component for displaying additional information on hover
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - The element that triggers the tooltip
 * @param {string} props.content - The tooltip content
 * @param {string} props.position - Tooltip position: top, right, bottom, left
 * @param {string} props.className - Additional CSS classes for the tooltip
 * @param {boolean} props.arrow - Whether to show an arrow pointing to the target
 * @param {number} props.delay - Delay before showing the tooltip in ms
 * @returns {JSX.Element} Tooltip component
 */
const Tooltip = ({ 
  children, 
  content, 
  position = 'top', 
  className, 
  arrow = true,
  delay = 300,
  ...props 
}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [coords, setCoords] = React.useState({ x: 0, y: 0 });
  const targetRef = React.useRef(null);
  const tooltipRef = React.useRef(null);
  const timeoutRef = React.useRef(null);
  
  const positionMap = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2"
  };
  
  const arrowPositionMap = {
    top: "bottom-[-4px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent",
    right: "left-[-4px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent",
    bottom: "top-[-4px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent",
    left: "right-[-4px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent"
  };
  
  const handleMouseEnter = React.useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (targetRef.current) {
        const rect = targetRef.current.getBoundingClientRect();
        setCoords({ x: rect.x, y: rect.y });
        setIsVisible(true);
      }
    }, delay);
  }, [delay]);
  
  const handleMouseLeave = React.useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setIsVisible(false);
  }, []);
  
  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);
  
  // Handle clicks outside to close tooltip
  React.useEffect(() => {
    const handleOutsideClick = (e) => {
      if (
        isVisible && 
        tooltipRef.current && 
        !tooltipRef.current.contains(e.target) && 
        targetRef.current && 
        !targetRef.current.contains(e.target)
      ) {
        setIsVisible(false);
      }
    };
    
    document.addEventListener('mousedown', handleOutsideClick);
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isVisible]);
  
  return (
    <div className="relative inline-block">
      <div
        ref={targetRef}
        className="inline-flex"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        {children}
      </div>
      
      {isVisible && content && (
        <div
          ref={tooltipRef}
          role="tooltip"
          className={cn(
            "absolute z-50 max-w-xs px-3 py-1.5 text-sm text-white bg-gray-900 rounded shadow-sm",
            positionMap[position],
            className
          )}
        >
          {content}
          {arrow && (
            <span 
              className={cn(
                "absolute w-0 h-0 border-4 border-gray-900",
                arrowPositionMap[position]
              )}
            />
          )}
        </div>
      )}
    </div>
  );
};

export { Tooltip };