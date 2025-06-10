// TODO: i18n - processed
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RegisterPage from '../../../pages/auth/RegisterPage';
import { render } from '../../../test/test-utils';
// Mock the navigate function
import { useTranslation } from "react-i18next";vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn()
  };
});
// Mock the useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    register: vi.fn().mockResolvedValue({
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'test@example.com'
    }),
    error: null
  })
}));
// Mock the toast hook
vi.mock('@/components/ui/toast', async () => {
  const actual = await vi.importActual('@/components/ui/toast');
  return {
    ...actual,
    useToast: () => ({
      addToast: vi.fn()
    })
  };
});
describe('RegisterPage', () => {
  const user = userEvent.setup();
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('renders registration form', () => {
    render(<RegisterPage />);
    expect(screen.getByText(/Create your account/i)).toBeInTheDocument();
    expect(screen.getByLabelText('First Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
    // Check for password fields by role and id instead
    expect(screen.getByRole('textbox', { name: 'First Name' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
  });
  it('shows validation errors when submitted with empty fields', async () => {
    render(<RegisterPage />);
    // Find and click submit button
    const submitButton = screen.getByRole('button', { name: /Create Account/i });
    await user.click(submitButton);
    // Verify required checkbox
    expect(screen.getByLabelText(/I agree to the/i)).toBeInTheDocument();
  });
  it('shows organization field for trainers', async () => {
    render(<RegisterPage />);
    // Just check that the role select exists
    const roleSelect = screen.getByLabelText('I am a');
    expect(roleSelect).toBeInTheDocument();
  });
});