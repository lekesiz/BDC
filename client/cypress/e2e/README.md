# BDC E2E Test Suite Documentation

This comprehensive E2E test suite covers all critical user journeys and functionality in the BDC (Beneficiary Development Center) application.

## Test Architecture

### Test Categories

1. **Authentication Tests** (`auth-comprehensive.cy.js`)
   - Login/logout functionality
   - Role-based access control
   - Session management
   - Password reset flow
   - Security features

2. **Admin Dashboard Tests** (`admin-dashboard-comprehensive.cy.js`)
   - User management
   - System settings
   - Analytics and reporting
   - Tenant management
   - System monitoring

3. **Beneficiary Management Tests** (`beneficiary-management-comprehensive.cy.js`)
   - CRUD operations for beneficiaries
   - Bulk operations
   - Search and filtering
   - Data import/export
   - Advanced workflows

4. **Evaluation System Tests** (`evaluation-system-comprehensive.cy.js`)
   - Test creation and management
   - Taking evaluations
   - Grading and results
   - Question bank management
   - Proctoring features

5. **Calendar System Tests** (`calendar-system-comprehensive.cy.js`)
   - Appointment scheduling
   - Availability management
   - Notifications and reminders
   - Calendar integrations
   - Mobile interface

6. **Accessibility Tests** (`accessibility-comprehensive.cy.js`)
   - WCAG compliance
   - Keyboard navigation
   - Screen reader compatibility
   - Color contrast
   - Focus management

## Test Data Management

### Database Seeding

The test suite uses a comprehensive database seeding system to ensure consistent test data:

```javascript
// Automatic seeding before each test suite
beforeEach(() => {
  cy.clearDatabase();
  cy.seedDatabase();
  cy.waitForLoad();
});
```

### Test Users

Pre-seeded test users for different roles:

- **Admin**: `admin@bdc.test` / `Admin123!Test`
- **Tenant**: `tenant@bdc.test` / `Tenant123!Test`
- **Trainer**: `trainer@bdc.test` / `Trainer123!Test`
- **Student**: `student@bdc.test` / `Student123!Test`

### Custom Commands

Enhanced custom commands for common operations:

```javascript
// Enhanced login with session management
cy.loginAsAdmin();
cy.loginAsTrainer();
cy.loginAsStudent();

// Form helpers
cy.fillForm({ 'field-name': 'value' });
cy.selectDropdown('selector', 'value');
cy.uploadFile('selector', 'filename.pdf');

// Accessibility testing
cy.checkA11y();
cy.checkFocusManagement();
cy.checkAriaLabels();

// API testing
cy.authenticatedRequest('GET', '/api/beneficiaries', null, 'admin');
cy.createTestData('user', userData);
```

## Running Tests

### Local Development

```bash
# Run all tests
npm run cy:run

# Run specific test suite
npm run cy:run -- --spec "cypress/e2e/auth-comprehensive.cy.js"

# Run tests in browser (interactive mode)
npm run cy:open

# Run with custom configuration
CYPRESS_baseUrl=http://localhost:3000 npm run cy:run
```

### Using the Test Script

The comprehensive test runner script provides multiple options:

```bash
# Run all tests
./scripts/run-tests.sh all

# Run specific test categories
./scripts/run-tests.sh auth
./scripts/run-tests.sh admin
./scripts/run-tests.sh beneficiary
./scripts/run-tests.sh evaluation
./scripts/run-tests.sh calendar
./scripts/run-tests.sh accessibility

# Run smoke tests (critical journeys only)
./scripts/run-tests.sh smoke

# Run performance tests
./scripts/run-tests.sh performance

# Run with specific browser
CYPRESS_BROWSER=firefox ./scripts/run-tests.sh all

# Run in headed mode (visible browser)
CYPRESS_HEADLESS=false ./scripts/run-tests.sh auth
```

### CI/CD Pipeline

The GitHub Actions workflow runs tests automatically:

- **On Pull Requests**: Full test suite across multiple browsers
- **On Main Branch**: Complete regression testing
- **Scheduled**: Daily comprehensive testing
- **Matrix Testing**: Chrome, Firefox, Edge browsers with desktop/mobile viewports

## Test Patterns and Best Practices

### Page Object Model

Tests use a command-based approach rather than traditional page objects:

```javascript
// Instead of page objects, use semantic data attributes
cy.get('[data-cy=login-button]').click();
cy.get('[data-testid=user-menu]').should('be.visible');
```

### Data Attributes

All interactive elements should have data attributes:

```html
<!-- Preferred: data-cy for Cypress-specific selectors -->
<button data-cy="save-user-btn">Save</button>

<!-- Alternative: data-testid for general testing -->
<input data-testid="email-input" type="email" />
```

### Test Structure

Each test follows a consistent structure:

```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    // Setup: clear database, seed data, login
    cy.clearDatabase();
    cy.seedDatabase();
    cy.loginAsTrainer();
    cy.visit('/feature-page');
    cy.waitForLoad();
  });

  afterEach(() => {
    // Cleanup: dismiss notifications
    cy.dismissNotification();
  });

  describe('Sub-feature', () => {
    it('should perform specific action successfully', () => {
      // Test implementation
    });

    it('should handle error cases gracefully', () => {
      // Error testing
    });

    it('should be accessible', () => {
      cy.checkA11y();
    });
  });
});
```

## Accessibility Testing

### WCAG Compliance

All pages are tested for WCAG 2.1 AA compliance:

```javascript
cy.checkA11y(null, {
  runOnly: {
    type: 'tag',
    values: ['wcag2a', 'wcag2aa', 'section508']
  }
});
```

### Keyboard Navigation

Tests verify complete keyboard accessibility:

```javascript
cy.get('body').tab();
cy.focused().should('be.visible');
cy.focused().type('{enter}');
```

## Troubleshooting

### Common Issues

1. **Test Timeouts**
   ```javascript
   // Increase timeouts for slow operations
   cy.get('[data-cy=slow-element]', { timeout: 30000 }).should('be.visible');
   ```

2. **Flaky Tests**
   ```javascript
   // Use proper waiting strategies
   cy.intercept('GET', '/api/data').as('dataLoad');
   cy.wait('@dataLoad');
   cy.get('[data-cy=data-table]').should('be.visible');
   ```

### Debug Mode

Run tests in debug mode for troubleshooting:

```bash
# Open Cypress with debug logs
DEBUG=cypress:* npm run cy:open

# Run specific test with verbose output
npx cypress run --spec "cypress/e2e/test.cy.js" --config video=true
```