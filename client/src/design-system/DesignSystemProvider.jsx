// TODO: i18n - processed
// Design System Provider
import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeProvider } from './themes/ThemeProvider';
import { AnimatePresence, MotionConfig } from 'framer-motion';
import { a11yUtils } from './accessibility/a11yUtils';
import './design-system.css';import { useTranslation } from "react-i18next";

const DesignSystemContext = createContext();

export const DesignSystemProvider = ({
  children,
  theme = 'light',
  reducedMotion = false,
  highContrast = false,
  focusVisible = true,
  rtl = false,
  locale = 'en',
  ...props
}) => {const { t } = useTranslation();
  const [config, setConfig] = useState({
    reducedMotion,
    highContrast,
    focusVisible,
    rtl,
    locale
  });

  // Apply global configurations
  useEffect(() => {
    const root = document.documentElement;

    // RTL support
    root.setAttribute('dir', config.rtl ? 'rtl' : 'ltr');

    // Language
    root.setAttribute('lang', config.locale);

    // Accessibility classes
    root.classList.toggle('reduced-motion', config.reducedMotion);
    root.classList.toggle('high-contrast', config.highContrast);
    root.classList.toggle('focus-visible', config.focusVisible);

    // Check system preferences
    if (window.matchMedia) {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
      const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');

      const handleMotionChange = (e) => {
        setConfig((prev) => ({ ...prev, reducedMotion: e.matches }));
      };

      const handleContrastChange = (e) => {
        setConfig((prev) => ({ ...prev, highContrast: e.matches }));
      };

      prefersReducedMotion.addEventListener('change', handleMotionChange);
      prefersHighContrast.addEventListener('change', handleContrastChange);

      return () => {
        prefersReducedMotion.removeEventListener('change', handleMotionChange);
        prefersHighContrast.removeEventListener('change', handleContrastChange);
      };
    }
  }, [config]);

  // Skip links for accessibility
  useEffect(() => {
    const handleSkipLinks = (e) => {
      if (e.key === 'Tab' && !document.body.classList.contains('user-is-tabbing')) {
        document.body.classList.add('user-is-tabbing');
      }
    };

    const handleMouseDown = () => {
      document.body.classList.remove('user-is-tabbing');
    };

    window.addEventListener('keydown', handleSkipLinks);
    window.addEventListener('mousedown', handleMouseDown);

    return () => {
      window.removeEventListener('keydown', handleSkipLinks);
      window.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  const value = {
    config,
    setConfig,
    updateConfig: (updates) => setConfig((prev) => ({ ...prev, ...updates })),
    a11yUtils
  };

  return (
    <DesignSystemContext.Provider value={value}>
      <ThemeProvider defaultTheme={theme}>
        <MotionConfig reducedMotion={config.reducedMotion ? 'always' : 'never'}>
          <AnimatePresence mode="wait">
            {children}
          </AnimatePresence>
        </MotionConfig>
      </ThemeProvider>
    </DesignSystemContext.Provider>);

};

export const useDesignSystem = () => {
  const context = useContext(DesignSystemContext);
  if (!context) {
    throw new Error('useDesignSystem must be used within a DesignSystemProvider');
  }
  return context;
};