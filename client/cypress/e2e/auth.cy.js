describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('allows user to login successfully', () => {
    cy.get('[data-cy=email-input]').type('trainer@example.com');
    cy.get('[data-cy=password-input]').type('password123');
    cy.get('[data-cy=login-button]').click();

    cy.url().should('eq', Cypress.config().baseUrl + '/');
    cy.get('[data-cy=user-menu]').should('contain', 'Trainer User');
  });

  it('shows error for invalid credentials', () => {
    cy.get('[data-cy=email-input]').type('invalid@example.com');
    cy.get('[data-cy=password-input]').type('wrongpassword');
    cy.get('[data-cy=login-button]').click();

    cy.get('[data-cy=error-message]').should('contain', 'Invalid credentials');
    cy.url().should('include', '/login');
  });

  it('validates form fields', () => {
    cy.get('[data-cy=login-button]').click();
    
    cy.get('[data-cy=email-error]').should('contain', 'Email is required');
    cy.get('[data-cy=password-error]').should('contain', 'Password is required');
  });

  it('allows user to logout', () => {
    // Login first
    cy.login('trainer@example.com', 'password123');
    
    cy.get('[data-cy=user-menu]').click();
    cy.get('[data-cy=logout-button]').click();
    
    cy.url().should('include', '/login');
    cy.get('[data-cy=login-button]').should('be.visible');
  });

  it('redirects to requested page after login', () => {
    cy.visit('/beneficiaries');
    cy.url().should('include', '/login');
    
    cy.get('[data-cy=email-input]').type('trainer@example.com');
    cy.get('[data-cy=password-input]').type('password123');
    cy.get('[data-cy=login-button]').click();
    
    cy.url().should('include', '/beneficiaries');
  });

  it('handles password reset flow', () => {
    cy.get('[data-cy=forgot-password-link]').click();
    cy.url().should('include', '/forgot-password');
    
    cy.get('[data-cy=email-input]').type('user@example.com');
    cy.get('[data-cy=reset-button]').click();
    
    cy.get('[data-cy=success-message]').should('contain', 'Password reset email sent');
  });

  it('persists authentication across page refreshes', () => {
    cy.login('trainer@example.com', 'password123');
    cy.reload();
    
    cy.get('[data-cy=user-menu]').should('contain', 'Trainer User');
    cy.url().should('not.include', '/login');
  });

  it('enforces role-based access', () => {
    // Login as student
    cy.login('student@example.com', 'password123');
    
    // Try to access admin page
    cy.visit('/users');
    cy.url().should('include', '/unauthorized');
    cy.get('[data-cy=error-message]').should('contain', 'You do not have permission');
  });
});