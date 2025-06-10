// TODO: i18n - processed
// Theme Provider Component
import React, { createContext, useContext, useEffect, useState } from 'react';
import { generateCSSVariables } from './createTheme';
import { lightTheme } from './lightTheme';
import { darkTheme } from './darkTheme';import { useTranslation } from "react-i18next";

const ThemeContext = createContext();

export const ThemeProvider = ({
  children,
  defaultTheme = 'light',
  storageKey = 'bdc-theme'
}) => {const { t } = useTranslation();
  const [currentTheme, setCurrentTheme] = useState(() => {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem(storageKey);
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      return savedTheme;
    }

    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }

    return defaultTheme;
  });

  const theme = currentTheme === 'dark' ? darkTheme : lightTheme;

  useEffect(() => {
    // Apply theme CSS variables
    const root = document.documentElement;
    const cssVars = generateCSSVariables(theme);

    Object.entries(cssVars).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });

    // Update body class for theme-specific styles
    document.body.className = document.body.className.
    replace(/theme-\w+/g, '').
    trim() + ` theme-${currentTheme}`;

    // Save theme preference
    localStorage.setItem(storageKey, currentTheme);
  }, [currentTheme, theme, storageKey]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      const savedTheme = localStorage.getItem(storageKey);
      if (!savedTheme) {
        setCurrentTheme(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [storageKey]);

  const toggleTheme = () => {
    setCurrentTheme((prev) => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (themeName) => {
    if (themeName === 'light' || themeName === 'dark') {
      setCurrentTheme(themeName);
    }
  };

  const value = {
    theme,
    currentTheme,
    toggleTheme,
    setTheme,
    isDark: currentTheme === 'dark',
    isLight: currentTheme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>);

};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};