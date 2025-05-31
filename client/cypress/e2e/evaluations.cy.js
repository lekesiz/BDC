describe('Evaluations Module', () => {
  context('Trainer role', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/evaluations');
    });

    it('displays list of evaluations', () => {
      cy.getByCy('evaluations-list').should('exist');
      cy.getByCy('evaluation-card').should('have.length.at.least', 1);
      
      // Check that each card contains the expected elements
      cy.getByCy('evaluation-card').first().within(() => {
        cy.getByCy('evaluation-title').should('exist');
        cy.getByCy('evaluation-status').should('exist');
        cy.getByCy('evaluation-date').should('exist');
        cy.getByCy('evaluation-beneficiary').should('exist');
        cy.getByCy('view-evaluation-button').should('exist');
      });
    });

    it('allows filtering evaluations', () => {
      // Test status filter
      cy.getByCy('status-filter').click();
      cy.getByCy('status-option-completed').click();
      cy.getByCy('evaluation-card').each(($card) => {
        cy.wrap($card).find('[data-cy=evaluation-status]').should('contain', 'Completed');
      });
      
      // Test date range filter
      cy.getByCy('date-filter').click();
      cy.getByCy('date-range-this-month').click();
      // Assuming the UI shows filtered results
      cy.getByCy('active-filters').should('contain', 'This Month');
    });

    it('navigates to evaluation details', () => {
      cy.getByCy('evaluation-card').first().within(() => {
        cy.getByCy('evaluation-title').invoke('text').as('evaluationTitle');
        cy.getByCy('view-evaluation-button').click();
      });
      
      cy.url().should('include', '/evaluations/');
      
      // Verify the title is displayed on the details page
      cy.get('@evaluationTitle').then(title => {
        cy.getByCy('evaluation-detail-title').should('contain', title.trim());
      });
    });

    it('creates a new evaluation', () => {
      const uniqueId = Date.now().toString();
      const testTitle = `Test Evaluation ${uniqueId}`;
      
      // Open creation form
      cy.getByCy('create-evaluation-button').click();
      
      // Fill out the form
      cy.getByCy('evaluation-form-title').type(testTitle);
      cy.getByCy('evaluation-form-description').type('This is an automated test evaluation');
      
      // Select a beneficiary
      cy.getByCy('evaluation-form-beneficiary').click();
      cy.getByCy('beneficiary-option').first().click();
      
      // Add questions (assuming there's a way to add questions)
      cy.getByCy('add-question-button').click();
      cy.getByCy('question-type-selector').select('Multiple Choice');
      cy.getByCy('question-text').type('What is the capital of France?');
      cy.getByCy('add-option-button').click();
      cy.getByCy('option-text-0').type('Paris');
      cy.getByCy('correct-option-0').check();
      cy.getByCy('add-option-button').click();
      cy.getByCy('option-text-1').type('London');
      cy.getByCy('add-option-button').click();
      cy.getByCy('option-text-2').type('Berlin');
      cy.getByCy('save-question-button').click();
      
      // Submit the form
      cy.getByCy('save-evaluation-button').click();
      
      // Verify success message
      cy.getByCy('success-message').should('contain', 'Evaluation created successfully');
      
      // Verify the new evaluation appears in the list
      cy.visit('/evaluations');
      cy.getByCy('search-input').type(testTitle);
      cy.getByCy('evaluation-card').should('have.length', 1);
      cy.getByCy('evaluation-title').should('contain', testTitle);
    });

    it('allows grading a submitted evaluation', () => {
      // Find an evaluation with 'Submitted' status
      cy.getByCy('status-filter').click();
      cy.getByCy('status-option-submitted').click();
      
      cy.getByCy('evaluation-card').first().within(() => {
        cy.getByCy('view-evaluation-button').click();
      });
      
      // Grade the evaluation
      cy.getByCy('grade-evaluation-button').click();
      
      // Provide feedback and scores
      cy.getByCy('overall-score').type('85');
      cy.getByCy('feedback-text').type('Good work on this evaluation. Some areas for improvement include...');
      
      // Save the grading
      cy.getByCy('submit-grading-button').click();
      
      // Verify success message
      cy.getByCy('success-message').should('contain', 'Evaluation graded successfully');
      
      // Verify status changed to 'Graded'
      cy.getByCy('evaluation-status').should('contain', 'Graded');
    });
  });

  context('Student role', () => {
    beforeEach(() => {
      cy.loginAsStudent();
      cy.visit('/portal/assessments');
    });

    it('displays assigned evaluations', () => {
      cy.getByCy('my-evaluations-list').should('exist');
      cy.getByCy('evaluation-card').should('have.length.at.least', 1);
    });

    it('allows taking an evaluation', () => {
      // Find an evaluation with 'Assigned' status
      cy.getByCy('evaluation-card').first().within(() => {
        cy.getByCy('start-evaluation-button').click();
      });
      
      // Should be on the evaluation page
      cy.getByCy('evaluation-question').should('exist');
      
      // Answer all questions (simplified for test)
      cy.getByCy('answer-option').first().click();
      cy.getByCy('next-question-button').click();
      
      // Continue until reaching the last question
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy=submit-evaluation-button]').length === 0) {
          cy.getByCy('answer-option').first().click();
          cy.getByCy('next-question-button').click();
        }
      });
      
      // Submit the evaluation
      cy.getByCy('submit-evaluation-button').click();
      cy.getByCy('confirm-submit-button').click();
      
      // Verify success message
      cy.getByCy('success-message').should('contain', 'Evaluation submitted successfully');
      
      // Should be redirected to results page
      cy.url().should('include', '/results');
    });

    it('shows evaluation results', () => {
      // Find a completed evaluation
      cy.getByCy('status-filter').click();
      cy.getByCy('status-option-graded').click();
      
      cy.getByCy('evaluation-card').first().within(() => {
        cy.getByCy('view-results-button').click();
      });
      
      // Verify results page components
      cy.getByCy('evaluation-score').should('exist');
      cy.getByCy('evaluation-feedback').should('exist');
      cy.getByCy('questions-summary').should('exist');
    });
  });

  it('performs accessibility check on evaluations list', () => {
    cy.loginAsTrainer();
    cy.visit('/evaluations');
    cy.checkA11y();
  });
});