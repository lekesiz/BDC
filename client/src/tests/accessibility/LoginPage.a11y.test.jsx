import { render as rtlRender, screen, act } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import LoginPage from '../../pages/auth/LoginPage';
import { AuthContext } from '../../contexts/AuthContext';
import { ToastProvider } from '../../components/ui/toast';
import { mockAuthContext } from '../../test/test-utils';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => {
  const actual = require('../../test/__mocks__/framer-motion.js');
  return actual;
});

// Mock animated components
vi.mock('../../components/animations', () => {
  return {
    AnimatedButton: ({ children, isLoading, ...props }) => (
      <button data-testid="animated-button" {...props}>{children}</button>
    ),
    AnimatedForm: ({ children, ...props }) => (
      <form data-testid="animated-form" {...props}>{children}</form>
    ),
    AnimatedInput: ({ label, error, leftIcon, rightIcon, ...props }) => (
      <div data-testid="animated-input">
        <label htmlFor={props.id}>{label}</label>
        <input aria-label={label} {...props} />
        {error && <span role="alert">{error}</span>}
      </div>
    ),
    AnimatedCheckbox: ({ label, ...props }) => (
      <div data-testid="animated-checkbox">
        <input 
          type="checkbox" 
          {...props} 
          aria-label={label}
        />
        <label htmlFor={props.id}>{label}</label>
      </div>
    )
  };
});

// Mock hooks
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    login: vi.fn().mockResolvedValue({ success: true, user: { id: 1, first_name: 'Test', role: 'admin' } }),
    logout: vi.fn(),
    isAuthenticated: false,
    isLoading: false,
    error: null,
    hasRole: vi.fn(),
    hasPermission: vi.fn()
  })
}));

// Mock useToast hook
vi.mock('../../components/ui/toast', () => {
  return {
    useToast: () => ({
      addToast: vi.fn(),
      removeToast: vi.fn(),
      toasts: []
    }),
    ToastProvider: ({ children }) => <div data-testid="toast-provider">{children}</div>
  };
});

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ state: { from: '/' } })
  };
});

expect.extend(toHaveNoViolations);

// Custom render function with auth context
function render(ui, options) {
  const wrapper = ({ children }) => (
    <BrowserRouter>
      <AuthContext.Provider value={mockAuthContext}>
        <ToastProvider>
          {children}
        </ToastProvider>
      </AuthContext.Provider>
    </BrowserRouter>
  );
  return rtlRender(ui, { wrapper, ...options });
}

beforeEach(() => {
  // Clear any mock implementations and reset mocks
  vi.resetAllMocks();
  
  // Set up document body
  document.body.innerHTML = '<div id="root"></div>';
});

afterEach(() => {
  // Clean up after each test
  vi.restoreAllMocks();
});

describe('LoginPage Accessibility', () => {
  it('has proper semantic structure', () => {
    const { container } = render(<LoginPage />);
    
    // Check for proper semantic elements
    expect(container.querySelector('h2')).toBeInTheDocument();
    expect(container.querySelector('form')).toBeInTheDocument();
    expect(container.querySelectorAll('label').length).toBeGreaterThan(0);
    expect(container.querySelectorAll('input').length).toBeGreaterThan(0);
    expect(container.querySelectorAll('button').length).toBeGreaterThan(0);
    
    // Check for link to registration
    const links = container.querySelectorAll('a');
    const registerLink = Array.from(links).find(link => 
      link.textContent.includes('account') || link.textContent.includes('register')
    );
    expect(registerLink).toBeInTheDocument();
  });

  it('has proper form labels', () => {
    const { getAllByTestId } = render(<LoginPage />);
    
    // Get all the animated inputs
    const inputs = getAllByTestId('animated-input');
    
    // Check that we have the expected inputs
    expect(inputs.length).toBeGreaterThanOrEqual(2);
    
    // Check that the labels exist
    const emailInput = inputs.find(input => input.textContent.includes('Email'));
    const passwordInput = inputs.find(input => input.textContent.includes('Password'));
    
    expect(emailInput).toBeTruthy();
    expect(passwordInput).toBeTruthy();
  });

  it('has proper heading hierarchy', () => {
    const { container } = render(<LoginPage />);
    
    // Find the h2 element for sign in
    const signInHeading = container.querySelector('h2');
    expect(signInHeading).toBeInTheDocument();
    expect(signInHeading).toHaveTextContent(/sign in/i);
  });

  it('has proper ARIA attributes', () => {
    const { getByTestId } = render(<LoginPage />);
    
    // Check that the form and button have the right attributes
    const form = getByTestId('animated-form');
    expect(form).toBeInTheDocument();
    
    const submitButton = getByTestId('animated-button');
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  it('handles form validation properly', async () => {
    const { getByTestId, findAllByRole } = render(<LoginPage />);
    
    // Get the form and button
    const form = getByTestId('animated-form');
    
    // Submit the form
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    });
    
    // Find all error messages (there will be multiple)
    const errorMessages = await findAllByRole('alert');
    expect(errorMessages.length).toBeGreaterThanOrEqual(1);
    
    // Check that one of them is about email being required
    const emailError = errorMessages.find(el => 
      el.textContent.toLowerCase().includes('email is required')
    );
    expect(emailError).toBeTruthy();
  });

  it('validates form elements have proper attributes', () => {
    const { getAllByTestId } = render(<LoginPage />);
    
    const inputs = getAllByTestId('animated-input');
    inputs.forEach(input => {
      const inputElement = input.querySelector('input');
      const labelElement = input.querySelector('label');
      
      // Each input should have an aria-label
      expect(inputElement).toHaveAttribute('aria-label');
      
      // And a corresponding label element with matching text
      expect(labelElement).toBeInTheDocument();
      expect(labelElement.textContent).toBe(inputElement.getAttribute('aria-label'));
    });
  });

  it('supports proper account creation links', () => {
    const { container } = render(<LoginPage />);
    
    // Check for the account creation link
    const links = container.querySelectorAll('a');
    const signUpLink = Array.from(links).find(link => link.textContent.includes('Sign up'));
    
    expect(signUpLink).toBeInTheDocument();
    expect(signUpLink.getAttribute('href')).toBe('/register');
  });
});