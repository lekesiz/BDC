import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../../../components/common/ErrorBoundary';
import { describe, it, expect, vi, beforeEach } from 'vitest';
// Create a component that will throw an error
const ThrowError = () => {
  throw new Error('Test error');
  return null;
};
// Create a component that doesn't throw an error
const NoError = () => <div>No error</div>;
describe('ErrorBoundary', () => {
  // Suppress console.error during tests
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <NoError />
      </ErrorBoundary>
    );
    expect(screen.getByText('No error')).toBeInTheDocument();
  });
  it('renders fallback UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    // Check that the error message is displayed
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });
  it('calls onError when there is an error', () => {
    const mockOnError = vi.fn();
    render(
      <ErrorBoundary onError={mockOnError}>
        <ThrowError />
      </ErrorBoundary>
    );
    // Check that the error handler was called
    expect(mockOnError).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'Test error' }),
      expect.anything()
    );
  });
  it('has a reset button', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    // Error UI should be shown
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    // Verify the reset button exists
    const resetButton = screen.getByRole('button', { name: /Try Again/i });
    expect(resetButton).toBeInTheDocument();
  });
  it('has a go to home button', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    // Error UI should be shown
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    // Verify the home button exists
    const homeButton = screen.getByRole('button', { name: /Go to Home/i });
    expect(homeButton).toBeInTheDocument();
  });
});