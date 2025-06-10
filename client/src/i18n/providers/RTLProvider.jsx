// TODO: i18n - processed
/**
 * RTL Provider Component
 * Manages Right-to-Left layout support for Arabic and Hebrew languages
 */

import React, { createContext, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

// RTL Context
export const RTLContext = createContext({
  isRTL: false,
  direction: 'ltr',
  alignment: 'left'
});

// RTL CSS styles injection
const injectRTLStyles = () => {
  if (document.getElementById('rtl-styles')) return;
  
  const style = document.createElement('style');
  style.id = 'rtl-styles';
  style.textContent = `
    /* RTL specific styles */
    [dir="rtl"] {
      /* Typography adjustments */
      text-align: right;
      
      /* Flexbox adjustments */
      .flex-row {
        flex-direction: row-reverse;
      }
      
      /* Grid adjustments */
      .grid {
        direction: rtl;
      }
      
      /* Margin and padding adjustments */
      .ml-auto {
        margin-left: 0 !important;
        margin-right: auto !important;
      }
      
      .mr-auto {
        margin-right: 0 !important;
        margin-left: auto !important;
      }
      
      /* Border adjustments */
      .border-l {
        border-left: none !important;
        border-right: 1px solid var(--border-color, #e5e7eb) !important;
      }
      
      .border-r {
        border-right: none !important;
        border-left: 1px solid var(--border-color, #e5e7eb) !important;
      }
      
      /* Form adjustments */
      input[type="text"],
      input[type="email"],
      input[type="password"],
      input[type="search"],
      textarea {
        text-align: right;
        direction: rtl;
      }
      
      input[type="number"],
      input[type="tel"] {
        text-align: left;
        direction: ltr;
      }
      
      /* Select adjustments */
      select {
        background-position: left 0.5rem center;
        padding-left: 2.5rem;
        padding-right: 0.75rem;
      }
      
      /* Table adjustments */
      table {
        text-align: right;
      }
      
      th,
      td {
        text-align: right;
      }
      
      /* Modal adjustments */
      .modal-close {
        right: auto;
        left: 1rem;
      }
      
      /* Dropdown adjustments */
      .dropdown-menu {
        text-align: right;
        right: 0;
        left: auto;
      }
      
      /* Pagination adjustments */
      .pagination {
        flex-direction: row-reverse;
      }
    }
    
    /* LTR specific styles (default) */
    [dir="ltr"] {
      /* Ensure proper text direction */
      text-align: left;
      direction: ltr;
    }
    
    /* Bidirectional text support */
    .bidi-override {
      unicode-bidi: bidi-override;
    }
    
    .bidi-embed {
      unicode-bidi: embed;
    }
    
    .bidi-isolate {
      unicode-bidi: isolate;
    }

  `;
  document.head.appendChild(style);
};

const RTLProvider = ({ children, isRTL = false }) => {
  const { t } = useTranslation();
  
  // Inject RTL styles on mount
  useEffect(() => {
    injectRTLStyles();
  }, []);
  
  // Update CSS variables for RTL
  useEffect(() => {
    const root = document.documentElement;

    if (isRTL) {
      // RTL-specific CSS variables
      root.style.setProperty('--direction', 'rtl');
      root.style.setProperty('--text-align', 'right');
      root.style.setProperty('--flex-direction', 'row-reverse');
      root.style.setProperty('--margin-inline-start', '0');
      root.style.setProperty('--margin-inline-end', 'auto');
      root.style.setProperty('--padding-inline-start', '0');
      root.style.setProperty('--padding-inline-end', '1rem');
      root.style.setProperty('--float-start', 'right');
      root.style.setProperty('--float-end', 'left');
      root.style.setProperty('--clear-start', 'right');
      root.style.setProperty('--clear-end', 'left');
    } else {
      // LTR CSS variables
      root.style.setProperty('--direction', 'ltr');
      root.style.setProperty('--text-align', 'left');
      root.style.setProperty('--flex-direction', 'row');
      root.style.setProperty('--margin-inline-start', '0');
      root.style.setProperty('--margin-inline-end', 'auto');
      root.style.setProperty('--padding-inline-start', '0');
      root.style.setProperty('--padding-inline-end', '1rem');
      root.style.setProperty('--float-start', 'left');
      root.style.setProperty('--float-end', 'right');
      root.style.setProperty('--clear-start', 'left');
      root.style.setProperty('--clear-end', 'right');
    }
  }, [isRTL]);

  // Context value
  const contextValue = useMemo(() => ({
    isRTL,
    direction: isRTL ? 'rtl' : 'ltr',
    alignment: isRTL ? 'right' : 'left',
    // Helper functions for RTL-aware styling
    getMargin: (start, end) => isRTL ?
    { marginRight: start, marginLeft: end } :
    { marginLeft: start, marginRight: end },
    getPadding: (start, end) => isRTL ?
    { paddingRight: start, paddingLeft: end } :
    { paddingLeft: start, paddingRight: end },
    getBorder: (start, end) => isRTL ?
    { borderRight: start, borderLeft: end } :
    { borderLeft: start, borderRight: end },
    getPosition: (start, end) => isRTL ?
    { right: start, left: end } :
    { left: start, right: end },
    getTransform: (value) => isRTL ?
    `scaleX(-1) ${value}` :
    value,
    getTextAlign: (align) => {
      if (align === 'start') return isRTL ? 'right' : 'left';
      if (align === 'end') return isRTL ? 'left' : 'right';
      return align;
    }
  }), [isRTL]);

  return (
    <RTLContext.Provider value={contextValue}>
      {children}
    </RTLContext.Provider>
  );

};

export default RTLProvider;