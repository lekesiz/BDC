/**
 * i18n Component Tests
 * Tests for React components with internationalization
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useTranslation, I18nextProvider } from 'react-i18next';
import '@testing-library/jest-dom';

import { 
  initTestI18n, 
  switchLanguage, 
  mockLocalStorage,
  checkRTLStyles,
  isRTL 
} from './utils.js';

// Mock components for testing
const WelcomeComponent = ({ name }) => {
  const { t } = useTranslation();
  return (
    <div data-testid="welcome-component">
      <h1>{t('common.welcome')}</h1>
      <p>{t('common.hello', { name })}</p>
    </div>
  );
};

const CounterComponent = ({ count }) => {
  const { t } = useTranslation();
  return (
    <div data-testid="counter-component">
      {t('common.items_count', { count })}
    </div>
  );
};

const AuthForm = () => {
  const { t } = useTranslation();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [errors, setErrors] = React.useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!email) {
      newErrors.email = t('validation.required', { field: t('auth.email') });
    }
    if (!password) {
      newErrors.password = t('validation.required', { field: t('auth.password') });
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  return (
    <form data-testid="auth-form">
      <div>
        <label htmlFor="email">{t('auth.email')}</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          data-testid="email-input"
        />
        {errors.email && (
          <span data-testid="email-error" className="error">
            {errors.email}
          </span>
        )}
      </div>
      
      <div>
        <label htmlFor="password">{t('auth.password')}</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          data-testid="password-input"
        />
        {errors.password && (
          <span data-testid="password-error" className="error">
            {errors.password}
          </span>
        )}
      </div>
      
      <button type="button" onClick={validateForm} data-testid="submit-button">
        {t('auth.login')}
      </button>
    </form>
  );
};

const RTLComponent = () => {
  const { t, i18n } = useTranslation();
  const isRTLLanguage = isRTL(i18n.language);
  
  return (
    <div 
      data-testid="rtl-component"
      dir={isRTLLanguage ? 'rtl' : 'ltr'}
      style={{
        textAlign: isRTLLanguage ? 'right' : 'left',
        direction: isRTLLanguage ? 'rtl' : 'ltr'
      }}
    >
      <p data-testid="rtl-text">{t('rtl_test.text_alignment')}</p>
      <p data-testid="mixed-content">{t('rtl_test.mixed_content')}</p>
      <p data-testid="number-format">{t('rtl_test.number_format', { number: 12345 })}</p>
    </div>
  );
};

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  
  const changeLanguage = (lang) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div data-testid="language-switcher">
      <button onClick={() => changeLanguage('en')} data-testid="lang-en">
        English
      </button>
      <button onClick={() => changeLanguage('es')} data-testid="lang-es">
        Español
      </button>
      <button onClick={() => changeLanguage('ar')} data-testid="lang-ar">
        العربية
      </button>
      <button onClick={() => changeLanguage('he')} data-testid="lang-he">
        עברית
      </button>
      <span data-testid="current-lang">{i18n.language}</span>
    </div>
  );
};

const DashboardComponent = ({ userName }) => {
  const { t } = useTranslation();
  
  return (
    <div data-testid="dashboard">
      <h1>{t('dashboard.title')}</h1>
      <p data-testid="welcome-message">
        {t('dashboard.welcome_back', { name: userName })}
      </p>
      <div data-testid="statistics">{t('dashboard.statistics')}</div>
      <div data-testid="recent-activity">{t('dashboard.recent_activity')}</div>
    </div>
  );
};

// Test wrapper component
const TestWrapper = ({ children, language = 'en' }) => {
  const i18n = initTestI18n(language);
  
  return (
    <I18nextProvider i18n={i18n}>
      {children}
    </I18nextProvider>
  );
};

describe('i18n Component Tests', () => {
  let mockStorage;

  beforeEach(() => {
    mockStorage = mockLocalStorage();
    Object.defineProperty(window, 'localStorage', {
      value: mockStorage,
      writable: true
    });
  });

  describe('Basic Translation Tests', () => {
    test('renders welcome component in English', () => {
      render(
        <TestWrapper language="en">
          <WelcomeComponent name="John" />
        </TestWrapper>
      );

      expect(screen.getByText('Welcome')).toBeInTheDocument();
      expect(screen.getByText('Hello John')).toBeInTheDocument();
    });

    test('renders welcome component in Spanish', () => {
      render(
        <TestWrapper language="es">
          <WelcomeComponent name="Juan" />
        </TestWrapper>
      );

      expect(screen.getByText('Bienvenido')).toBeInTheDocument();
      expect(screen.getByText('Hola Juan')).toBeInTheDocument();
    });

    test('renders welcome component in Arabic', () => {
      render(
        <TestWrapper language="ar">
          <WelcomeComponent name="أحمد" />
        </TestWrapper>
      );

      expect(screen.getByText('مرحبا')).toBeInTheDocument();
      expect(screen.getByText('مرحبا أحمد')).toBeInTheDocument();
    });
  });

  describe('Pluralization Tests', () => {
    test('handles singular form in English', () => {
      render(
        <TestWrapper language="en">
          <CounterComponent count={1} />
        </TestWrapper>
      );

      expect(screen.getByText('1 item')).toBeInTheDocument();
    });

    test('handles plural form in English', () => {
      render(
        <TestWrapper language="en">
          <CounterComponent count={5} />
        </TestWrapper>
      );

      expect(screen.getByText('5 items')).toBeInTheDocument();
    });

    test('handles Spanish pluralization', () => {
      render(
        <TestWrapper language="es">
          <CounterComponent count={1} />
        </TestWrapper>
      );

      expect(screen.getByText('1 artículo')).toBeInTheDocument();

      render(
        <TestWrapper language="es">
          <CounterComponent count={3} />
        </TestWrapper>
      );

      expect(screen.getByText('3 artículos')).toBeInTheDocument();
    });

    test('handles Arabic complex pluralization', () => {
      const { rerender } = render(
        <TestWrapper language="ar">
          <CounterComponent count={0} />
        </TestWrapper>
      );

      expect(screen.getByText('لا توجد عناصر')).toBeInTheDocument();

      rerender(
        <TestWrapper language="ar">
          <CounterComponent count={1} />
        </TestWrapper>
      );

      expect(screen.getByText('عنصر واحد')).toBeInTheDocument();

      rerender(
        <TestWrapper language="ar">
          <CounterComponent count={2} />
        </TestWrapper>
      );

      expect(screen.getByText('عنصران')).toBeInTheDocument();
    });
  });

  describe('Form Validation Tests', () => {
    test('shows validation errors in English', async () => {
      render(
        <TestWrapper language="en">
          <AuthForm />
        </TestWrapper>
      );

      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('email-error')).toHaveTextContent('Email is required');
        expect(screen.getByTestId('password-error')).toHaveTextContent('Password is required');
      });
    });

    test('shows validation errors in Spanish', async () => {
      render(
        <TestWrapper language="es">
          <AuthForm />
        </TestWrapper>
      );

      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('email-error')).toHaveTextContent('Correo electrónico es requerido');
        expect(screen.getByTestId('password-error')).toHaveTextContent('Contraseña es requerido');
      });
    });

    test('displays form labels in correct language', () => {
      const { rerender } = render(
        <TestWrapper language="en">
          <AuthForm />
        </TestWrapper>
      );

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByText('Login')).toBeInTheDocument();

      rerender(
        <TestWrapper language="es">
          <AuthForm />
        </TestWrapper>
      );

      expect(screen.getByLabelText('Correo electrónico')).toBeInTheDocument();
      expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
      expect(screen.getByText('Iniciar sesión')).toBeInTheDocument();
    });
  });

  describe('RTL Layout Tests', () => {
    test('applies RTL styles for Arabic', () => {
      render(
        <TestWrapper language="ar">
          <RTLComponent />
        </TestWrapper>
      );

      const component = screen.getByTestId('rtl-component');
      expect(component).toHaveAttribute('dir', 'rtl');
      expect(component).toHaveStyle('direction: rtl');
      expect(component).toHaveStyle('text-align: right');
    });

    test('applies LTR styles for English', () => {
      render(
        <TestWrapper language="en">
          <RTLComponent />
        </TestWrapper>
      );

      const component = screen.getByTestId('rtl-component');
      expect(component).toHaveAttribute('dir', 'ltr');
      expect(component).toHaveStyle('direction: ltr');
      expect(component).toHaveStyle('text-align: left');
    });

    test('applies RTL styles for Hebrew', () => {
      render(
        <TestWrapper language="he">
          <RTLComponent />
        </TestWrapper>
      );

      const component = screen.getByTestId('rtl-component');
      expect(component).toHaveAttribute('dir', 'rtl');
      expect(component).toHaveStyle('direction: rtl');
      expect(component).toHaveStyle('text-align: right');
    });

    test('displays mixed content correctly', () => {
      render(
        <TestWrapper language="ar">
          <RTLComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('mixed-content')).toHaveTextContent('نص عربي مع English مختلط');
    });
  });

  describe('Language Switching Tests', () => {
    test('switches language dynamically', async () => {
      const TestComponent = () => (
        <TestWrapper language="en">
          <LanguageSwitcher />
          <WelcomeComponent name="Test" />
        </TestWrapper>
      );

      render(<TestComponent />);

      // Initial state
      expect(screen.getByText('Welcome')).toBeInTheDocument();
      expect(screen.getByTestId('current-lang')).toHaveTextContent('en');

      // Switch to Spanish
      fireEvent.click(screen.getByTestId('lang-es'));

      await waitFor(() => {
        expect(screen.getByText('Bienvenido')).toBeInTheDocument();
        expect(screen.getByTestId('current-lang')).toHaveTextContent('es');
      });

      // Switch to Arabic
      fireEvent.click(screen.getByTestId('lang-ar'));

      await waitFor(() => {
        expect(screen.getByText('مرحبا')).toBeInTheDocument();
        expect(screen.getByTestId('current-lang')).toHaveTextContent('ar');
      });
    });

    test('persists language choice in localStorage', async () => {
      render(
        <TestWrapper language="en">
          <LanguageSwitcher />
        </TestWrapper>
      );

      fireEvent.click(screen.getByTestId('lang-es'));

      await waitFor(() => {
        expect(mockStorage.getItem('bdc_user_language')).toBe('es');
      });
    });
  });

  describe('Dashboard Component Tests', () => {
    test('renders dashboard in multiple languages', () => {
      const { rerender } = render(
        <TestWrapper language="en">
          <DashboardComponent userName="John" />
        </TestWrapper>
      );

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByTestId('welcome-message')).toHaveTextContent('Welcome back, John!');

      rerender(
        <TestWrapper language="es">
          <DashboardComponent userName="Juan" />
        </TestWrapper>
      );

      expect(screen.getByText('Tablero')).toBeInTheDocument();
      expect(screen.getByTestId('welcome-message')).toHaveTextContent('¡Bienvenido de nuevo, Juan!');
    });

    test('handles missing translations gracefully', () => {
      // Test with a language that has incomplete translations
      render(
        <TestWrapper language="de">
          <DashboardComponent userName="Hans" />
        </TestWrapper>
      );

      // Should fallback to English for missing translations
      expect(screen.getByTestId('welcome-message')).toHaveTextContent('Welcome back, Hans!');
    });
  });

  describe('Edge Cases', () => {
    test('handles empty translation values', () => {
      const i18n = initTestI18n('en');
      i18n.addResource('en', 'translation', 'empty.key', '');

      render(
        <I18nextProvider i18n={i18n}>
          <div>{i18n.t('empty.key')}</div>
        </I18nextProvider>
      );

      expect(screen.getByText('empty.key')).toBeInTheDocument();
    });

    test('handles missing interpolation variables', () => {
      render(
        <TestWrapper language="en">
          <div data-testid="test">{initTestI18n().t('common.hello')}</div>
        </TestWrapper>
      );

      expect(screen.getByTestId('test')).toHaveTextContent('Hello {{name}}');
    });

    test('handles invalid language codes', () => {
      render(
        <TestWrapper language="invalid">
          <WelcomeComponent name="Test" />
        </TestWrapper>
      );

      // Should fallback to English
      expect(screen.getByText('Welcome')).toBeInTheDocument();
    });
  });

  describe('Performance Tests', () => {
    test('does not re-render unnecessarily on language change', () => {
      let renderCount = 0;
      
      const CountingComponent = () => {
        renderCount++;
        const { t } = useTranslation();
        return <div>{t('common.welcome')}</div>;
      };

      const { rerender } = render(
        <TestWrapper language="en">
          <CountingComponent />
        </TestWrapper>
      );

      const initialRenderCount = renderCount;

      rerender(
        <TestWrapper language="es">
          <CountingComponent />
        </TestWrapper>
      );

      expect(renderCount).toBe(initialRenderCount + 1);
    });
  });

  describe('Accessibility Tests', () => {
    test('sets correct lang attribute for screen readers', () => {
      render(
        <TestWrapper language="ar">
          <RTLComponent />
        </TestWrapper>
      );

      const component = screen.getByTestId('rtl-component');
      expect(component.closest('div')).toHaveAttribute('dir', 'rtl');
    });

    test('provides proper form labels for all languages', () => {
      render(
        <TestWrapper language="ar">
          <AuthForm />
        </TestWrapper>
      );

      expect(screen.getByLabelText('البريد الإلكتروني')).toBeInTheDocument();
      expect(screen.getByLabelText('كلمة المرور')).toBeInTheDocument();
    });
  });
});