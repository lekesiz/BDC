import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { NetworkError } from '@/components/common/ErrorStates';

describe('NetworkError component', () => {
  it('renders default message', () => {
    render(<NetworkError />);
    expect(screen.getByText(/Unable to connect/i)).toBeInTheDocument();
  });
});