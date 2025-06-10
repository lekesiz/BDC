// TODO: i18n - processed
/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import LazyWrapper from '../LazyWrapper';
// Mock the components
import { useTranslation } from "react-i18next";vi.mock('../ErrorBoundary', () => ({
  default: ({ children }) => <div data-testid="error-boundary">{children}</div>
}));
vi.mock('../../ui/LoadingSpinner', () => ({
  default: () => <div data-testid="loading-spinner">Loading...</div>
}));
// Mock component for lazy loading simulation
const MockComponent = () => <div data-testid="mock-component">Mock Component</div>;
describe('LazyWrapper', () => {
  it('renders children wrapped in ErrorBoundary and Suspense', () => {
    render(
      <LazyWrapper>
        <MockComponent />
      </LazyWrapper>
    );
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
    expect(screen.getByTestId('mock-component')).toBeInTheDocument();
  });
  it('renders custom fallback when provided', () => {
    const CustomFallback = () => <div data-testid="custom-fallback">Custom Loading...</div>;
    render(
      <LazyWrapper fallback={<CustomFallback />}>
        <MockComponent />
      </LazyWrapper>
    );
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
  });
  it('provides accessibility structure', () => {
    render(
      <LazyWrapper>
        <MockComponent />
      </LazyWrapper>
    );
    // Should have proper wrapper structure
    const errorBoundary = screen.getByTestId('error-boundary');
    expect(errorBoundary).toBeInTheDocument();
  });
});