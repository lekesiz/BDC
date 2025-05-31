describe('Beneficiaries Management', () => {
  beforeEach(() => {
    cy.loginAsTrainer();
    cy.visit('/beneficiaries');
  });

  it('displays list of beneficiaries with correct information', () => {
    cy.getByCy('beneficiaries-list').should('exist');
    cy.getByCy('beneficiary-card').should('have.length.at.least', 1);
    
    // Check that each card contains the expected elements
    cy.getByCy('beneficiary-card').first().within(() => {
      cy.getByCy('beneficiary-name').should('exist');
      cy.getByCy('beneficiary-email').should('exist');
      cy.getByCy('beneficiary-status').should('exist');
      cy.getByCy('view-details-button').should('exist');
    });
  });

  it('allows filtering beneficiaries', () => {
    // Test search filter
    cy.getByCy('search-input').type('John');
    cy.getByCy('beneficiary-card').should('have.length.at.most', 5);
    cy.getByCy('search-input').clear();
    
    // Test status filter
    cy.getByCy('status-filter').click();
    cy.getByCy('status-option-active').click();
    cy.getByCy('beneficiary-card').each(($card) => {
      cy.wrap($card).find('[data-cy=beneficiary-status]').should('contain', 'Active');
    });
  });

  it('allows sorting beneficiaries', () => {
    // Test name sorting
    cy.getByCy('sort-dropdown').click();
    cy.getByCy('sort-by-name').click();
    
    // Get names before and after changing sort direction
    cy.getByCy('beneficiary-name').first().invoke('text').as('firstNameAsc');
    
    cy.getByCy('sort-direction').click(); // Change to descending
    cy.getByCy('beneficiary-name').first().invoke('text').as('firstNameDesc');
    
    // Compare names to verify sorting changed
    cy.get('@firstNameAsc').then(nameAsc => {
      cy.get('@firstNameDesc').then(nameDesc => {
        expect(nameAsc).not.to.eq(nameDesc);
      });
    });
  });

  it('navigates to beneficiary details page', () => {
    // Click on first beneficiary details button
    cy.getByCy('beneficiary-card').first().within(() => {
      cy.getByCy('beneficiary-name').invoke('text').as('beneficiaryName');
      cy.getByCy('view-details-button').click();
    });
    
    // Check we're on the details page
    cy.url().should('include', '/beneficiaries/');
    
    // Verify the name is displayed on the details page
    cy.get('@beneficiaryName').then(name => {
      cy.getByCy('beneficiary-detail-name').should('contain', name.trim());
    });
  });

  it('allows creating a new beneficiary', () => {
    const uniqueId = Date.now().toString();
    const testEmail = `test.beneficiary.${uniqueId}@example.com`;
    
    // Open creation form
    cy.getByCy('add-beneficiary-button').click();
    
    // Fill out the form
    cy.getByCy('beneficiary-form-firstName').type('Test');
    cy.getByCy('beneficiary-form-lastName').type(`Beneficiary ${uniqueId}`);
    cy.getByCy('beneficiary-form-email').type(testEmail);
    cy.getByCy('beneficiary-form-phone').type('555-123-4567');
    cy.getByCy('beneficiary-form-status').select('Active');
    
    // Submit the form
    cy.getByCy('save-beneficiary-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'Beneficiary created successfully');
    
    // Verify the new beneficiary appears in the list
    cy.getByCy('search-input').type(testEmail);
    cy.getByCy('beneficiary-card').should('have.length', 1);
    cy.getByCy('beneficiary-email').should('contain', testEmail);
  });

  it('allows editing an existing beneficiary', () => {
    // Click on first beneficiary details button
    cy.getByCy('beneficiary-card').first().within(() => {
      cy.getByCy('view-details-button').click();
    });
    
    // Click edit button on details page
    cy.getByCy('edit-beneficiary-button').click();
    
    // Change some information
    const newNote = 'Automated test note ' + Date.now();
    cy.getByCy('beneficiary-form-notes').clear().type(newNote);
    
    // Save changes
    cy.getByCy('save-beneficiary-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'Beneficiary updated successfully');
    
    // Verify note was updated
    cy.getByCy('beneficiary-notes').should('contain', newNote);
  });

  it('performs accessibility check on beneficiaries list', () => {
    cy.checkA11y();
  });
});