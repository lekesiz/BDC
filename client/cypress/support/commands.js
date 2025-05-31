// ***********************************************
// Enhanced custom commands for BDC application
// ***********************************************

import 'cypress-axe';

// Enhanced login with better error handling and validation
Cypress.Commands.add('login', (email, password, options = {}) => {
  const { skipSession = false, validateRedirect = true } = options;
  
  const loginFunc = () => {
    cy.visit('/login');
    cy.get('[data-cy=email-input]', { timeout: 10000 }).should('be.visible').clear().type(email);
    cy.get('[data-cy=password-input]').should('be.visible').clear().type(password);
    cy.get('[data-cy=login-button]').should('be.enabled').click();
    
    if (validateRedirect) {
      cy.url({ timeout: 15000 }).should('not.include', '/login');
      // Wait for authentication to be fully processed
      cy.get('[data-cy=user-menu]', { timeout: 10000 }).should('exist');
    }
  };

  if (skipSession) {
    loginFunc();
  } else {
    cy.session([email, password], loginFunc, {
      validate() {
        cy.visit('/');
        cy.get('[data-cy=user-menu]').should('exist');
      }
    });
  }
  
  if (!skipSession) {
    cy.visit('/');
  }
});

// Role-based login shortcuts with environment variables
Cypress.Commands.add('loginAsAdmin', (options = {}) => {
  cy.login(Cypress.env('adminEmail'), Cypress.env('adminPassword'), options);
});

Cypress.Commands.add('loginAsTenant', (options = {}) => {
  cy.login(Cypress.env('tenantEmail'), Cypress.env('tenantPassword'), options);
});

Cypress.Commands.add('loginAsTrainer', (options = {}) => {
  cy.login(Cypress.env('trainerEmail'), Cypress.env('trainerPassword'), options);
});

Cypress.Commands.add('loginAsStudent', (options = {}) => {
  cy.login(Cypress.env('studentEmail'), Cypress.env('studentPassword'), options);
});

// API testing helpers with enhanced error handling
Cypress.Commands.add('getToken', (email, password) => {
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: { email, password },
    failOnStatusCode: false
  }).then(response => {
    expect(response.status).to.eq(200);
    expect(response.body).to.have.property('token');
    return response.body.token;
  });
});

Cypress.Commands.add('apiLogin', (role) => {
  const credentials = {
    admin: { email: Cypress.env('adminEmail'), password: Cypress.env('adminPassword') },
    tenant: { email: Cypress.env('tenantEmail'), password: Cypress.env('tenantPassword') },
    trainer: { email: Cypress.env('trainerEmail'), password: Cypress.env('trainerPassword') },
    student: { email: Cypress.env('studentEmail'), password: Cypress.env('studentPassword') }
  };
  
  const { email, password } = credentials[role];
  return cy.getToken(email, password);
});

// Enhanced API request with authentication
Cypress.Commands.add('authenticatedRequest', (method, url, body = null, role = 'admin') => {
  return cy.apiLogin(role).then(token => {
    return cy.request({
      method,
      url: `${Cypress.env('apiUrl')}${url}`,
      headers: { Authorization: `Bearer ${token}` },
      body,
      failOnStatusCode: false
    });
  });
});

// Component testing helpers
Cypress.Commands.add('getByCy', (selector, options = {}) => {
  return cy.get(`[data-cy=${selector}]`, options);
});

Cypress.Commands.add('getByTestId', (selector, options = {}) => {
  return cy.get(`[data-testid=${selector}]`, options);
});

// Form helpers
Cypress.Commands.add('fillForm', (formData) => {
  Object.entries(formData).forEach(([field, value]) => {
    if (value !== null && value !== undefined) {
      cy.get(`[data-cy=${field}], [data-testid=${field}]`).clear().type(value.toString());
    }
  });
});

Cypress.Commands.add('selectDropdown', (selector, value) => {
  cy.get(`[data-cy=${selector}], [data-testid=${selector}]`).select(value);
});

// File upload helper
Cypress.Commands.add('uploadFile', (selector, fileName, fileType = 'application/pdf') => {
  cy.get(`[data-cy=${selector}], [data-testid=${selector}]`).selectFile({
    contents: Cypress.Buffer.from('file contents'),
    fileName,
    mimeType: fileType
  });
});

// Wait helpers
Cypress.Commands.add('waitForLoad', (timeout = 10000) => {
  cy.get('[data-cy=loading], [data-testid=loading]', { timeout: 1000 }).should('not.exist');
  cy.get('body').should('not.have.class', 'loading');
});

Cypress.Commands.add('waitForModal', (selector = '[data-cy=modal], [data-testid=modal]') => {
  cy.get(selector, { timeout: 10000 }).should('be.visible');
});

// Accessibility testing with enhanced options
Cypress.Commands.add('checkA11y', (context = null, options = {}) => {
  const defaultOptions = {
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'section508']
    },
    rules: {
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
      'focus-management': { enabled: true }
    }
  };
  
  cy.injectAxe();
  cy.checkA11y(context, { ...defaultOptions, ...options });
});

// Enhanced accessibility helpers
Cypress.Commands.add('checkFocusManagement', () => {
  // Check tab navigation
  cy.get('body').tab();
  cy.focused().should('have.attr', 'tabindex').should('not.equal', '-1');
});

Cypress.Commands.add('checkAriaLabels', () => {
  cy.get('button, input, select, textarea').each($el => {
    cy.wrap($el).should('satisfy', el => {
      return el.attr('aria-label') || el.attr('aria-labelledby') || el.text().trim() !== '';
    });
  });
});

// Database operations
Cypress.Commands.add('seedDatabase', () => {
  cy.task('seedDatabase');
});

Cypress.Commands.add('clearDatabase', () => {
  cy.task('clearDatabase');
});

Cypress.Commands.add('createTestData', (type, data) => {
  return cy.authenticatedRequest('POST', `/test/${type}`, data);
});

// Visual testing helpers
Cypress.Commands.add('matchImageSnapshot', (name, options = {}) => {
  const defaultOptions = {
    threshold: 0.1,
    thresholdType: 'percent'
  };
  cy.screenshot(name, { ...defaultOptions, ...options });
});

// Mobile testing helpers
Cypress.Commands.add('setMobileViewport', () => {
  cy.viewport(375, 667); // iPhone SE
});

Cypress.Commands.add('setTabletViewport', () => {
  cy.viewport(768, 1024); // iPad
});

Cypress.Commands.add('setDesktopViewport', () => {
  cy.viewport(1280, 720); // Desktop
});

// Performance testing
Cypress.Commands.add('measurePageLoad', () => {
  cy.window().then(win => {
    const performanceEntries = win.performance.getEntriesByType('navigation');
    const loadTime = performanceEntries[0].loadEventEnd - performanceEntries[0].loadEventStart;
    expect(loadTime).to.be.lessThan(3000); // 3 seconds max
  });
});

// Network simulation
Cypress.Commands.add('simulateSlowNetwork', () => {
  cy.intercept('**', (req) => {
    req.reply((res) => {
      res.delay(2000); // 2 second delay
    });
  });
});

// Error handling helpers
Cypress.Commands.add('handleUnexpectedErrors', () => {
  cy.window().then(win => {
    win.addEventListener('error', e => {
      cy.log(`Unexpected error: ${e.message}`);
      throw e;
    });
  });
});

// Logout helper
Cypress.Commands.add('logout', () => {
  cy.get('[data-cy=user-menu]').click();
  cy.get('[data-cy=logout-button]').click();
  cy.url().should('include', '/login');
});

// Notification helpers
Cypress.Commands.add('dismissNotification', () => {
  cy.get('[data-cy=notification-close], [data-testid=notification-close]', { timeout: 5000 })
    .if('visible')
    .click();
});

Cypress.Commands.add('verifyNotification', (message, type = 'success') => {
  cy.get(`[data-cy=notification-${type}], [data-testid=notification-${type}]`)
    .should('be.visible')
    .and('contain.text', message);
});