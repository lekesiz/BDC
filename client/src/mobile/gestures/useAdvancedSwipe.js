// TODO: i18n - processed
import { useState, useCallback, useRef, useEffect } from 'react';
import { useMobile } from '../components/MobileProvider';

/**
 * Advanced swipe gesture hook with velocity tracking, multi-directional support,
 * and configurable behavior
 */import { useTranslation } from "react-i18next";
export const useAdvancedSwipe = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onSwipeStart,
  onSwipeEnd,
  onSwipeCancel,
  threshold = 50,
  velocityThreshold = 0.3,
  timeThreshold = 500,
  maxDuration = 1000,
  preventDefaultOnSwipe = true,
  enabled = true,
  direction = 'all', // 'horizontal', 'vertical', 'all'
  hapticFeedback = true,
  debug = false
} = {}) => {
  const { hapticFeedback: triggerHaptic, isMobile } = useMobile();

  const [swipeState, setSwipeState] = useState({
    isSwiping: false,
    direction: null,
    distance: 0,
    velocity: 0,
    startTime: 0,
    currentX: 0,
    currentY: 0
  });

  const startPosRef = useRef({ x: 0, y: 0 });
  const currentPosRef = useRef({ x: 0, y: 0 });
  const velocityRef = useRef({ x: 0, y: 0 });
  const startTimeRef = useRef(0);
  const lastTimeRef = useRef(0);
  const animationFrameRef = useRef(null);

  // Calculate velocity using a sliding window approach
  const updateVelocity = useCallback((deltaX, deltaY, deltaTime) => {
    if (deltaTime > 0) {
      const alpha = 0.8; // Smoothing factor
      velocityRef.current.x = alpha * velocityRef.current.x + (1 - alpha) * (deltaX / deltaTime);
      velocityRef.current.y = alpha * velocityRef.current.y + (1 - alpha) * (deltaY / deltaTime);
    }
  }, []);

  // Determine swipe direction
  const getSwipeDirection = useCallback((deltaX, deltaY) => {
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);

    if (direction === 'horizontal' && absX < absY) return null;
    if (direction === 'vertical' && absY < absX) return null;

    if (absX > absY) {
      return deltaX > 0 ? 'right' : 'left';
    } else {
      return deltaY > 0 ? 'down' : 'up';
    }
  }, [direction]);

  // Touch start handler
  const handleTouchStart = useCallback((e) => {
    if (!enabled) return;

    const touch = e.touches[0];
    const now = Date.now();

    startPosRef.current = { x: touch.clientX, y: touch.clientY };
    currentPosRef.current = { x: touch.clientX, y: touch.clientY };
    velocityRef.current = { x: 0, y: 0 };
    startTimeRef.current = now;
    lastTimeRef.current = now;

    setSwipeState((prev) => ({
      ...prev,
      isSwiping: true,
      startTime: now,
      currentX: touch.clientX,
      currentY: touch.clientY
    }));

    onSwipeStart?.(e, {
      x: touch.clientX,
      y: touch.clientY,
      time: now
    });

    if (debug) {
      console.log('Swipe started:', { x: touch.clientX, y: touch.clientY });
    }
  }, [enabled, onSwipeStart, debug]);

  // Touch move handler
  const handleTouchMove = useCallback((e) => {
    if (!enabled || !swipeState.isSwiping) return;

    const touch = e.touches[0];
    const now = Date.now();
    const deltaTime = now - lastTimeRef.current;

    if (deltaTime < 16) return; // Throttle to ~60fps

    const deltaX = touch.clientX - currentPosRef.current.x;
    const deltaY = touch.clientY - currentPosRef.current.y;

    currentPosRef.current = { x: touch.clientX, y: touch.clientY };
    lastTimeRef.current = now;

    updateVelocity(deltaX, deltaY, deltaTime);

    const totalDeltaX = touch.clientX - startPosRef.current.x;
    const totalDeltaY = touch.clientY - startPosRef.current.y;
    const distance = Math.sqrt(totalDeltaX * totalDeltaX + totalDeltaY * totalDeltaY);
    const swipeDirection = getSwipeDirection(totalDeltaX, totalDeltaY);

    setSwipeState((prev) => ({
      ...prev,
      direction: swipeDirection,
      distance,
      velocity: Math.sqrt(velocityRef.current.x ** 2 + velocityRef.current.y ** 2),
      currentX: touch.clientX,
      currentY: touch.clientY
    }));

    // Prevent default if we detect a swipe
    if (preventDefaultOnSwipe && distance > 10 && swipeDirection) {
      e.preventDefault();
    }

    if (debug && distance > threshold) {
      console.log('Swipe progress:', {
        direction: swipeDirection,
        distance,
        velocity: velocityRef.current
      });
    }
  }, [
  enabled,
  swipeState.isSwiping,
  updateVelocity,
  getSwipeDirection,
  preventDefaultOnSwipe,
  threshold,
  debug]
  );

  // Touch end handler
  const handleTouchEnd = useCallback((e) => {
    if (!enabled || !swipeState.isSwiping) return;

    const now = Date.now();
    const duration = now - startTimeRef.current;
    const totalDeltaX = currentPosRef.current.x - startPosRef.current.x;
    const totalDeltaY = currentPosRef.current.y - startPosRef.current.y;
    const distance = Math.sqrt(totalDeltaX * totalDeltaX + totalDeltaY * totalDeltaY);
    const velocity = Math.sqrt(velocityRef.current.x ** 2 + velocityRef.current.y ** 2);
    const swipeDirection = getSwipeDirection(totalDeltaX, totalDeltaY);

    // Check if swipe is valid
    const isValidSwipe =
    swipeDirection &&
    duration <= maxDuration && (
    distance >= threshold || velocity >= velocityThreshold);


    // Cancel if duration is too long
    const isCancelled = duration > maxDuration;

    if (debug) {
      console.log('Swipe ended:', {
        direction: swipeDirection,
        distance,
        velocity,
        duration,
        isValid: isValidSwipe,
        isCancelled
      });
    }

    if (isCancelled) {
      onSwipeCancel?.(e, {
        direction: swipeDirection,
        distance,
        velocity,
        duration
      });
    } else if (isValidSwipe) {
      // Trigger haptic feedback
      if (hapticFeedback && isMobile) {
        triggerHaptic('light');
      }

      // Call appropriate handler
      switch (swipeDirection) {
        case 'left':
          onSwipeLeft?.(e, { distance, velocity, duration });
          break;
        case 'right':
          onSwipeRight?.(e, { distance, velocity, duration });
          break;
        case 'up':
          onSwipeUp?.(e, { distance, velocity, duration });
          break;
        case 'down':
          onSwipeDown?.(e, { distance, velocity, duration });
          break;
      }
    }

    // Reset state
    setSwipeState({
      isSwiping: false,
      direction: null,
      distance: 0,
      velocity: 0,
      startTime: 0,
      currentX: 0,
      currentY: 0
    });

    onSwipeEnd?.(e, {
      direction: swipeDirection,
      distance,
      velocity,
      duration,
      isValid: isValidSwipe,
      isCancelled
    });
  }, [
  enabled,
  swipeState.isSwiping,
  maxDuration,
  threshold,
  velocityThreshold,
  getSwipeDirection,
  hapticFeedback,
  isMobile,
  triggerHaptic,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onSwipeCancel,
  onSwipeEnd,
  debug]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    // Event handlers
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,

    // Current state
    ...swipeState,

    // Utilities
    isSwipingLeft: swipeState.direction === 'left',
    isSwipingRight: swipeState.direction === 'right',
    isSwipingUp: swipeState.direction === 'up',
    isSwipingDown: swipeState.direction === 'down',
    isSwipingHorizontal: swipeState.direction === 'left' || swipeState.direction === 'right',
    isSwipingVertical: swipeState.direction === 'up' || swipeState.direction === 'down',

    // Progress (0-1)
    progress: Math.min(swipeState.distance / threshold, 1),

    // Reset function
    reset: () => setSwipeState({
      isSwiping: false,
      direction: null,
      distance: 0,
      velocity: 0,
      startTime: 0,
      currentX: 0,
      currentY: 0
    })
  };
};

/**
 * Simplified swipe hook for basic left/right swipes
 */
export const useSimpleSwipe = ({
  onSwipeLeft,
  onSwipeRight,
  threshold = 50,
  enabled = true
}) => {
  return useAdvancedSwipe({
    onSwipeLeft,
    onSwipeRight,
    threshold,
    enabled,
    direction: 'horizontal'
  });
};

/**
 * Vertical swipe hook for pull-to-refresh or navigation
 */
export const useVerticalSwipe = ({
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  enabled = true
}) => {
  return useAdvancedSwipe({
    onSwipeUp,
    onSwipeDown,
    threshold,
    enabled,
    direction: 'vertical'
  });
};

export default useAdvancedSwipe;