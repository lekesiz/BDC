import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../../pages/auth/LoginPage';

expect.extend(toHaveNoViolations);

describe('LoginPage Accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper form labels', () => {
    const { getByLabelText } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    expect(getByLabelText(/email/i)).toBeInTheDocument();
    expect(getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('has proper heading hierarchy', () => {
    const { container } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const h1Elements = container.querySelectorAll('h1');
    const h2Elements = container.querySelectorAll('h2');
    
    expect(h1Elements).toHaveLength(1);
    expect(h1Elements[0]).toHaveTextContent(/sign in/i);
  });

  it('has proper ARIA attributes', () => {
    const { getByRole } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const submitButton = getByRole('button', { name: /sign in/i });
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  it('has keyboard navigation support', () => {
    const { getByLabelText, getByRole } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const emailInput = getByLabelText(/email/i);
    const passwordInput = getByLabelText(/password/i);
    const submitButton = getByRole('button', { name: /sign in/i });
    
    emailInput.focus();
    expect(document.activeElement).toBe(emailInput);
    
    emailInput.blur();
    passwordInput.focus();
    expect(document.activeElement).toBe(passwordInput);
    
    passwordInput.blur();
    submitButton.focus();
    expect(document.activeElement).toBe(submitButton);
  });

  it('has proper error announcements', async () => {
    const { getByRole, findByRole } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const submitButton = getByRole('button', { name: /sign in/i });
    submitButton.click();
    
    const alert = await findByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveAttribute('aria-live', 'polite');
  });

  it('has sufficient color contrast', async () => {
    const { container } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true }
      }
    });
    
    expect(results).toHaveNoViolations();
  });

  it('supports screen reader navigation', () => {
    const { getByRole, getByText } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    expect(getByRole('main')).toBeInTheDocument();
    expect(getByRole('form')).toBeInTheDocument();
    expect(getByText(/don't have an account/i)).toBeInTheDocument();
  });
});