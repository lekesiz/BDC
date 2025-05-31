import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'light';
  });

  const [accentColor, setAccentColor] = useState(() => {
    const savedColor = localStorage.getItem('accentColor');
    return savedColor || 'blue';
  });

  const [fontSize, setFontSize] = useState(() => {
    const savedSize = localStorage.getItem('fontSize');
    return savedSize || 'medium';
  });

  // Apply theme to document root
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Save theme preference
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Apply accent color
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-accent', accentColor);
    localStorage.setItem('accentColor', accentColor);
  }, [accentColor]);

  // Apply font size
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-font-size', fontSize);
    localStorage.setItem('fontSize', fontSize);
  }, [fontSize]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const changeTheme = (newTheme) => {
    setTheme(newTheme);
  };

  const changeAccentColor = (newColor) => {
    setAccentColor(newColor);
  };

  const changeFontSize = (newSize) => {
    setFontSize(newSize);
  };

  const value = {
    theme,
    setTheme,
    toggleTheme,
    changeTheme,
    isDark: theme === 'dark',
    accentColor,
    changeAccentColor,
    fontSize,
    changeFontSize
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};