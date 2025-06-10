// TODO: i18n - processed
// Breakpoint Hook
import { useState, useEffect } from 'react';
import { breakpoints } from '../tokens/breakpoints';import { useTranslation } from "react-i18next";

export const useBreakpoint = () => {
  const [currentBreakpoint, setCurrentBreakpoint] = useState(getBreakpoint());
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  function getBreakpoint() {
    const width = window.innerWidth;

    if (width >= breakpoints.values['2xl']) return '2xl';
    if (width >= breakpoints.values.xl) return 'xl';
    if (width >= breakpoints.values.lg) return 'lg';
    if (width >= breakpoints.values.md) return 'md';
    if (width >= breakpoints.values.sm) return 'sm';
    return 'xs';
  }

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
      setCurrentBreakpoint(getBreakpoint());
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isBreakpoint = (bp) => {
    const breakpointOrder = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
    const currentIndex = breakpointOrder.indexOf(currentBreakpoint);
    const targetIndex = breakpointOrder.indexOf(bp);
    return currentIndex >= targetIndex;
  };

  const isMobile = currentBreakpoint === 'xs' || currentBreakpoint === 'sm';
  const isTablet = currentBreakpoint === 'md';
  const isDesktop = currentBreakpoint === 'lg' || currentBreakpoint === 'xl' || currentBreakpoint === '2xl';

  return {
    currentBreakpoint,
    windowSize,
    isBreakpoint,
    isMobile,
    isTablet,
    isDesktop,
    // Utility functions
    isXs: () => currentBreakpoint === 'xs',
    isSm: () => currentBreakpoint === 'sm',
    isMd: () => currentBreakpoint === 'md',
    isLg: () => currentBreakpoint === 'lg',
    isXl: () => currentBreakpoint === 'xl',
    is2xl: () => currentBreakpoint === '2xl',
    // Range checks
    isSmUp: () => isBreakpoint('sm'),
    isMdUp: () => isBreakpoint('md'),
    isLgUp: () => isBreakpoint('lg'),
    isXlUp: () => isBreakpoint('xl'),
    is2xlUp: () => isBreakpoint('2xl'),
    // Specific ranges
    isSmToMd: () => currentBreakpoint === 'sm' || currentBreakpoint === 'md',
    isMdToLg: () => currentBreakpoint === 'md' || currentBreakpoint === 'lg',
    isLgToXl: () => currentBreakpoint === 'lg' || currentBreakpoint === 'xl'
  };
};

// Media query hook
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);

    const handleChange = (e) => {
      setMatches(e.matches);
    };

    // Add listener
    mediaQuery.addEventListener('change', handleChange);

    // Initial check
    setMatches(mediaQuery.matches);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [query]);

  return matches;
};

// Responsive value hook
export const useResponsive = (values) => {
  const breakpoint = useBreakpoint();

  if (typeof values !== 'object') {
    return values;
  }

  // If values is an object with breakpoint keys
  const breakpointOrder = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
  const currentIndex = breakpointOrder.indexOf(breakpoint.currentBreakpoint);

  // Find the value for current or nearest smaller breakpoint
  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpointOrder[i];
    if (values[bp] !== undefined) {
      return values[bp];
    }
  }

  // Return default or first value
  return values.default || values.xs || Object.values(values)[0];
};