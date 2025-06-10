// TODO: i18n - processed
import React, { forwardRef, useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';

/**
 * MobileSafeArea - Component that handles safe areas for mobile devices
 * Automatically adjusts for notches, home indicators, and system UI
 */import { useTranslation } from "react-i18next";
export const MobileSafeArea = forwardRef(({
  children,
  className,
  top = true,
  bottom = true,
  left = true,
  right = true,
  fallback = true,
  onlyStandalone = false,
  ...props
}, ref) => {
  const { capabilities, isMobile } = useMobile();
  const [safeAreaInsets, setSafeAreaInsets] = useState({
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  });

  // Check if we should apply safe area
  const shouldApplySafeArea = isMobile && (!onlyStandalone || capabilities.isStandalone);

  // Detect safe area insets
  useEffect(() => {
    if (!shouldApplySafeArea) return;

    const detectSafeAreaInsets = () => {
      // Try to get CSS environment variables
      const computedStyle = getComputedStyle(document.documentElement);

      const newInsets = {
        top: parseInt(computedStyle.getPropertyValue('--safe-area-inset-top')) || (
        fallback && capabilities.isStandalone ? 44 : 0),
        bottom: parseInt(computedStyle.getPropertyValue('--safe-area-inset-bottom')) || (
        fallback && capabilities.isStandalone ? 34 : 0),
        left: parseInt(computedStyle.getPropertyValue('--safe-area-inset-left')) || 0,
        right: parseInt(computedStyle.getPropertyValue('--safe-area-inset-right')) || 0
      };

      setSafeAreaInsets(newInsets);
    };

    detectSafeAreaInsets();

    // Listen for orientation changes
    window.addEventListener('orientationchange', detectSafeAreaInsets);
    window.addEventListener('resize', detectSafeAreaInsets);

    return () => {
      window.removeEventListener('orientationchange', detectSafeAreaInsets);
      window.removeEventListener('resize', detectSafeAreaInsets);
    };
  }, [shouldApplySafeArea, capabilities.isStandalone, fallback]);

  const paddingStyle = shouldApplySafeArea ? {
    paddingTop: top ? `max(${safeAreaInsets.top}px, env(safe-area-inset-top, 0px))` : undefined,
    paddingBottom: bottom ? `max(${safeAreaInsets.bottom}px, env(safe-area-inset-bottom, 0px))` : undefined,
    paddingLeft: left ? `max(${safeAreaInsets.left}px, env(safe-area-inset-left, 0px))` : undefined,
    paddingRight: right ? `max(${safeAreaInsets.right}px, env(safe-area-inset-right, 0px))` : undefined
  } : {};

  return (
    <div
      ref={ref}
      className={className}
      style={paddingStyle}
      {...props}>

      {children}
    </div>);

});

MobileSafeArea.displayName = 'MobileSafeArea';

/**
 * SafeAreaProvider - Provides safe area context and CSS variables
 */
export const SafeAreaProvider = ({ children }) => {const { t } = useTranslation();
  const { isMobile, capabilities } = useMobile();

  useEffect(() => {
    if (!isMobile) return;

    // Set CSS custom properties for safe area insets
    const updateSafeAreaVars = () => {
      const root = document.documentElement;

      // Get safe area insets from CSS env() if available
      const testEl = document.createElement('div');
      testEl.style.position = 'fixed';
      testEl.style.top = 'env(safe-area-inset-top)';
      testEl.style.left = 'env(safe-area-inset-left)';
      testEl.style.right = 'env(safe-area-inset-right)';
      testEl.style.bottom = 'env(safe-area-inset-bottom)';
      testEl.style.visibility = 'hidden';
      document.body.appendChild(testEl);

      const computedStyle = getComputedStyle(testEl);
      const top = computedStyle.top;
      const left = computedStyle.left;
      const right = computedStyle.right;
      const bottom = computedStyle.bottom;

      document.body.removeChild(testEl);

      // Set fallback values for older browsers
      if (capabilities.isStandalone) {
        root.style.setProperty('--safe-area-inset-top', top === 'env(safe-area-inset-top)' ? '44px' : top);
        root.style.setProperty('--safe-area-inset-bottom', bottom === 'env(safe-area-inset-bottom)' ? '34px' : bottom);
        root.style.setProperty('--safe-area-inset-left', left === 'env(safe-area-inset-left)' ? '0px' : left);
        root.style.setProperty('--safe-area-inset-right', right === 'env(safe-area-inset-right)' ? '0px' : right);
      } else {
        root.style.setProperty('--safe-area-inset-top', '0px');
        root.style.setProperty('--safe-area-inset-bottom', '0px');
        root.style.setProperty('--safe-area-inset-left', '0px');
        root.style.setProperty('--safe-area-inset-right', '0px');
      }
    };

    updateSafeAreaVars();

    // Update on orientation change
    window.addEventListener('orientationchange', updateSafeAreaVars);
    window.addEventListener('resize', updateSafeAreaVars);

    return () => {
      window.removeEventListener('orientationchange', updateSafeAreaVars);
      window.removeEventListener('resize', updateSafeAreaVars);
    };
  }, [isMobile, capabilities.isStandalone]);

  return children;
};

/**
 * SafeAreaView - Full screen container with safe area handling
 */
export const SafeAreaView = forwardRef(({
  children,
  className,
  background = 'bg-background',
  ...props
}, ref) => {
  return (
    <MobileSafeArea
      ref={ref}
      className={cn(
        'min-h-screen flex flex-col',
        background,
        className
      )}
      {...props}>

      {children}
    </MobileSafeArea>);

});

SafeAreaView.displayName = 'SafeAreaView';

/**
 * SafeAreaInsets - Hook to get current safe area inset values
 */
export const useSafeAreaInsets = () => {
  const { isMobile, capabilities } = useMobile();
  const [insets, setInsets] = useState({
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  });

  useEffect(() => {
    if (!isMobile) return;

    const updateInsets = () => {
      const computedStyle = getComputedStyle(document.documentElement);

      setInsets({
        top: parseInt(computedStyle.getPropertyValue('--safe-area-inset-top')) || 0,
        bottom: parseInt(computedStyle.getPropertyValue('--safe-area-inset-bottom')) || 0,
        left: parseInt(computedStyle.getPropertyValue('--safe-area-inset-left')) || 0,
        right: parseInt(computedStyle.getPropertyValue('--safe-area-inset-right')) || 0
      });
    };

    updateInsets();

    window.addEventListener('orientationchange', updateInsets);
    window.addEventListener('resize', updateInsets);

    return () => {
      window.removeEventListener('orientationchange', updateInsets);
      window.removeEventListener('resize', updateInsets);
    };
  }, [isMobile]);

  return insets;
};

/**
 * SafeAreaBottom - Component for bottom safe area spacing
 */
export const SafeAreaBottom = forwardRef(({
  className,
  minHeight = 16,
  ...props
}, ref) => {
  const insets = useSafeAreaInsets();

  return (
    <div
      ref={ref}
      className={className}
      style={{
        height: Math.max(insets.bottom, minHeight),
        minHeight: minHeight
      }}
      {...props} />);


});

SafeAreaBottom.displayName = 'SafeAreaBottom';

/**
 * SafeAreaTop - Component for top safe area spacing
 */
export const SafeAreaTop = forwardRef(({
  className,
  minHeight = 16,
  ...props
}, ref) => {
  const insets = useSafeAreaInsets();

  return (
    <div
      ref={ref}
      className={className}
      style={{
        height: Math.max(insets.top, minHeight),
        minHeight: minHeight
      }}
      {...props} />);


});

SafeAreaTop.displayName = 'SafeAreaTop';

export default MobileSafeArea;