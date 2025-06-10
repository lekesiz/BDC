// TODO: i18n - processed
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/card';import { useTranslation } from "react-i18next";
describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <CardContent>Card content</CardContent>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });
  it('renders title when provided', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
        </CardHeader>
      </Card>
    );
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
  it('renders content and title', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>
    );
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
  it('renders footer when provided', () => {
    render(
      <Card>
        <CardContent>Content</CardContent>
        <CardFooter>Footer content</CardFooter>
      </Card>
    );
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });
  it('applies custom className', () => {
    render(
      <Card className="custom-class">
        <CardContent>Content</CardContent>
      </Card>
    );
    const card = screen.getByText('Content').closest('.custom-class');
    expect(card).toBeInTheDocument();
  });
  it('has default card classes', () => {
    render(
      <Card>
        <CardContent>Content</CardContent>
      </Card>
    );
    const card = screen.getByText('Content').closest('.rounded-lg');
    expect(card).toHaveClass('rounded-lg', 'border', 'bg-card');
  });
});