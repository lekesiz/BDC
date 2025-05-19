import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import BeneficiariesPageV2 from './BeneficiariesPageV2';
import api from '@/lib/api';

// Mock the API
vi.mock('@/lib/api');

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockBeneficiariesData = {
  items: [
    {
      id: '1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      status: 'active',
      created_at: '2024-01-01T00:00:00Z',
      evaluation_count: 5,
      completed_evaluation_count: 3
    },
    {
      id: '2',
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane@example.com',
      phone: null,
      status: 'pending',
      created_at: '2024-01-02T00:00:00Z',
      evaluation_count: 2,
      completed_evaluation_count: 0
    },
  ],
  total: 2,
  pages: 1,
  current_page: 1
};

describe('BeneficiariesPageV2', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders beneficiaries data correctly', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
  });

  it('handles empty state correctly', async () => {
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0, pages: 0 } });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No beneficiaries found')).toBeInTheDocument();
      expect(screen.getByText('Get started by adding your first beneficiary')).toBeInTheDocument();
    });
  });

  it('handles error state with retry', async () => {
    const error = new Error('Failed to fetch');
    api.get.mockRejectedValueOnce(error);

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to load beneficiaries')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    // Mock successful retry
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    // Click retry button
    fireEvent.click(screen.getByText('Try Again'));

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('handles search functionality', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by name, email or phone...');
    
    // Mock search results
    api.get.mockResolvedValueOnce({
      data: {
        items: [mockBeneficiariesData.items[0]],
        total: 1,
        pages: 1
      }
    });

    fireEvent.change(searchInput, { target: { value: 'John' } });

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries', {
        params: expect.objectContaining({
          query: 'John'
        })
      });
    });
  });

  it('handles pagination', async () => {
    const multiPageData = {
      ...mockBeneficiariesData,
      pages: 3,
      total_pages: 3,
      total: 30
    };
    
    api.get.mockResolvedValueOnce({ data: multiPageData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Mock page 2 data
    api.get.mockResolvedValueOnce({
      data: {
        ...multiPageData,
        current_page: 2,
        items: [{
          id: '3',
          first_name: 'Alice',
          last_name: 'Johnson',
          email: 'alice@example.com',
          phone: null,
          status: 'active',
          created_at: '2024-01-03T00:00:00Z',
          evaluation_count: 0,
          completed_evaluation_count: 0
        }]
      }
    });

    // Click next page
    fireEvent.click(screen.getByText('Next'));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries', {
        params: expect.objectContaining({
          page: 2
        })
      });
    });
  });

  it('handles sorting', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Mock sorted data
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    // Click on Name column to sort
    fireEvent.click(screen.getByText('Name'));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries', {
        params: expect.objectContaining({
          sort_by: 'last_name',
          sort_dir: 'asc'
        })
      });
    });
  });

  it('navigates to beneficiary detail on row click', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Click on the first row
    const firstRow = screen.getByText('John Doe').closest('tr');
    fireEvent.click(firstRow);

    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/1');
  });

  it('navigates to create beneficiary on button click', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add Beneficiary'));

    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/new');
  });

  it('handles filter toggle correctly', async () => {
    api.get.mockResolvedValueOnce({ data: mockBeneficiariesData });

    render(
      <BrowserRouter>
        <BeneficiariesPageV2 />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Filters should be hidden initially
    expect(screen.queryByLabelText('Status')).not.toBeInTheDocument();

    // Click to show filters
    fireEvent.click(screen.getByText('Filters'));

    // Filters should now be visible
    expect(screen.getByLabelText('Status')).toBeInTheDocument();
    expect(screen.getByLabelText('Sort By')).toBeInTheDocument();
    expect(screen.getByLabelText('Sort Order')).toBeInTheDocument();
  });
});