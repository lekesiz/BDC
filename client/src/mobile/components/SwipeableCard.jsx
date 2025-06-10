// TODO: i18n - processed
import React, { useState, useRef, useCallback, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';
import { Card } from '@/components/ui/card';

/**
 * SwipeableCard - Card component with swipe actions and gestures
 * Features left/right swipe actions, customizable thresholds, and haptic feedback
 */import { useTranslation } from "react-i18next";
export const SwipeableCard = forwardRef(({
  children,
  className,
  leftAction,
  rightAction,
  leftActionComponent,
  rightActionComponent,
  swipeThreshold = 80,
  hapticFeedback = true,
  animationDuration = 300,
  disabled = false,
  onSwipeStart,
  onSwipeEnd,
  onSwipeLeft,
  onSwipeRight,
  resetOnAction = true,
  ...props
}, ref) => {
  const {
    isMobile,
    hapticFeedback: triggerHaptic,
    shouldReduceAnimations
  } = useMobile();

  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [actionTriggered, setActionTriggered] = useState(null);

  const cardRef = useRef(null);
  const startXRef = useRef(0);
  const currentXRef = useRef(0);
  const startTimeRef = useRef(0);

  // Calculate action visibility and intensity
  const leftActionVisible = dragOffset > 20;
  const rightActionVisible = dragOffset < -20;
  const leftActionIntensity = Math.min(Math.abs(dragOffset) / swipeThreshold, 1);
  const rightActionIntensity = Math.min(Math.abs(dragOffset) / swipeThreshold, 1);

  // Touch start handler
  const handleTouchStart = useCallback((e) => {
    if (disabled || isAnimating) return;

    const touch = e.touches[0];
    startXRef.current = touch.clientX;
    currentXRef.current = touch.clientX;
    startTimeRef.current = Date.now();

    setIsDragging(true);
    onSwipeStart?.();
  }, [disabled, isAnimating, onSwipeStart]);

  // Touch move handler
  const handleTouchMove = useCallback((e) => {
    if (disabled || !isDragging) return;

    const touch = e.touches[0];
    currentXRef.current = touch.clientX;

    const deltaX = touch.clientX - startXRef.current;

    // Apply resistance at extremes
    const resistance = 0.7;
    const maxDrag = swipeThreshold * 1.5;

    let newOffset = deltaX;
    if (Math.abs(deltaX) > maxDrag) {
      const excess = Math.abs(deltaX) - maxDrag;
      newOffset = Math.sign(deltaX) * (maxDrag + excess * resistance);
    }

    setDragOffset(newOffset);

    // Provide haptic feedback at threshold points
    if (hapticFeedback && isMobile) {
      const wasOverThreshold = Math.abs(dragOffset) >= swipeThreshold;
      const isOverThreshold = Math.abs(newOffset) >= swipeThreshold;

      if (!wasOverThreshold && isOverThreshold) {
        triggerHaptic('medium');
      }
    }

    // Prevent default to avoid scrolling
    e.preventDefault();
  }, [disabled, isDragging, swipeThreshold, hapticFeedback, isMobile, triggerHaptic, dragOffset]);

  // Touch end handler
  const handleTouchEnd = useCallback(() => {
    if (disabled || !isDragging) return;

    const deltaX = currentXRef.current - startXRef.current;
    const deltaTime = Date.now() - startTimeRef.current;
    const velocity = Math.abs(deltaX) / deltaTime;

    // Determine if action should be triggered
    const shouldTriggerAction = Math.abs(dragOffset) >= swipeThreshold || velocity > 0.5;

    if (shouldTriggerAction) {
      if (dragOffset > 0 && leftAction) {
        // Left swipe action
        setActionTriggered('left');
        triggerHaptic('success');
        onSwipeLeft?.();
        leftAction();
      } else if (dragOffset < 0 && rightAction) {
        // Right swipe action
        setActionTriggered('right');
        triggerHaptic('success');
        onSwipeRight?.();
        rightAction();
      }
    }

    // Reset or maintain position
    if (resetOnAction || !shouldTriggerAction) {
      resetPosition();
    }

    setIsDragging(false);
    onSwipeEnd?.();
  }, [
  disabled,
  isDragging,
  dragOffset,
  swipeThreshold,
  leftAction,
  rightAction,
  resetOnAction,
  triggerHaptic,
  onSwipeLeft,
  onSwipeRight,
  onSwipeEnd]
  );

  // Reset card position
  const resetPosition = useCallback(() => {
    setIsAnimating(true);
    setDragOffset(0);
    setActionTriggered(null);

    setTimeout(() => {
      setIsAnimating(false);
    }, animationDuration);
  }, [animationDuration]);

  // Mouse events for desktop testing
  const handleMouseDown = useCallback((e) => {
    if (isMobile) return;

    startXRef.current = e.clientX;
    currentXRef.current = e.clientX;
    startTimeRef.current = Date.now();
    setIsDragging(true);

    const handleMouseMove = (e) => {
      if (!isDragging) return;
      currentXRef.current = e.clientX;
      const deltaX = e.clientX - startXRef.current;
      setDragOffset(deltaX);
    };

    const handleMouseUp = () => {
      handleTouchEnd();
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [isMobile, isDragging, handleTouchEnd]);

  return (
    <div className="relative overflow-hidden">
      {/* Background Actions */}
      <div className="absolute inset-0 flex">
        {/* Left Action Background */}
        {leftActionComponent &&
        <div
          className={cn(
            'flex items-center justify-start pl-4 bg-green-500 text-white',
            'transition-all duration-200',
            leftActionVisible ? 'opacity-100' : 'opacity-0'
          )}
          style={{
            width: Math.max(0, dragOffset),
            transform: `translateX(${Math.min(0, dragOffset)}px)`
          }}>

            <div
            style={{
              opacity: leftActionIntensity,
              transform: `scale(${0.8 + leftActionIntensity * 0.2})`
            }}>

              {leftActionComponent}
            </div>
          </div>
        }

        {/* Right Action Background */}
        {rightActionComponent &&
        <div
          className={cn(
            'flex items-center justify-end pr-4 bg-red-500 text-white ml-auto',
            'transition-all duration-200',
            rightActionVisible ? 'opacity-100' : 'opacity-0'
          )}
          style={{
            width: Math.max(0, -dragOffset),
            transform: `translateX(${Math.max(0, dragOffset)}px)`
          }}>

            <div
            style={{
              opacity: rightActionIntensity,
              transform: `scale(${0.8 + rightActionIntensity * 0.2})`
            }}>

              {rightActionComponent}
            </div>
          </div>
        }
      </div>

      {/* Card Content */}
      <Card
        ref={ref}
        className={cn(
          'relative z-10 select-none',
          isDragging && 'cursor-grabbing',
          !isDragging && !disabled && 'cursor-grab',
          shouldReduceAnimations || isDragging ? '' : `transition-transform duration-${animationDuration}`,
          actionTriggered === 'left' && 'animate-pulse',
          actionTriggered === 'right' && 'animate-pulse',
          className
        )}
        style={{
          transform: `translateX(${dragOffset}px)`,
          ...(isDragging && {
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)'
          })
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        {...props}>

        {children}
      </Card>

      {/* Action Indicators */}
      {(leftActionVisible || rightActionVisible) &&
      <div className="absolute inset-0 pointer-events-none z-20">
          {leftActionVisible &&
        <div className="absolute left-2 top-1/2 transform -translate-y-1/2">
              <div
            className="w-2 h-8 bg-white rounded-full opacity-80"
            style={{ opacity: leftActionIntensity * 0.8 }} />

            </div>
        }
          
          {rightActionVisible &&
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div
            className="w-2 h-8 bg-white rounded-full opacity-80"
            style={{ opacity: rightActionIntensity * 0.8 }} />

            </div>
        }
        </div>
      }
    </div>);

});

SwipeableCard.displayName = 'SwipeableCard';

/**
 * SwipeableListItem - Specialized swipeable component for list items
 */
export const SwipeableListItem = forwardRef(({
  children,
  className,
  onDelete,
  onEdit,
  onArchive,
  onFavorite,
  deleteLabel = 'Delete',
  editLabel = 'Edit',
  archiveLabel = 'Archive',
  favoriteLabel = 'Favorite',
  ...props
}, ref) => {
  return (
    <SwipeableCard
      ref={ref}
      className={cn('border-0 shadow-none bg-transparent', className)}
      leftAction={onEdit || onFavorite}
      rightAction={onDelete || onArchive}
      leftActionComponent={
      onEdit ?
      <div className="flex items-center gap-2">
            <span>{editLabel}</span>
          </div> :
      onFavorite ?
      <div className="flex items-center gap-2">
            <span>{favoriteLabel}</span>
          </div> :
      null
      }
      rightActionComponent={
      onDelete ?
      <div className="flex items-center gap-2">
            <span>{deleteLabel}</span>
          </div> :
      onArchive ?
      <div className="flex items-center gap-2">
            <span>{archiveLabel}</span>
          </div> :
      null
      }
      {...props}>

      <div className="bg-card border rounded-lg p-4 shadow-sm">
        {children}
      </div>
    </SwipeableCard>);

});

SwipeableListItem.displayName = 'SwipeableListItem';

export default SwipeableCard;