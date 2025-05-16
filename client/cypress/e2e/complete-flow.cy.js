describe('Complete User Journey - End to End', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173')
  })

  describe('New User Registration and Setup', () => {
    it('should allow new user to register, login, and complete profile', () => {
      // Navigate to registration
      cy.get('[data-testid=login-register-link]').click()
      
      // Fill registration form
      cy.get('[data-testid=register-username]').type('newuser123')
      cy.get('[data-testid=register-email]').type('newuser123@example.com')
      cy.get('[data-testid=register-password]').type('Password123!')
      cy.get('[data-testid=register-confirm-password]').type('Password123!')
      cy.get('[data-testid=register-firstname]').type('John')
      cy.get('[data-testid=register-lastname]').type('Doe')
      cy.get('[data-testid=register-role]').select('student')
      
      // Submit registration
      cy.get('[data-testid=register-submit]').click()
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard')
      cy.contains('Welcome, John').should('be.visible')
      
      // Complete profile
      cy.visit('/profile')
      cy.get('[data-testid=profile-phone]').type('+1234567890')
      cy.get('[data-testid=profile-bio]').type('I am a new student eager to learn.')
      cy.get('[data-testid=profile-save]').click()
      
      // Verify success message
      cy.contains('Profile updated successfully').should('be.visible')
    })
  })

  describe('Trainer Workflow', () => {
    beforeEach(() => {
      // Login as trainer
      cy.login('trainer@example.com', 'password123')
    })

    it('should create program, add beneficiaries, and schedule appointment', () => {
      // Create a new program
      cy.visit('/programs')
      cy.get('[data-testid=create-program-btn]').click()
      
      cy.get('[data-testid=program-name]').type('Web Development Bootcamp')
      cy.get('[data-testid=program-description]').type('Full-stack web development course')
      cy.get('[data-testid=program-start-date]').type('2025-06-01')
      cy.get('[data-testid=program-end-date]').type('2025-08-31')
      cy.get('[data-testid=program-submit]').click()
      
      // Should redirect to program detail
      cy.url().should('include', '/programs/')
      cy.contains('Web Development Bootcamp').should('be.visible')
      
      // Add beneficiaries to program
      cy.get('[data-testid=assign-beneficiaries-btn]').click()
      cy.get('[data-testid=beneficiary-checkbox-1]').check()
      cy.get('[data-testid=beneficiary-checkbox-2]').check()
      cy.get('[data-testid=assign-beneficiaries-submit]').click()
      
      cy.contains('2 beneficiaries assigned').should('be.visible')
      
      // Create assessment for program
      cy.get('[data-testid=create-assessment-btn]').click()
      cy.get('[data-testid=assessment-title]').type('HTML/CSS Basics Quiz')
      cy.get('[data-testid=assessment-type]').select('quiz')
      
      // Add quiz questions
      cy.get('[data-testid=add-question-btn]').click()
      cy.get('[data-testid=question-text]').type('What does HTML stand for?')
      cy.get('[data-testid=question-type]').select('multiple_choice')
      cy.get('[data-testid=option-1]').type('Hyper Text Markup Language')
      cy.get('[data-testid=option-2]').type('High Tech Modern Language')
      cy.get('[data-testid=option-3]').type('Home Tool Markup Language')
      cy.get('[data-testid=correct-answer]').select('1')
      
      cy.get('[data-testid=save-assessment]').click()
      cy.contains('Assessment created successfully').should('be.visible')
      
      // Set availability
      cy.visit('/calendar/availability')
      cy.get('[data-testid=monday-available]').check()
      cy.get('[data-testid=monday-start]').type('09:00')
      cy.get('[data-testid=monday-end]').type('17:00')
      cy.get('[data-testid=save-availability]').click()
      
      cy.contains('Availability updated').should('be.visible')
    })
  })

  describe('Beneficiary Workflow', () => {
    beforeEach(() => {
      // Login as beneficiary
      cy.login('beneficiary@example.com', 'password123')
    })

    it('should view programs, take assessment, and book appointment', () => {
      // View assigned programs
      cy.visit('/portal/courses')
      cy.contains('Web Development Bootcamp').should('be.visible')
      cy.get('[data-testid=program-card-1]').click()
      
      // View program details
      cy.contains('Program Details').should('be.visible')
      cy.contains('Duration: 3 months').should('be.visible')
      
      // Take assessment
      cy.get('[data-testid=take-assessment-btn]').click()
      cy.contains('HTML/CSS Basics Quiz').should('be.visible')
      
      // Answer questions
      cy.get('[data-testid=question-1-option-1]').click()
      cy.get('[data-testid=submit-assessment]').click()
      
      // View results
      cy.contains('Assessment Submitted').should('be.visible')
      cy.contains('Score: 100%').should('be.visible')
      
      // Book appointment with trainer
      cy.visit('/calendar')
      cy.get('[data-testid=book-appointment-btn]').click()
      
      cy.get('[data-testid=appointment-trainer]').select('John Trainer')
      cy.get('[data-testid=appointment-date]').type('2025-06-05')
      cy.get('[data-testid=appointment-time]').select('10:00')
      cy.get('[data-testid=appointment-title]').type('Career Guidance')
      cy.get('[data-testid=appointment-description]').type('Discuss career opportunities after the bootcamp')
      
      cy.get('[data-testid=book-appointment-submit]').click()
      cy.contains('Appointment requested successfully').should('be.visible')
      
      // Check notifications
      cy.get('[data-testid=notification-bell]').click()
      cy.contains('New appointment request').should('be.visible')
    })
  })

  describe('Document Management Flow', () => {
    beforeEach(() => {
      cy.login('trainer@example.com', 'password123')
    })

    it('should upload document and share with beneficiaries', () => {
      cy.visit('/documents')
      
      // Upload document
      cy.get('[data-testid=upload-document-btn]').click()
      cy.get('[data-testid=document-title]').type('JavaScript Basics Guide')
      cy.get('[data-testid=document-description]').type('Introduction to JavaScript programming')
      cy.get('[data-testid=document-category]').select('Training Material')
      
      // Upload file
      cy.fixture('javascript-guide.pdf').then(fileContent => {
        cy.get('[data-testid=document-file]').upload({
          fileContent: fileContent.toString(),
          fileName: 'javascript-guide.pdf',
          mimeType: 'application/pdf'
        })
      })
      
      cy.get('[data-testid=upload-document-submit]').click()
      cy.contains('Document uploaded successfully').should('be.visible')
      
      // Share document
      cy.get('[data-testid=document-actions-1]').click()
      cy.get('[data-testid=share-document]').click()
      
      cy.get('[data-testid=share-with-program]').check()
      cy.get('[data-testid=select-program]').select('Web Development Bootcamp')
      cy.get('[data-testid=share-permission]').select('read')
      cy.get('[data-testid=share-document-submit]').click()
      
      cy.contains('Document shared successfully').should('be.visible')
    })
  })

  describe('Analytics and Reporting', () => {
    beforeEach(() => {
      cy.login('admin@example.com', 'admin123')
    })

    it('should generate and view analytics reports', () => {
      cy.visit('/analytics')
      
      // View beneficiary analytics
      cy.get('[data-testid=analytics-tab-beneficiaries]').click()
      cy.contains('Total Beneficiaries').should('be.visible')
      cy.contains('Active Programs').should('be.visible')
      cy.contains('Completion Rate').should('be.visible')
      
      // Generate custom report
      cy.visit('/reports')
      cy.get('[data-testid=create-report-btn]').click()
      
      cy.get('[data-testid=report-name]').type('Monthly Progress Report')
      cy.get('[data-testid=report-type]').select('Program Progress')
      cy.get('[data-testid=report-period]').select('Last Month')
      cy.get('[data-testid=include-charts]').check()
      cy.get('[data-testid=include-detailed-data]').check()
      
      cy.get('[data-testid=generate-report]').click()
      
      // View generated report
      cy.contains('Report generated successfully').should('be.visible')
      cy.get('[data-testid=view-report-btn]').click()
      
      // Download report
      cy.get('[data-testid=download-pdf]').click()
      cy.contains('Report downloaded').should('be.visible')
    })
  })

  describe('Real-time Features', () => {
    it('should send and receive real-time messages', () => {
      // Open app in two different viewports to simulate multiple users
      cy.viewport(1200, 800)
      
      // Login as trainer in main window
      cy.login('trainer@example.com', 'password123')
      cy.visit('/messaging')
      
      // In a real e2e test, we would open another browser instance
      // For this example, we'll simulate the interaction
      
      // Select conversation
      cy.get('[data-testid=conversation-1]').click()
      
      // Send message
      cy.get('[data-testid=message-input]').type('Hello, how is the training going?')
      cy.get('[data-testid=send-message]').click()
      
      // Verify message appears
      cy.contains('Hello, how is the training going?').should('be.visible')
      
      // Simulate receiving a message (in real test, this would come from another user)
      cy.window().then(win => {
        win.postMessage({
          type: 'new-message',
          message: {
            text: 'Going great! Just completed the JavaScript module.',
            sender: 'beneficiary@example.com',
            timestamp: new Date().toISOString()
          }
        }, '*')
      })
      
      // Verify received message appears
      cy.contains('Going great! Just completed the JavaScript module.').should('be.visible')
    })
  })

  describe('Error Handling and Edge Cases', () => {
    it('should handle network errors gracefully', () => {
      cy.intercept('GET', '/api/programs', { statusCode: 500 })
      
      cy.login('trainer@example.com', 'password123')
      cy.visit('/programs')
      
      cy.contains('Failed to load programs').should('be.visible')
      cy.get('[data-testid=retry-btn]').should('be.visible')
    })

    it('should validate form inputs', () => {
      cy.visit('/register')
      
      // Try to submit empty form
      cy.get('[data-testid=register-submit]').click()
      
      // Should show validation errors
      cy.contains('Username is required').should('be.visible')
      cy.contains('Email is required').should('be.visible')
      cy.contains('Password is required').should('be.visible')
      
      // Invalid email
      cy.get('[data-testid=register-email]').type('invalid-email')
      cy.get('[data-testid=register-submit]').click()
      cy.contains('Invalid email address').should('be.visible')
      
      // Weak password
      cy.get('[data-testid=register-password]').type('weak')
      cy.get('[data-testid=register-submit]').click()
      cy.contains('Password must be at least 8 characters').should('be.visible')
    })
  })
})