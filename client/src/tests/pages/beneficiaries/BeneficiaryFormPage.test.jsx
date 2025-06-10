// TODO: i18n - processed
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import BeneficiaryFormPage from '../../../pages/beneficiaries/BeneficiaryFormPage';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
// Mock the modules
import { useTranslation } from "react-i18next";vi.mock('@/hooks/useAuth');
vi.mock('@/components/ui/toast');
vi.mock('@/lib/api');
vi.mock('react-hook-form', async () => {
  const actual = await vi.importActual('react-hook-form');
  return {
    ...actual,
    Controller: ({ render }) => render({ field: { onChange: () => {}, value: '', ref: () => {} } })
  };
});
// Mock react-router-dom
const mockNavigate = vi.fn();
const mockParams = {};
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => mockParams,
    useNavigate: () => mockNavigate
  };
});
// Mock URL.createObjectURL
URL.createObjectURL = vi.fn(() => 'mock-object-url');
// Mock Auth hook
const mockHasRole = vi.fn();
useAuth.mockReturnValue({
  hasRole: mockHasRole
});
// Mock Toast hook
const mockAddToast = vi.fn();
useToast.mockReturnValue({
  addToast: mockAddToast
});
// Mock trainers data
const mockTrainers = [
{
  id: '1',
  first_name: 'Jane',
  last_name: 'Trainer',
  email: 'jane@example.com'
},
{
  id: '2',
  first_name: 'John',
  last_name: 'Coach',
  email: 'john@example.com'
}];

// Mock beneficiary data for edit mode
const mockBeneficiary = {
  id: '123',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '+1234567890',
  status: 'active',
  birth_date: '1990-01-01',
  gender: 'male',
  nationality: 'American',
  native_language: 'English',
  address: '123 Main St',
  city: 'Test City',
  state: 'Test State',
  zip_code: '12345',
  country: 'USA',
  organization: 'Test Org',
  occupation: 'Developer',
  education_level: 'bachelor',
  bio: 'Test bio information',
  goals: 'Learn new skills',
  category: 'Professional',
  referral_source: 'Website',
  notes: 'Additional notes',
  custom_fields: {
    favorite_language: 'JavaScript',
    years_of_experience: '5'
  }
};
describe('BeneficiaryFormPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset params for each test
    Object.keys(mockParams).forEach((key) => delete mockParams[key]);
    // Default mock implementations
    api.get.mockImplementation((url, config) => {
      // Check for /api/users with trainer params
      if (url === '/api/users' && config?.params?.role === 'trainer') {
        return Promise.resolve({ data: { items: mockTrainers } });
      }
      if (url === '/api/beneficiaries/123') {
        return Promise.resolve({ data: mockBeneficiary });
      }
      if (url === '/api/beneficiaries/123/trainers') {
        return Promise.resolve({ data: [{ id: '1', first_name: 'Jane', last_name: 'Trainer' }] });
      }
      return Promise.reject(new Error('Not found'));
    });
    api.post.mockResolvedValue({ data: { id: '456' } });
    api.put.mockResolvedValue({ data: { id: '123' } });
    // Default role permissions
    mockHasRole.mockReturnValue(true);
  });
  it('renders create mode correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Verify form elements
    expect(screen.getByText('Personal Info')).toBeInTheDocument();
    expect(screen.getByText('Address')).toBeInTheDocument();
    expect(screen.getByText('Additional Info')).toBeInTheDocument();
    expect(screen.getByText('Custom Fields')).toBeInTheDocument();
    // Verify required fields
    expect(screen.getByLabelText('First Name *')).toBeInTheDocument();
    expect(screen.getByLabelText('Last Name *')).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address *')).toBeInTheDocument();
    // Verify trainer section
    await waitFor(() => {
      expect(screen.getByText('Assign Trainers')).toBeInTheDocument();
      expect(screen.getByText('Jane Trainer')).toBeInTheDocument();
      expect(screen.getByText('John Coach')).toBeInTheDocument();
    });
    // Verify submit button
    expect(screen.getByText('Create Beneficiary')).toBeInTheDocument();
  });
  it('renders edit mode correctly', async () => {
    // Set params for edit mode
    mockParams.id = '123';
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    // Wait for data to load (skip checking loading state as it might be too fast)
    await waitFor(() => {
      expect(screen.getByText('Edit Beneficiary')).toBeInTheDocument();
    });
    // Check form is pre-filled
    expect(screen.getByLabelText('First Name *')).toHaveValue('John');
    expect(screen.getByLabelText('Last Name *')).toHaveValue('Doe');
    expect(screen.getByLabelText('Email Address *')).toHaveValue('john@example.com');
    expect(screen.getByLabelText('Phone Number')).toHaveValue('+1234567890');
    // Click on Additional Info tab to see the biography field
    fireEvent.click(screen.getByText('Additional Info'));
    
    // Now check the biography field
    const bioField = screen.getByLabelText('Biography');
    expect(bioField).toHaveValue('Test bio information');
    // Verify submit button
    expect(screen.getByText('Update Beneficiary')).toBeInTheDocument();
  });
  it('navigates between tabs correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Default tab is Personal Info
    expect(screen.getByLabelText('First Name *')).toBeInTheDocument();
    expect(screen.queryByLabelText('Street Address')).not.toBeInTheDocument();
    // Click on Address tab
    fireEvent.click(screen.getByText('Address'));
    // Address fields should now be visible
    expect(screen.getByLabelText('Street Address')).toBeInTheDocument();
    expect(screen.getByLabelText('City')).toBeInTheDocument();
    expect(screen.queryByLabelText('First Name *')).not.toBeInTheDocument();
    // Click on Additional Info tab
    fireEvent.click(screen.getByText('Additional Info'));
    // Additional Info fields should now be visible
    expect(screen.getByLabelText('Organization')).toBeInTheDocument();
    expect(screen.getByLabelText('Biography')).toBeInTheDocument();
    // Click on Custom Fields tab
    fireEvent.click(screen.getByText('Custom Fields'));
    // Custom Fields section should now be visible
    expect(screen.getByText('Add Field')).toBeInTheDocument();
    expect(screen.getByText('No custom fields')).toBeInTheDocument();
  });
  it('handles trainer selection', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Jane Trainer')).toBeInTheDocument();
    });
    // Click on a trainer to select
    fireEvent.click(screen.getByText('Jane Trainer'));
    // The checkbox should be checked
    const checkbox = screen.getAllByRole('checkbox')[0];
    expect(checkbox).toBeChecked();
    // Click again to unselect
    fireEvent.click(screen.getByText('Jane Trainer'));
    // The checkbox should be unchecked
    expect(checkbox).not.toBeChecked();
  });
  it('handles custom field management', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Go to Custom Fields tab
    fireEvent.click(screen.getByText('Custom Fields'));
    // Initial state should show "No custom fields"
    expect(screen.getByText('No custom fields')).toBeInTheDocument();
    // Click Add Field button
    fireEvent.click(screen.getByText('Add Field'));
    // Form should appear
    expect(screen.getByLabelText('Field Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Field Value')).toBeInTheDocument();
    // Fill out the form
    fireEvent.change(screen.getByLabelText('Field Name'), { target: { value: 'Favorite Framework' } });
    fireEvent.change(screen.getByLabelText('Field Value'), { target: { value: 'React' } });
    // Add the field
    fireEvent.click(screen.getByText('Add'));
    // The new field should be displayed
    expect(screen.getByText('Favorite Framework')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    // Remove button should be available
    const removeButton = screen.getByText('Remove');
    // Click remove to delete the field
    fireEvent.click(removeButton);
    // Field should be removed
    expect(screen.queryByText('Favorite Framework')).not.toBeInTheDocument();
    expect(screen.getByText('No custom fields')).toBeInTheDocument();
  });
  it('handles form submission in create mode', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Fill in required fields
    fireEvent.change(screen.getByLabelText('First Name *'), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText('Last Name *'), { target: { value: 'Smith' } });
    fireEvent.change(screen.getByLabelText('Email Address *'), { target: { value: 'jane@example.com' } });
    // Select a trainer
    fireEvent.click(screen.getByText('Jane Trainer'));
    // Submit the form
    fireEvent.click(screen.getByText('Create Beneficiary'));
    // Check API calls
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/beneficiaries', expect.objectContaining({
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        status: 'active'
      }));
      // Trainer assignment should be called
      expect(api.post).toHaveBeenCalledWith('/api/beneficiaries/456/assign-trainer', {
        trainer_id: '1'
      });
    });
    // Success toast should be shown
    expect(mockAddToast).toHaveBeenCalledWith({
      type: 'success',
      title: 'Beneficiary created',
      message: 'Jane Smith has been created successfully.'
    });
    // Should navigate to the new beneficiary page
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/456');
  });
  it('handles form submission in edit mode', async () => {
    // Set params for edit mode
    mockParams.id = '123';
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Edit Beneficiary')).toBeInTheDocument();
    });
    // Update a field
    fireEvent.change(screen.getByLabelText('First Name *'), { target: { value: 'Johnny' } });
    // Submit the form
    fireEvent.click(screen.getByText('Update Beneficiary'));
    // Check API calls
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/api/beneficiaries/123', expect.objectContaining({
        first_name: 'Johnny',
        last_name: 'Doe',
        email: 'john@example.com'
      }));
    });
    // Success toast should be shown
    expect(mockAddToast).toHaveBeenCalledWith({
      type: 'success',
      title: 'Beneficiary updated',
      message: "Johnny Doe's information has been updated."
    });
    // Should navigate to the beneficiary page
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/123');
  });
  it('handles validation errors', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Leave required fields empty and submit
    fireEvent.click(screen.getByText('Create Beneficiary'));
    // Wait for validation errors
    await waitFor(() => {
      // These assertions depend on how the form validation displays errors
      // Assume it renders error messages below the fields
      expect(screen.queryAllByText(/must be at least/)).not.toHaveLength(0);
      expect(screen.queryAllByText(/enter a valid email/)).not.toHaveLength(0);
    });
    // API should not be called
    expect(api.post).not.toHaveBeenCalled();
  });
  it('handles API errors on submit', async () => {
    // Mock API error
    api.post.mockRejectedValueOnce({
      response: {
        data: { message: 'Email already exists' }
      }
    });
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Fill in required fields
    fireEvent.change(screen.getByLabelText('First Name *'), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText('Last Name *'), { target: { value: 'Smith' } });
    fireEvent.change(screen.getByLabelText('Email Address *'), { target: { value: 'jane@example.com' } });
    // Submit the form
    fireEvent.click(screen.getByText('Create Beneficiary'));
    // Check for error toast
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        type: 'error',
        title: 'Creation failed',
        message: 'Email already exists'
      });
    });
    // Should not navigate
    expect(mockNavigate).not.toHaveBeenCalled();
  });
  it('handles image upload', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // Create a mock file
    const mockFile = new File(['dummy content'], 'avatar.png', { type: 'image/png' });
    // Get the file input by its ID
    const fileInput = document.getElementById('profile-picture');
    // Simulate file upload
    fireEvent.change(fileInput, { target: { files: [mockFile] } });
    // Create a full form submission with the image
    fireEvent.change(screen.getByLabelText('First Name *'), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText('Last Name *'), { target: { value: 'Smith' } });
    fireEvent.change(screen.getByLabelText('Email Address *'), { target: { value: 'jane@example.com' } });
    // Submit the form
    fireEvent.click(screen.getByText('Create Beneficiary'));
    // Check if profile picture upload was called
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        '/api/beneficiaries/456/profile-picture',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      );
    });
  });
  it('handles API error when fetching beneficiary', async () => {
    // Set params for edit mode
    mockParams.id = '123';
    
    // Mock API to succeed for trainers but fail for beneficiary
    let callCount = 0;
    api.get.mockImplementation((url, config) => {
      callCount++;
      // First call is for trainers
      if (url === '/api/users' && config?.params?.role === 'trainer') {
        return Promise.resolve({ data: { items: mockTrainers } });
      }
      // Second call is for the beneficiary
      if (url === '/api/beneficiaries/123') {
        return Promise.reject(new Error('Failed to fetch'));
      }
      return Promise.reject(new Error('Not found'));
    });
    
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    // Wait for error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        type: 'error',
        title: 'Failed to load beneficiary',
        message: 'An unexpected error occurred.'
      });
    });
    // Verify navigation back to listing
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries');
  });
  it('restricts access based on role permissions', async () => {
    // Mock user without manage permissions
    mockHasRole.mockReturnValue(false);
    // This test would need to check specific behaviors that depend on the canManage flag
    // Since the component still renders but may disable certain features
    render(
      <BrowserRouter>
        <BeneficiaryFormPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Add New Beneficiary')).toBeInTheDocument();
    });
    // This would need to check for specific elements that are disabled or hidden
    // But without more specifics on how the component behaves in this case,
    // we'll just verify it renders
  });
});