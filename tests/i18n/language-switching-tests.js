/**
 * Language Switching Test Scenarios
 * End-to-end tests for dynamic language switching functionality
 */

describe('Language Switching Test Scenarios', () => {
  const BASE_URL = Cypress.env('baseUrl') || 'http://localhost:3000';
  
  beforeEach(() => {
    // Clear localStorage before each test
    cy.clearLocalStorage();
    
    // Mock API responses for different languages
    cy.intercept('GET', '/api/translations/*', { fixture: 'translations.json' });
    cy.intercept('GET', '/api/user/profile', { fixture: 'user-profile.json' });
    cy.intercept('PUT', '/api/user/language', { success: true });
    
    // Visit the application
    cy.visit('/');
  });

  describe('Basic Language Switching', () => {
    it('should switch from English to Spanish', () => {
      // Verify initial language is English
      cy.get('[data-testid="welcome-text"]').should('contain', 'Welcome');
      cy.get('html').should('have.attr', 'lang', 'en');
      
      // Open language selector
      cy.get('[data-testid="language-selector"]').click();
      
      // Select Spanish
      cy.get('[data-testid="language-option-es"]').click();
      
      // Verify language changed to Spanish
      cy.get('[data-testid="welcome-text"]').should('contain', 'Bienvenido');
      cy.get('html').should('have.attr', 'lang', 'es');
      
      // Verify localStorage is updated
      cy.window().its('localStorage').invoke('getItem', 'bdc_user_language')
        .should('equal', 'es');
    });

    it('should switch to Arabic and apply RTL layout', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Verify Arabic content
      cy.get('[data-testid="welcome-text"]').should('contain', 'مرحبا');
      
      // Verify RTL attributes
      cy.get('html').should('have.attr', 'dir', 'rtl');
      cy.get('html').should('have.attr', 'lang', 'ar');
      
      // Verify CSS direction
      cy.get('body').should('have.css', 'direction', 'rtl');
      
      // Check navigation alignment
      cy.get('[data-testid="main-navigation"]')
        .should('have.css', 'text-align', 'right');
    });

    it('should switch to Hebrew and maintain RTL layout', () => {
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Verify Hebrew content
      cy.get('[data-testid="welcome-text"]').should('contain', 'ברוך הבא');
      
      // Verify RTL layout
      cy.get('html').should('have.attr', 'dir', 'rtl');
      cy.get('html').should('have.attr', 'lang', 'he');
      cy.get('body').should('have.css', 'direction', 'rtl');
    });

    it('should switch between multiple languages rapidly', () => {
      const languages = [
        { code: 'es', text: 'Bienvenido' },
        { code: 'fr', text: 'Bienvenue' },
        { code: 'de', text: 'Willkommen' },
        { code: 'en', text: 'Welcome' }
      ];

      languages.forEach(({ code, text }) => {
        cy.get('[data-testid="language-selector"]').click();
        cy.get(`[data-testid="language-option-${code}"]`).click();
        cy.get('[data-testid="welcome-text"]').should('contain', text);
        cy.get('html').should('have.attr', 'lang', code);
      });
    });
  });

  describe('Page Navigation with Language Persistence', () => {
    it('should maintain language when navigating between pages', () => {
      // Set language to Spanish
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      // Navigate to dashboard
      cy.get('[data-testid="nav-dashboard"]').click();
      cy.url().should('include', '/dashboard');
      cy.get('[data-testid="dashboard-title"]').should('contain', 'Tablero');
      
      // Navigate to beneficiaries
      cy.get('[data-testid="nav-beneficiaries"]').click();
      cy.url().should('include', '/beneficiaries');
      cy.get('[data-testid="page-title"]').should('contain', 'Beneficiarios');
      
      // Verify language is still Spanish
      cy.get('html').should('have.attr', 'lang', 'es');
    });

    it('should persist language after page refresh', () => {
      // Set language to French
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-fr"]').click();
      
      // Verify French is active
      cy.get('[data-testid="welcome-text"]').should('contain', 'Bienvenue');
      
      // Refresh page
      cy.reload();
      
      // Verify language persisted
      cy.get('[data-testid="welcome-text"]').should('contain', 'Bienvenue');
      cy.get('html').should('have.attr', 'lang', 'fr');
    });

    it('should handle browser back/forward with language state', () => {
      // Start with English, navigate to page
      cy.get('[data-testid="nav-dashboard"]').click();
      
      // Change to Spanish
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      // Navigate to another page
      cy.get('[data-testid="nav-evaluations"]').click();
      cy.get('[data-testid="page-title"]').should('contain', 'Evaluaciones');
      
      // Go back
      cy.go('back');
      cy.get('[data-testid="dashboard-title"]').should('contain', 'Tablero');
      
      // Go forward
      cy.go('forward');
      cy.get('[data-testid="page-title"]').should('contain', 'Evaluaciones');
    });
  });

  describe('Form Interactions with Language Switching', () => {
    it('should update form labels when language changes', () => {
      // Navigate to a form page
      cy.visit('/register');
      
      // Verify English labels
      cy.get('[data-testid="email-label"]').should('contain', 'Email');
      cy.get('[data-testid="password-label"]').should('contain', 'Password');
      cy.get('[data-testid="submit-button"]').should('contain', 'Register');
      
      // Switch to Spanish
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      // Verify Spanish labels
      cy.get('[data-testid="email-label"]').should('contain', 'Correo electrónico');
      cy.get('[data-testid="password-label"]').should('contain', 'Contraseña');
      cy.get('[data-testid="submit-button"]').should('contain', 'Registrarse');
    });

    it('should show validation errors in selected language', () => {
      cy.visit('/register');
      
      // Switch to Spanish first
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      // Submit form without filling fields
      cy.get('[data-testid="submit-button"]').click();
      
      // Verify Spanish error messages
      cy.get('[data-testid="email-error"]')
        .should('contain', 'Correo electrónico es requerido');
      cy.get('[data-testid="password-error"]')
        .should('contain', 'Contraseña es requerido');
    });

    it('should handle placeholder text in different languages', () => {
      cy.visit('/search');
      
      // Check English placeholder
      cy.get('[data-testid="search-input"]')
        .should('have.attr', 'placeholder', 'Search...');
      
      // Switch to German
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-de"]').click();
      
      // Check German placeholder
      cy.get('[data-testid="search-input"]')
        .should('have.attr', 'placeholder', 'Suchen...');
    });
  });

  describe('Data Display with Language Switching', () => {
    it('should format dates according to locale', () => {
      cy.visit('/evaluations');
      
      // Mock evaluation data with dates
      cy.intercept('GET', '/api/evaluations', {
        data: [
          {
            id: 1,
            created_at: '2025-01-15T10:30:00Z',
            beneficiary: 'John Doe'
          }
        ]
      });
      
      // Check English date format (MM/DD/YYYY)
      cy.get('[data-testid="evaluation-date"]').should('contain', '01/15/2025');
      
      // Switch to German
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-de"]').click();
      
      // Check German date format (DD.MM.YYYY)
      cy.get('[data-testid="evaluation-date"]').should('contain', '15.01.2025');
    });

    it('should format numbers according to locale', () => {
      cy.visit('/statistics');
      
      // Mock statistics data
      cy.intercept('GET', '/api/statistics', {
        total_users: 1234,
        total_evaluations: 5678
      });
      
      // Check English number format
      cy.get('[data-testid="total-users"]').should('contain', '1,234');
      
      // Switch to French (uses space as thousand separator)
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-fr"]').click();
      
      // Check French number format
      cy.get('[data-testid="total-users"]').should('contain', '1 234');
    });

    it('should show currency in appropriate format', () => {
      cy.visit('/billing');
      
      // Start with USD for English
      cy.get('[data-testid="amount"]').should('contain', '$100.00');
      
      // Switch to Euro zone (German)
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-de"]').click();
      
      // Should show Euro format
      cy.get('[data-testid="amount"]').should('contain', '€100,00');
    });
  });

  describe('RTL Layout Behavior', () => {
    it('should properly align content in RTL mode', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check text alignment
      cy.get('[data-testid="main-content"]')
        .should('have.css', 'text-align', 'right');
      
      // Check sidebar position
      cy.get('[data-testid="sidebar"]')
        .should('have.css', 'float', 'right');
      
      // Check button alignment
      cy.get('[data-testid="action-buttons"]')
        .should('have.css', 'justify-content', 'flex-end');
    });

    it('should handle mixed LTR/RTL content properly', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check that English text within Arabic content maintains proper direction
      cy.get('[data-testid="mixed-content"]')
        .should('have.css', 'direction', 'rtl')
        .find('.english-text')
        .should('have.css', 'direction', 'ltr');
    });

    it('should flip icons and images appropriately', () => {
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check that directional icons are flipped
      cy.get('[data-testid="arrow-icon"]')
        .should('have.css', 'transform')
        .and('include', 'scaleX(-1)');
      
      // Check navigation arrows
      cy.get('[data-testid="next-button"]')
        .should('have.attr', 'data-direction', 'rtl');
    });
  });

  describe('User Preferences and API Integration', () => {
    it('should save language preference to user profile', () => {
      // Mock authenticated user
      cy.intercept('GET', '/api/user/profile', {
        id: 1,
        email: 'user@example.com',
        language: 'en'
      });
      
      // Mock language update API
      cy.intercept('PUT', '/api/user/language', { success: true }).as('updateLanguage');
      
      // Login first
      cy.visit('/login');
      cy.get('[data-testid="email-input"]').type('user@example.com');
      cy.get('[data-testid="password-input"]').type('password');
      cy.get('[data-testid="login-button"]').click();
      
      // Change language
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-fr"]').click();
      
      // Verify API was called
      cy.wait('@updateLanguage').then((interception) => {
        expect(interception.request.body).to.deep.equal({ language: 'fr' });
      });
    });

    it('should load user preferred language on login', () => {
      // Mock user with Spanish preference
      cy.intercept('GET', '/api/user/profile', {
        id: 1,
        email: 'user@example.com',
        language: 'es'
      });
      
      // Login
      cy.visit('/login');
      cy.get('[data-testid="email-input"]').type('user@example.com');
      cy.get('[data-testid="password-input"]').type('password');
      cy.get('[data-testid="login-button"]').click();
      
      // Verify Spanish is loaded
      cy.get('[data-testid="welcome-text"]').should('contain', 'Bienvenido');
      cy.get('html').should('have.attr', 'lang', 'es');
    });

    it('should handle API responses in different languages', () => {
      // Mock API responses with different languages
      cy.intercept('POST', '/api/evaluations', (req) => {
        const acceptLanguage = req.headers['accept-language'];
        if (acceptLanguage.includes('es')) {
          req.reply({
            success: true,
            message: 'Evaluación creada exitosamente'
          });
        } else {
          req.reply({
            success: true,
            message: 'Evaluation created successfully'
          });
        }
      }).as('createEvaluation');
      
      // Create evaluation in English
      cy.visit('/evaluations/new');
      cy.get('[data-testid="beneficiary-select"]').select('John Doe');
      cy.get('[data-testid="submit-button"]').click();
      
      cy.wait('@createEvaluation');
      cy.get('[data-testid="success-message"]')
        .should('contain', 'Evaluation created successfully');
      
      // Switch to Spanish and create another
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      cy.get('[data-testid="beneficiary-select"]').select('Juan Pérez');
      cy.get('[data-testid="submit-button"]').click();
      
      cy.wait('@createEvaluation');
      cy.get('[data-testid="success-message"]')
        .should('contain', 'Evaluación creada exitosamente');
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle missing translations gracefully', () => {
      // Mock incomplete translations
      cy.intercept('GET', '/api/translations/incomplete', {
        common: {
          welcome: 'Welcome'
          // Missing other keys
        }
      });
      
      // Switch to a language with missing translations
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-incomplete"]').click();
      
      // Should fallback to English or show key
      cy.get('[data-testid="missing-translation"]')
        .should('not.be.empty');
    });

    it('should handle slow translation loading', () => {
      // Mock slow translation API
      cy.intercept('GET', '/api/translations/es', (req) => {
        req.reply({ delay: 2000, fixture: 'translations-es.json' });
      });
      
      // Switch to Spanish
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-es"]').click();
      
      // Should show loading state
      cy.get('[data-testid="loading-indicator"]').should('be.visible');
      
      // Should eventually load Spanish
      cy.get('[data-testid="welcome-text"]', { timeout: 5000 })
        .should('contain', 'Bienvenido');
    });

    it('should handle network errors during language switch', () => {
      // Mock network error
      cy.intercept('GET', '/api/translations/fr', { forceNetworkError: true });
      
      // Switch to French
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-fr"]').click();
      
      // Should show error message or fallback
      cy.get('[data-testid="error-message"]')
        .should('contain', 'Failed to load language');
      
      // Should remain in previous language
      cy.get('html').should('have.attr', 'lang', 'en');
    });

    it('should validate language codes', () => {
      // Attempt to set invalid language via URL
      cy.visit('/?lang=invalid');
      
      // Should fallback to default language
      cy.get('html').should('have.attr', 'lang', 'en');
      cy.get('[data-testid="welcome-text"]').should('contain', 'Welcome');
    });
  });

  describe('Performance and Memory Management', () => {
    it('should not create memory leaks during rapid language switching', () => {
      // Rapidly switch between languages multiple times
      const languages = ['en', 'es', 'fr', 'de', 'ar'];
      
      for (let i = 0; i < 5; i++) {
        languages.forEach(lang => {
          cy.get('[data-testid="language-selector"]').click();
          cy.get(`[data-testid="language-option-${lang}"]`).click();
          cy.wait(100); // Brief pause
        });
      }
      
      // Should still be responsive
      cy.get('[data-testid="language-selector"]').should('be.visible');
      cy.get('[data-testid="welcome-text"]').should('not.be.empty');
    });

    it('should lazy load translations', () => {
      // Mock translation loading
      cy.intercept('GET', '/api/translations/ru', { fixture: 'translations-ru.json' }).as('loadRussian');
      
      // Initially Russian should not be loaded
      cy.window().its('i18n.store.data.ru').should('not.exist');
      
      // Switch to Russian
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ru"]').click();
      
      // Should load Russian translations
      cy.wait('@loadRussian');
      cy.window().its('i18n.store.data.ru').should('exist');
    });
  });
});