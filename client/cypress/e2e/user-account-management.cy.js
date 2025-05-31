describe('User Account Management', () => {
  beforeEach(() => {
    cy.loginAsAdmin();
    cy.visit('/admin/users');
  });

  it('displays user list with correct information', () => {
    cy.getByCy('user-list').should('exist');
    cy.getByCy('user-row').should('have.length.at.least', 1);
    
    // Check that each user row contains the expected elements
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('user-name').should('exist');
      cy.getByCy('user-email').should('exist');
      cy.getByCy('user-role').should('exist');
      cy.getByCy('user-status').should('exist');
      cy.getByCy('user-actions').should('exist');
    });
  });

  it('allows creating a new user', () => {
    const uniqueId = Date.now().toString();
    const testEmail = `test.user.${uniqueId}@example.com`;
    
    // Open creation form
    cy.getByCy('add-user-button').click();
    
    // Fill out the form
    cy.getByCy('user-form-firstName').type('Test');
    cy.getByCy('user-form-lastName').type(`User ${uniqueId}`);
    cy.getByCy('user-form-email').type(testEmail);
    cy.getByCy('user-form-role').select('Trainer');
    cy.getByCy('user-form-password').type('TestPassword123!');
    cy.getByCy('user-form-confirmPassword').type('TestPassword123!');
    
    // Submit the form
    cy.getByCy('save-user-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'User created successfully');
    
    // Verify the new user appears in the list
    cy.getByCy('search-input').type(testEmail);
    cy.getByCy('user-row').should('have.length', 1);
    cy.getByCy('user-email').should('contain', testEmail);
  });

  it('allows editing an existing user', () => {
    // Click on first user edit button
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('edit-user-button').click();
    });
    
    // Change some information
    const newTitle = 'Updated Title ' + Date.now();
    cy.getByCy('user-form-title').clear().type(newTitle);
    
    // Save changes
    cy.getByCy('save-user-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'User updated successfully');
    
    // Verify title was updated
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('user-title').should('contain', newTitle);
    });
  });

  it('allows changing user role', () => {
    // Open role change dialog for first user
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('user-role').invoke('text').as('initialRole');
      cy.getByCy('change-role-button').click();
    });
    
    // Select a different role
    cy.getByCy('role-select').click();
    cy.getByCy('role-option-trainer').click();
    
    // Confirm role change
    cy.getByCy('confirm-role-change').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'Role updated successfully');
    
    // Verify role was changed
    cy.get('@initialRole').then(initialRole => {
      cy.getByCy('user-row').first().within(() => {
        cy.getByCy('user-role').should('not.contain', initialRole.trim());
      });
    });
  });

  it('allows deactivating a user', () => {
    // Find an active user
    cy.getByCy('status-filter').select('Active');
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('user-email').invoke('text').as('userEmail');
      cy.getByCy('deactivate-user-button').click();
    });
    
    // Confirm deactivation
    cy.getByCy('confirm-deactivate-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'User deactivated successfully');
    
    // Verify user status changed to inactive
    cy.get('@userEmail').then(email => {
      cy.getByCy('search-input').clear().type(email);
      cy.getByCy('user-row').first().within(() => {
        cy.getByCy('user-status').should('contain', 'Inactive');
      });
    });
  });

  it('allows reactivating a user', () => {
    // Find an inactive user
    cy.getByCy('status-filter').select('Inactive');
    cy.getByCy('user-row').first().within(() => {
      cy.getByCy('user-email').invoke('text').as('userEmail');
      cy.getByCy('reactivate-user-button').click();
    });
    
    // Confirm reactivation
    cy.getByCy('confirm-reactivate-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'User reactivated successfully');
    
    // Verify user status changed to active
    cy.get('@userEmail').then(email => {
      cy.getByCy('search-input').clear().type(email);
      cy.getByCy('user-row').first().within(() => {
        cy.getByCy('user-status').should('contain', 'Active');
      });
    });
  });

  it('allows filtering and sorting users', () => {
    // Test role filter
    cy.getByCy('role-filter').select('Trainer');
    cy.getByCy('user-row').each(($row) => {
      cy.wrap($row).find('[data-cy=user-role]').should('contain', 'Trainer');
    });
    
    // Test status filter
    cy.getByCy('role-filter').select('All'); // Reset role filter
    cy.getByCy('status-filter').select('Active');
    cy.getByCy('user-row').each(($row) => {
      cy.wrap($row).find('[data-cy=user-status]').should('contain', 'Active');
    });
    
    // Test search filter
    cy.getByCy('status-filter').select('All'); // Reset status filter
    cy.getByCy('search-input').type('admin');
    cy.getByCy('user-row').should('have.length.at.most', 5);
    
    // Test sorting
    cy.getByCy('sort-by-name').click();
    cy.getByCy('user-name').first().invoke('text').as('firstNameAsc');
    
    cy.getByCy('sort-direction').click(); // Change to descending
    cy.getByCy('user-name').first().invoke('text').as('firstNameDesc');
    
    cy.get('@firstNameAsc').then(nameAsc => {
      cy.get('@firstNameDesc').then(nameDesc => {
        expect(nameAsc).not.to.eq(nameDesc);
      });
    });
  });

  it('allows users to change their own password', () => {
    // Navigate to profile page
    cy.getByCy('user-menu').click();
    cy.getByCy('profile-link').click();
    
    // Go to change password tab
    cy.getByCy('change-password-tab').click();
    
    // Fill in password form
    cy.getByCy('current-password').type('Admin123!');
    cy.getByCy('new-password').type('NewAdmin123!');
    cy.getByCy('confirm-password').type('NewAdmin123!');
    
    // Submit form
    cy.getByCy('update-password-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'Password updated successfully');
    
    // Reset password for future tests
    cy.getByCy('current-password').type('NewAdmin123!');
    cy.getByCy('new-password').type('Admin123!');
    cy.getByCy('confirm-password').type('Admin123!');
    cy.getByCy('update-password-button').click();
  });

  it('allows users to update their profile information', () => {
    // Navigate to profile page
    cy.getByCy('user-menu').click();
    cy.getByCy('profile-link').click();
    
    // Edit profile info
    const newTitle = 'Updated Title ' + Date.now();
    cy.getByCy('edit-profile-button').click();
    cy.getByCy('profile-title').clear().type(newTitle);
    
    // Save changes
    cy.getByCy('save-profile-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'Profile updated successfully');
    
    // Verify changes persisted
    cy.reload();
    cy.getByCy('profile-title-value').should('contain', newTitle);
  });

  it('performs accessibility check on user management', () => {
    cy.checkA11y();
  });

  it('performs accessibility check on user profile page', () => {
    cy.getByCy('user-menu').click();
    cy.getByCy('profile-link').click();
    cy.checkA11y();
  });
});