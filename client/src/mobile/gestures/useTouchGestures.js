// TODO: i18n - processed
import { useState, useCallback, useRef, useEffect } from 'react';
import { useMobile } from '../components/MobileProvider';

/**
 * Comprehensive touch gesture hook supporting multiple touch types
 * Includes tap, double tap, long press, pinch, and pan gestures
 */import { useTranslation } from "react-i18next";
export const useTouchGestures = ({
  onTap,
  onDoubleTap,
  onLongPress,
  onPinch,
  onPan,
  onTouchStart,
  onTouchEnd,

  // Tap configuration
  tapThreshold = 10,
  doubleTapDelay = 300,
  longPressDelay = 500,

  // Pan configuration
  panThreshold = 10,

  // Pinch configuration
  pinchThreshold = 10,

  // General configuration
  enabled = true,
  preventDefault = false,
  hapticFeedback = true,
  debug = false
} = {}) => {
  const { hapticFeedback: triggerHaptic, isMobile } = useMobile();

  const [gestureState, setGestureState] = useState({
    isTouching: false,
    isPanning: false,
    isPinching: false,
    isLongPressing: false,
    touchCount: 0,
    panDistance: 0,
    pinchScale: 1,
    pinchDistance: 0
  });

  // Refs for gesture tracking
  const touchStartRef = useRef([]);
  const touchCurrentRef = useRef([]);
  const tapCountRef = useRef(0);
  const lastTapTimeRef = useRef(0);
  const longPressTimerRef = useRef(null);
  const doubleTapTimerRef = useRef(null);
  const initialPinchDistanceRef = useRef(0);
  const panStartRef = useRef({ x: 0, y: 0 });

  // Utility functions
  const getDistance = useCallback((touch1, touch2) => {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  const getMidpoint = useCallback((touch1, touch2) => {
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  }, []);

  const getTouchInfo = useCallback((touches) => {
    return Array.from(touches).map((touch) => ({
      id: touch.identifier,
      x: touch.clientX,
      y: touch.clientY,
      pageX: touch.pageX,
      pageY: touch.pageY
    }));
  }, []);

  // Clear timers
  const clearTimers = useCallback(() => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
    if (doubleTapTimerRef.current) {
      clearTimeout(doubleTapTimerRef.current);
      doubleTapTimerRef.current = null;
    }
  }, []);

  // Handle touch start
  const handleTouchStart = useCallback((e) => {
    if (!enabled) return;

    const touches = getTouchInfo(e.touches);
    touchStartRef.current = touches;
    touchCurrentRef.current = touches;

    setGestureState((prev) => ({
      ...prev,
      isTouching: true,
      touchCount: touches.length,
      isPanning: false,
      isPinching: false,
      isLongPressing: false
    }));

    // Single touch - prepare for tap/long press/pan
    if (touches.length === 1) {
      panStartRef.current = { x: touches[0].x, y: touches[0].y };

      // Start long press timer
      longPressTimerRef.current = setTimeout(() => {
        if (hapticFeedback && isMobile) {
          triggerHaptic('medium');
        }

        setGestureState((prev) => ({ ...prev, isLongPressing: true }));

        onLongPress?.(e, {
          touch: touches[0],
          duration: longPressDelay
        });

        if (debug) {
          console.log('Long press detected');
        }
      }, longPressDelay);
    }

    // Two touches - prepare for pinch
    else if (touches.length === 2) {
      clearTimers();
      const distance = getDistance(touches[0], touches[1]);
      initialPinchDistanceRef.current = distance;

      setGestureState((prev) => ({
        ...prev,
        isPinching: true,
        pinchDistance: distance,
        pinchScale: 1
      }));
    }

    onTouchStart?.(e, {
      touches,
      touchCount: touches.length
    });

    if (preventDefault) {
      e.preventDefault();
    }

    if (debug) {
      console.log('Touch start:', { touchCount: touches.length, touches });
    }
  }, [
  enabled,
  getTouchInfo,
  hapticFeedback,
  isMobile,
  triggerHaptic,
  onLongPress,
  longPressDelay,
  onTouchStart,
  preventDefault,
  debug,
  getDistance]
  );

  // Handle touch move
  const handleTouchMove = useCallback((e) => {
    if (!enabled || !gestureState.isTouching) return;

    const touches = getTouchInfo(e.touches);
    touchCurrentRef.current = touches;

    // Single touch - handle pan
    if (touches.length === 1 && touchStartRef.current.length === 1) {
      const startTouch = touchStartRef.current[0];
      const currentTouch = touches[0];

      const deltaX = currentTouch.x - startTouch.x;
      const deltaY = currentTouch.y - startTouch.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      // Start panning if threshold exceeded
      if (!gestureState.isPanning && distance > panThreshold) {
        clearTimers(); // Cancel tap/long press

        setGestureState((prev) => ({
          ...prev,
          isPanning: true,
          panDistance: distance,
          isLongPressing: false
        }));

        if (debug) {
          console.log('Pan started');
        }
      }

      // Continue panning
      if (gestureState.isPanning) {
        setGestureState((prev) => ({
          ...prev,
          panDistance: distance
        }));

        onPan?.(e, {
          deltaX,
          deltaY,
          distance,
          startTouch,
          currentTouch,
          velocity: {
            x: deltaX / (Date.now() - (touchStartRef.current[0].timestamp || Date.now())),
            y: deltaY / (Date.now() - (touchStartRef.current[0].timestamp || Date.now()))
          }
        });
      }
    }

    // Two touches - handle pinch
    else if (touches.length === 2 && gestureState.isPinching) {
      const currentDistance = getDistance(touches[0], touches[1]);
      const scale = currentDistance / initialPinchDistanceRef.current;
      const center = getMidpoint(touches[0], touches[1]);

      setGestureState((prev) => ({
        ...prev,
        pinchDistance: currentDistance,
        pinchScale: scale
      }));

      onPinch?.(e, {
        scale,
        distance: currentDistance,
        center,
        touches
      });

      if (debug) {
        console.log('Pinch:', { scale, distance: currentDistance });
      }
    }

    if (preventDefault || gestureState.isPanning || gestureState.isPinching) {
      e.preventDefault();
    }
  }, [
  enabled,
  gestureState.isTouching,
  gestureState.isPanning,
  gestureState.isPinching,
  getTouchInfo,
  panThreshold,
  clearTimers,
  onPan,
  getDistance,
  getMidpoint,
  onPinch,
  preventDefault,
  debug]
  );

  // Handle touch end
  const handleTouchEnd = useCallback((e) => {
    if (!enabled) return;

    const remainingTouches = getTouchInfo(e.touches);
    const endedTouches = touchCurrentRef.current.filter(
      (current) => !remainingTouches.some((remaining) => remaining.id === current.id)
    );

    // Handle tap detection
    if (
    !gestureState.isPanning &&
    !gestureState.isPinching &&
    !gestureState.isLongPressing &&
    endedTouches.length === 1 &&
    touchStartRef.current.length === 1)
    {
      const now = Date.now();
      const timeSinceLastTap = now - lastTapTimeRef.current;

      // Double tap detection
      if (timeSinceLastTap < doubleTapDelay && tapCountRef.current === 1) {
        clearTimeout(doubleTapTimerRef.current);
        tapCountRef.current = 0;
        lastTapTimeRef.current = 0;

        if (hapticFeedback && isMobile) {
          triggerHaptic('light');
        }

        onDoubleTap?.(e, {
          touch: endedTouches[0],
          timeBetweenTaps: timeSinceLastTap
        });

        if (debug) {
          console.log('Double tap detected');
        }
      } else {
        // Single tap (with delay for double tap detection)
        tapCountRef.current = 1;
        lastTapTimeRef.current = now;

        doubleTapTimerRef.current = setTimeout(() => {
          if (tapCountRef.current === 1) {
            if (hapticFeedback && isMobile) {
              triggerHaptic('light');
            }

            onTap?.(e, {
              touch: endedTouches[0]
            });

            if (debug) {
              console.log('Single tap detected');
            }
          }
          tapCountRef.current = 0;
        }, doubleTapDelay);
      }
    }

    // Clean up timers
    clearTimers();

    // Reset state if no touches remaining
    if (remainingTouches.length === 0) {
      setGestureState({
        isTouching: false,
        isPanning: false,
        isPinching: false,
        isLongPressing: false,
        touchCount: 0,
        panDistance: 0,
        pinchScale: 1,
        pinchDistance: 0
      });

      touchStartRef.current = [];
      touchCurrentRef.current = [];
    } else {
      // Update for remaining touches
      touchStartRef.current = remainingTouches;
      touchCurrentRef.current = remainingTouches;

      setGestureState((prev) => ({
        ...prev,
        touchCount: remainingTouches.length,
        isPinching: remainingTouches.length === 2,
        isPanning: remainingTouches.length === 1 && prev.isPanning
      }));
    }

    onTouchEnd?.(e, {
      endedTouches,
      remainingTouches,
      touchCount: remainingTouches.length
    });

    if (debug) {
      console.log('Touch end:', {
        endedTouches: endedTouches.length,
        remaining: remainingTouches.length
      });
    }
  }, [
  enabled,
  gestureState.isPanning,
  gestureState.isPinching,
  gestureState.isLongPressing,
  getTouchInfo,
  doubleTapDelay,
  hapticFeedback,
  isMobile,
  triggerHaptic,
  onDoubleTap,
  onTap,
  clearTimers,
  onTouchEnd,
  debug]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimers();
    };
  }, [clearTimers]);

  return {
    // Event handlers
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,

    // Current state
    ...gestureState,

    // Utilities
    clearGestures: () => {
      clearTimers();
      setGestureState({
        isTouching: false,
        isPanning: false,
        isPinching: false,
        isLongPressing: false,
        touchCount: 0,
        panDistance: 0,
        pinchScale: 1,
        pinchDistance: 0
      });
    }
  };
};

export default useTouchGestures;