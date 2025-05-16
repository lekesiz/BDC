# Cypress E2E Tests

This directory contains end-to-end tests using Cypress.

## Structure

```
e2e/
├── auth.cy.js         # Authentication flow tests
├── beneficiaries.cy.js # Beneficiary management tests
├── complete-flow.cy.js # Complete user journey tests
└── README.md          # This file
```

## Running Tests

```bash
# Open Cypress Test Runner
npm run cypress:open

# Run tests headlessly
npm run cypress:run

# Run specific test file
npm run cypress:run -- --spec "cypress/e2e/auth.cy.js"
```

## Writing Tests

1. Create test file with `.cy.js` extension
2. Use descriptive test names
3. Use data-testid attributes for element selection
4. Mock API responses when needed
5. Test complete user flows

Example:
```javascript
describe('User Authentication', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('should login successfully', () => {
    cy.get('[data-testid=email-input]').type('user@example.com')
    cy.get('[data-testid=password-input]').type('password123')
    cy.get('[data-testid=login-button]').click()
    
    cy.url().should('include', '/dashboard')
    cy.contains('Welcome').should('be.visible')
  })
})
```

## Best Practices

1. Use data-testid attributes instead of CSS selectors
2. Keep tests independent
3. Use fixtures for test data
4. Test happy paths and error scenarios
5. Use custom commands for common actions
6. Avoid hard-coded waits

## Custom Commands

Custom commands are defined in `cypress/support/commands.js`:

```javascript
// Login command
cy.login(email, password)

// Create beneficiary
cy.createBeneficiary(data)

// Navigate to page
cy.navigateTo('dashboard')
```