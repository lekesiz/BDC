// TODO: i18n - processed
import { useState, useEffect } from 'react';
/**
 * Custom hook for responsive design
 * @param {string} query - Media query string
 * @returns {boolean} - Whether the media query matches
 */import { useTranslation } from "react-i18next";
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(query);
    // Set initial value
    setMatches(media.matches);
    // Create event listener
    const listener = (event) => {
      setMatches(event.matches);
    };
    // Add event listener
    if (media.addListener) {
      media.addListener(listener);
    } else {
      media.addEventListener('change', listener);
    }
    // Clean up
    return () => {
      if (media.removeListener) {
        media.removeListener(listener);
      } else {
        media.removeEventListener('change', listener);
      }
    };
  }, [query]);
  return matches;
};
// Predefined breakpoints matching Tailwind CSS
export const useBreakpoint = () => {
  const isMobile = useMediaQuery('(max-width: 639px)'); // < 640px
  const isSmall = useMediaQuery('(min-width: 640px) and (max-width: 767px)'); // 640px - 767px
  const isMedium = useMediaQuery('(min-width: 768px) and (max-width: 1023px)'); // 768px - 1023px
  const isLarge = useMediaQuery('(min-width: 1024px) and (max-width: 1279px)'); // 1024px - 1279px
  const isXLarge = useMediaQuery('(min-width: 1280px)'); // >= 1280px
  // Common mobile breakpoints
  const isPhone = useMediaQuery('(max-width: 414px)'); // iPhone Plus
  const isPhoneSmall = useMediaQuery('(max-width: 375px)'); // iPhone 6/7/8
  const isPhoneTiny = useMediaQuery('(max-width: 320px)'); // iPhone SE
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)');
  const isDesktop = useMediaQuery('(min-width: 1024px)');
  return {
    isMobile,
    isSmall,
    isMedium,
    isLarge,
    isXLarge,
    isPhone,
    isPhoneSmall,
    isPhoneTiny,
    isTablet,
    isDesktop,
    currentBreakpoint: isXLarge ? 'xl' : isLarge ? 'lg' : isMedium ? 'md' : isSmall ? 'sm' : 'xs'
  };
};
// Hook for detecting touch devices
export const useTouchDevice = () => {
  const [isTouch, setIsTouch] = useState(false);
  useEffect(() => {
    const checkTouch = () => {
      setIsTouch('ontouchstart' in window || navigator.maxTouchPoints > 0);
    };
    checkTouch();
    window.addEventListener('resize', checkTouch);
    return () => {
      window.removeEventListener('resize', checkTouch);
    };
  }, []);
  return isTouch;
};