// TODO: i18n - processed
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';
import { TouchOptimizedButton } from './TouchOptimizedButton';

/**
 * MobileDrawer - Responsive drawer component optimized for mobile devices
 * Features swipe gestures, backdrop blur, and smooth animations
 */import { useTranslation } from "react-i18next";
export const MobileDrawer = ({
  isOpen,
  onClose,
  children,
  title,
  position = 'bottom',
  size = 'auto',
  backdrop = true,
  backdropBlur = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  showCloseButton = true,
  swipeToClose = true,
  className,
  contentClassName,
  overlayClassName,
  ...props
}) => {const { t } = useTranslation();
  const {
    isMobile,
    shouldReduceAnimations,
    hapticFeedback,
    screenSize
  } = useMobile();

  const [isAnimating, setIsAnimating] = useState(false);
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const drawerRef = useRef(null);
  const startTouchRef = useRef(null);
  const currentTouchRef = useRef(null);

  // Animation classes based on position
  const getAnimationClasses = () => {
    const base = shouldReduceAnimations ? '' : 'transition-transform duration-300 ease-out';

    if (!isOpen && !isAnimating) return 'invisible';

    const transforms = {
      bottom: isOpen && !isDragging ? 'translate-y-0' : 'translate-y-full',
      top: isOpen && !isDragging ? 'translate-y-0' : '-translate-y-full',
      left: isOpen && !isDragging ? 'translate-x-0' : '-translate-x-full',
      right: isOpen && !isDragging ? 'translate-x-0' : 'translate-x-full'
    };

    return cn(base, transforms[position]);
  };

  // Size classes
  const getSizeClasses = () => {
    const sizeMap = {
      sm: {
        bottom: 'h-1/3',
        top: 'h-1/3',
        left: 'w-80',
        right: 'w-80'
      },
      md: {
        bottom: 'h-1/2',
        top: 'h-1/2',
        left: 'w-96',
        right: 'w-96'
      },
      lg: {
        bottom: 'h-2/3',
        top: 'h-2/3',
        left: 'w-1/2',
        right: 'w-1/2'
      },
      full: {
        bottom: 'h-full',
        top: 'h-full',
        left: 'w-full',
        right: 'w-full'
      },
      auto: position === 'bottom' || position === 'top' ? 'max-h-[90vh]' : 'max-w-[90vw]'
    };

    if (size === 'auto') return sizeMap.auto;
    return sizeMap[size]?.[position] || sizeMap.md[position];
  };

  // Position classes
  const getPositionClasses = () => {
    const positions = {
      bottom: 'bottom-0 left-0 right-0 rounded-t-xl',
      top: 'top-0 left-0 right-0 rounded-b-xl',
      left: 'top-0 left-0 bottom-0 rounded-r-xl',
      right: 'top-0 right-0 bottom-0 rounded-l-xl'
    };
    return positions[position];
  };

  // Handle escape key
  useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        hapticFeedback('light');
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose, hapticFeedback]);

  // Handle body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  // Animation state management
  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 300);
      return () => clearTimeout(timer);
    } else {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Touch handlers for swipe to close
  const handleTouchStart = useCallback((e) => {
    if (!swipeToClose) return;

    const touch = e.touches[0];
    startTouchRef.current = {
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    };
    currentTouchRef.current = { x: touch.clientX, y: touch.clientY };
    setIsDragging(false);
  }, [swipeToClose]);

  const handleTouchMove = useCallback((e) => {
    if (!swipeToClose || !startTouchRef.current) return;

    const touch = e.touches[0];
    currentTouchRef.current = { x: touch.clientX, y: touch.clientY };

    const deltaX = touch.clientX - startTouchRef.current.x;
    const deltaY = touch.clientY - startTouchRef.current.y;

    // Determine if we should start dragging based on direction
    const shouldDrag = (() => {
      switch (position) {
        case 'bottom':
          return deltaY > 10 && Math.abs(deltaY) > Math.abs(deltaX);
        case 'top':
          return deltaY < -10 && Math.abs(deltaY) > Math.abs(deltaX);
        case 'left':
          return deltaX < -10 && Math.abs(deltaX) > Math.abs(deltaY);
        case 'right':
          return deltaX > 10 && Math.abs(deltaX) > Math.abs(deltaY);
        default:
          return false;
      }
    })();

    if (shouldDrag) {
      setIsDragging(true);

      const offset = (() => {
        switch (position) {
          case 'bottom':
            return Math.max(0, deltaY);
          case 'top':
            return Math.min(0, deltaY);
          case 'left':
            return Math.min(0, deltaX);
          case 'right':
            return Math.max(0, deltaX);
          default:
            return 0;
        }
      })();

      setDragOffset(offset);

      // Prevent scrolling while dragging
      e.preventDefault();
    }
  }, [swipeToClose, position]);

  const handleTouchEnd = useCallback(() => {
    if (!swipeToClose || !startTouchRef.current || !currentTouchRef.current) return;

    const deltaTime = Date.now() - startTouchRef.current.time;
    const deltaX = currentTouchRef.current.x - startTouchRef.current.x;
    const deltaY = currentTouchRef.current.y - startTouchRef.current.y;

    // Calculate velocity
    const velocity = (() => {
      switch (position) {
        case 'bottom':
          return deltaY / deltaTime;
        case 'top':
          return -deltaY / deltaTime;
        case 'left':
          return -deltaX / deltaTime;
        case 'right':
          return deltaX / deltaTime;
        default:
          return 0;
      }
    })();

    // Determine if we should close
    const shouldClose = (() => {
      const threshold = position === 'bottom' || position === 'top' ?
      screenSize.height * 0.3 : screenSize.width * 0.3;

      return Math.abs(dragOffset) > threshold || velocity > 0.5;
    })();

    if (shouldClose) {
      hapticFeedback('medium');
      onClose();
    }

    // Reset states
    setIsDragging(false);
    setDragOffset(0);
    startTouchRef.current = null;
    currentTouchRef.current = null;
  }, [swipeToClose, position, dragOffset, screenSize, hapticFeedback, onClose]);

  // Handle backdrop click
  const handleBackdropClick = useCallback((e) => {
    if (closeOnBackdrop && e.target === e.currentTarget) {
      hapticFeedback('light');
      onClose();
    }
  }, [closeOnBackdrop, onClose, hapticFeedback]);

  if (!isOpen && !isAnimating) return null;

  const drawer =
  <div
    className={cn(
      'fixed inset-0 z-50 flex',
      overlayClassName
    )}
    onClick={handleBackdropClick}
    {...props}>

      {/* Backdrop */}
      {backdrop &&
    <div
      className={cn(
        'absolute inset-0 bg-black/50',
        backdropBlur && 'backdrop-blur-sm',
        shouldReduceAnimations ? '' : 'transition-opacity duration-300',
        isOpen ? 'opacity-100' : 'opacity-0'
      )} />

    }

      {/* Drawer Content */}
      <div
      ref={drawerRef}
      className={cn(
        'fixed bg-background shadow-xl',
        getPositionClasses(),
        getSizeClasses(),
        getAnimationClasses(),
        // Apply drag transform
        isDragging && 'transition-none',
        contentClassName
      )}
      style={{
        transform: isDragging ? (() => {
          switch (position) {
            case 'bottom':
              return `translateY(${dragOffset}px)`;
            case 'top':
              return `translateY(${dragOffset}px)`;
            case 'left':
              return `translateX(${dragOffset}px)`;
            case 'right':
              return `translateX(${dragOffset}px)`;
            default:
              return 'none';
          }
        })() : undefined
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}>

        {/* Handle for visual indication of swipe capability */}
        {swipeToClose && (position === 'bottom' || position === 'top') &&
      <div className="flex justify-center py-2">
            <div className="w-12 h-1 bg-muted-foreground/30 rounded-full" />
          </div>
      }

        {/* Header */}
        {(title || showCloseButton) &&
      <div className="flex items-center justify-between p-4 border-b">
            <h3 className="text-lg font-semibold">{title}</h3>
            {showCloseButton &&
        <TouchOptimizedButton
          variant="ghost"
          size="icon"
          onClick={() => {
            hapticFeedback('light');
            onClose();
          }}
          className="h-8 w-8">

                <X className="h-4 w-4" />
              </TouchOptimizedButton>
        }
          </div>
      }

        {/* Content */}
        <div className={cn('flex-1 overflow-auto', className)}>
          {children}
        </div>
      </div>
    </div>;


  // Render in portal for proper z-index handling
  return createPortal(drawer, document.body);
};

/**
 * MobileBottomSheet - Specialized drawer for bottom sheets
 */
export const MobileBottomSheet = (props) =>
<MobileDrawer position="bottom" {...props} />;


/**
 * MobileSidebar - Specialized drawer for sidebars
 */
export const MobileSidebar = (props) =>
<MobileDrawer position="left" size="md" {...props} />;


export default MobileDrawer;