describe('Comprehensive Authentication Flow', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.visit('/login');
  });

  afterEach(() => {
    cy.dismissNotification();
  });

  describe('Login Flow', () => {
    it('should login with valid credentials and redirect based on role', () => {
      // Test admin login and redirection
      cy.get('[data-cy=email-input]').type(Cypress.env('adminEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('adminPassword'));
      cy.get('[data-cy=login-button]').click();

      cy.url({ timeout: 15000 }).should('include', '/admin/dashboard');
      cy.get('[data-cy=user-menu]').should('contain', 'Admin');
      
      cy.logout();

      // Test trainer login and redirection
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('trainerPassword'));
      cy.get('[data-cy=login-button]').click();

      cy.url({ timeout: 15000 }).should('include', '/dashboard');
      cy.get('[data-cy=user-menu]').should('contain', 'Trainer');
      
      cy.logout();

      // Test student login and redirection
      cy.get('[data-cy=email-input]').type(Cypress.env('studentEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('studentPassword'));
      cy.get('[data-cy=login-button]').click();

      cy.url({ timeout: 15000 }).should('include', '/portal');
      cy.get('[data-cy=user-menu]').should('contain', 'Student');
    });

    it('should handle invalid credentials gracefully', () => {
      cy.get('[data-cy=email-input]').type('invalid@test.com');
      cy.get('[data-cy=password-input]').type('wrongpassword');
      cy.get('[data-cy=login-button]').click();

      cy.get('[data-cy=error-message]')
        .should('be.visible')
        .and('contain', 'Invalid credentials');
      cy.url().should('include', '/login');
    });

    it('should validate form fields with appropriate error messages', () => {
      // Test empty form submission
      cy.get('[data-cy=login-button]').click();
      
      cy.get('[data-cy=email-error]').should('contain', 'Email is required');
      cy.get('[data-cy=password-error]').should('contain', 'Password is required');

      // Test invalid email format
      cy.get('[data-cy=email-input]').type('invalid-email');
      cy.get('[data-cy=login-button]').click();
      cy.get('[data-cy=email-error]').should('contain', 'Invalid email format');

      // Test valid email, empty password
      cy.get('[data-cy=email-input]').clear().type('user@test.com');
      cy.get('[data-cy=login-button]').click();
      cy.get('[data-cy=password-error]').should('contain', 'Password is required');
    });

    it('should handle account lockout after multiple failed attempts', () => {
      const invalidCredentials = { email: 'user@test.com', password: 'wrongpassword' };
      
      // Attempt login 5 times with wrong password
      for (let i = 0; i < 5; i++) {
        cy.get('[data-cy=email-input]').clear().type(invalidCredentials.email);
        cy.get('[data-cy=password-input]').clear().type(invalidCredentials.password);
        cy.get('[data-cy=login-button]').click();
        cy.wait(1000);
      }

      // Should show account locked message
      cy.get('[data-cy=error-message]')
        .should('contain', 'Account temporarily locked');
    });

    it('should redirect to requested page after successful login', () => {
      // Try to access protected page
      cy.visit('/beneficiaries');
      cy.url().should('include', '/login');
      cy.url().should('include', 'redirect=');

      // Login and verify redirection
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('trainerPassword'));
      cy.get('[data-cy=login-button]').click();

      cy.url({ timeout: 15000 }).should('include', '/beneficiaries');
    });

    it('should handle session expiration gracefully', () => {
      cy.loginAsTrainer();
      
      // Simulate token expiration by intercepting API calls
      cy.intercept('GET', '**/api/**', {
        statusCode: 401,
        body: { message: 'Token expired' }
      }).as('expiredToken');

      cy.visit('/beneficiaries');
      cy.wait('@expiredToken');

      // Should redirect to login with session expired message
      cy.url().should('include', '/login');
      cy.get('[data-cy=session-expired-message]')
        .should('contain', 'Your session has expired');
    });
  });

  describe('Registration Flow', () => {
    beforeEach(() => {
      cy.visit('/register');
    });

    it('should allow new user registration with complete flow', () => {
      const newUser = {
        username: `testuser_${Date.now()}`,
        email: `test_${Date.now()}@example.com`,
        password: 'TestPassword123!',
        firstName: 'Test',
        lastName: 'User',
        role: 'student'
      };

      cy.fillForm({
        'register-username': newUser.username,
        'register-email': newUser.email,
        'register-password': newUser.password,
        'register-confirm-password': newUser.password,
        'register-firstname': newUser.firstName,
        'register-lastname': newUser.lastName
      });

      cy.selectDropdown('register-role', newUser.role);
      cy.get('[data-cy=terms-checkbox]').check();
      cy.get('[data-cy=register-submit]').click();

      // Should redirect to welcome page or dashboard
      cy.url({ timeout: 15000 }).should('not.include', '/register');
      cy.verifyNotification('Registration successful');
    });

    it('should validate registration form fields', () => {
      cy.get('[data-cy=register-submit]').click();

      // Check all required field errors
      cy.get('[data-cy=username-error]').should('contain', 'Username is required');
      cy.get('[data-cy=email-error]').should('contain', 'Email is required');
      cy.get('[data-cy=password-error]').should('contain', 'Password is required');
      cy.get('[data-cy=firstname-error]').should('contain', 'First name is required');
      cy.get('[data-cy=lastname-error]').should('contain', 'Last name is required');

      // Test password strength validation
      cy.get('[data-cy=register-password]').type('weak');
      cy.get('[data-cy=password-error]').should('contain', 'Password must be at least 8 characters');

      cy.get('[data-cy=register-password]').clear().type('password123');
      cy.get('[data-cy=password-error]').should('contain', 'Password must contain uppercase letter');

      cy.get('[data-cy=register-password]').clear().type('Password123');
      cy.get('[data-cy=password-error]').should('contain', 'Password must contain special character');

      // Test password confirmation
      cy.get('[data-cy=register-password]').clear().type('Password123!');
      cy.get('[data-cy=register-confirm-password]').type('DifferentPassword123!');
      cy.get('[data-cy=confirm-password-error]').should('contain', 'Passwords do not match');
    });

    it('should handle duplicate email registration', () => {
      cy.fillForm({
        'register-username': 'newuser',
        'register-email': Cypress.env('trainerEmail'), // Use existing email
        'register-password': 'Password123!',
        'register-confirm-password': 'Password123!',
        'register-firstname': 'Test',
        'register-lastname': 'User'
      });

      cy.selectDropdown('register-role', 'student');
      cy.get('[data-cy=terms-checkbox]').check();
      cy.get('[data-cy=register-submit]').click();

      cy.get('[data-cy=error-message]')
        .should('contain', 'Email already exists');
    });
  });

  describe('Password Reset Flow', () => {
    it('should handle forgot password flow', () => {
      cy.get('[data-cy=forgot-password-link]').click();
      cy.url().should('include', '/forgot-password');

      // Request password reset
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=reset-button]').click();

      cy.verifyNotification('Password reset email sent');
    });

    it('should validate email for password reset', () => {
      cy.get('[data-cy=forgot-password-link]').click();
      
      // Test empty email
      cy.get('[data-cy=reset-button]').click();
      cy.get('[data-cy=email-error]').should('contain', 'Email is required');

      // Test invalid email format
      cy.get('[data-cy=email-input]').type('invalid-email');
      cy.get('[data-cy=reset-button]').click();
      cy.get('[data-cy=email-error]').should('contain', 'Invalid email format');

      // Test non-existent email
      cy.get('[data-cy=email-input]').clear().type('nonexistent@test.com');
      cy.get('[data-cy=reset-button]').click();
      cy.get('[data-cy=error-message]').should('contain', 'Email not found');
    });
  });

  describe('Session Management', () => {
    it('should persist authentication across page refreshes', () => {
      cy.loginAsTrainer();
      cy.get('[data-cy=user-menu]').should('exist');
      
      cy.reload();
      cy.get('[data-cy=user-menu]').should('exist');
      cy.url().should('not.include', '/login');
    });

    it('should handle multiple tab sessions', () => {
      cy.loginAsTrainer();
      
      // Open new tab and verify session persists
      cy.window().then(win => {
        win.open('/dashboard', '_blank');
      });
      
      // Original tab should still be authenticated
      cy.get('[data-cy=user-menu]').should('exist');
    });

    it('should auto-logout on session timeout', () => {
      cy.loginAsTrainer();
      
      // Mock session timeout
      cy.window().then(win => {
        win.localStorage.removeItem('authToken');
        win.sessionStorage.removeItem('authToken');
      });
      
      cy.visit('/beneficiaries');
      cy.url().should('include', '/login');
    });
  });

  describe('Role-Based Access Control', () => {
    it('should enforce admin-only access', () => {
      cy.loginAsStudent();
      
      // Try to access admin page
      cy.visit('/admin/users');
      cy.url().should('include', '/unauthorized');
      cy.get('[data-cy=error-message]')
        .should('contain', 'You do not have permission to access this page');
    });

    it('should enforce trainer-only access', () => {
      cy.loginAsStudent();
      
      // Try to access trainer page
      cy.visit('/programs/create');
      cy.url().should('include', '/unauthorized');
      cy.get('[data-cy=error-message]')
        .should('contain', 'You do not have permission');
    });

    it('should allow proper role access', () => {
      // Admin should access admin pages
      cy.loginAsAdmin();
      cy.visit('/admin/users');
      cy.url().should('include', '/admin/users');
      cy.logout();

      // Trainer should access trainer pages
      cy.loginAsTrainer();
      cy.visit('/programs');
      cy.url().should('include', '/programs');
      cy.logout();

      // Student should access portal pages
      cy.loginAsStudent();
      cy.visit('/portal/courses');
      cy.url().should('include', '/portal/courses');
    });
  });

  describe('Security Features', () => {
    it('should protect against XSS in login form', () => {
      const xssPayload = '<script>alert("xss")</script>';
      
      cy.get('[data-cy=email-input]').type(xssPayload);
      cy.get('[data-cy=password-input]').type(xssPayload);
      cy.get('[data-cy=login-button]').click();

      // Should not execute script
      cy.window().then(win => {
        expect(win.document.body.innerHTML).not.to.contain('<script>');
      });
    });

    it('should enforce HTTPS redirect in production', () => {
      // This would be tested in actual production environment
      cy.log('HTTPS redirect testing would be environment-specific');
    });

    it('should clear sensitive data on logout', () => {
      cy.loginAsTrainer();
      
      cy.window().then(win => {
        expect(win.localStorage.getItem('authToken')).to.exist;
      });
      
      cy.logout();
      
      cy.window().then(win => {
        expect(win.localStorage.getItem('authToken')).to.be.null;
        expect(win.sessionStorage.getItem('authToken')).to.be.null;
      });
    });
  });

  describe('Accessibility in Authentication', () => {
    it('should be accessible with keyboard navigation', () => {
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-cy', 'email-input');
      
      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'password-input');
      
      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'login-button');
    });

    it('should have proper ARIA labels and roles', () => {
      cy.checkAriaLabels();
      cy.get('[data-cy=email-input]').should('have.attr', 'aria-label');
      cy.get('[data-cy=password-input]').should('have.attr', 'aria-label');
      cy.get('[data-cy=login-button]').should('have.attr', 'role', 'button');
    });

    it('should meet WCAG accessibility standards', () => {
      cy.checkA11y();
    });
  });

  describe('Performance and Network Conditions', () => {
    it('should handle slow network conditions', () => {
      cy.simulateSlowNetwork();
      
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('trainerPassword'));
      cy.get('[data-cy=login-button]').click();

      // Should show loading state
      cy.get('[data-cy=loading-spinner]').should('be.visible');
      
      // Should eventually succeed
      cy.url({ timeout: 30000 }).should('not.include', '/login');
    });

    it('should handle network errors gracefully', () => {
      cy.intercept('POST', '**/auth/login', { statusCode: 500 }).as('loginError');
      
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('trainerPassword'));
      cy.get('[data-cy=login-button]').click();

      cy.wait('@loginError');
      cy.get('[data-cy=error-message]')
        .should('contain', 'Login failed. Please try again.');
    });

    it('should measure login performance', () => {
      cy.get('[data-cy=email-input]').type(Cypress.env('trainerEmail'));
      cy.get('[data-cy=password-input]').type(Cypress.env('trainerPassword'));
      
      const startTime = Date.now();
      cy.get('[data-cy=login-button]').click();
      
      cy.url({ timeout: 15000 }).should('not.include', '/login').then(() => {
        const endTime = Date.now();
        const loginTime = endTime - startTime;
        expect(loginTime).to.be.lessThan(5000); // Login should take less than 5 seconds
      });
    });
  });
});