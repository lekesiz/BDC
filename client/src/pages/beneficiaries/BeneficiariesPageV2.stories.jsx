// TODO: i18n - processed
import BeneficiariesPageV2 from './BeneficiariesPageV2';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '@/components/ui/toast';import { useTranslation } from "react-i18next";
export default {
  title: 'Pages/BeneficiariesPageV2',
  component: BeneficiariesPageV2,
  decorators: [
  (Story) =>
  <BrowserRouter>
        <ToastProvider>
          <div className="min-h-screen bg-gray-50 p-6">
            <Story />
          </div>
        </ToastProvider>
      </BrowserRouter>],


  parameters: {
    layout: 'fullscreen'
  }
};
// Mock data for different scenarios
const mockBeneficiaries = [
{
  id: '1',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  phone: '+1234567890',
  status: 'active',
  created_at: '2024-01-15T10:00:00Z',
  evaluation_count: 8,
  completed_evaluation_count: 6
},
{
  id: '2',
  first_name: 'Jane',
  last_name: 'Smith',
  email: 'jane.smith@example.com',
  phone: '+0987654321',
  status: 'pending',
  created_at: '2024-01-14T15:30:00Z',
  evaluation_count: 5,
  completed_evaluation_count: 2
},
{
  id: '3',
  first_name: 'Alice',
  last_name: 'Johnson',
  email: 'alice.johnson@example.com',
  phone: null,
  status: 'inactive',
  created_at: '2024-01-13T08:45:00Z',
  evaluation_count: 0,
  completed_evaluation_count: 0
},
{
  id: '4',
  first_name: 'Bob',
  last_name: 'Wilson',
  email: 'bob.wilson@example.com',
  phone: '+1122334455',
  status: 'completed',
  created_at: '2024-01-12T14:20:00Z',
  evaluation_count: 10,
  completed_evaluation_count: 10
},
{
  id: '5',
  first_name: 'Emma',
  last_name: 'Davis',
  email: 'emma.davis@example.com',
  phone: '+5544332211',
  status: 'active',
  created_at: '2024-01-11T11:00:00Z',
  evaluation_count: 3,
  completed_evaluation_count: 3
}];

// Mock API responses
const mockApiSuccess = () => ({
  get: () => Promise.resolve({
    data: {
      items: mockBeneficiaries,
      total: mockBeneficiaries.length,
      pages: 1,
      current_page: 1
    }
  })
});
const mockApiLoading = () => ({
  get: () => new Promise(() => {}) // Never resolves to show loading state
});
const mockApiError = () => ({
  get: () => Promise.reject(new Error('Failed to fetch beneficiaries'))
});
const mockApiEmpty = () => ({
  get: () => Promise.resolve({
    data: {
      items: [],
      total: 0,
      pages: 0,
      current_page: 1
    }
  })
});
// Default story
export const Default = {
  name: 'Default View',
  parameters: {
    mockData: {
      api: mockApiSuccess()
    }
  }
};
// Loading state
export const Loading = {
  name: 'Loading State',
  parameters: {
    mockData: {
      api: mockApiLoading()
    }
  }
};
// Error state
export const Error = {
  name: 'Error State',
  parameters: {
    mockData: {
      api: mockApiError()
    }
  }
};
// Empty state
export const Empty = {
  name: 'Empty State',
  parameters: {
    mockData: {
      api: mockApiEmpty()
    }
  }
};
// With pagination
export const WithPagination = {
  name: 'With Pagination',
  parameters: {
    mockData: {
      api: {
        get: () => Promise.resolve({
          data: {
            items: mockBeneficiaries.slice(0, 2),
            total: 30,
            pages: 15,
            current_page: 1
          }
        })
      }
    }
  }
};
// Filtered results
export const FilteredResults = {
  name: 'Filtered Results',
  parameters: {
    mockData: {
      api: {
        get: () => Promise.resolve({
          data: {
            items: mockBeneficiaries.filter((b) => b.status === 'active'),
            total: 2,
            pages: 1,
            current_page: 1
          }
        })
      }
    }
  }
};
// Search results
export const SearchResults = {
  name: 'Search Results',
  parameters: {
    mockData: {
      api: {
        get: () => Promise.resolve({
          data: {
            items: [mockBeneficiaries[0]],
            total: 1,
            pages: 1,
            current_page: 1
          }
        })
      }
    }
  }
};
// Mobile view
export const Mobile = {
  name: 'Mobile View',
  parameters: {
    viewport: {
      defaultViewport: 'mobile1'
    },
    mockData: {
      api: mockApiSuccess()
    }
  }
};
// Dark mode (if supported)
export const DarkMode = {
  name: 'Dark Mode',
  parameters: {
    theme: 'dark',
    mockData: {
      api: mockApiSuccess()
    }
  }
};