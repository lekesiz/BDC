describe('Comprehensive Evaluation System', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.waitForLoad();
  });

  afterEach(() => {
    cy.dismissNotification();
  });

  describe('Test Creation (Trainer View)', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/evaluations/create');
      cy.waitForLoad();
    });

    it('should create a comprehensive test with multiple question types', () => {
      const testData = {
        title: `Comprehensive Test ${Date.now()}`,
        description: 'A test covering multiple question types and assessment methods',
        duration: 60,
        passingScore: 70,
        maxAttempts: 3,
        category: 'Assessment'
      };

      // Basic test information
      cy.fillForm({
        'test-title': testData.title,
        'test-description': testData.description,
        'test-duration': testData.duration,
        'passing-score': testData.passingScore,
        'max-attempts': testData.maxAttempts
      });

      cy.selectDropdown('test-category', testData.category);
      cy.get('[data-cy=randomize-questions]').check();
      cy.get('[data-cy=show-results-immediately]').check();

      // Add multiple choice question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-type-select]').select('multiple_choice');
      cy.get('[data-cy=question-text]').type('What is the capital of France?');
      cy.get('[data-cy=question-points]').clear().type('5');

      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-1]').type('Paris');
      cy.get('[data-cy=option-correct-1]').check();

      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-2]').type('London');

      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-3]').type('Berlin');

      cy.get('[data-cy=save-question-btn]').click();

      // Add true/false question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-type-select]').select('true_false');
      cy.get('[data-cy=question-text]').type('JavaScript is a programming language.');
      cy.get('[data-cy=question-points]').clear().type('3');
      cy.get('[data-cy=correct-answer]').select('true');
      cy.get('[data-cy=save-question-btn]').click();

      // Add short answer question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-type-select]').select('short_answer');
      cy.get('[data-cy=question-text]').type('Explain the concept of object-oriented programming in 2-3 sentences.');
      cy.get('[data-cy=question-points]').clear().type('10');
      cy.get('[data-cy=save-question-btn]').click();

      // Add essay question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-type-select]').select('essay');
      cy.get('[data-cy=question-text]').type('Discuss the advantages and disadvantages of different programming paradigms.');
      cy.get('[data-cy=question-points]').clear().type('15');
      cy.get('[data-cy=word-limit]').type('500');
      cy.get('[data-cy=save-question-btn]').click();

      // Save the test
      cy.get('[data-cy=save-test-btn]').click();
      cy.verifyNotification('Test created successfully');
      
      cy.url().should('include', '/evaluations');
      cy.get('[data-cy=test-list]').should('contain', testData.title);
    });

    it('should validate test creation form', () => {
      cy.get('[data-cy=save-test-btn]').click();
      
      cy.get('[data-cy=title-error]').should('contain', 'Title is required');
      cy.get('[data-cy=duration-error]').should('contain', 'Duration is required');

      // Test invalid duration
      cy.get('[data-cy=test-duration]').type('0');
      cy.get('[data-cy=save-test-btn]').click();
      cy.get('[data-cy=duration-error]').should('contain', 'Duration must be at least 1 minute');

      // Test invalid passing score
      cy.get('[data-cy=passing-score]').type('150');
      cy.get('[data-cy=save-test-btn]').click();
      cy.get('[data-cy=passing-score-error]').should('contain', 'Passing score cannot exceed 100%');
    });

    it('should support question reordering and editing', () => {
      // Create test with multiple questions first
      cy.fillForm({
        'test-title': 'Reorder Test',
        'test-duration': '30'
      });

      // Add first question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-text]').type('Question 1');
      cy.get('[data-cy=save-question-btn]').click();

      // Add second question
      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-text]').type('Question 2');
      cy.get('[data-cy=save-question-btn]').click();

      // Reorder questions using drag and drop
      cy.get('[data-cy=question-item-2]').drag('[data-cy=question-item-1]');
      
      // Verify order changed
      cy.get('[data-cy=question-item]').first().should('contain', 'Question 2');

      // Edit question
      cy.get('[data-cy=question-item]').first().within(() => {
        cy.get('[data-cy=edit-question-btn]').click();
      });

      cy.get('[data-cy=question-text]').clear().type('Updated Question 2');
      cy.get('[data-cy=save-question-btn]').click();

      cy.get('[data-cy=question-item]').first().should('contain', 'Updated Question 2');
    });

    it('should import questions from question bank', () => {
      cy.fillForm({
        'test-title': 'Import Questions Test',
        'test-duration': '45'
      });

      cy.get('[data-cy=import-from-bank-btn]').click();
      cy.waitForModal();

      // Filter by category
      cy.selectDropdown('question-category-filter', 'Programming');
      cy.waitForLoad();

      // Select questions
      cy.get('[data-cy=question-bank-item]').first().within(() => {
        cy.get('[data-cy=select-question-checkbox]').check();
      });

      cy.get('[data-cy=question-bank-item]').eq(1).within(() => {
        cy.get('[data-cy=select-question-checkbox]').check();
      });

      cy.get('[data-cy=import-selected-btn]').click();
      cy.verifyNotification('2 questions imported successfully');

      cy.get('[data-cy=question-item]').should('have.length', 2);
    });

    it('should preview test before publishing', () => {
      cy.fillForm({
        'test-title': 'Preview Test',
        'test-duration': '20'
      });

      cy.get('[data-cy=add-question-btn]').click();
      cy.get('[data-cy=question-text]').type('Sample question for preview');
      cy.get('[data-cy=save-question-btn]').click();

      cy.get('[data-cy=preview-test-btn]').click();
      cy.waitForModal();

      // Verify preview interface
      cy.get('[data-cy=test-preview]').should('be.visible');
      cy.get('[data-cy=preview-question]').should('contain', 'Sample question for preview');
      cy.get('[data-cy=preview-timer]').should('be.visible');
      cy.get('[data-cy=preview-navigation]').should('be.visible');

      cy.get('[data-cy=close-preview-btn]').click();
    });
  });

  describe('Test Taking (Student View)', () => {
    beforeEach(() => {
      cy.loginAsStudent();
      cy.visit('/portal/assessments');
      cy.waitForLoad();
    });

    it('should display available tests and allow starting', () => {
      cy.get('[data-cy=available-tests]').should('be.visible');
      cy.get('[data-cy=test-card]').should('have.length.at.least', 1);

      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=test-title]').should('be.visible');
        cy.get('[data-cy=test-duration]').should('be.visible');
        cy.get('[data-cy=test-questions-count]').should('be.visible');
        cy.get('[data-cy=test-attempts-remaining]').should('be.visible');
        cy.get('[data-cy=start-test-btn]').should('be.visible');
      });
    });

    it('should complete a full test session', () => {
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();
      cy.get('[data-cy=test-session]').should('be.visible');

      // Check test interface elements
      cy.get('[data-cy=test-timer]').should('be.visible');
      cy.get('[data-cy=question-counter]').should('be.visible');
      cy.get('[data-cy=current-question]').should('be.visible');
      cy.get('[data-cy=navigation-buttons]').should('be.visible');

      // Answer multiple choice question
      cy.get('[data-cy=question-type]').then($type => {
        if ($type.text().includes('multiple_choice')) {
          cy.get('[data-cy=answer-option]').first().click();
        }
      });

      // Navigate through questions
      cy.get('[data-cy=next-question-btn]').click();

      // Answer true/false question
      cy.get('[data-cy=question-type]').then($type => {
        if ($type.text().includes('true_false')) {
          cy.get('[data-cy=true-option]').click();
        }
      });

      cy.get('[data-cy=next-question-btn]').click();

      // Answer short answer question
      cy.get('[data-cy=question-type]').then($type => {
        if ($type.text().includes('short_answer')) {
          cy.get('[data-cy=answer-textarea]').type('Object-oriented programming is a programming paradigm based on objects and classes.');
        }
      });

      // Submit test
      cy.get('[data-cy=finish-test-btn]').click();
      cy.get('[data-cy=confirm-submit-modal]').should('be.visible');
      cy.get('[data-cy=confirm-submit-btn]').click();

      // Verify submission
      cy.verifyNotification('Test submitted successfully');
      cy.url().should('include', '/portal/assessments/results');
    });

    it('should handle test timer and auto-submit', () => {
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Mock timer expiration
      cy.window().then(win => {
        win.testTimer = { timeRemaining: 0 };
        win.dispatchEvent(new Event('timer-expired'));
      });

      cy.get('[data-cy=time-expired-modal]').should('be.visible');
      cy.get('[data-cy=auto-submit-message]').should('contain', 'Time has expired');
      
      cy.verifyNotification('Test auto-submitted due to time expiration');
    });

    it('should save answers automatically and allow resuming', () => {
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Answer first question
      cy.get('[data-cy=answer-option]').first().click();
      cy.wait(2000); // Wait for auto-save

      // Simulate browser refresh/close
      cy.reload();
      cy.waitForLoad();

      // Should be able to resume
      cy.get('[data-cy=resume-test-modal]').should('be.visible');
      cy.get('[data-cy=resume-test-btn]').click();

      // Verify answer is preserved
      cy.get('[data-cy=answer-option]').first().should('be.checked');
    });

    it('should handle network interruptions gracefully', () => {
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Simulate network error
      cy.intercept('POST', '**/api/test-sessions/*/answers', { statusCode: 500 }).as('saveError');

      cy.get('[data-cy=answer-option]').first().click();
      cy.wait('@saveError');

      cy.get('[data-cy=connection-error-banner]').should('be.visible');
      cy.get('[data-cy=offline-mode-indicator]').should('be.visible');
      
      // Should queue answers for later submission
      cy.get('[data-cy=queued-answers-count]').should('be.visible');
    });

    it('should validate test attempt limits', () => {
      // Find a test with limited attempts
      cy.get('[data-cy=test-card]').contains('[data-cy=test-attempts-remaining]', '0 attempts remaining')
        .parent().within(() => {
          cy.get('[data-cy=start-test-btn]').should('be.disabled');
          cy.get('[data-cy=attempts-exhausted-message]').should('be.visible');
        });
    });

    it('should support test accessibility features', () => {
      cy.get('[data-cy=accessibility-options-btn]').click();
      cy.waitForModal();

      cy.get('[data-cy=large-font-option]').check();
      cy.get('[data-cy=high-contrast-option]').check();
      cy.get('[data-cy=screen-reader-mode]').check();
      cy.get('[data-cy=extended-time-option]').check();

      cy.get('[data-cy=save-accessibility-options]').click();

      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Verify accessibility features are applied
      cy.get('[data-cy=test-session]').should('have.class', 'large-font');
      cy.get('[data-cy=test-session]').should('have.class', 'high-contrast');
      cy.get('[data-cy=extended-time-indicator]').should('be.visible');
    });
  });

  describe('Test Results and Analytics', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/evaluations/results');
      cy.waitForLoad();
    });

    it('should display comprehensive test results', () => {
      cy.get('[data-cy=results-list]').should('be.visible');
      cy.get('[data-cy=result-item]').should('have.length.at.least', 1);

      cy.get('[data-cy=result-item]').first().within(() => {
        cy.get('[data-cy=student-name]').should('be.visible');
        cy.get('[data-cy=test-title]').should('be.visible');
        cy.get('[data-cy=score]').should('be.visible');
        cy.get('[data-cy=completion-date]').should('be.visible');
        cy.get('[data-cy=time-taken]').should('be.visible');
        cy.get('[data-cy=view-details-btn]').should('be.visible');
      });
    });

    it('should allow detailed result analysis', () => {
      cy.get('[data-cy=result-item]').first().within(() => {
        cy.get('[data-cy=view-details-btn]').click();
      });

      cy.waitForLoad();
      cy.get('[data-cy=result-details]').should('be.visible');

      // Student information
      cy.get('[data-cy=student-info-section]').should('be.visible');
      cy.get('[data-cy=student-name]').should('be.visible');
      cy.get('[data-cy=student-email]').should('be.visible');

      // Test summary
      cy.get('[data-cy=test-summary-section]').should('be.visible');
      cy.get('[data-cy=overall-score]').should('be.visible');
      cy.get('[data-cy=questions-correct]').should('be.visible');
      cy.get('[data-cy=time-taken]').should('be.visible');

      // Question-by-question breakdown
      cy.get('[data-cy=question-breakdown]').should('be.visible');
      cy.get('[data-cy=question-result]').each($question => {
        cy.wrap($question).within(() => {
          cy.get('[data-cy=question-text]').should('be.visible');
          cy.get('[data-cy=student-answer]').should('be.visible');
          cy.get('[data-cy=correct-answer]').should('be.visible');
          cy.get('[data-cy=points-earned]').should('be.visible');
        });
      });
    });

    it('should support manual grading for subjective questions', () => {
      // Find a result with essay/short answer questions
      cy.get('[data-cy=result-item]').contains('[data-cy=requires-grading]', 'Manual grading required')
        .parent().within(() => {
          cy.get('[data-cy=grade-test-btn]').click();
        });

      cy.waitForLoad();
      cy.get('[data-cy=grading-interface]').should('be.visible');

      // Grade essay question
      cy.get('[data-cy=essay-question]').first().within(() => {
        cy.get('[data-cy=student-answer]').should('be.visible');
        cy.get('[data-cy=rubric-criteria]').should('be.visible');
        
        cy.get('[data-cy=points-input]').clear().type('12');
        cy.get('[data-cy=feedback-textarea]').type('Good understanding demonstrated. Could provide more specific examples.');
        cy.get('[data-cy=save-grade-btn]').click();
      });

      // Submit final grade
      cy.get('[data-cy=submit-final-grade-btn]').click();
      cy.verifyNotification('Grade submitted successfully');
    });

    it('should generate analytics and reports', () => {
      cy.get('[data-cy=analytics-tab]').click();
      cy.waitForLoad();

      // Test performance overview
      cy.get('[data-cy=performance-overview]').should('be.visible');
      cy.get('[data-cy=average-score-chart]').should('be.visible');
      cy.get('[data-cy=completion-rate-chart]').should('be.visible');
      cy.get('[data-cy=time-distribution-chart]').should('be.visible');

      // Question analysis
      cy.get('[data-cy=question-analysis-section]').should('be.visible');
      cy.get('[data-cy=difficult-questions-list]').should('be.visible');
      cy.get('[data-cy=discrimination-index]').should('be.visible');

      // Generate detailed report
      cy.get('[data-cy=generate-report-btn]').click();
      cy.waitForModal();

      cy.selectDropdown('report-type', 'detailed-analysis');
      cy.get('[data-cy=include-individual-results]').check();
      cy.get('[data-cy=include-question-analysis]').check();
      cy.get('[data-cy=include-recommendations]').check();

      cy.get('[data-cy=generate-report-submit]').click();
      cy.verifyNotification('Report generated successfully');
    });

    it('should allow bulk result operations', () => {
      cy.get('[data-cy=result-checkbox]').first().check();
      cy.get('[data-cy=result-checkbox]').eq(1).check();
      cy.get('[data-cy=result-checkbox]').eq(2).check();

      cy.get('[data-cy=bulk-actions-menu]').click();
      cy.get('[data-cy=bulk-export-results]').click();
      cy.waitForModal();

      cy.selectDropdown('export-format', 'csv');
      cy.get('[data-cy=include-answers]').check();
      cy.get('[data-cy=include-feedback]').check();

      cy.get('[data-cy=confirm-export]').click();
      cy.verifyNotification('Results export started');
    });
  });

  describe('Question Bank Management', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/evaluations/question-bank');
      cy.waitForLoad();
    });

    it('should display and manage question bank', () => {
      cy.get('[data-cy=question-bank]').should('be.visible');
      cy.get('[data-cy=question-item]').should('have.length.at.least', 1);

      // Test search functionality
      cy.get('[data-cy=question-search]').type('programming');
      cy.waitForLoad();
      
      cy.get('[data-cy=question-item]').each($question => {
        cy.wrap($question).should('contain.text', 'programming');
      });

      // Test category filter
      cy.get('[data-cy=category-filter]').select('Multiple Choice');
      cy.waitForLoad();
      
      cy.get('[data-cy=question-item]').each($question => {
        cy.wrap($question).find('[data-cy=question-type]').should('contain', 'Multiple Choice');
      });
    });

    it('should create new questions for the bank', () => {
      cy.get('[data-cy=add-to-bank-btn]').click();
      cy.waitForModal();

      cy.selectDropdown('question-type', 'multiple_choice');
      cy.get('[data-cy=question-text]').type('What is the time complexity of binary search?');
      cy.selectDropdown('question-category', 'Algorithms');
      cy.selectDropdown('difficulty-level', 'intermediate');

      // Add options
      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-1]').type('O(log n)');
      cy.get('[data-cy=option-correct-1]').check();

      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-2]').type('O(n)');

      cy.get('[data-cy=add-option-btn]').click();
      cy.get('[data-cy=option-text-3]').type('O(n²)');

      cy.get('[data-cy=explanation]').type('Binary search divides the search space in half with each comparison.');
      cy.get('[data-cy=tags-input]').type('algorithms,search,complexity');

      cy.get('[data-cy=save-to-bank-btn]').click();
      cy.verifyNotification('Question added to bank successfully');
    });

    it('should allow question versioning and updates', () => {
      cy.get('[data-cy=question-item]').first().within(() => {
        cy.get('[data-cy=edit-question-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=create-new-version]').check();
      cy.get('[data-cy=version-notes]').type('Updated with clearer wording');
      
      cy.get('[data-cy=question-text]').clear().type('Updated question text with better clarity');
      cy.get('[data-cy=save-question-btn]').click();

      cy.verifyNotification('New question version created');
      
      // Verify version history
      cy.get('[data-cy=question-item]').first().within(() => {
        cy.get('[data-cy=version-history-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=version-item]').should('have.length.at.least', 2);
    });

    it('should support question tagging and organization', () => {
      cy.get('[data-cy=tag-filter]').type('algorithms');
      cy.waitForLoad();
      
      cy.get('[data-cy=question-item]').each($question => {
        cy.wrap($question).find('[data-cy=question-tags]').should('contain', 'algorithms');
      });

      // Create new tag category
      cy.get('[data-cy=manage-tags-btn]').click();
      cy.waitForModal();

      cy.get('[data-cy=new-tag-input]').type('advanced-concepts');
      cy.get('[data-cy=tag-color-picker]').click();
      cy.get('[data-cy=color-option-blue]').click();
      cy.get('[data-cy=add-tag-btn]').click();

      cy.verifyNotification('Tag created successfully');
    });
  });

  describe('Test Scheduling and Assignments', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/evaluations/schedule');
      cy.waitForLoad();
    });

    it('should schedule tests for specific programs or students', () => {
      cy.get('[data-cy=schedule-test-btn]').click();
      cy.waitForModal();

      cy.selectDropdown('test-select', 'JavaScript Fundamentals Quiz');
      cy.selectDropdown('assignment-type', 'program');
      cy.selectDropdown('target-program', 'Web Development Bootcamp');

      cy.get('[data-cy=start-date]').type('2025-07-01');
      cy.get('[data-cy=start-time]').type('09:00');
      cy.get('[data-cy=end-date]').type('2025-07-07');
      cy.get('[data-cy=end-time]').type('23:59');

      cy.get('[data-cy=send-notifications]').check();
      cy.get('[data-cy=reminder-schedule]').select('24-hours');

      cy.get('[data-cy=schedule-assignment-btn]').click();
      cy.verifyNotification('Test scheduled successfully');
    });

    it('should manage scheduled assessments', () => {
      cy.get('[data-cy=scheduled-tests-list]').should('be.visible');
      cy.get('[data-cy=scheduled-test-item]').should('have.length.at.least', 1);

      cy.get('[data-cy=scheduled-test-item]').first().within(() => {
        cy.get('[data-cy=test-title]').should('be.visible');
        cy.get('[data-cy=assigned-to]').should('be.visible');
        cy.get('[data-cy=schedule-dates]').should('be.visible');
        cy.get('[data-cy=completion-status]').should('be.visible');
        cy.get('[data-cy=manage-assignment-btn]').should('be.visible');
      });
    });

    it('should send automated reminders', () => {
      cy.get('[data-cy=scheduled-test-item]').first().within(() => {
        cy.get('[data-cy=manage-assignment-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=reminder-settings-tab]').click();

      cy.get('[data-cy=send-manual-reminder]').click();
      cy.get('[data-cy=reminder-message]').type('Reminder: Your test is due in 24 hours.');
      cy.get('[data-cy=send-reminder-btn]').click();

      cy.verifyNotification('Reminder sent successfully');
    });
  });

  describe('Proctoring and Security', () => {
    beforeEach(() => {
      cy.loginAsStudent();
      cy.visit('/portal/assessments');
      cy.waitForLoad();
    });

    it('should enforce browser restrictions during proctored tests', () => {
      // Find a proctored test
      cy.get('[data-cy=test-card]').contains('[data-cy=proctoring-enabled]', 'Proctored')
        .parent().within(() => {
          cy.get('[data-cy=start-test-btn]').click();
        });

      cy.get('[data-cy=proctoring-setup-modal]').should('be.visible');
      cy.get('[data-cy=camera-permission-btn]').click();
      cy.get('[data-cy=screen-recording-permission-btn]').click();
      cy.get('[data-cy=fullscreen-mode-btn]').click();

      cy.get('[data-cy=start-proctored-test-btn]').click();
      cy.waitForLoad();

      // Verify proctoring elements
      cy.get('[data-cy=proctoring-indicator]').should('be.visible');
      cy.get('[data-cy=camera-view]').should('be.visible');
      cy.get('[data-cy=fullscreen-warning]').should('not.exist');

      // Test tab switching detection
      cy.window().then(win => {
        win.dispatchEvent(new Event('blur'));
      });

      cy.get('[data-cy=tab-switch-warning]').should('be.visible');
    });

    it('should detect and prevent cheating attempts', () => {
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Simulate copy attempt
      cy.get('[data-cy=current-question]').trigger('copy');
      cy.get('[data-cy=security-warning]').should('contain', 'Copy operation detected');

      // Simulate right-click attempt
      cy.get('[data-cy=current-question]').rightclick();
      cy.get('[data-cy=security-warning]').should('contain', 'Right-click disabled');

      // Simulate multiple failed attempts to leave fullscreen
      cy.window().then(win => {
        for (let i = 0; i < 3; i++) {
          win.dispatchEvent(new Event('fullscreenchange'));
        }
      });

      cy.get('[data-cy=security-violation-modal]').should('be.visible');
    });

    it('should provide accessibility accommodations for proctored tests', () => {
      cy.get('[data-cy=accessibility-settings-btn]').click();
      cy.waitForModal();

      cy.get('[data-cy=screen-reader-accommodation]').check();
      cy.get('[data-cy=extended-time-accommodation]').check();
      cy.get('[data-cy=reduced-proctoring-accommodation]').check();

      cy.get('[data-cy=save-accommodations-btn]').click();

      // Start proctored test with accommodations
      cy.get('[data-cy=test-card]').contains('[data-cy=proctoring-enabled]', 'Proctored')
        .parent().within(() => {
          cy.get('[data-cy=start-test-btn]').click();
        });

      cy.get('[data-cy=accommodations-applied-notice]').should('be.visible');
      cy.get('[data-cy=extended-time-indicator]').should('be.visible');
    });
  });

  describe('Performance and Accessibility', () => {
    it('should handle large question sets efficiently', () => {
      cy.loginAsTrainer();
      cy.visit('/evaluations/create');
      
      // Create test with many questions
      cy.fillForm({
        'test-title': 'Large Test',
        'test-duration': '120'
      });

      // Add 50 questions via bulk import simulation
      cy.get('[data-cy=bulk-import-btn]').click();
      cy.waitForModal();

      cy.uploadFile('questions-file', 'large-question-set.json', 'application/json');
      cy.get('[data-cy=import-questions-btn]').click();
      cy.waitForLoad();

      cy.get('[data-cy=question-item]').should('have.length', 50);
      cy.measurePageLoad();
    });

    it('should be accessible for screen readers', () => {
      cy.loginAsStudent();
      cy.visit('/portal/assessments');
      
      cy.checkA11y();
      cy.checkAriaLabels();
      cy.checkFocusManagement();
    });

    it('should work on mobile devices', () => {
      cy.setMobileViewport();
      cy.loginAsStudent();
      cy.visit('/portal/assessments');

      cy.get('[data-cy=mobile-test-interface]').should('be.visible');
      cy.get('[data-cy=mobile-navigation]').should('be.visible');

      // Start mobile test
      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();
      cy.get('[data-cy=mobile-test-session]').should('be.visible');
      cy.get('[data-cy=mobile-question-navigation]').should('be.visible');
    });

    it('should handle offline scenarios', () => {
      cy.loginAsStudent();
      cy.visit('/portal/assessments');

      cy.get('[data-cy=test-card]').first().within(() => {
        cy.get('[data-cy=start-test-btn]').click();
      });

      cy.waitForLoad();

      // Simulate going offline
      cy.window().then(win => {
        win.navigator.onLine = false;
        win.dispatchEvent(new Event('offline'));
      });

      cy.get('[data-cy=offline-mode-banner]').should('be.visible');
      cy.get('[data-cy=offline-answers-queue]').should('be.visible');

      // Answer questions while offline
      cy.get('[data-cy=answer-option]').first().click();
      cy.get('[data-cy=queued-changes-indicator]').should('be.visible');

      // Simulate coming back online
      cy.window().then(win => {
        win.navigator.onLine = true;
        win.dispatchEvent(new Event('online'));
      });

      cy.get('[data-cy=sync-progress-indicator]').should('be.visible');
      cy.verifyNotification('Answers synchronized successfully');
    });
  });
});