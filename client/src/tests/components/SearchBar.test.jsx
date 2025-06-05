import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchBar from '@/components/ui/SearchBar';
describe('SearchBar', () => {
  it('renders with placeholder text', () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search programs..." 
        onSearch={onSearch} 
      />
    );
    expect(screen.getByPlaceholderText('Search programs...')).toBeInTheDocument();
  });
  it('calls onSearch when typing', async () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
      />
    );
    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'test query' } });
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test query');
    });
  });
  it('shows search icon', () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
      />
    );
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });
  it('clears search when clear button is clicked', async () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        value="initial value"
      />
    );
    const clearButton = screen.getByRole('button', { name: /clear/i });
    fireEvent.click(clearButton);
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('');
    });
  });
  it('supports keyboard shortcuts', () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
      />
    );
    const input = screen.getByPlaceholderText('Search...');
    // Test Ctrl+K focus
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    expect(input).toHaveFocus();
    // Test Escape clear
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.keyDown(input, { key: 'Escape' });
    expect(input.value).toBe('');
  });
  it('shows loading state when searching', () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        isLoading={true}
      />
    );
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
  it('displays search results count', () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        resultsCount={5}
        value="test"
      />
    );
    expect(screen.getByText('5 results')).toBeInTheDocument();
  });
  it('handles debounced search', async () => {
    const onSearch = vi.fn();
    render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        debounce={300}
      />
    );
    const input = screen.getByPlaceholderText('Search...');
    // Type multiple characters quickly
    fireEvent.change(input, { target: { value: 't' } });
    fireEvent.change(input, { target: { value: 'te' } });
    fireEvent.change(input, { target: { value: 'test' } });
    // Should only call onSearch once after debounce
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledTimes(1);
      expect(onSearch).toHaveBeenCalledWith('test');
    }, { timeout: 500 });
  });
  it('supports different sizes', () => {
    const onSearch = vi.fn();
    const { rerender } = render(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        size="sm"
      />
    );
    expect(screen.getByPlaceholderText('Search...')).toHaveClass('h-8');
    rerender(
      <SearchBar 
        placeholder="Search..." 
        onSearch={onSearch} 
        size="lg"
      />
    );
    expect(screen.getByPlaceholderText('Search...')).toHaveClass('h-12');
  });
});