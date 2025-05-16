describe('Beneficiaries Management', () => {
  beforeEach(() => {
    cy.login('trainer@example.com', 'password123');
    cy.visit('/beneficiaries');
  });

  it('displays beneficiaries list', () => {
    cy.get('[data-cy=beneficiaries-table]').should('be.visible');
    cy.get('[data-cy=beneficiary-row]').should('have.length.greaterThan', 0);
  });

  it('searches beneficiaries', () => {
    cy.get('[data-cy=search-input]').type('John');
    cy.get('[data-cy=beneficiary-row]').should('contain', 'John');
    cy.get('[data-cy=beneficiary-row]').should('not.contain', 'Mary');
  });

  it('filters beneficiaries by status', () => {
    cy.get('[data-cy=status-filter]').select('active');
    cy.get('[data-cy=beneficiary-status]').each(($el) => {
      cy.wrap($el).should('contain', 'Active');
    });
  });

  it('creates new beneficiary', () => {
    cy.get('[data-cy=create-beneficiary-button]').click();
    cy.url().should('include', '/beneficiaries/new');

    cy.get('[data-cy=first-name-input]').type('New');
    cy.get('[data-cy=last-name-input]').type('Beneficiary');
    cy.get('[data-cy=email-input]').type('new.beneficiary@example.com');
    cy.get('[data-cy=phone-input]').type('+90 555 1234567');
    cy.get('[data-cy=status-select]').select('active');
    
    cy.get('[data-cy=save-button]').click();
    
    cy.url().should('match', /\/beneficiaries\/\d+$/);
    cy.get('[data-cy=beneficiary-name]').should('contain', 'New Beneficiary');
  });

  it('edits beneficiary details', () => {
    cy.get('[data-cy=beneficiary-row]').first().click();
    cy.get('[data-cy=edit-button]').click();
    
    cy.get('[data-cy=first-name-input]').clear().type('Updated');
    cy.get('[data-cy=last-name-input]').clear().type('Name');
    cy.get('[data-cy=save-button]').click();
    
    cy.get('[data-cy=beneficiary-name]').should('contain', 'Updated Name');
    cy.get('[data-cy=success-toast]').should('contain', 'Beneficiary updated successfully');
  });

  it('assigns trainer to beneficiary', () => {
    cy.get('[data-cy=beneficiary-row]').first().click();
    cy.get('[data-cy=assign-trainer-button]').click();
    
    cy.get('[data-cy=trainer-select]').select('John Trainer');
    cy.get('[data-cy=assign-button]').click();
    
    cy.get('[data-cy=trainer-name]').should('contain', 'John Trainer');
    cy.get('[data-cy=success-toast]').should('contain', 'Trainer assigned successfully');
  });

  it('views beneficiary progress', () => {
    cy.get('[data-cy=beneficiary-row]').first().click();
    cy.get('[data-cy=progress-tab]').click();
    
    cy.get('[data-cy=progress-chart]').should('be.visible');
    cy.get('[data-cy=progress-percentage]').should('be.visible');
    cy.get('[data-cy=recent-activities]').should('be.visible');
  });

  it('exports beneficiaries list', () => {
    cy.get('[data-cy=export-button]').click();
    cy.get('[data-cy=export-csv]').click();
    
    cy.readFile('cypress/downloads/beneficiaries.csv').should('exist');
  });

  it('paginates through beneficiaries', () => {
    cy.get('[data-cy=page-2]').click();
    cy.url().should('include', 'page=2');
    cy.get('[data-cy=beneficiary-row]').should('have.length.greaterThan', 0);
  });

  it('sorts beneficiaries', () => {
    cy.get('[data-cy=sort-name]').click();
    cy.get('[data-cy=beneficiary-name]').first().should('contain', 'Aaron');
    
    cy.get('[data-cy=sort-name]').click();
    cy.get('[data-cy=beneficiary-name]').first().should('contain', 'Zachary');
  });

  it('performs bulk actions', () => {
    cy.get('[data-cy=select-all]').click();
    cy.get('[data-cy=bulk-actions]').select('activate');
    cy.get('[data-cy=apply-bulk-action]').click();
    
    cy.get('[data-cy=confirm-dialog]').should('be.visible');
    cy.get('[data-cy=confirm-button]').click();
    
    cy.get('[data-cy=success-toast]').should('contain', 'Bulk action completed');
  });
});