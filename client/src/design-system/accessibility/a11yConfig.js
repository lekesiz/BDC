// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // WCAG 2.1 Compliance Configuration
export const a11yConfig = {
  // Color contrast requirements
  contrast: {
    normal: {
      AA: 4.5,
      AAA: 7
    },
    large: {
      AA: 3,
      AAA: 4.5
    }
  },

  // Focus indicators
  focus: {
    outlineWidth: '3px',
    outlineStyle: 'solid',
    outlineColor: 'var(--color-interactive-focus)',
    outlineOffset: '2px'
  },

  // Keyboard navigation
  keyboard: {
    tabIndex: {
      interactive: 0,
      programmatic: -1,
      disabled: -1
    },
    shortcuts: {
      skipToMain: 'Alt+M',
      skipToNav: 'Alt+N',
      skipToSearch: 'Alt+S',
      openMenu: 'Alt+O',
      closeModal: 'Escape'
    }
  },

  // ARIA attributes
  aria: {
    landmarks: {
      main: 'main',
      navigation: 'navigation',
      banner: 'banner',
      contentinfo: 'contentinfo',
      complementary: 'complementary',
      search: 'search'
    },
    liveRegions: {
      polite: 'polite',
      assertive: 'assertive',
      off: 'off'
    },
    states: {
      expanded: 'aria-expanded',
      selected: 'aria-selected',
      checked: 'aria-checked',
      pressed: 'aria-pressed',
      current: 'aria-current',
      hidden: 'aria-hidden',
      disabled: 'aria-disabled'
    }
  },

  // Animation preferences
  motion: {
    reducedMotion: '@media (prefers-reduced-motion: reduce)',
    noPreference: '@media (prefers-reduced-motion: no-preference)'
  },

  // Screen reader announcements
  announcements: {
    loading: 'Loading content',
    loaded: 'Content loaded',
    error: 'An error occurred',
    success: 'Action completed successfully',
    formError: 'Please fix the errors in the form',
    required: 'This field is required',
    characterCount: (current, max) => `${current} of ${max} characters`,
    itemsSelected: (count) => `${count} items selected`,
    pageChange: (page) => `Page ${page} loaded`
  },

  // Touch target sizes (WCAG 2.1 Level AAA)
  touchTargets: {
    minimum: '44px',
    recommended: '48px'
  },

  // Time limits
  timeLimits: {
    toastDuration: 5000,
    sessionWarning: 120000, // 2 minutes before timeout
    minimumReadTime: 20 // seconds per 100 words
  },

  // Form validation
  validation: {
    patterns: {
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      phone: /^\+?[\d\s-()]+$/,
      url: /^https?:\/\/.+$/
    },
    messages: {
      required: 'This field is required',
      email: 'Please enter a valid email address',
      phone: 'Please enter a valid phone number',
      url: 'Please enter a valid URL',
      minLength: (min) => `Must be at least ${min} characters`,
      maxLength: (max) => `Must be no more than ${max} characters`,
      pattern: 'Please match the requested format'
    }
  },

  // Semantic HTML elements
  semantics: {
    headingLevels: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    interactiveElements: ['a', 'button', 'input', 'select', 'textarea'],
    landmarkElements: ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
  }
};