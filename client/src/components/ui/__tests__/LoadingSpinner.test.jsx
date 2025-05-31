/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default message', () => {
    render(<LoadingSpinner />);
    
    expect(screen.getByText('Loading page...')).toBeInTheDocument();
  });

  it('renders with custom message', () => {
    render(<LoadingSpinner message="Loading data..." />);
    
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  it('renders without message when not provided', () => {
    render(<LoadingSpinner message="" />);
    
    expect(screen.queryByText('Loading page...')).not.toBeInTheDocument();
  });

  it('has proper CSS classes for styling', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerContainer = container.firstChild;
    expect(spinnerContainer).toHaveClass('min-h-[400px]', 'flex', 'items-center', 'justify-center');
  });

  it('has spinning animation element', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('rounded-full', 'border-b-2', 'border-primary');
  });

  it('provides accessible loading indication', () => {
    render(<LoadingSpinner message="Loading content..." />);
    
    // Message should be readable by screen readers
    expect(screen.getByText('Loading content...')).toBeInTheDocument();
  });
});