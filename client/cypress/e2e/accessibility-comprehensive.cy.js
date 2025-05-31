describe('Comprehensive Accessibility Testing', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.waitForLoad();
  });

  describe('Authentication Pages Accessibility', () => {
    it('should meet WCAG standards on login page', () => {
      cy.visit('/login');
      cy.waitForLoad();

      // Check overall WCAG compliance
      cy.checkA11y();

      // Specific accessibility checks
      cy.get('[data-cy=email-input]').should('have.attr', 'aria-label');
      cy.get('[data-cy=password-input]').should('have.attr', 'aria-label');
      cy.get('[data-cy=login-button]').should('have.attr', 'aria-describedby');

      // Check form labels
      cy.get('label[for="email"]').should('exist');
      cy.get('label[for="password"]').should('exist');

      // Check error message accessibility
      cy.get('[data-cy=login-button]').click();
      cy.get('[data-cy=email-error]').should('have.attr', 'role', 'alert');
      cy.get('[data-cy=password-error]').should('have.attr', 'role', 'alert');
    });

    it('should support keyboard navigation on login page', () => {
      cy.visit('/login');
      cy.waitForLoad();

      // Tab through form elements
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-cy', 'email-input');

      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'password-input');

      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'login-button');

      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'forgot-password-link');

      // Test reverse tab navigation
      cy.focused().tab({ shift: true });
      cy.focused().should('have.attr', 'data-cy', 'login-button');
    });

    it('should provide proper focus management on registration page', () => {
      cy.visit('/register');
      cy.waitForLoad();

      cy.checkA11y();

      // Check focus order
      const expectedOrder = [
        'register-username',
        'register-email',
        'register-password',
        'register-confirm-password',
        'register-firstname',
        'register-lastname',
        'register-role',
        'terms-checkbox',
        'register-submit'
      ];

      let currentIndex = 0;
      cy.get('body').tab();

      expectedOrder.forEach(expectedElement => {
        cy.focused().should('have.attr', 'data-cy', expectedElement);
        if (currentIndex < expectedOrder.length - 1) {
          cy.focused().tab();
          currentIndex++;
        }
      });
    });

    it('should announce errors properly with screen readers', () => {
      cy.visit('/login');
      cy.waitForLoad();

      // Submit form to trigger errors
      cy.get('[data-cy=login-button]').click();

      // Check aria-live regions
      cy.get('[data-cy=error-summary]').should('have.attr', 'aria-live', 'assertive');
      cy.get('[data-cy=email-error]').should('have.attr', 'aria-live', 'polite');

      // Check error association
      cy.get('[data-cy=email-input]').should('have.attr', 'aria-describedby');
      cy.get('[data-cy=password-input]').should('have.attr', 'aria-describedby');
    });
  });

  describe('Dashboard Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();
    });

    it('should meet WCAG standards for dashboard layout', () => {
      cy.checkA11y();

      // Check landmark roles
      cy.get('header').should('have.attr', 'role', 'banner');
      cy.get('nav').should('have.attr', 'role', 'navigation');
      cy.get('main').should('have.attr', 'role', 'main');
      cy.get('aside').should('have.attr', 'role', 'complementary');

      // Check heading hierarchy
      cy.get('h1').should('have.length', 1);
      cy.get('h2').should('exist');
      
      // Verify no skipped heading levels
      cy.get('h1, h2, h3, h4, h5, h6').then($headings => {
        const levels = Array.from($headings).map(h => parseInt(h.tagName.charAt(1)));
        for (let i = 1; i < levels.length; i++) {
          expect(levels[i] - levels[i-1]).to.be.at.most(1);
        }
      });
    });

    it('should support keyboard navigation for dashboard widgets', () => {
      // Test widget focus
      cy.get('[data-cy=dashboard-widget]').first().focus();
      cy.focused().should('be.visible');

      // Test widget keyboard interaction
      cy.focused().type('{enter}');
      // Widget should expand or show details

      // Test widget navigation
      cy.focused().type('{rightarrow}');
      cy.focused().should('not.be', cy.get('[data-cy=dashboard-widget]').first());
    });

    it('should provide proper ARIA labels for interactive elements', () => {
      // Check navigation items
      cy.get('[data-cy=nav-item]').each($item => {
        cy.wrap($item).should('have.attr', 'aria-label');
      });

      // Check action buttons
      cy.get('[data-cy=action-button]').each($button => {
        cy.wrap($button).should('satisfy', $el => {
          return $el.attr('aria-label') || $el.text().trim() !== '';
        });
      });

      // Check dropdown menus
      cy.get('[data-cy=dropdown-trigger]').each($dropdown => {
        cy.wrap($dropdown).should('have.attr', 'aria-haspopup', 'true');
        cy.wrap($dropdown).should('have.attr', 'aria-expanded');
      });
    });

    it('should announce dynamic content changes', () => {
      // Check live regions for notifications
      cy.get('[data-cy=notification-area]').should('have.attr', 'aria-live');
      cy.get('[data-cy=status-updates]').should('have.attr', 'aria-live');

      // Test dynamic content updates
      cy.get('[data-cy=refresh-data-btn]').click();
      cy.get('[data-cy=loading-announcement]').should('have.attr', 'aria-live', 'assertive');
    });
  });

  describe('Forms Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/beneficiaries/create');
      cy.waitForLoad();
    });

    it('should meet WCAG standards for form accessibility', () => {
      cy.checkA11y();

      // Check form structure
      cy.get('form').should('have.attr', 'novalidate'); // Custom validation
      cy.get('fieldset').should('exist');
      cy.get('legend').should('exist');

      // Check required field indicators
      cy.get('[required]').each($field => {
        cy.wrap($field).should('have.attr', 'aria-required', 'true');
      });

      // Check field descriptions
      cy.get('input, select, textarea').each($field => {
        const fieldId = $field.attr('id');
        if (fieldId) {
          cy.get(`[data-cy=${fieldId}-description]`).should('exist');
        }
      });
    });

    it('should provide clear error messages and associations', () => {
      // Submit form to trigger validation errors
      cy.get('[data-cy=save-beneficiary-btn]').click();

      // Check error summary
      cy.get('[data-cy=error-summary]').should('be.visible');
      cy.get('[data-cy=error-summary]').should('have.attr', 'role', 'alert');
      cy.get('[data-cy=error-summary]').should('have.attr', 'aria-labelledby');

      // Check individual field errors
      cy.get('[data-cy=first-name-error]').should('be.visible');
      cy.get('[data-cy=beneficiary-first-name]').should('have.attr', 'aria-describedby');
      cy.get('[data-cy=beneficiary-first-name]').should('have.attr', 'aria-invalid', 'true');

      // Check error message content
      cy.get('[data-cy=first-name-error]').should('contain', 'First name is required');
      cy.get('[data-cy=first-name-error]').should('have.attr', 'role', 'alert');
    });

    it('should support keyboard navigation in complex forms', () => {
      // Test fieldset navigation
      cy.get('body').tab();
      cy.focused().should('be.visible');

      // Test skip links within form
      cy.get('[data-cy=skip-to-save]').type('{enter}');
      cy.focused().should('have.attr', 'data-cy', 'save-beneficiary-btn');

      // Test radio group navigation
      cy.get('[data-cy=gender-group] input[type="radio"]').first().focus();
      cy.focused().type('{rightarrow}');
      cy.focused().should('be.checked');
    });

    it('should provide helpful form instructions', () => {
      // Check form instructions
      cy.get('[data-cy=form-instructions]').should('be.visible');
      cy.get('[data-cy=form-instructions]').should('have.attr', 'aria-describedby');

      // Check password requirements
      cy.get('[data-cy=password-requirements]').should('be.visible');
      cy.get('[data-cy=password-requirements]').should('have.attr', 'aria-live', 'polite');

      // Check character count indicators
      cy.get('[data-cy=character-count]').should('have.attr', 'aria-live', 'polite');
      cy.get('[data-cy=character-count]').should('have.attr', 'aria-describedby');
    });
  });

  describe('Tables and Data Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/beneficiaries');
      cy.waitForLoad();
    });

    it('should provide accessible table structure', () => {
      cy.checkA11y();

      // Check table roles and structure
      cy.get('[data-cy=beneficiaries-table]').should('have.attr', 'role', 'table');
      cy.get('[data-cy=beneficiaries-table] thead').should('have.attr', 'role', 'rowgroup');
      cy.get('[data-cy=beneficiaries-table] tbody').should('have.attr', 'role', 'rowgroup');
      cy.get('[data-cy=beneficiaries-table] tr').should('have.attr', 'role', 'row');
      cy.get('[data-cy=beneficiaries-table] th').should('have.attr', 'role', 'columnheader');
      cy.get('[data-cy=beneficiaries-table] td').should('have.attr', 'role', 'cell');

      // Check table caption
      cy.get('[data-cy=beneficiaries-table] caption').should('exist');
      cy.get('[data-cy=beneficiaries-table] caption').should('be.visible');

      // Check column headers
      cy.get('[data-cy=beneficiaries-table] th').each($header => {
        cy.wrap($header).should('have.attr', 'scope', 'col');
      });
    });

    it('should support keyboard navigation in tables', () => {
      // Focus on first table cell
      cy.get('[data-cy=beneficiaries-table] tbody tr:first td:first').focus();
      cy.focused().should('be.visible');

      // Navigate with arrow keys
      cy.focused().type('{rightarrow}');
      cy.focused().should('not.be', cy.get('[data-cy=beneficiaries-table] tbody tr:first td:first'));

      cy.focused().type('{downarrow}');
      cy.focused().should('be.visible');

      cy.focused().type('{leftarrow}');
      cy.focused().should('be.visible');

      cy.focused().type('{uparrow}');
      cy.focused().should('be.visible');
    });

    it('should provide sortable column accessibility', () => {
      // Check sortable headers
      cy.get('[data-cy=sortable-header]').each($header => {
        cy.wrap($header).should('have.attr', 'aria-sort');
        cy.wrap($header).should('have.attr', 'tabindex', '0');
        cy.wrap($header).should('have.attr', 'role', 'button');
      });

      // Test sorting interaction
      cy.get('[data-cy=sort-by-name]').click();
      cy.get('[data-cy=sort-by-name]').should('have.attr', 'aria-sort', 'ascending');

      cy.get('[data-cy=sort-by-name]').click();
      cy.get('[data-cy=sort-by-name]').should('have.attr', 'aria-sort', 'descending');
    });

    it('should announce table updates and filtering', () => {
      // Check live region for table updates
      cy.get('[data-cy=table-announcement]').should('have.attr', 'aria-live', 'polite');

      // Test search/filter announcements
      cy.get('[data-cy=beneficiary-search]').type('john');
      cy.waitForLoad();
      
      cy.get('[data-cy=table-announcement]').should('contain', 'results found');
      cy.get('[data-cy=results-count]').should('have.attr', 'aria-live', 'polite');
    });
  });

  describe('Modals and Dialogs Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/beneficiaries');
      cy.waitForLoad();
    });

    it('should provide accessible modal behavior', () => {
      cy.get('[data-cy=create-beneficiary-btn]').click();
      cy.waitForModal();

      // Check modal attributes
      cy.get('[data-cy=modal]').should('have.attr', 'role', 'dialog');
      cy.get('[data-cy=modal]').should('have.attr', 'aria-modal', 'true');
      cy.get('[data-cy=modal]').should('have.attr', 'aria-labelledby');
      cy.get('[data-cy=modal]').should('have.attr', 'aria-describedby');

      // Check focus management
      cy.focused().should('be.within', '[data-cy=modal]');
      cy.get('[data-cy=modal-title]').should('have.attr', 'id');

      // Test escape key
      cy.get('body').type('{esc}');
      cy.get('[data-cy=modal]').should('not.exist');
      cy.focused().should('have.attr', 'data-cy', 'create-beneficiary-btn');
    });

    it('should trap focus within modals', () => {
      cy.get('[data-cy=create-beneficiary-btn]').click();
      cy.waitForModal();

      // Find all focusable elements in modal
      cy.get('[data-cy=modal]').within(() => {
        cy.get('button, input, select, textarea, [tabindex]:not([tabindex="-1"])').then($focusable => {
          const firstElement = $focusable.first();
          const lastElement = $focusable.last();

          // Focus should start on first element
          cy.wrap(firstElement).should('be.focused');

          // Tab to last element
          cy.wrap(lastElement).focus();
          cy.focused().tab();

          // Should wrap to first element
          cy.wrap(firstElement).should('be.focused');

          // Shift+Tab should wrap to last element
          cy.focused().tab({ shift: true });
          cy.wrap(lastElement).should('be.focused');
        });
      });
    });

    it('should provide clear modal labels and descriptions', () => {
      cy.get('[data-cy=delete-beneficiary-btn]').first().click();
      cy.waitForModal();

      // Check confirmation dialog
      cy.get('[data-cy=confirmation-modal]').should('have.attr', 'role', 'alertdialog');
      cy.get('[data-cy=confirmation-modal]').should('have.attr', 'aria-labelledby');
      cy.get('[data-cy=confirmation-modal]').should('have.attr', 'aria-describedby');

      // Check warning message
      cy.get('[data-cy=warning-message]').should('have.attr', 'role', 'alert');
      cy.get('[data-cy=warning-message]').should('be.visible');

      // Check button labels
      cy.get('[data-cy=confirm-delete-btn]').should('have.attr', 'aria-describedby');
      cy.get('[data-cy=cancel-btn]').should('have.attr', 'aria-label');
    });
  });

  describe('Navigation Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();
    });

    it('should provide accessible navigation structure', () => {
      cy.checkA11y();

      // Check navigation landmarks
      cy.get('[data-cy=main-navigation]').should('have.attr', 'role', 'navigation');
      cy.get('[data-cy=main-navigation]').should('have.attr', 'aria-label');

      // Check breadcrumb navigation
      cy.get('[data-cy=breadcrumb]').should('have.attr', 'role', 'navigation');
      cy.get('[data-cy=breadcrumb]').should('have.attr', 'aria-label', 'Breadcrumb');

      // Check skip links
      cy.get('[data-cy=skip-to-main]').should('be.focused');
      cy.get('[data-cy=skip-to-main]').type('{enter}');
      cy.focused().should('have.attr', 'data-cy', 'main-content');
    });

    it('should support keyboard navigation in menus', () => {
      // Test main menu keyboard navigation
      cy.get('[data-cy=nav-item]').first().focus();
      cy.focused().type('{rightarrow}');
      cy.focused().should('not.be', cy.get('[data-cy=nav-item]').first());

      // Test dropdown menu
      cy.get('[data-cy=dropdown-trigger]').focus();
      cy.focused().type('{enter}');
      cy.get('[data-cy=dropdown-menu]').should('be.visible');

      // Navigate within dropdown
      cy.focused().type('{downarrow}');
      cy.focused().should('be.within', '[data-cy=dropdown-menu]');

      // Escape to close dropdown
      cy.focused().type('{esc}');
      cy.get('[data-cy=dropdown-menu]').should('not.be.visible');
      cy.focused().should('have.attr', 'data-cy', 'dropdown-trigger');
    });

    it('should indicate current page/section', () => {
      // Check current page indication
      cy.get('[data-cy=nav-item][aria-current="page"]').should('exist');
      cy.get('[data-cy=nav-item][aria-current="page"]').should('be.visible');

      // Check visual focus indicator
      cy.get('[data-cy=nav-item][aria-current="page"]').should('have.css', 'background-color');
      
      // Test navigation to different page
      cy.get('[data-cy=nav-beneficiaries]').click();
      cy.url().should('include', '/beneficiaries');
      cy.get('[data-cy=nav-beneficiaries]').should('have.attr', 'aria-current', 'page');
    });
  });

  describe('Color and Contrast Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();
    });

    it('should meet color contrast requirements', () => {
      // Test with axe-core color contrast rules
      cy.checkA11y(null, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });

      // Test high contrast mode
      cy.get('[data-cy=accessibility-settings]').click();
      cy.get('[data-cy=high-contrast-mode]').check();
      
      cy.get('body').should('have.class', 'high-contrast');
      cy.checkA11y(null, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
    });

    it('should not rely solely on color for information', () => {
      // Check status indicators have icons/text in addition to color
      cy.get('[data-cy=status-indicator]').each($indicator => {
        cy.wrap($indicator).should('satisfy', $el => {
          const hasIcon = $el.find('[data-cy=status-icon]').length > 0;
          const hasText = $el.text().trim() !== '';
          const hasAriaLabel = $el.attr('aria-label') !== undefined;
          return hasIcon || hasText || hasAriaLabel;
        });
      });

      // Check form validation doesn't rely only on color
      cy.visit('/beneficiaries/create');
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      cy.get('[data-cy=form-field].error').each($field => {
        cy.wrap($field).should('satisfy', $el => {
          const hasErrorIcon = $el.find('[data-cy=error-icon]').length > 0;
          const hasErrorText = $el.find('[data-cy=field-error]').length > 0;
          const hasAriaInvalid = $el.find('[aria-invalid="true"]').length > 0;
          return hasErrorIcon || hasErrorText || hasAriaInvalid;
        });
      });
    });
  });

  describe('Screen Reader Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();
    });

    it('should provide proper heading structure for screen readers', () => {
      // Check page has main heading
      cy.get('h1').should('have.length', 1);
      cy.get('h1').should('be.visible');

      // Check heading hierarchy
      cy.get('h1, h2, h3, h4, h5, h6').then($headings => {
        let previousLevel = 0;
        $headings.each((index, heading) => {
          const currentLevel = parseInt(heading.tagName.charAt(1));
          if (previousLevel > 0) {
            expect(currentLevel - previousLevel).to.be.at.most(1);
          }
          previousLevel = currentLevel;
        });
      });
    });

    it('should provide meaningful alternative text for images', () => {
      cy.get('img').each($img => {
        cy.wrap($img).should('satisfy', $el => {
          const alt = $el.attr('alt');
          const ariaLabel = $el.attr('aria-label');
          const isDecorative = $el.attr('role') === 'presentation' || alt === '';
          return alt !== undefined || ariaLabel !== undefined || isDecorative;
        });
      });

      // Check complex images have extended descriptions
      cy.get('[data-cy=chart-image]').each($chart => {
        cy.wrap($chart).should('have.attr', 'aria-describedby');
      });
    });

    it('should announce dynamic content appropriately', () => {
      // Check live regions
      cy.get('[aria-live]').should('exist');
      
      // Test notification announcements
      cy.get('[data-cy=create-beneficiary-btn]').click();
      cy.waitForModal();
      
      cy.fillForm({
        'beneficiary-first-name': 'Test',
        'beneficiary-last-name': 'User',
        'beneficiary-email': 'test@example.com'
      });
      
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      // Check success message is announced
      cy.get('[data-cy=notification-area]').should('have.attr', 'aria-live');
      cy.get('[data-cy=success-message]').should('be.visible');
    });

    it('should provide clear link purposes', () => {
      cy.get('a').each($link => {
        cy.wrap($link).should('satisfy', $el => {
          const linkText = $el.text().trim();
          const ariaLabel = $el.attr('aria-label');
          const ariaLabelledBy = $el.attr('aria-labelledby');
          const title = $el.attr('title');
          
          // Link should have meaningful text or label
          const hasMeaningfulText = linkText.length > 0 && linkText !== 'Click here' && linkText !== 'Read more';
          const hasAriaLabel = ariaLabel && ariaLabel.length > 0;
          const hasAriaLabelledBy = ariaLabelledBy && ariaLabelledBy.length > 0;
          const hasTitle = title && title.length > 0;
          
          return hasMeaningfulText || hasAriaLabel || hasAriaLabelledBy || hasTitle;
        });
      });
    });
  });

  describe('Responsive Accessibility', () => {
    it('should maintain accessibility on mobile devices', () => {
      cy.setMobileViewport();
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();

      // Check mobile accessibility
      cy.checkA11y();

      // Check mobile navigation
      cy.get('[data-cy=mobile-menu-button]').should('be.visible');
      cy.get('[data-cy=mobile-menu-button]').should('have.attr', 'aria-expanded', 'false');
      cy.get('[data-cy=mobile-menu-button]').should('have.attr', 'aria-controls');

      // Test mobile menu
      cy.get('[data-cy=mobile-menu-button]').click();
      cy.get('[data-cy=mobile-menu-button]').should('have.attr', 'aria-expanded', 'true');
      cy.get('[data-cy=mobile-navigation]').should('be.visible');

      // Check touch targets are large enough
      cy.get('button, a, input').each($element => {
        cy.wrap($element).then($el => {
          const rect = $el[0].getBoundingClientRect();
          const minSize = 44; // WCAG minimum touch target size
          expect(Math.max(rect.width, rect.height)).to.be.at.least(minSize);
        });
      });
    });

    it('should work with zoom levels up to 200%', () => {
      cy.visit('/dashboard');
      cy.loginAsTrainer();
      cy.waitForLoad();

      // Simulate 200% zoom
      cy.viewport(640, 360); // Half the normal size simulates 200% zoom
      
      // Check content is still accessible
      cy.checkA11y();
      
      // Check horizontal scrolling is not required
      cy.get('body').should('not.have.css', 'overflow-x', 'scroll');
      
      // Check all functionality is still available
      cy.get('[data-cy=main-navigation]').should('be.visible');
      cy.get('[data-cy=dashboard-content]').should('be.visible');
    });
  });

  describe('Assistive Technology Compatibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/dashboard');
      cy.waitForLoad();
    });

    it('should work with keyboard-only navigation', () => {
      // Disable mouse
      cy.get('body').invoke('css', 'pointer-events', 'none');

      // Navigate entire interface with keyboard
      cy.get('body').tab();
      cy.focused().should('be.visible');

      // Test all major interface elements
      let tabCount = 0;
      const maxTabs = 50; // Prevent infinite loop

      function tabToNextElement() {
        if (tabCount < maxTabs) {
          cy.focused().then($el => {
            if ($el.length > 0) {
              tabCount++;
              cy.focused().tab();
              cy.focused().should('be.visible');
              tabToNextElement();
            }
          });
        }
      }

      tabToNextElement();
    });

    it('should provide proper ARIA landmarks and regions', () => {
      // Check all required landmarks exist
      const requiredLandmarks = ['banner', 'navigation', 'main', 'contentinfo'];
      
      requiredLandmarks.forEach(landmark => {
        cy.get(`[role="${landmark}"]`).should('exist');
      });

      // Check landmark labels
      cy.get('[role="navigation"]').each($nav => {
        cy.wrap($nav).should('have.attr', 'aria-label');
      });

      // Check complementary regions
      cy.get('[role="complementary"]').each($aside => {
        cy.wrap($aside).should('have.attr', 'aria-labelledby');
      });
    });

    it('should support voice control software', () => {
      // Check elements have speech-friendly labels
      cy.get('button, input, select, textarea, a').each($element => {
        cy.wrap($element).should('satisfy', $el => {
          const text = $el.text().trim();
          const ariaLabel = $el.attr('aria-label');
          const ariaLabelledBy = $el.attr('aria-labelledby');
          
          // Should have recognizable voice command targets
          return text.length > 0 || ariaLabel || ariaLabelledBy;
        });
      });

      // Check for speech recognition landmarks
      cy.get('[data-speech-target]').should('exist');
    });
  });

  describe('Error Handling Accessibility', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
    });

    it('should provide accessible error messages', () => {
      // Test form validation errors
      cy.visit('/beneficiaries/create');
      cy.get('[data-cy=save-beneficiary-btn]').click();

      // Check error summary
      cy.get('[data-cy=error-summary]').should('be.visible');
      cy.get('[data-cy=error-summary]').should('have.attr', 'role', 'alert');
      cy.get('[data-cy=error-summary]').should('have.attr', 'tabindex', '-1');
      cy.get('[data-cy=error-summary]').should('be.focused');

      // Check individual field errors
      cy.get('[aria-invalid="true"]').each($field => {
        const describedBy = $field.attr('aria-describedby');
        cy.get(`#${describedBy}`).should('exist');
        cy.get(`#${describedBy}`).should('have.attr', 'role', 'alert');
      });
    });

    it('should handle network errors accessibly', () => {
      // Simulate network error
      cy.intercept('GET', '**/api/beneficiaries', { statusCode: 500 }).as('networkError');
      
      cy.visit('/beneficiaries');
      cy.wait('@networkError');

      // Check error announcement
      cy.get('[data-cy=error-message]').should('be.visible');
      cy.get('[data-cy=error-message]').should('have.attr', 'role', 'alert');
      cy.get('[data-cy=error-announcement]').should('have.attr', 'aria-live', 'assertive');

      // Check retry functionality is accessible
      cy.get('[data-cy=retry-btn]').should('be.visible');
      cy.get('[data-cy=retry-btn]').should('have.attr', 'aria-describedby');
    });

    it('should provide accessible loading states', () => {
      cy.visit('/beneficiaries');
      
      // Check loading announcement
      cy.get('[data-cy=loading-announcement]').should('have.attr', 'aria-live', 'polite');
      cy.get('[data-cy=loading-spinner]').should('have.attr', 'aria-label');
      cy.get('[data-cy=loading-spinner]').should('have.attr', 'role', 'status');

      // Check content is hidden during loading
      cy.get('[data-cy=main-content]').should('have.attr', 'aria-busy', 'true');
    });
  });
});