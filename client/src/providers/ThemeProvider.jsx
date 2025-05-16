import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [systemTheme, setSystemTheme] = useState('light');
  const [accentColor, setAccentColor] = useState('blue');
  const [fontSize, setFontSize] = useState('medium');

  useEffect(() => {
    // Load saved theme preferences
    const savedTheme = localStorage.getItem('theme');
    const savedAccentColor = localStorage.getItem('accentColor');
    const savedFontSize = localStorage.getItem('fontSize');

    if (savedTheme) setTheme(savedTheme);
    if (savedAccentColor) setAccentColor(savedAccentColor);
    if (savedFontSize) setFontSize(savedFontSize);

    // Detect system theme
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light');

    const handleChange = (e) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
      if (theme === 'system') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    if (theme === 'system') {
      applyTheme(systemTheme);
    } else {
      applyTheme(theme);
    }
  }, [theme, systemTheme]);

  useEffect(() => {
    applyAccentColor(accentColor);
  }, [accentColor]);

  useEffect(() => {
    applyFontSize(fontSize);
  }, [fontSize]);

  const applyTheme = (themeName) => {
    const root = document.documentElement;
    const isDark = themeName === 'dark';

    if (isDark) {
      root.classList.add('dark');
      root.style.setProperty('--bg-primary', '#1f2937');
      root.style.setProperty('--bg-secondary', '#374151');
      root.style.setProperty('--text-primary', '#f9fafb');
      root.style.setProperty('--text-secondary', '#e5e7eb');
      root.style.setProperty('--border-color', '#4b5563');
    } else {
      root.classList.remove('dark');
      root.style.setProperty('--bg-primary', '#ffffff');
      root.style.setProperty('--bg-secondary', '#f9fafb');
      root.style.setProperty('--text-primary', '#111827');
      root.style.setProperty('--text-secondary', '#6b7280');
      root.style.setProperty('--border-color', '#e5e7eb');
    }
  };

  const applyAccentColor = (color) => {
    const root = document.documentElement;
    const colors = {
      blue: {
        50: '#eff6ff',
        100: '#dbeafe',
        200: '#bfdbfe',
        300: '#93c5fd',
        400: '#60a5fa',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
        800: '#1e40af',
        900: '#1e3a8a'
      },
      green: {
        50: '#f0fdf4',
        100: '#dcfce7',
        200: '#bbf7d0',
        300: '#86efac',
        400: '#4ade80',
        500: '#22c55e',
        600: '#16a34a',
        700: '#15803d',
        800: '#166534',
        900: '#14532d'
      },
      purple: {
        50: '#faf5ff',
        100: '#f3e8ff',
        200: '#e9d5ff',
        300: '#d8b4fe',
        400: '#c084fc',
        500: '#a855f7',
        600: '#9333ea',
        700: '#7e22ce',
        800: '#6b21a8',
        900: '#581c87'
      },
      red: {
        50: '#fef2f2',
        100: '#fee2e2',
        200: '#fecaca',
        300: '#fca5a5',
        400: '#f87171',
        500: '#ef4444',
        600: '#dc2626',
        700: '#b91c1c',
        800: '#991b1b',
        900: '#7f1d1d'
      }
    };

    const selectedColor = colors[color];
    Object.entries(selectedColor).forEach(([shade, value]) => {
      root.style.setProperty(`--color-accent-${shade}`, value);
    });
  };

  const applyFontSize = (size) => {
    const root = document.documentElement;
    const sizes = {
      small: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem'
      },
      medium: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem'
      },
      large: {
        xs: '0.875rem',
        sm: '1rem',
        base: '1.125rem',
        lg: '1.25rem',
        xl: '1.5rem',
        '2xl': '1.875rem',
        '3xl': '2.25rem',
        '4xl': '3rem'
      }
    };

    const selectedSize = sizes[size];
    Object.entries(selectedSize).forEach(([key, value]) => {
      root.style.setProperty(`--text-${key}`, value);
    });
  };

  const changeTheme = (newTheme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const changeAccentColor = (newColor) => {
    setAccentColor(newColor);
    localStorage.setItem('accentColor', newColor);
  };

  const changeFontSize = (newSize) => {
    setFontSize(newSize);
    localStorage.setItem('fontSize', newSize);
  };

  const value = {
    theme,
    systemTheme,
    accentColor,
    fontSize,
    changeTheme,
    changeAccentColor,
    changeFontSize,
    isDark: theme === 'dark' || (theme === 'system' && systemTheme === 'dark')
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;