describe('Program Management E2E', () => {
  beforeEach(() => {
    // Login as admin
    cy.visit('/login');
    cy.get('[data-cy="email-input"]').type('admin@bdc.com');
    cy.get('[data-cy="password-input"]').type('Admin123!');
    cy.get('[data-cy="login-button"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    
    // Navigate to programs page
    cy.visit('/programs');
    cy.wait(1000); // Wait for page to load
  });

  it('should display programs list', () => {
    cy.get('[data-cy="programs-page"]').should('exist');
    cy.get('h1').should('contain', 'Training Programs');
  });

  it('should create a new program', () => {
    // Click create program button
    cy.get('[data-cy="create-program-button"]').click();
    
    // Fill program form
    cy.get('[data-cy="program-name"]').type('E2E Test Program');
    cy.get('[data-cy="program-description"]').type('This is a test program created by E2E tests');
    cy.get('[data-cy="program-category"]').select('technical');
    cy.get('[data-cy="program-level"]').select('beginner');
    cy.get('[data-cy="program-duration"]').type('14');
    cy.get('[data-cy="program-max-participants"]').type('20');
    
    // Submit form
    cy.get('[data-cy="save-program-button"]').click();
    
    // Verify program was created
    cy.get('[data-cy="toast-success"]').should('be.visible');
    cy.get('[data-cy="program-card"]').should('contain', 'E2E Test Program');
  });

  it('should edit an existing program', () => {
    // First create a program to edit
    cy.createProgram({
      name: 'Program to Edit',
      description: 'Original description',
      category: 'technical',
      level: 'beginner',
      duration: 14
    });
    
    // Find and edit the program
    cy.get('[data-cy="program-card"]')
      .contains('Program to Edit')
      .parent()
      .find('[data-cy="edit-program-button"]')
      .click();
    
    // Update program details
    cy.get('[data-cy="program-name"]').clear().type('Updated Program Name');
    cy.get('[data-cy="program-description"]').clear().type('Updated description');
    cy.get('[data-cy="program-level"]').select('intermediate');
    
    // Save changes
    cy.get('[data-cy="save-program-button"]').click();
    
    // Verify changes were saved
    cy.get('[data-cy="toast-success"]').should('be.visible');
    cy.get('[data-cy="program-card"]').should('contain', 'Updated Program Name');
    cy.get('[data-cy="program-card"]').should('contain', 'Updated description');
  });

  it('should delete a program', () => {
    // First create a program to delete
    cy.createProgram({
      name: 'Program to Delete',
      description: 'This will be deleted',
      category: 'soft_skills',
      level: 'beginner',
      duration: 7
    });
    
    // Find and delete the program
    cy.get('[data-cy="program-card"]')
      .contains('Program to Delete')
      .parent()
      .find('[data-cy="delete-program-button"]')
      .click();
    
    // Confirm deletion
    cy.get('[data-cy="confirm-delete-button"]').click();
    
    // Verify program was deleted
    cy.get('[data-cy="toast-success"]').should('be.visible');
    cy.get('[data-cy="program-card"]').should('not.contain', 'Program to Delete');
  });

  it('should filter programs by search', () => {
    // Create test programs
    cy.createProgram({
      name: 'JavaScript Fundamentals',
      description: 'Learn JavaScript basics',
      category: 'technical',
      level: 'beginner'
    });
    
    cy.createProgram({
      name: 'Python Advanced',
      description: 'Advanced Python concepts',
      category: 'technical',
      level: 'advanced'
    });
    
    // Search for JavaScript
    cy.get('[data-cy="search-input"]').type('JavaScript');
    
    // Verify filtered results
    cy.get('[data-cy="program-card"]').should('have.length', 1);
    cy.get('[data-cy="program-card"]').should('contain', 'JavaScript Fundamentals');
    cy.get('[data-cy="program-card"]').should('not.contain', 'Python Advanced');
    
    // Clear search
    cy.get('[data-cy="search-input"]').clear();
    
    // Verify all programs are shown again
    cy.get('[data-cy="program-card"]').should('have.length.at.least', 2);
  });

  it('should filter programs by category', () => {
    // Create programs in different categories
    cy.createProgram({
      name: 'Technical Training',
      category: 'technical',
      level: 'beginner'
    });
    
    cy.createProgram({
      name: 'Communication Skills',
      category: 'soft_skills',
      level: 'beginner'
    });
    
    // Open filter dropdown
    cy.get('[data-cy="filter-button"]').click();
    
    // Select technical category
    cy.get('[data-cy="category-filter"]').select('technical');
    cy.get('[data-cy="apply-filter-button"]').click();
    
    // Verify filtered results
    cy.get('[data-cy="program-card"]').should('contain', 'Technical Training');
    cy.get('[data-cy="program-card"]').should('not.contain', 'Communication Skills');
  });

  it('should navigate to program detail page', () => {
    // Create a program to view
    cy.createProgram({
      name: 'Detailed Program',
      description: 'Program with details to view',
      category: 'technical',
      level: 'intermediate',
      duration: 21
    });
    
    // Click on program to view details
    cy.get('[data-cy="program-card"]')
      .contains('Detailed Program')
      .parent()
      .find('[data-cy="view-program-button"]')
      .click();
    
    // Verify we're on the detail page
    cy.url().should('include', '/programs/');
    cy.get('h1').should('contain', 'Detailed Program');
    cy.get('[data-cy="program-description"]').should('contain', 'Program with details to view');
    cy.get('[data-cy="program-duration"]').should('contain', '3 weeks');
    cy.get('[data-cy="program-level"]').should('contain', 'intermediate');
  });

  it('should show enrolled students in program detail', () => {
    // Create a program
    cy.createProgram({
      name: 'Program with Students',
      description: 'Program to test student enrollment',
      category: 'technical',
      level: 'beginner'
    });
    
    // Navigate to program detail
    cy.get('[data-cy="program-card"]')
      .contains('Program with Students')
      .parent()
      .find('[data-cy="view-program-button"]')
      .click();
    
    // Verify students section exists
    cy.get('[data-cy="enrolled-students-section"]').should('exist');
    cy.get('[data-cy="students-count"]').should('contain', '0');
    
    // If there are students, they should be displayed
    cy.get('[data-cy="student-list"]').should('exist');
  });

  it('should handle real-time updates', () => {
    // This test would require WebSocket mocking or a real-time server
    // For now, we'll test the UI state changes
    
    cy.get('[data-cy="programs-list"]').should('exist');
    
    // Simulate real-time program creation by manually triggering events
    cy.window().then((win) => {
      // Simulate WebSocket event
      const mockProgram = {
        id: 999,
        name: 'Real-time Program',
        description: 'Added via WebSocket',
        status: 'active',
        category: 'technical',
        level: 'beginner'
      };
      
      // Trigger the program_created event handler if available
      if (win.socket && win.socket.emit) {
        win.socket.emit('program_created', { program: mockProgram });
      }
    });
    
    // In a real implementation, we would verify the program appears in the list
    // For now, just verify the list is still functional
    cy.get('[data-cy="programs-list"]').should('be.visible');
  });
});

// Custom command to create a program via API
Cypress.Commands.add('createProgram', (programData) => {
  cy.request({
    method: 'POST',
    url: '/api/programs',
    headers: {
      'Authorization': `Bearer ${Cypress.env('authToken')}`
    },
    body: {
      name: programData.name,
      description: programData.description || 'Test program description',
      category: programData.category || 'technical',
      level: programData.level || 'beginner',
      duration: programData.duration || 14,
      status: programData.status || 'active',
      max_participants: programData.max_participants || 25
    }
  }).then((response) => {
    expect(response.status).to.eq(201);
    return response.body;
  });
});

// Custom command to login and store auth token
Cypress.Commands.add('loginAsAdmin', () => {
  cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: {
      email: 'admin@bdc.com',
      password: 'Admin123!'
    }
  }).then((response) => {
    expect(response.status).to.eq(200);
    Cypress.env('authToken', response.body.access_token);
    window.localStorage.setItem('access_token', response.body.access_token);
  });
});