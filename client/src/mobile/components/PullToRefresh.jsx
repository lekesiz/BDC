// TODO: i18n - processed
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { RefreshCw, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';

/**
 * PullToRefresh - Implement pull-to-refresh functionality for mobile
 * Features smooth animations, haptic feedback, and customizable thresholds
 */import { useTranslation } from "react-i18next";
export const PullToRefresh = ({
  children,
  onRefresh,
  className,
  refreshThreshold = 80,
  maxPullDistance = 120,
  refreshingText = 'Refreshing...',
  pullText = 'Pull to refresh',
  releaseText = 'Release to refresh',
  disabled = false,
  hapticFeedback = true,
  showIndicator = true,
  indicatorHeight = 60,
  ...props
}) => {const { t } = useTranslation();
  const {
    isMobile,
    hapticFeedback: triggerHaptic,
    shouldReduceAnimations
  } = useMobile();

  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isPulling, setIsPulling] = useState(false);
  const [canRefresh, setCanRefresh] = useState(false);

  const containerRef = useRef(null);
  const startYRef = useRef(0);
  const currentYRef = useRef(0);
  const startTimeRef = useRef(0);
  const lastScrollTopRef = useRef(0);

  // Check if we're at the top of the scroll container
  const isAtTop = useCallback(() => {
    if (!containerRef.current) return false;
    return containerRef.current.scrollTop <= 0;
  }, []);

  // Handle refresh action
  const handleRefresh = useCallback(async () => {
    if (disabled || isRefreshing || !onRefresh) return;

    setIsRefreshing(true);
    setCanRefresh(false);

    if (hapticFeedback && isMobile) {
      triggerHaptic('success');
    }

    try {
      await onRefresh();
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      // Add minimum refresh time for better UX
      setTimeout(() => {
        setIsRefreshing(false);
        setPullDistance(0);
        setIsPulling(false);
      }, 500);
    }
  }, [disabled, isRefreshing, onRefresh, hapticFeedback, isMobile, triggerHaptic]);

  // Touch start handler
  const handleTouchStart = useCallback((e) => {
    if (disabled || isRefreshing || !isAtTop()) return;

    const touch = e.touches[0];
    startYRef.current = touch.clientY;
    currentYRef.current = touch.clientY;
    startTimeRef.current = Date.now();
    lastScrollTopRef.current = containerRef.current?.scrollTop || 0;
  }, [disabled, isRefreshing, isAtTop]);

  // Touch move handler
  const handleTouchMove = useCallback((e) => {
    if (disabled || isRefreshing || !startYRef.current) return;

    const touch = e.touches[0];
    currentYRef.current = touch.clientY;

    const deltaY = touch.clientY - startYRef.current;
    const currentScrollTop = containerRef.current?.scrollTop || 0;

    // Only start pulling if we're at the top and pulling down
    if (deltaY > 0 && currentScrollTop === 0 && lastScrollTopRef.current === 0) {
      setIsPulling(true);

      // Apply resistance curve
      const resistance = 0.5;
      const distance = Math.min(deltaY * resistance, maxPullDistance);
      setPullDistance(distance);

      // Check if we can refresh
      const canRefreshNow = distance >= refreshThreshold;
      if (canRefreshNow !== canRefresh) {
        setCanRefresh(canRefreshNow);

        // Haptic feedback when threshold is reached
        if (canRefreshNow && hapticFeedback && isMobile) {
          triggerHaptic('medium');
        }
      }

      // Prevent default scrolling when pulling
      if (distance > 10) {
        e.preventDefault();
      }
    }

    lastScrollTopRef.current = currentScrollTop;
  }, [
  disabled,
  isRefreshing,
  maxPullDistance,
  refreshThreshold,
  canRefresh,
  hapticFeedback,
  isMobile,
  triggerHaptic]
  );

  // Touch end handler
  const handleTouchEnd = useCallback(() => {
    if (disabled || isRefreshing) return;

    if (isPulling) {
      if (canRefresh) {
        handleRefresh();
      } else {
        // Reset position
        setPullDistance(0);
        setIsPulling(false);
        setCanRefresh(false);
      }
    }

    // Reset refs
    startYRef.current = 0;
    currentYRef.current = 0;
    startTimeRef.current = 0;
  }, [disabled, isRefreshing, isPulling, canRefresh, handleRefresh]);

  // Calculate indicator progress
  const progress = Math.min(pullDistance / refreshThreshold, 1);
  const rotation = isRefreshing ? 'rotate-360' : `rotate-${Math.floor(progress * 180)}`;

  // Get indicator text
  const getIndicatorText = () => {
    if (isRefreshing) return refreshingText;
    if (canRefresh) return releaseText;
    return pullText;
  };

  // Indicator transform
  const indicatorTransform = `translateY(${Math.min(pullDistance - indicatorHeight, 0)}px)`;

  return (
    <div
      className={cn('relative overflow-hidden', className)}
      {...props}>

      {/* Pull Indicator */}
      {showIndicator && (isPulling || isRefreshing) &&
      <div
        className={cn(
          'absolute top-0 left-0 right-0 z-10',
          'flex flex-col items-center justify-center',
          'bg-background/95 backdrop-blur-sm border-b',
          shouldReduceAnimations ? '' : 'transition-transform duration-200'
        )}
        style={{
          height: indicatorHeight,
          transform: indicatorTransform
        }}>

          {/* Icon */}
          <div className="flex items-center justify-center mb-1">
            {isRefreshing ?
          <RefreshCw
            className={cn(
              'h-5 w-5 text-primary',
              shouldReduceAnimations ? '' : 'animate-spin'
            )} /> :


          <ChevronDown
            className={cn(
              'h-5 w-5 text-muted-foreground transition-transform duration-200',
              canRefresh && 'rotate-180 text-primary'
            )}
            style={{
              transform: shouldReduceAnimations ?
              canRefresh ? 'rotate(180deg)' : 'rotate(0deg)' :
              `rotate(${Math.min(progress * 180, 180)}deg)`
            }} />

          }
          </div>

          {/* Text */}
          <span className="text-xs text-muted-foreground font-medium">
            {getIndicatorText()}
          </span>

          {/* Progress Bar */}
          <div className="w-12 h-1 bg-muted rounded-full mt-2 overflow-hidden">
            <div
            className={cn(
              'h-full bg-primary rounded-full transition-all duration-200',
              isRefreshing && (shouldReduceAnimations ? '' : 'animate-pulse')
            )}
            style={{
              width: `${isRefreshing ? 100 : progress * 100}%`
            }} />

          </div>
        </div>
      }

      {/* Content Container */}
      <div
        ref={containerRef}
        className={cn(
          'h-full overflow-auto touch-scroll',
          shouldReduceAnimations ? '' : 'transition-transform duration-200'
        )}
        style={{
          transform: isPulling || isRefreshing ?
          `translateY(${Math.min(pullDistance, indicatorHeight)}px)` :
          'translateY(0px)'
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}>

        {children}
      </div>
    </div>);

};

/**
 * SimplePullToRefresh - Simplified version without complex indicators
 */
export const SimplePullToRefresh = ({
  children,
  onRefresh,
  className,
  ...props
}) => {const { t } = useTranslation();
  return (
    <PullToRefresh
      onRefresh={onRefresh}
      className={className}
      showIndicator={false}
      refreshThreshold={60}
      maxPullDistance={80}
      {...props}>

      {children}
    </PullToRefresh>);

};

/**
 * Hook for programmatic refresh control
 */
export const useRefreshControl = (onRefresh) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refresh = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  }, [isRefreshing, onRefresh]);

  return {
    isRefreshing,
    refresh
  };
};

export default PullToRefresh;