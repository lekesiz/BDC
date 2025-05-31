describe('Comprehensive Beneficiary Management', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.loginAsTrainer();
    cy.waitForLoad();
  });

  afterEach(() => {
    cy.dismissNotification();
  });

  describe('Beneficiaries List View', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.waitForLoad();
    });

    it('should display beneficiaries list with complete information', () => {
      cy.get('[data-cy=beneficiaries-table]').should('be.visible');
      cy.get('[data-cy=beneficiary-row]').should('have.length.at.least', 1);
      
      // Verify table headers
      cy.get('[data-cy=beneficiaries-table-header]').within(() => {
        cy.contains('Name').should('be.visible');
        cy.contains('Email').should('be.visible');
        cy.contains('Phone').should('be.visible');
        cy.contains('Status').should('be.visible');
        cy.contains('Programs').should('be.visible');
        cy.contains('Progress').should('be.visible');
        cy.contains('Actions').should('be.visible');
      });

      // Verify row data structure
      cy.get('[data-cy=beneficiary-row]').first().within(() => {
        cy.get('[data-cy=beneficiary-name]').should('be.visible');
        cy.get('[data-cy=beneficiary-email]').should('be.visible');
        cy.get('[data-cy=beneficiary-status]').should('be.visible');
        cy.get('[data-cy=beneficiary-actions]').should('be.visible');
      });
    });

    it('should support searching beneficiaries', () => {
      cy.get('[data-cy=beneficiary-search]').type('john');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').each($row => {
        cy.wrap($row).should('contain.text', 'john');
      });

      // Clear search
      cy.get('[data-cy=beneficiary-search]').clear();
      cy.waitForLoad();
      cy.get('[data-cy=beneficiary-row]').should('have.length.at.least', 1);
    });

    it('should support filtering by status', () => {
      cy.get('[data-cy=status-filter]').select('active');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').each($row => {
        cy.wrap($row).find('[data-cy=beneficiary-status]').should('contain', 'Active');
      });

      cy.get('[data-cy=status-filter]').select('inactive');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').each($row => {
        cy.wrap($row).find('[data-cy=beneficiary-status]').should('contain', 'Inactive');
      });
    });

    it('should support filtering by program', () => {
      cy.get('[data-cy=program-filter]').select('Web Development');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').each($row => {
        cy.wrap($row).find('[data-cy=beneficiary-programs]').should('contain', 'Web Development');
      });
    });

    it('should support sorting by different columns', () => {
      // Sort by name
      cy.get('[data-cy=sort-by-name]').click();
      cy.waitForLoad();
      
      // Verify ascending order
      cy.get('[data-cy=beneficiary-name]').then($names => {
        const names = Array.from($names).map(el => el.textContent);
        const sortedNames = [...names].sort();
        expect(names).to.deep.equal(sortedNames);
      });

      // Click again for descending order
      cy.get('[data-cy=sort-by-name]').click();
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-name]').then($names => {
        const names = Array.from($names).map(el => el.textContent);
        const sortedNames = [...names].sort().reverse();
        expect(names).to.deep.equal(sortedNames);
      });
    });

    it('should support pagination', () => {
      cy.get('[data-cy=pagination-info]').should('be.visible');
      cy.get('[data-cy=next-page-btn]').click();
      cy.waitForLoad();
      
      cy.get('[data-cy=current-page]').should('contain', '2');
      
      cy.get('[data-cy=prev-page-btn]').click();
      cy.waitForLoad();
      
      cy.get('[data-cy=current-page]').should('contain', '1');
    });

    it('should allow changing page size', () => {
      cy.get('[data-cy=page-size-select]').select('50');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').should('have.length.at.most', 50);
    });
  });

  describe('Create Beneficiary', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=create-beneficiary-btn]').click();
      cy.waitForModal();
    });

    it('should create a new beneficiary with complete information', () => {
      const newBeneficiary = {
        firstName: 'Jane',
        lastName: 'Smith',
        email: `jane.smith.${Date.now()}@example.com`,
        phone: '+1234567890',
        dateOfBirth: '1990-05-15',
        address: '123 Main St',
        city: 'New York',
        state: 'NY',
        zipCode: '10001',
        emergencyContactName: 'John Smith',
        emergencyContactPhone: '+1234567891',
        educationLevel: 'bachelor',
        employmentStatus: 'unemployed',
        interests: 'Web Development, Data Science'
      };

      // Fill personal information
      cy.fillForm({
        'beneficiary-first-name': newBeneficiary.firstName,
        'beneficiary-last-name': newBeneficiary.lastName,
        'beneficiary-email': newBeneficiary.email,
        'beneficiary-phone': newBeneficiary.phone,
        'beneficiary-date-of-birth': newBeneficiary.dateOfBirth
      });

      // Fill address information
      cy.fillForm({
        'beneficiary-address': newBeneficiary.address,
        'beneficiary-city': newBeneficiary.city,
        'beneficiary-state': newBeneficiary.state,
        'beneficiary-zip-code': newBeneficiary.zipCode
      });

      // Fill emergency contact
      cy.fillForm({
        'emergency-contact-name': newBeneficiary.emergencyContactName,
        'emergency-contact-phone': newBeneficiary.emergencyContactPhone
      });

      // Fill additional information
      cy.selectDropdown('education-level', newBeneficiary.educationLevel);
      cy.selectDropdown('employment-status', newBeneficiary.employmentStatus);
      cy.get('[data-cy=beneficiary-interests]').type(newBeneficiary.interests);

      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.verifyNotification('Beneficiary created successfully');
      
      // Verify beneficiary appears in list
      cy.get('[data-cy=beneficiaries-table]').should('contain', newBeneficiary.email);
    });

    it('should validate required fields', () => {
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      cy.get('[data-cy=first-name-error]').should('contain', 'First name is required');
      cy.get('[data-cy=last-name-error]').should('contain', 'Last name is required');
      cy.get('[data-cy=email-error]').should('contain', 'Email is required');
    });

    it('should validate email format', () => {
      cy.get('[data-cy=beneficiary-email]').type('invalid-email');
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      cy.get('[data-cy=email-error]').should('contain', 'Invalid email format');
    });

    it('should validate phone number format', () => {
      cy.get('[data-cy=beneficiary-phone]').type('invalid-phone');
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      cy.get('[data-cy=phone-error]').should('contain', 'Invalid phone number format');
    });

    it('should prevent duplicate email addresses', () => {
      cy.fillForm({
        'beneficiary-first-name': 'Test',
        'beneficiary-last-name': 'User',
        'beneficiary-email': Cypress.env('studentEmail') // Use existing email
      });

      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.get('[data-cy=email-error]').should('contain', 'Email already exists');
    });

    it('should validate date of birth', () => {
      cy.get('[data-cy=beneficiary-date-of-birth]').type('2030-01-01'); // Future date
      cy.get('[data-cy=save-beneficiary-btn]').click();
      
      cy.get('[data-cy=date-of-birth-error]').should('contain', 'Date of birth cannot be in the future');
    });
  });

  describe('Edit Beneficiary', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=beneficiary-row]').first().within(() => {
        cy.get('[data-cy=edit-beneficiary-btn]').click();
      });
      cy.waitForModal();
    });

    it('should update beneficiary information', () => {
      cy.get('[data-cy=beneficiary-first-name]').clear().type('Updated Name');
      cy.get('[data-cy=beneficiary-phone]').clear().type('+9876543210');
      
      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.verifyNotification('Beneficiary updated successfully');
    });

    it('should update emergency contact information', () => {
      cy.get('[data-cy=emergency-contact-name]').clear().type('Updated Emergency Contact');
      cy.get('[data-cy=emergency-contact-phone]').clear().type('+1111111111');
      
      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.verifyNotification('Beneficiary updated successfully');
    });

    it('should update education and employment status', () => {
      cy.selectDropdown('education-level', 'masters');
      cy.selectDropdown('employment-status', 'employed');
      
      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.verifyNotification('Beneficiary updated successfully');
    });

    it('should handle concurrent edits', () => {
      // Simulate another user editing the same beneficiary
      cy.intercept('PUT', '**/api/beneficiaries/**', {
        statusCode: 409,
        body: { message: 'Beneficiary was modified by another user' }
      }).as('concurrentEdit');

      cy.get('[data-cy=beneficiary-first-name]').clear().type('Conflicted Name');
      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.wait('@concurrentEdit');

      cy.get('[data-cy=conflict-resolution-modal]').should('be.visible');
      cy.get('[data-cy=reload-and-retry-btn]').click();
    });
  });

  describe('Beneficiary Details View', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=beneficiary-row]').first().within(() => {
        cy.get('[data-cy=view-beneficiary-btn]').click();
      });
      cy.waitForLoad();
    });

    it('should display complete beneficiary profile', () => {
      cy.get('[data-cy=beneficiary-profile]').should('be.visible');
      
      // Personal information section
      cy.get('[data-cy=personal-info-section]').within(() => {
        cy.get('[data-cy=beneficiary-name]').should('be.visible');
        cy.get('[data-cy=beneficiary-email]').should('be.visible');
        cy.get('[data-cy=beneficiary-phone]').should('be.visible');
        cy.get('[data-cy=beneficiary-address]').should('be.visible');
      });

      // Programs section
      cy.get('[data-cy=programs-section]').should('be.visible');
      cy.get('[data-cy=program-card]').should('have.length.at.least', 0);

      // Progress section
      cy.get('[data-cy=progress-section]').should('be.visible');
      cy.get('[data-cy=progress-chart]').should('be.visible');

      // Documents section
      cy.get('[data-cy=documents-section]').should('be.visible');
    });

    it('should display program enrollment history', () => {
      cy.get('[data-cy=programs-section]').within(() => {
        cy.get('[data-cy=enrollment-history]').should('be.visible');
        cy.get('[data-cy=program-card]').each($card => {
          cy.wrap($card).within(() => {
            cy.get('[data-cy=program-name]').should('be.visible');
            cy.get('[data-cy=enrollment-date]').should('be.visible');
            cy.get('[data-cy=program-status]').should('be.visible');
          });
        });
      });
    });

    it('should display assessment results', () => {
      cy.get('[data-cy=assessments-section]').should('be.visible');
      cy.get('[data-cy=assessment-result]').each($result => {
        cy.wrap($result).within(() => {
          cy.get('[data-cy=assessment-name]').should('be.visible');
          cy.get('[data-cy=assessment-score]').should('be.visible');
          cy.get('[data-cy=assessment-date]').should('be.visible');
        });
      });
    });

    it('should display notes and communications', () => {
      cy.get('[data-cy=notes-section]').should('be.visible');
      cy.get('[data-cy=add-note-btn]').should('be.visible');
      
      cy.get('[data-cy=note-item]').each($note => {
        cy.wrap($note).within(() => {
          cy.get('[data-cy=note-content]').should('be.visible');
          cy.get('[data-cy=note-author]').should('be.visible');
          cy.get('[data-cy=note-date]').should('be.visible');
        });
      });
    });

    it('should allow adding notes', () => {
      cy.get('[data-cy=add-note-btn]').click();
      cy.waitForModal();

      cy.get('[data-cy=note-content]').type('This is a test note about the beneficiary progress.');
      cy.get('[data-cy=note-type]').select('progress');
      cy.get('[data-cy=save-note-btn]').click();

      cy.verifyNotification('Note added successfully');
      cy.get('[data-cy=note-item]').should('contain', 'This is a test note');
    });
  });

  describe('Bulk Operations', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.waitForLoad();
    });

    it('should select multiple beneficiaries', () => {
      cy.get('[data-cy=beneficiary-checkbox]').first().check();
      cy.get('[data-cy=beneficiary-checkbox]').eq(1).check();
      cy.get('[data-cy=beneficiary-checkbox]').eq(2).check();

      cy.get('[data-cy=selected-count]').should('contain', '3 selected');
      cy.get('[data-cy=bulk-actions-menu]').should('be.visible');
    });

    it('should bulk assign to program', () => {
      cy.get('[data-cy=beneficiary-checkbox]').first().check();
      cy.get('[data-cy=beneficiary-checkbox]').eq(1).check();

      cy.get('[data-cy=bulk-actions-menu]').click();
      cy.get('[data-cy=bulk-assign-program]').click();
      cy.waitForModal();

      cy.selectDropdown('program-select', 'Web Development Bootcamp');
      cy.get('[data-cy=confirm-bulk-assign]').click();

      cy.verifyNotification('2 beneficiaries assigned to program');
    });

    it('should bulk update status', () => {
      cy.get('[data-cy=beneficiary-checkbox]').first().check();
      cy.get('[data-cy=beneficiary-checkbox]').eq(1).check();

      cy.get('[data-cy=bulk-actions-menu]').click();
      cy.get('[data-cy=bulk-update-status]').click();
      cy.waitForModal();

      cy.selectDropdown('status-select', 'inactive');
      cy.get('[data-cy=confirm-bulk-update]').click();

      cy.verifyNotification('2 beneficiaries status updated');
    });

    it('should bulk export data', () => {
      cy.get('[data-cy=select-all-checkbox]').check();
      
      cy.get('[data-cy=bulk-actions-menu]').click();
      cy.get('[data-cy=bulk-export]').click();
      cy.waitForModal();

      cy.selectDropdown('export-format', 'csv');
      cy.get('[data-cy=include-personal-info]').check();
      cy.get('[data-cy=include-progress-data]').check();
      cy.get('[data-cy=confirm-export]').click();

      cy.verifyNotification('Export started. Download will begin shortly.');
    });

    it('should bulk delete with confirmation', () => {
      cy.get('[data-cy=beneficiary-checkbox]').first().check();
      cy.get('[data-cy=beneficiary-checkbox]').eq(1).check();

      cy.get('[data-cy=bulk-actions-menu]').click();
      cy.get('[data-cy=bulk-delete]').click();
      cy.waitForModal();

      cy.get('[data-cy=delete-confirmation-input]').type('DELETE');
      cy.get('[data-cy=confirm-bulk-delete]').click();

      cy.verifyNotification('2 beneficiaries deleted successfully');
    });
  });

  describe('Program Assignment', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=beneficiary-row]').first().within(() => {
        cy.get('[data-cy=assign-programs-btn]').click();
      });
      cy.waitForModal();
    });

    it('should assign beneficiary to programs', () => {
      cy.get('[data-cy=available-programs]').within(() => {
        cy.get('[data-cy=program-checkbox]').first().check();
        cy.get('[data-cy=program-checkbox]').eq(1).check();
      });

      cy.get('[data-cy=assign-programs-btn]').click();
      cy.verifyNotification('Programs assigned successfully');
    });

    it('should remove beneficiary from programs', () => {
      cy.get('[data-cy=assigned-programs]').within(() => {
        cy.get('[data-cy=remove-program-btn]').first().click();
      });

      cy.get('[data-cy=confirm-remove-btn]').click();
      cy.verifyNotification('Program assignment removed');
    });

    it('should set enrollment preferences', () => {
      cy.get('[data-cy=program-checkbox]').first().check();
      cy.get('[data-cy=set-preferences-btn]').click();
      cy.waitForModal();

      cy.selectDropdown('priority-level', 'high');
      cy.get('[data-cy=start-date]').type('2025-07-01');
      cy.get('[data-cy=notification-enabled]').check();
      
      cy.get('[data-cy=save-preferences-btn]').click();
      cy.verifyNotification('Enrollment preferences saved');
    });
  });

  describe('Advanced Search and Filtering', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=advanced-search-btn]').click();
      cy.waitForModal();
    });

    it('should support advanced search criteria', () => {
      cy.get('[data-cy=age-range-min]').type('18');
      cy.get('[data-cy=age-range-max]').type('35');
      cy.selectDropdown('education-level-filter', 'bachelor');
      cy.selectDropdown('employment-status-filter', 'unemployed');
      cy.get('[data-cy=enrollment-date-start]').type('2025-01-01');
      cy.get('[data-cy=enrollment-date-end]').type('2025-12-31');

      cy.get('[data-cy=apply-advanced-search]').click();
      cy.waitForLoad();

      cy.get('[data-cy=advanced-search-results]').should('be.visible');
      cy.get('[data-cy=search-criteria-summary]').should('be.visible');
    });

    it('should save and load search filters', () => {
      cy.get('[data-cy=age-range-min]').type('25');
      cy.selectDropdown('education-level-filter', 'masters');
      
      cy.get('[data-cy=save-filter-btn]').click();
      cy.get('[data-cy=filter-name]').type('Masters Degree 25+');
      cy.get('[data-cy=save-filter-confirm]').click();

      cy.get('[data-cy=saved-filters-dropdown]').select('Masters Degree 25+');
      cy.get('[data-cy=age-range-min]').should('have.value', '25');
    });

    it('should export filtered results', () => {
      cy.get('[data-cy=age-range-min]').type('20');
      cy.get('[data-cy=apply-advanced-search]').click();
      cy.waitForLoad();

      cy.get('[data-cy=export-filtered-results]').click();
      cy.waitForModal();

      cy.selectDropdown('export-format', 'excel');
      cy.get('[data-cy=confirm-export]').click();

      cy.verifyNotification('Filtered results exported successfully');
    });
  });

  describe('Data Import and Export', () => {
    beforeEach(() => {
      cy.visit('/beneficiaries');
    });

    it('should import beneficiaries from CSV', () => {
      cy.get('[data-cy=import-btn]').click();
      cy.waitForModal();

      cy.uploadFile('csv-file-input', 'beneficiaries.csv', 'text/csv');
      cy.get('[data-cy=validate-import-btn]').click();
      cy.waitForLoad();

      cy.get('[data-cy=import-preview]').should('be.visible');
      cy.get('[data-cy=import-summary]').should('contain', 'rows to import');
      
      cy.get('[data-cy=confirm-import-btn]').click();
      cy.verifyNotification('Import completed successfully');
    });

    it('should validate import data', () => {
      cy.get('[data-cy=import-btn]').click();
      cy.waitForModal();

      // Upload invalid CSV
      cy.uploadFile('csv-file-input', 'invalid-beneficiaries.csv', 'text/csv');
      cy.get('[data-cy=validate-import-btn]').click();
      cy.waitForLoad();

      cy.get('[data-cy=validation-errors]').should('be.visible');
      cy.get('[data-cy=error-row]').should('have.length.at.least', 1);
      cy.get('[data-cy=fix-errors-btn]').should('be.visible');
    });

    it('should export all beneficiaries', () => {
      cy.get('[data-cy=export-all-btn]').click();
      cy.waitForModal();

      cy.selectDropdown('export-format', 'csv');
      cy.get('[data-cy=include-programs]').check();
      cy.get('[data-cy=include-progress]').check();
      cy.get('[data-cy=include-notes]').check();

      cy.get('[data-cy=start-export-btn]').click();
      cy.verifyNotification('Export started. Download will begin shortly.');
    });
  });

  describe('Accessibility and Usability', () => {
    it('should be accessible with keyboard navigation', () => {
      cy.visit('/beneficiaries');
      cy.get('body').tab();
      cy.focused().should('be.visible');

      // Navigate through table
      cy.get('[data-cy=beneficiaries-table]').within(() => {
        cy.get('button, input, select').first().focus();
        cy.focused().tab();
        cy.focused().should('be.visible');
      });
    });

    it('should meet WCAG accessibility standards', () => {
      cy.visit('/beneficiaries');
      cy.checkA11y();
    });

    it('should be responsive on mobile devices', () => {
      cy.setMobileViewport();
      cy.visit('/beneficiaries');
      
      cy.get('[data-cy=mobile-beneficiaries-view]').should('be.visible');
      cy.get('[data-cy=mobile-search-toggle]').click();
      cy.get('[data-cy=mobile-search-panel]').should('be.visible');
    });

    it('should support screen readers', () => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=beneficiaries-table]').should('have.attr', 'role', 'table');
      cy.get('[data-cy=beneficiary-row]').should('have.attr', 'role', 'row');
      cy.get('[data-cy=beneficiary-name]').should('have.attr', 'role', 'cell');
    });
  });

  describe('Performance and Error Handling', () => {
    it('should handle large datasets efficiently', () => {
      cy.visit('/beneficiaries');
      cy.measurePageLoad();
      
      // Test virtual scrolling with large dataset
      cy.get('[data-cy=page-size-select]').select('100');
      cy.waitForLoad();
      
      cy.get('[data-cy=beneficiary-row]').should('have.length.at.most', 100);
    });

    it('should handle network errors gracefully', () => {
      cy.intercept('GET', '**/api/beneficiaries', { statusCode: 500 }).as('beneficiariesError');
      
      cy.visit('/beneficiaries');
      cy.wait('@beneficiariesError');
      
      cy.get('[data-cy=error-message]').should('contain', 'Failed to load beneficiaries');
      cy.get('[data-cy=retry-btn]').click();
    });

    it('should show loading states during operations', () => {
      cy.visit('/beneficiaries');
      cy.get('[data-cy=create-beneficiary-btn]').click();
      cy.waitForModal();

      // Mock slow API response
      cy.intercept('POST', '**/api/beneficiaries', (req) => {
        req.reply((res) => {
          res.delay(2000);
          res.send({ statusCode: 201, body: { id: 1, message: 'Created' } });
        });
      }).as('slowCreate');

      cy.fillForm({
        'beneficiary-first-name': 'Test',
        'beneficiary-last-name': 'User',
        'beneficiary-email': 'test@example.com'
      });

      cy.get('[data-cy=save-beneficiary-btn]').click();
      cy.get('[data-cy=loading-spinner]').should('be.visible');
      cy.get('[data-cy=save-beneficiary-btn]').should('be.disabled');
      
      cy.wait('@slowCreate');
      cy.get('[data-cy=loading-spinner]').should('not.exist');
    });
  });
});