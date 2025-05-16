import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Card from '../../components/common/Card';

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(<Card title="Test Title">Content</Card>);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<Card title="Title" subtitle="Subtitle">Content</Card>);
    expect(screen.getByText('Subtitle')).toBeInTheDocument();
  });

  it('renders header actions', () => {
    render(
      <Card 
        title="Title"
        headerActions={<button>Action</button>}
      >
        Content
      </Card>
    );
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  it('applies hover effect when hoverable', () => {
    render(<Card hoverable>Content</Card>);
    const card = screen.getByText('Content').parentElement;
    expect(card).toHaveClass('hover:shadow-lg');
  });

  it('applies border when bordered', () => {
    render(<Card bordered>Content</Card>);
    const card = screen.getByText('Content').parentElement;
    expect(card).toHaveClass('border');
  });

  it('renders footer when provided', () => {
    render(
      <Card footer={<div>Footer content</div>}>
        Content
      </Card>
    );
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Card className="custom-class">Content</Card>);
    const card = screen.getByText('Content').parentElement;
    expect(card).toHaveClass('custom-class');
  });
});