import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ThemeToggle from '@/components/common/ThemeToggle';
import * as ThemeContext from '@/contexts/ThemeContext';
// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    button: ({ 
      children, 
      whileHover, 
      whileTap, 
      initial, 
      animate, 
      transition, 
      ...props 
    }) => <button {...props}>{children}</button>,
    div: ({ 
      children, 
      initial, 
      animate, 
      transition, 
      ...props 
    }) => <div {...props}>{children}</div>
  }
}));
// Mock the ThemeContext
vi.mock('@/contexts/ThemeContext', () => ({
  useTheme: vi.fn()
}));
describe('ThemeToggle', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });
  it('renders light theme icon when theme is light', () => {
    // Mock the theme context for light theme
    ThemeContext.useTheme.mockReturnValue({
      theme: 'light',
      toggleTheme: vi.fn(),
      isDark: false
    });
    render(<ThemeToggle />);
    // Verify the sun icon title text
    expect(screen.getByTitle('Switch to dark mode')).toBeInTheDocument();
  });
  it('renders dark theme icon when theme is dark', () => {
    // Mock the theme context for dark theme
    ThemeContext.useTheme.mockReturnValue({
      theme: 'dark',
      toggleTheme: vi.fn(),
      isDark: true
    });
    render(<ThemeToggle />);
    // Verify the moon icon title text
    expect(screen.getByTitle('Switch to light mode')).toBeInTheDocument();
  });
  it('calls toggleTheme when button is clicked', () => {
    // Create a mock for the toggleTheme function
    const toggleTheme = vi.fn();
    // Mock the theme context with the mock function
    ThemeContext.useTheme.mockReturnValue({
      theme: 'light',
      toggleTheme,
      isDark: false
    });
    render(<ThemeToggle />);
    // Find and click the toggle button
    const button = screen.getByTitle('Switch to dark mode');
    fireEvent.click(button);
    // Verify that toggleTheme was called
    expect(toggleTheme).toHaveBeenCalledTimes(1);
  });
  it('applies appropriate styles based on theme', () => {
    // Test light theme styling
    ThemeContext.useTheme.mockReturnValue({
      theme: 'light',
      toggleTheme: vi.fn(),
      isDark: false
    });
    const { rerender } = render(<ThemeToggle />);
    let button = screen.getByRole('button');
    // Verify light theme styles
    expect(button).toHaveClass('bg-gray-100');
    expect(button).toHaveClass('text-gray-800');
    // Test dark theme styling
    ThemeContext.useTheme.mockReturnValue({
      theme: 'dark',
      toggleTheme: vi.fn(),
      isDark: true
    });
    rerender(<ThemeToggle />);
    button = screen.getByRole('button');
    // Verify dark theme styles
    expect(button).toHaveClass('bg-gray-800');
    expect(button).toHaveClass('text-yellow-400');
  });
});