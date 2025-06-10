// TODO: i18n - processed
import { useState, useCallback, useRef, useEffect } from 'react';
import { useMobile } from '../components/MobileProvider';

/**
 * Advanced pinch-to-zoom gesture hook with smooth animations and constraints
 */import { useTranslation } from "react-i18next";
export const usePinchZoom = ({
  minZoom = 0.5,
  maxZoom = 3,
  initialZoom = 1,
  zoomSpeed = 1,
  doubleTapZoom = 2,
  animationDuration = 300,
  constrainToContainer = true,
  enabled = true,
  onZoomChange,
  onZoomStart,
  onZoomEnd,
  hapticFeedback = true,
  debug = false
} = {}) => {
  const { hapticFeedback: triggerHaptic, isMobile, shouldReduceAnimations } = useMobile();

  const [zoomState, setZoomState] = useState({
    scale: initialZoom,
    translateX: 0,
    translateY: 0,
    isZooming: false,
    isAnimating: false
  });

  const containerRef = useRef(null);
  const contentRef = useRef(null);
  const gestureRef = useRef({
    startDistance: 0,
    startScale: 1,
    startCenter: { x: 0, y: 0 },
    startTranslate: { x: 0, y: 0 },
    lastTouchTime: 0,
    touchCount: 0
  });

  // Calculate distance between two touches
  const getDistance = useCallback((touch1, touch2) => {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  // Calculate center point between two touches
  const getCenter = useCallback((touch1, touch2) => {
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  }, []);

  // Get container bounds
  const getContainerBounds = useCallback(() => {
    if (!containerRef.current) return { width: 0, height: 0 };
    const rect = containerRef.current.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  }, []);

  // Get content bounds
  const getContentBounds = useCallback(() => {
    if (!contentRef.current) return { width: 0, height: 0 };
    const rect = contentRef.current.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  }, []);

  // Constrain translation to keep content within container
  const constrainTranslation = useCallback((translateX, translateY, scale) => {
    if (!constrainToContainer) return { x: translateX, y: translateY };

    const containerBounds = getContainerBounds();
    const contentBounds = getContentBounds();

    const scaledWidth = contentBounds.width * scale;
    const scaledHeight = contentBounds.height * scale;

    // Calculate maximum translation bounds
    const maxTranslateX = Math.max(0, (scaledWidth - containerBounds.width) / 2);
    const maxTranslateY = Math.max(0, (scaledHeight - containerBounds.height) / 2);

    return {
      x: Math.max(-maxTranslateX, Math.min(maxTranslateX, translateX)),
      y: Math.max(-maxTranslateY, Math.min(maxTranslateY, translateY))
    };
  }, [constrainToContainer, getContainerBounds, getContentBounds]);

  // Constrain zoom level
  const constrainZoom = useCallback((scale) => {
    return Math.max(minZoom, Math.min(maxZoom, scale));
  }, [minZoom, maxZoom]);

  // Update zoom state with constraints
  const updateZoom = useCallback((scale, translateX, translateY, animate = false) => {
    const constrainedScale = constrainZoom(scale);
    const constrainedTranslate = constrainTranslation(translateX, translateY, constrainedScale);

    setZoomState((prev) => ({
      ...prev,
      scale: constrainedScale,
      translateX: constrainedTranslate.x,
      translateY: constrainedTranslate.y,
      isAnimating: animate
    }));

    onZoomChange?.({
      scale: constrainedScale,
      translateX: constrainedTranslate.x,
      translateY: constrainedTranslate.y
    });

    if (debug) {
      console.log('Zoom updated:', {
        scale: constrainedScale,
        translateX: constrainedTranslate.x,
        translateY: constrainedTranslate.y
      });
    }
  }, [constrainZoom, constrainTranslation, onZoomChange, debug]);

  // Handle touch start
  const handleTouchStart = useCallback((e) => {
    if (!enabled) return;

    const touches = e.touches;
    gestureRef.current.touchCount = touches.length;
    gestureRef.current.lastTouchTime = Date.now();

    if (touches.length === 2) {
      // Start pinch gesture
      const distance = getDistance(touches[0], touches[1]);
      const center = getCenter(touches[0], touches[1]);

      gestureRef.current.startDistance = distance;
      gestureRef.current.startScale = zoomState.scale;
      gestureRef.current.startCenter = center;
      gestureRef.current.startTranslate = {
        x: zoomState.translateX,
        y: zoomState.translateY
      };

      setZoomState((prev) => ({ ...prev, isZooming: true }));
      onZoomStart?.();

      if (debug) {
        console.log('Pinch started:', { distance, center, scale: zoomState.scale });
      }

      e.preventDefault();
    }
  }, [enabled, getDistance, getCenter, zoomState.scale, zoomState.translateX, zoomState.translateY, onZoomStart, debug]);

  // Handle touch move
  const handleTouchMove = useCallback((e) => {
    if (!enabled || !zoomState.isZooming || e.touches.length !== 2) return;

    const touches = e.touches;
    const currentDistance = getDistance(touches[0], touches[1]);
    const currentCenter = getCenter(touches[0], touches[1]);

    // Calculate new scale
    const scaleChange = currentDistance / gestureRef.current.startDistance * zoomSpeed;
    const newScale = gestureRef.current.startScale * scaleChange;

    // Calculate translation to keep zoom centered on pinch center
    const containerBounds = getContainerBounds();
    const centerX = currentCenter.x - containerBounds.width / 2;
    const centerY = currentCenter.y - containerBounds.height / 2;

    const scaleDelta = newScale - gestureRef.current.startScale;
    const translateX = gestureRef.current.startTranslate.x - centerX * scaleDelta;
    const translateY = gestureRef.current.startTranslate.y - centerY * scaleDelta;

    updateZoom(newScale, translateX, translateY);

    e.preventDefault();
  }, [enabled, zoomState.isZooming, getDistance, getCenter, zoomSpeed, getContainerBounds, updateZoom]);

  // Handle touch end
  const handleTouchEnd = useCallback((e) => {
    if (!enabled) return;

    const now = Date.now();
    const timeSinceStart = now - gestureRef.current.lastTouchTime;

    // Handle double tap to zoom
    if (
    e.touches.length === 0 &&
    gestureRef.current.touchCount === 1 &&
    timeSinceStart < 300 &&
    !zoomState.isZooming)
    {
      const lastTap = gestureRef.current.lastTouchTime;
      gestureRef.current.lastTouchTime = now;

      if (now - lastTap < 300) {
        // Double tap detected
        const targetScale = zoomState.scale === initialZoom ? doubleTapZoom : initialZoom;

        if (hapticFeedback && isMobile) {
          triggerHaptic('medium');
        }

        updateZoom(targetScale, 0, 0, !shouldReduceAnimations);

        if (debug) {
          console.log('Double tap zoom:', { from: zoomState.scale, to: targetScale });
        }

        // Reset animation after duration
        if (!shouldReduceAnimations) {
          setTimeout(() => {
            setZoomState((prev) => ({ ...prev, isAnimating: false }));
          }, animationDuration);
        }
      }
    }

    // End pinch gesture
    if (zoomState.isZooming) {
      setZoomState((prev) => ({ ...prev, isZooming: false }));
      onZoomEnd?.({
        scale: zoomState.scale,
        translateX: zoomState.translateX,
        translateY: zoomState.translateY
      });

      if (debug) {
        console.log('Pinch ended:', { scale: zoomState.scale });
      }
    }

    gestureRef.current.touchCount = e.touches.length;
  }, [
  enabled,
  zoomState.isZooming,
  zoomState.scale,
  zoomState.translateX,
  zoomState.translateY,
  initialZoom,
  doubleTapZoom,
  hapticFeedback,
  isMobile,
  triggerHaptic,
  updateZoom,
  shouldReduceAnimations,
  animationDuration,
  onZoomEnd,
  debug]
  );

  // Programmatic zoom functions
  const zoomIn = useCallback((factor = 1.5, animate = true) => {
    const newScale = zoomState.scale * factor;
    updateZoom(newScale, zoomState.translateX, zoomState.translateY, animate);

    if (animate && !shouldReduceAnimations) {
      setTimeout(() => {
        setZoomState((prev) => ({ ...prev, isAnimating: false }));
      }, animationDuration);
    }
  }, [zoomState.scale, zoomState.translateX, zoomState.translateY, updateZoom, shouldReduceAnimations, animationDuration]);

  const zoomOut = useCallback((factor = 1.5, animate = true) => {
    const newScale = zoomState.scale / factor;
    updateZoom(newScale, zoomState.translateX, zoomState.translateY, animate);

    if (animate && !shouldReduceAnimations) {
      setTimeout(() => {
        setZoomState((prev) => ({ ...prev, isAnimating: false }));
      }, animationDuration);
    }
  }, [zoomState.scale, zoomState.translateX, zoomState.translateY, updateZoom, shouldReduceAnimations, animationDuration]);

  const resetZoom = useCallback((animate = true) => {
    updateZoom(initialZoom, 0, 0, animate);

    if (animate && !shouldReduceAnimations) {
      setTimeout(() => {
        setZoomState((prev) => ({ ...prev, isAnimating: false }));
      }, animationDuration);
    }
  }, [initialZoom, updateZoom, shouldReduceAnimations, animationDuration]);

  const setZoom = useCallback((scale, translateX = 0, translateY = 0, animate = true) => {
    updateZoom(scale, translateX, translateY, animate);

    if (animate && !shouldReduceAnimations) {
      setTimeout(() => {
        setZoomState((prev) => ({ ...prev, isAnimating: false }));
      }, animationDuration);
    }
  }, [updateZoom, shouldReduceAnimations, animationDuration]);

  // Get transform styles
  const getTransformStyles = useCallback(() => {
    const { scale, translateX, translateY, isAnimating } = zoomState;

    return {
      transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
      transformOrigin: 'center center',
      transition: isAnimating && !shouldReduceAnimations ?
      `transform ${animationDuration}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)` :
      'none'
    };
  }, [zoomState, shouldReduceAnimations, animationDuration]);

  return {
    // Refs for container and content
    containerRef,
    contentRef,

    // Event handlers
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,

    // Current state
    ...zoomState,

    // Transform styles
    transformStyles: getTransformStyles(),

    // Control functions
    zoomIn,
    zoomOut,
    resetZoom,
    setZoom,

    // Utility functions
    canZoomIn: zoomState.scale < maxZoom,
    canZoomOut: zoomState.scale > minZoom,
    isZoomedIn: zoomState.scale > initialZoom,
    isZoomedOut: zoomState.scale < initialZoom,
    zoomLevel: zoomState.scale / initialZoom
  };
};

export default usePinchZoom;