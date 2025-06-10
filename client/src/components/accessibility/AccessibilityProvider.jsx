import React, { createContext, useContext, useState, useEffect } from 'react';
import { useLocalStorage } from '@/hooks/useLocalStorage';

// Accessibility Context
const AccessibilityContext = createContext();

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

// Accessibility Settings
const defaultSettings = {
  // Visual Settings
  fontSize: 'medium', // small, medium, large, extra-large
  contrast: 'normal', // normal, high, dark
  colorBlindMode: 'none', // none, protanopia, deuteranopia, tritanopia
  reducedMotion: false,
  focusIndicators: true,
  underlineLinks: false,
  
  // Audio Settings
  soundEffects: true,
  voiceAnnouncements: false,
  audioDescriptions: false,
  
  // Navigation Settings
  keyboardNavigation: true,
  skipLinks: true,
  breadcrumbs: true,
  headingNavigation: true,
  
  // Content Settings
  simplifiedUI: false,
  autoplay: false,
  tooltips: true,
  alternativeText: true,
  
  // Language and Reading
  language: 'en',
  readingMode: false,
  dyslexiaFont: false,
  lineHeight: 'normal', // normal, relaxed, loose
  letterSpacing: 'normal', // normal, wide, wider
  
  // Screen Reader Support
  screenReader: false,
  ariaLive: 'polite', // off, polite, assertive
  roleDescriptions: true,
  landmarkLabels: true
};

export const AccessibilityProvider = ({ children }) => {
  const [settings, setSettings] = useLocalStorage('accessibility-settings', defaultSettings);
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [announcement, setAnnouncement] = useState('');

  // Apply accessibility settings to document
  useEffect(() => {
    const root = document.documentElement;
    
    // Font size
    const fontSizeMap = {
      small: '14px',
      medium: '16px', 
      large: '18px',
      'extra-large': '20px'
    };
    root.style.setProperty('--base-font-size', fontSizeMap[settings.fontSize]);
    
    // Line height
    const lineHeightMap = {
      normal: '1.5',
      relaxed: '1.75',
      loose: '2'
    };
    root.style.setProperty('--line-height', lineHeightMap[settings.lineHeight]);
    
    // Letter spacing
    const letterSpacingMap = {
      normal: '0',
      wide: '0.025em',
      wider: '0.05em'
    };
    root.style.setProperty('--letter-spacing', letterSpacingMap[settings.letterSpacing]);
    
    // Contrast and theme
    root.classList.toggle('high-contrast', settings.contrast === 'high');
    root.classList.toggle('dark-theme', settings.contrast === 'dark');
    root.classList.toggle('reduced-motion', settings.reducedMotion);
    root.classList.toggle('underline-links', settings.underlineLinks);
    root.classList.toggle('dyslexia-font', settings.dyslexiaFont);
    root.classList.toggle('simplified-ui', settings.simplifiedUI);
    root.classList.toggle('reading-mode', settings.readingMode);
    
    // Color blind mode
    root.className = root.className.replace(/colorblind-\w+/g, '');
    if (settings.colorBlindMode !== 'none') {
      root.classList.add(`colorblind-${settings.colorBlindMode}`);
    }
    
  }, [settings]);

  // Keyboard navigation setup
  useEffect(() => {
    if (!settings.keyboardNavigation) return;

    const handleKeyDown = (e) => {
      // Skip links (Alt + S)
      if (e.altKey && e.key === 's' && settings.skipLinks) {
        e.preventDefault();
        const skipLink = document.querySelector('[data-skip-link]');
        if (skipLink) {
          skipLink.focus();
        }
      }
      
      // Heading navigation (Alt + H)
      if (e.altKey && e.key === 'h' && settings.headingNavigation) {
        e.preventDefault();
        navigateToNextHeading();
      }
      
      // Focus trap in modals
      if (e.key === 'Tab') {
        const modal = document.querySelector('[data-modal-open]');
        if (modal) {
          trapFocus(e, modal);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [settings.keyboardNavigation, settings.skipLinks, settings.headingNavigation]);

  // Screen reader announcements
  useEffect(() => {
    if (settings.voiceAnnouncements && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(announcement);
      utterance.rate = 0.8;
      utterance.volume = 0.8;
      
      if (announcement) {
        speechSynthesis.speak(utterance);
      }
    }
  }, [announcement, settings.voiceAnnouncements]);

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
  };

  const announce = (message, priority = 'polite') => {
    setAnnouncement(message);
    
    // Also update aria-live region
    const liveRegion = document.getElementById('aria-live-region');
    if (liveRegion) {
      liveRegion.setAttribute('aria-live', priority);
      liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  };

  const navigateToNextHeading = () => {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const currentFocus = document.activeElement;
    
    let nextHeading = null;
    let foundCurrent = false;
    
    for (const heading of headings) {
      if (foundCurrent) {
        nextHeading = heading;
        break;
      }
      if (heading === currentFocus) {
        foundCurrent = true;
      }
    }
    
    if (!nextHeading && headings.length > 0) {
      nextHeading = headings[0]; // Go to first heading if none found
    }
    
    if (nextHeading) {
      nextHeading.setAttribute('tabindex', '-1');
      nextHeading.focus();
      announce(`Navigated to heading: ${nextHeading.textContent}`);
    }
  };

  const trapFocus = (e, container) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  const getFontSizeClass = () => {
    const sizeMap = {
      small: 'text-sm',
      medium: 'text-base',
      large: 'text-lg',
      'extra-large': 'text-xl'
    };
    return sizeMap[settings.fontSize] || 'text-base';
  };

  const getContrastClass = () => {
    switch (settings.contrast) {
      case 'high':
        return 'high-contrast';
      case 'dark':
        return 'dark-theme';
      default:
        return '';
    }
  };

  const value = {
    settings,
    updateSetting,
    updateSettings,
    resetSettings,
    announce,
    navigateToNextHeading,
    getFontSizeClass,
    getContrastClass,
    isHighContrast: settings.contrast === 'high'
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
      
      {/* ARIA Live Region for Announcements */}
      <div
        id="aria-live-region"
        aria-live={settings.ariaLive}
        aria-atomic="true"
        className="sr-only"
      />
      
      {/* Skip Links */}
      {settings.skipLinks && (
        <div className="skip-links">
          <a
            href="#main-content"
            data-skip-link
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded z-50"
          >
            Skip to main content
          </a>
          <a
            href="#navigation"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-32 bg-blue-600 text-white px-4 py-2 rounded z-50"
          >
            Skip to navigation
          </a>
        </div>
      )}
    </AccessibilityContext.Provider>
  );
};

// Higher-order component for accessibility features
export const withAccessibility = (Component) => {
  return React.forwardRef((props, ref) => {
    const { settings, getFontSizeClass, getContrastClass } = useAccessibility();
    
    const accessibilityProps = {
      ...props,
      'data-font-size': settings.fontSize,
      'data-contrast': settings.contrast,
      className: `${props.className || ''} ${getFontSizeClass()} ${getContrastClass()}`.trim(),
      ref
    };
    
    return <Component {...accessibilityProps} />;
  });
};

// Accessibility utility functions
export const accessibilityUtils = {
  // Focus management
  focusElement: (selector) => {
    const element = document.querySelector(selector);
    if (element) {
      element.focus();
      return true;
    }
    return false;
  },
  
  // ARIA attributes
  setAriaLabel: (selector, label) => {
    const element = document.querySelector(selector);
    if (element) {
      element.setAttribute('aria-label', label);
    }
  },
  
  setAriaExpanded: (selector, expanded) => {
    const element = document.querySelector(selector);
    if (element) {
      element.setAttribute('aria-expanded', expanded.toString());
    }
  },
  
  // Color contrast checking
  checkContrast: (foreground, background) => {
    // Simple contrast ratio calculation
    const getRGB = (color) => {
      // This is a simplified version - in production, use a proper color library
      if (color.startsWith('#')) {
        const hex = color.slice(1);
        return {
          r: parseInt(hex.slice(0, 2), 16),
          g: parseInt(hex.slice(2, 4), 16),
          b: parseInt(hex.slice(4, 6), 16)
        };
      }
      return { r: 0, g: 0, b: 0 };
    };
    
    const getLuminance = (rgb) => {
      const { r, g, b } = rgb;
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };
    
    const fg = getLuminance(getRGB(foreground));
    const bg = getLuminance(getRGB(background));
    const ratio = (Math.max(fg, bg) + 0.05) / (Math.min(fg, bg) + 0.05);
    
    return {
      ratio,
      aa: ratio >= 4.5,
      aaa: ratio >= 7
    };
  },
  
  // Text alternatives
  generateAltText: (element) => {
    // Generate appropriate alt text based on element context
    if (element.tagName === 'IMG') {
      return element.src.split('/').pop().split('.')[0].replace(/[-_]/g, ' ');
    }
    return '';
  }
};

export default AccessibilityProvider;