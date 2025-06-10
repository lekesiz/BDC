// TODO: i18n - processed
import React, { forwardRef, useCallback, useState } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';
import { Button } from '@/components/ui/button';

/**
 * TouchOptimizedButton - Enhanced button component optimized for touch interactions
 * Features haptic feedback, touch target optimization, and mobile-specific states
 */import { useTranslation } from "react-i18next";
export const TouchOptimizedButton = forwardRef(({
  children,
  className,
  variant = 'default',
  size = 'default',
  hapticFeedback = true,
  hapticType = 'light',
  touchOptimized = true,
  pressAnimation = true,
  rippleEffect = true,
  disabled = false,
  loading = false,
  onClick,
  onTouchStart,
  onTouchEnd,
  ...props
}, ref) => {
  const {
    isMobile,
    capabilities,
    hapticFeedback: triggerHaptic,
    shouldReduceAnimations
  } = useMobile();

  const [isPressed, setIsPressed] = useState(false);
  const [ripples, setRipples] = useState([]);

  // Enhanced click handler with haptic feedback
  const handleClick = useCallback((event) => {
    if (disabled || loading) return;

    // Trigger haptic feedback on mobile
    if (hapticFeedback && isMobile) {
      triggerHaptic(hapticType);
    }

    onClick?.(event);
  }, [disabled, loading, hapticFeedback, isMobile, triggerHaptic, hapticType, onClick]);

  // Touch start handler for press state
  const handleTouchStart = useCallback((event) => {
    if (disabled || loading) return;

    setIsPressed(true);

    // Create ripple effect
    if (rippleEffect && !shouldReduceAnimations) {
      const rect = event.currentTarget.getBoundingClientRect();
      const touch = event.touches[0];
      const x = touch.clientX - rect.left;
      const y = touch.clientY - rect.top;

      const ripple = {
        id: Date.now(),
        x,
        y,
        size: Math.max(rect.width, rect.height) * 2
      };

      setRipples((prev) => [...prev, ripple]);

      // Remove ripple after animation
      setTimeout(() => {
        setRipples((prev) => prev.filter((r) => r.id !== ripple.id));
      }, 600);
    }

    onTouchStart?.(event);
  }, [disabled, loading, rippleEffect, shouldReduceAnimations, onTouchStart]);

  // Touch end handler
  const handleTouchEnd = useCallback((event) => {
    setIsPressed(false);
    onTouchEnd?.(event);
  }, [onTouchEnd]);

  // Size variants with touch optimization
  const sizeVariants = {
    sm: touchOptimized && isMobile ? 'h-11 px-4 text-sm' : 'h-9 px-3 text-sm',
    default: touchOptimized && isMobile ? 'h-12 px-6' : 'h-10 px-4',
    lg: touchOptimized && isMobile ? 'h-14 px-8 text-lg' : 'h-11 px-8',
    xl: touchOptimized && isMobile ? 'h-16 px-10 text-xl' : 'h-12 px-10',
    icon: touchOptimized && isMobile ? 'h-12 w-12' : 'h-10 w-10'
  };

  const buttonClasses = cn(
    // Base button classes
    'relative overflow-hidden select-none',

    // Touch optimizations
    touchOptimized && isMobile && [
    'min-h-[44px]', // iOS touch target guideline
    'min-w-[44px]',
    'touch-manipulation', // Disable double-tap zoom
    'active:scale-95' // Press animation
    ],

    // Press state
    pressAnimation && !shouldReduceAnimations && isPressed && 'scale-95',

    // Reduced motion
    shouldReduceAnimations && 'transition-none',

    // Custom className
    className
  );

  return (
    <Button
      ref={ref}
      variant={variant}
      size={size}
      disabled={disabled || loading}
      className={buttonClasses}
      onClick={handleClick}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      style={{
        // Override size if touch optimized
        ...(touchOptimized && isMobile && sizeVariants[size] && {
          height: sizeVariants[size].includes('h-') ?
          sizeVariants[size].match(/h-(\d+)/)?.[1] * 4 + 'px' : undefined
        })
      }}
      {...props}>

      {/* Ripple effects */}
      {rippleEffect && !shouldReduceAnimations &&
      <div className="absolute inset-0 pointer-events-none">
          {ripples.map((ripple) =>
        <div
          key={ripple.id}
          className="absolute rounded-full bg-white/20 animate-ping"
          style={{
            left: ripple.x - ripple.size / 2,
            top: ripple.y - ripple.size / 2,
            width: ripple.size,
            height: ripple.size,
            animationDuration: '600ms',
            animationIterationCount: 1
          }} />

        )}
        </div>
      }

      {/* Loading state */}
      {loading &&
      <div className="absolute inset-0 flex items-center justify-center bg-inherit">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        </div>
      }

      {/* Button content */}
      <span className={cn('relative z-10', loading && 'invisible')}>
        {children}
      </span>
    </Button>);

});

TouchOptimizedButton.displayName = 'TouchOptimizedButton';

/**
 * FloatingActionButton - Material Design inspired FAB optimized for mobile
 */
export const FloatingActionButton = forwardRef(({
  children,
  className,
  position = 'bottom-right',
  size = 'default',
  extended = false,
  ...props
}, ref) => {
  const { isMobile } = useMobile();

  const positionClasses = {
    'bottom-right': 'fixed bottom-6 right-6',
    'bottom-left': 'fixed bottom-6 left-6',
    'bottom-center': 'fixed bottom-6 left-1/2 transform -translate-x-1/2',
    'top-right': 'fixed top-6 right-6',
    'top-left': 'fixed top-6 left-6',
    'center': 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2'
  };

  const sizeClasses = {
    sm: extended ? 'h-12 px-4' : 'h-12 w-12',
    default: extended ? 'h-14 px-6' : 'h-14 w-14',
    lg: extended ? 'h-16 px-8' : 'h-16 w-16'
  };

  return (
    <TouchOptimizedButton
      ref={ref}
      variant="default"
      className={cn(
        'rounded-full shadow-lg hover:shadow-xl transition-shadow z-50',
        positionClasses[position],
        sizeClasses[size],
        extended ? 'flex items-center gap-2' : 'justify-center',
        // Mobile adjustments
        isMobile && 'pb-safe pr-safe', // Account for safe areas
        className
      )}
      touchOptimized
      hapticFeedback
      hapticType="medium"
      {...props}>

      {children}
    </TouchOptimizedButton>);

});

FloatingActionButton.displayName = 'FloatingActionButton';

/**
 * TouchOptimizedIconButton - Icon-only button optimized for touch
 */
export const TouchOptimizedIconButton = forwardRef(({
  children,
  className,
  size = 'default',
  variant = 'ghost',
  ...props
}, ref) => {
  const { isMobile } = useMobile();

  return (
    <TouchOptimizedButton
      ref={ref}
      variant={variant}
      size="icon"
      className={cn(
        'rounded-full',
        // Ensure minimum touch target on mobile
        isMobile && size === 'sm' && 'min-h-[44px] min-w-[44px]',
        className
      )}
      touchOptimized
      hapticFeedback
      hapticType="light"
      {...props}>

      {children}
    </TouchOptimizedButton>);

});

TouchOptimizedIconButton.displayName = 'TouchOptimizedIconButton';

export default TouchOptimizedButton;