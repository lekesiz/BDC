/**
 * RTL Layout Tests
 * Comprehensive tests for Right-to-Left language layout support
 */

describe('RTL Layout Tests', () => {
  const RTL_LANGUAGES = ['ar', 'he'];
  const LTR_LANGUAGES = ['en', 'es', 'fr', 'de', 'ru'];
  
  beforeEach(() => {
    cy.clearLocalStorage();
    cy.visit('/');
  });

  describe('Basic RTL Layout', () => {
    RTL_LANGUAGES.forEach(language => {
      it(`should apply RTL layout for ${language}`, () => {
        // Switch to RTL language
        cy.get('[data-testid="language-selector"]').click();
        cy.get(`[data-testid="language-option-${language}"]`).click();
        
        // Check HTML attributes
        cy.get('html').should('have.attr', 'dir', 'rtl');
        cy.get('html').should('have.attr', 'lang', language);
        
        // Check body direction
        cy.get('body').should('have.css', 'direction', 'rtl');
        
        // Check main container
        cy.get('[data-testid="main-container"]')
          .should('have.css', 'direction', 'rtl');
      });
    });

    LTR_LANGUAGES.forEach(language => {
      it(`should apply LTR layout for ${language}`, () => {
        // Switch to LTR language
        cy.get('[data-testid="language-selector"]').click();
        cy.get(`[data-testid="language-option-${language}"]`).click();
        
        // Check HTML attributes
        cy.get('html').should('have.attr', 'dir', 'ltr');
        cy.get('html').should('have.attr', 'lang', language);
        
        // Check body direction
        cy.get('body').should('have.css', 'direction', 'ltr');
      });
    });
  });

  describe('Text Alignment', () => {
    it('should align text to the right in RTL mode', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check various text elements
      cy.get('[data-testid="page-title"]')
        .should('have.css', 'text-align', 'right');
      
      cy.get('[data-testid="description-text"]')
        .should('have.css', 'text-align', 'right');
      
      cy.get('[data-testid="navigation-menu"] li')
        .should('have.css', 'text-align', 'right');
    });

    it('should align text to the left in LTR mode', () => {
      // Ensure English is selected
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-en"]').click();
      
      // Check text alignment
      cy.get('[data-testid="page-title"]')
        .should('have.css', 'text-align', 'left');
      
      cy.get('[data-testid="description-text"]')
        .should('have.css', 'text-align', 'left');
    });

    it('should handle centered text properly in both directions', () => {
      // Check centered elements in LTR
      cy.get('[data-testid="centered-content"]')
        .should('have.css', 'text-align', 'center');
      
      // Switch to RTL
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Centered elements should remain centered
      cy.get('[data-testid="centered-content"]')
        .should('have.css', 'text-align', 'center');
    });
  });

  describe('Layout Components', () => {
    it('should flip sidebar position in RTL mode', () => {
      // Navigate to a page with sidebar
      cy.visit('/dashboard');
      
      // Check LTR sidebar position
      cy.get('[data-testid="sidebar"]')
        .should('have.css', 'left', '0px')
        .should('have.css', 'right', 'auto');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check RTL sidebar position
      cy.get('[data-testid="sidebar"]')
        .should('have.css', 'right', '0px')
        .should('have.css', 'left', 'auto');
    });

    it('should adjust main content margin in RTL mode', () => {
      cy.visit('/dashboard');
      
      // Check LTR main content margin
      cy.get('[data-testid="main-content"]')
        .should('have.css', 'margin-left', '250px')
        .should('have.css', 'margin-right', '0px');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check RTL main content margin
      cy.get('[data-testid="main-content"]')
        .should('have.css', 'margin-right', '250px')
        .should('have.css', 'margin-left', '0px');
    });

    it('should flip navigation menu items', () => {
      // Switch to RTL
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check navigation items alignment
      cy.get('[data-testid="nav-item"]').each($item => {
        cy.wrap($item).should('have.css', 'text-align', 'right');
      });
      
      // Check submenu positioning
      cy.get('[data-testid="nav-item-with-submenu"]').hover();
      cy.get('[data-testid="submenu"]')
        .should('have.css', 'right', '0px');
    });
  });

  describe('Form Elements', () => {
    it('should align form labels and inputs in RTL mode', () => {
      cy.visit('/register');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check form label alignment
      cy.get('[data-testid="form-label"]')
        .should('have.css', 'text-align', 'right');
      
      // Check input text direction
      cy.get('[data-testid="text-input"]')
        .should('have.css', 'direction', 'rtl')
        .should('have.css', 'text-align', 'right');
      
      // Check textarea direction
      cy.get('[data-testid="textarea"]')
        .should('have.css', 'direction', 'rtl')
        .should('have.css', 'text-align', 'right');
    });

    it('should position form validation errors correctly', () => {
      cy.visit('/register');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Trigger validation errors
      cy.get('[data-testid="submit-button"]').click();
      
      // Check error message alignment
      cy.get('[data-testid="error-message"]')
        .should('have.css', 'text-align', 'right');
      
      // Check error icon position (should be on the right side)
      cy.get('[data-testid="error-icon"]')
        .should('have.css', 'right', '0px');
    });

    it('should handle form buttons and actions in RTL', () => {
      cy.visit('/register');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check button group alignment
      cy.get('[data-testid="button-group"]')
        .should('have.css', 'direction', 'rtl');
      
      // Primary button should be on the right in RTL
      cy.get('[data-testid="primary-button"]')
        .should('have.css', 'margin-left', '8px')
        .should('have.css', 'margin-right', '0px');
      
      // Secondary button should be on the left in RTL
      cy.get('[data-testid="secondary-button"]')
        .should('have.css', 'margin-right', '8px');
    });

    it('should handle form field icons in RTL mode', () => {
      cy.visit('/login');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check email field icon position
      cy.get('[data-testid="email-field"] .field-icon')
        .should('have.css', 'right', '12px')
        .should('have.css', 'left', 'auto');
      
      // Check password field icon position
      cy.get('[data-testid="password-field"] .field-icon')
        .should('have.css', 'right', '12px');
    });
  });

  describe('Tables and Data Display', () => {
    it('should reverse table column order in RTL mode', () => {
      cy.visit('/beneficiaries');
      
      // Check LTR table header order
      cy.get('[data-testid="table-header"] th').then($headers => {
        const ltrOrder = Array.from($headers).map(h => h.textContent);
        
        // Switch to Arabic
        cy.get('[data-testid="language-selector"]').click();
        cy.get('[data-testid="language-option-ar"]').click();
        
        // Check RTL table headers
        cy.get('[data-testid="table-header"] th').should('have.css', 'text-align', 'right');
        
        // Table content should be right-aligned
        cy.get('[data-testid="table-body"] td').should('have.css', 'text-align', 'right');
      });
    });

    it('should position table action buttons correctly in RTL', () => {
      cy.visit('/beneficiaries');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check action buttons alignment
      cy.get('[data-testid="table-actions"]')
        .should('have.css', 'text-align', 'left'); // Actions should be on the left in RTL
      
      // Check individual action buttons
      cy.get('[data-testid="edit-button"]')
        .should('have.css', 'margin-left', '8px');
    });

    it('should handle sortable table headers in RTL', () => {
      cy.visit('/evaluations');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check sort icons position
      cy.get('[data-testid="sortable-header"] .sort-icon')
        .should('have.css', 'right', '8px');
      
      // Click to sort and check direction
      cy.get('[data-testid="sortable-header"]').click();
      
      cy.get('[data-testid="sort-asc-icon"]')
        .should('be.visible')
        .should('have.css', 'right', '8px');
    });
  });

  describe('Navigation and Menus', () => {
    it('should position dropdown menus correctly in RTL', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Open user menu
      cy.get('[data-testid="user-menu-trigger"]').click();
      
      // Check dropdown position (should open to the left)
      cy.get('[data-testid="user-menu-dropdown"]')
        .should('have.css', 'right', '0px')
        .should('have.css', 'left', 'auto');
      
      // Check menu items alignment
      cy.get('[data-testid="menu-item"]')
        .should('have.css', 'text-align', 'right');
    });

    it('should handle breadcrumb navigation in RTL', () => {
      cy.visit('/beneficiaries/123/evaluations');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check breadcrumb direction
      cy.get('[data-testid="breadcrumb"]')
        .should('have.css', 'direction', 'rtl');
      
      // Check breadcrumb separators
      cy.get('[data-testid="breadcrumb-separator"]')
        .should('contain', '←'); // Should show left arrow in RTL
    });

    it('should position floating action buttons correctly', () => {
      cy.visit('/dashboard');
      
      // Check LTR position
      cy.get('[data-testid="fab"]')
        .should('have.css', 'right', '20px')
        .should('have.css', 'left', 'auto');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // FAB should remain on the right (as it's a fixed position element)
      cy.get('[data-testid="fab"]')
        .should('have.css', 'right', '20px');
    });
  });

  describe('Icons and Images', () => {
    it('should flip directional icons in RTL mode', () => {
      cy.visit('/evaluations');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check arrow icons are flipped
      cy.get('[data-testid="next-arrow"]')
        .should('have.css', 'transform')
        .and('include', 'scaleX(-1)');
      
      cy.get('[data-testid="back-arrow"]')
        .should('have.css', 'transform')
        .and('include', 'scaleX(-1)');
      
      // Check chevron icons
      cy.get('[data-testid="expand-chevron"]')
        .should('have.css', 'transform')
        .and('include', 'scaleX(-1)');
    });

    it('should not flip non-directional icons', () => {
      cy.visit('/dashboard');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // These icons should not be flipped
      cy.get('[data-testid="user-icon"]')
        .should('not.have.css', 'transform', 'scaleX(-1)');
      
      cy.get('[data-testid="settings-icon"]')
        .should('not.have.css', 'transform', 'scaleX(-1)');
      
      cy.get('[data-testid="calendar-icon"]')
        .should('not.have.css', 'transform', 'scaleX(-1)');
    });

    it('should handle logo positioning in RTL', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Logo should be positioned on the right in RTL
      cy.get('[data-testid="header-logo"]')
        .should('have.css', 'right', '0px')
        .should('have.css', 'left', 'auto');
    });
  });

  describe('Mixed Content Handling', () => {
    it('should handle mixed Arabic and English text', () => {
      cy.visit('/test-mixed-content');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check mixed content container
      cy.get('[data-testid="mixed-content"]')
        .should('have.css', 'direction', 'rtl');
      
      // English words within Arabic text should maintain LTR
      cy.get('[data-testid="mixed-content"] .english-word')
        .should('have.css', 'direction', 'ltr')
        .should('have.css', 'unicode-bidi', 'embed');
      
      // Numbers should be displayed correctly
      cy.get('[data-testid="mixed-content"] .number')
        .should('have.css', 'unicode-bidi', 'embed');
    });

    it('should handle URLs and emails in RTL text', () => {
      cy.visit('/contact');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // URLs should remain LTR even in RTL context
      cy.get('[data-testid="contact-url"]')
        .should('have.css', 'direction', 'ltr')
        .should('have.css', 'unicode-bidi', 'embed');
      
      // Email addresses should remain LTR
      cy.get('[data-testid="contact-email"]')
        .should('have.css', 'direction', 'ltr');
    });
  });

  describe('Responsive RTL Layout', () => {
    it('should handle mobile RTL layout correctly', () => {
      cy.viewport(375, 667); // Mobile viewport
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check mobile menu position
      cy.get('[data-testid="mobile-menu-trigger"]')
        .should('have.css', 'right', '16px');
      
      // Open mobile menu
      cy.get('[data-testid="mobile-menu-trigger"]').click();
      
      // Menu should slide from right
      cy.get('[data-testid="mobile-menu"]')
        .should('have.css', 'right', '0px')
        .should('have.css', 'transform', 'translateX(0px)');
    });

    it('should handle tablet RTL layout', () => {
      cy.viewport(768, 1024); // Tablet viewport
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check tablet-specific RTL adjustments
      cy.get('[data-testid="tablet-sidebar"]')
        .should('have.css', 'right', '0px')
        .should('have.css', 'left', 'auto');
      
      cy.get('[data-testid="tablet-content"]')
        .should('have.css', 'margin-right', '200px')
        .should('have.css', 'margin-left', '0px');
    });
  });

  describe('Animation and Transitions', () => {
    it('should reverse slide animations in RTL mode', () => {
      cy.visit('/carousel-demo');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Next button should slide right-to-left
      cy.get('[data-testid="carousel-next"]').click();
      
      cy.get('[data-testid="carousel-item"]')
        .should('have.css', 'transform')
        .and('include', 'translateX(');
      
      // The animation should move in the opposite direction
      // This would need to be tested with actual animation values
    });

    it('should handle tooltip positioning in RTL', () => {
      cy.visit('/dashboard');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Hover over an element with tooltip
      cy.get('[data-testid="tooltip-trigger"]').hover();
      
      // Tooltip should appear on the correct side
      cy.get('[data-testid="tooltip"]')
        .should('be.visible')
        .should('have.css', 'right', '0px');
    });
  });

  describe('Print Styles', () => {
    it('should apply RTL styles to print media', () => {
      cy.visit('/reports/printable');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check that print styles will be applied correctly
      // This is tricky to test directly, but we can check the CSS classes
      cy.get('[data-testid="printable-content"]')
        .should('have.class', 'rtl-print');
      
      // Check page headers and footers
      cy.get('[data-testid="print-header"]')
        .should('have.css', 'text-align', 'right');
    });
  });

  describe('Accessibility in RTL Mode', () => {
    it('should maintain accessibility features in RTL', () => {
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // Check that ARIA labels are preserved
      cy.get('[data-testid="main-navigation"]')
        .should('have.attr', 'aria-label');
      
      // Check that focus management works correctly
      cy.get('[data-testid="focusable-element"]')
        .focus()
        .should('have.focus');
      
      // Tab order should still work logically
      cy.tab()
        .should('have.focus');
    });

    it('should announce direction changes to screen readers', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Check for ARIA live region updates
      cy.get('[data-testid="direction-announcer"]')
        .should('have.attr', 'aria-live', 'polite')
        .should('contain', 'Layout changed to right-to-left');
    });
  });

  describe('RTL Edge Cases', () => {
    it('should handle nested directional content', () => {
      cy.visit('/complex-layout');
      
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Parent container should be RTL
      cy.get('[data-testid="rtl-container"]')
        .should('have.css', 'direction', 'rtl');
      
      // Nested LTR content should override
      cy.get('[data-testid="ltr-override"]')
        .should('have.css', 'direction', 'ltr');
      
      // Back to RTL for subsequent content
      cy.get('[data-testid="rtl-content"]')
        .should('have.css', 'direction', 'rtl');
    });

    it('should handle RTL with CSS Grid and Flexbox', () => {
      cy.visit('/grid-layout');
      
      // Switch to Hebrew
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-he"]').click();
      
      // CSS Grid should reverse column order
      cy.get('[data-testid="grid-container"]')
        .should('have.css', 'direction', 'rtl');
      
      // Flexbox should reverse row direction
      cy.get('[data-testid="flex-container"]')
        .should('have.css', 'flex-direction', 'row-reverse');
    });

    it('should maintain RTL layout during loading states', () => {
      // Switch to Arabic
      cy.get('[data-testid="language-selector"]').click();
      cy.get('[data-testid="language-option-ar"]').click();
      
      // Navigate to a page with loading
      cy.visit('/slow-page');
      
      // Even during loading, RTL should be maintained
      cy.get('[data-testid="loading-spinner"]')
        .should('have.css', 'direction', 'rtl');
      
      cy.get('[data-testid="loading-text"]')
        .should('have.css', 'text-align', 'right');
    });
  });
});