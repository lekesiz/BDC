// TODO: i18n - processed
import { useState, useEffect, useRef } from 'react';
/**
 * Hook for detecting swipe gestures on touch devices
 * @param {Object} config - Configuration object
 * @param {Function} config.onSwipeLeft - Callback for left swipe
 * @param {Function} config.onSwipeRight - Callback for right swipe
 * @param {Function} config.onSwipeUp - Callback for up swipe
 * @param {Function} config.onSwipeDown - Callback for down swipe
 * @param {number} config.threshold - Minimum distance for swipe detection (default: 50)
 * @param {number} config.timeout - Maximum time for swipe gesture (default: 500ms)
 * @returns {Object} - Touch event handlers to spread on element
 */import { useTranslation } from "react-i18next";
export const useSwipeGesture = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  timeout = 500,
  enabled = true
} = {}) => {
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  const [touchStartTime, setTouchStartTime] = useState(null);
  const handleTouchStart = (e) => {
    if (!enabled) return;
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY
    });
    setTouchStartTime(Date.now());
  };
  const handleTouchMove = (e) => {
    if (!enabled) return;
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY
    });
  };
  const handleTouchEnd = () => {
    if (!enabled || !touchStart || !touchEnd) return;
    const touchDuration = Date.now() - touchStartTime;
    if (touchDuration > timeout) return; // Gesture took too long
    const distanceX = touchStart.x - touchEnd.x;
    const distanceY = touchStart.y - touchEnd.y;
    const absDistanceX = Math.abs(distanceX);
    const absDistanceY = Math.abs(distanceY);
    // Determine if this was a horizontal or vertical swipe
    const isHorizontalSwipe = absDistanceX > absDistanceY;
    if (isHorizontalSwipe && absDistanceX > threshold) {
      if (distanceX > 0 && onSwipeLeft) {
        onSwipeLeft();
      } else if (distanceX < 0 && onSwipeRight) {
        onSwipeRight();
      }
    } else if (!isHorizontalSwipe && absDistanceY > threshold) {
      if (distanceY > 0 && onSwipeUp) {
        onSwipeUp();
      } else if (distanceY < 0 && onSwipeDown) {
        onSwipeDown();
      }
    }
    // Reset values
    setTouchStart(null);
    setTouchEnd(null);
    setTouchStartTime(null);
  };
  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd
  };
};
/**
 * Hook for carousel/slider swipe functionality
 * @param {Object} config - Configuration object
 * @param {number} config.totalItems - Total number of items
 * @param {number} config.currentIndex - Current active index
 * @param {Function} config.onChange - Callback when index changes
 * @param {boolean} config.loop - Whether to loop at ends (default: false)
 * @returns {Object} - Current index and swipe handlers
 */
export const useSwipeCarousel = ({
  totalItems,
  currentIndex = 0,
  onChange,
  loop = false,
  enabled = true
}) => {
  const [index, setIndex] = useState(currentIndex);
  useEffect(() => {
    setIndex(currentIndex);
  }, [currentIndex]);
  const goToNext = () => {
    const nextIndex = index + 1;
    if (nextIndex < totalItems) {
      setIndex(nextIndex);
      onChange && onChange(nextIndex);
    } else if (loop) {
      setIndex(0);
      onChange && onChange(0);
    }
  };
  const goToPrevious = () => {
    const prevIndex = index - 1;
    if (prevIndex >= 0) {
      setIndex(prevIndex);
      onChange && onChange(prevIndex);
    } else if (loop) {
      const lastIndex = totalItems - 1;
      setIndex(lastIndex);
      onChange && onChange(lastIndex);
    }
  };
  const swipeHandlers = useSwipeGesture({
    onSwipeLeft: goToNext,
    onSwipeRight: goToPrevious,
    enabled
  });
  return {
    currentIndex: index,
    ...swipeHandlers,
    goToNext,
    goToPrevious
  };
};