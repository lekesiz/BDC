describe('Document Management', () => {
  beforeEach(() => {
    cy.loginAsTrainer();
    cy.visit('/documents');
  });

  it('displays document list with correct information', () => {
    cy.getByCy('document-list').should('exist');
    cy.getByCy('document-item').should('have.length.at.least', 1);
    
    // Check that each document item contains expected elements
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('document-name').should('exist');
      cy.getByCy('document-type').should('exist');
      cy.getByCy('document-size').should('exist');
      cy.getByCy('document-actions').should('exist');
    });
  });

  it('allows filtering documents', () => {
    // Test search filter
    cy.getByCy('search-input').type('report');
    cy.getByCy('document-item').should('have.length.at.most', 10);
    cy.getByCy('search-input').clear();
    
    // Test type filter
    cy.getByCy('type-filter').click();
    cy.getByCy('type-option-pdf').click();
    cy.getByCy('document-item').each(($item) => {
      cy.wrap($item).find('[data-cy=document-type]').should('contain', 'PDF');
    });
  });

  it('allows sorting documents', () => {
    // Test name sorting
    cy.getByCy('sort-dropdown').click();
    cy.getByCy('sort-by-name').click();
    
    // Get names before and after changing sort direction
    cy.getByCy('document-name').first().invoke('text').as('firstNameAsc');
    
    cy.getByCy('sort-direction').click(); // Change to descending
    cy.getByCy('document-name').first().invoke('text').as('firstNameDesc');
    
    // Compare names to verify sorting changed
    cy.get('@firstNameAsc').then(nameAsc => {
      cy.get('@firstNameDesc').then(nameDesc => {
        expect(nameAsc).not.to.eq(nameDesc);
      });
    });
  });

  it('navigates to document viewer page', () => {
    // Click on first document view button
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('document-name').invoke('text').as('documentName');
      cy.getByCy('view-document-button').click();
    });
    
    // Check we're on the viewer page
    cy.url().should('include', '/documents/view/');
    
    // Verify document viewer is loaded
    cy.getByCy('document-viewer').should('exist');
    cy.getByCy('document-toolbar').should('exist');
    
    // Verify the name is displayed on the viewer page
    cy.get('@documentName').then(name => {
      cy.getByCy('document-title').should('contain', name.trim());
    });
  });

  it('allows uploading a new document', () => {
    // Navigate to upload page
    cy.getByCy('upload-document-button').click();
    cy.url().should('include', '/documents/upload');
    
    // Check document uploader exists
    cy.getByCy('document-uploader').should('exist');
    
    // Prepare test file
    cy.fixture('test-document.pdf', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(blob => {
        const testFile = new File([blob], 'test-document.pdf', { type: 'application/pdf' });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(testFile);
        
        // Upload file
        cy.getByCy('file-input').then(input => {
          input[0].files = dataTransfer.files;
          cy.wrap(input).trigger('change', { force: true });
        });
      });
    
    // Verify file appears in upload list
    cy.getByCy('file-item').should('exist');
    cy.getByCy('file-item').should('contain', 'test-document.pdf');
    
    // Submit upload
    cy.getByCy('upload-button').click();
    
    // Verify success message
    cy.getByCy('success-message', { timeout: 10000 }).should('contain', 'yüklendi');
  });

  it('allows sharing a document', () => {
    // Click on first document share button
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('share-document-button').click();
    });
    
    // Verify share modal is open
    cy.getByCy('document-share').should('exist');
    
    // Search for a user
    cy.getByCy('user-search-input').type('admin');
    cy.getByCy('user-search-result').should('exist');
    
    // Select user
    cy.getByCy('user-search-result').first().click();
    cy.getByCy('selected-user').should('exist');
    
    // Select permission
    cy.getByCy('permission-select').select('edit');
    
    // Share document
    cy.getByCy('share-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'paylaşıldı');
    
    // Verify user appears in shares list
    cy.getByCy('share-item').should('exist');
  });

  it('allows creating a public link', () => {
    // Click on first document share button
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('share-document-button').click();
    });
    
    // Verify share modal is open
    cy.getByCy('document-share').should('exist');
    
    // Enable public link
    cy.getByCy('enable-public-link').click();
    
    // Generate link
    cy.getByCy('generate-link').click();
    
    // Verify link is generated
    cy.getByCy('public-link', { timeout: 10000 }).should('exist');
    
    // Copy link
    cy.getByCy('copy-link').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'kopyalandı');
  });

  it('allows downloading a document', () => {
    // Navigate to first document viewer
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('view-document-button').click();
    });
    
    // Verify download button exists and is functional
    cy.getByCy('download-button').should('exist');
    
    // Note: Actual download cannot be tested in Cypress without plugins,
    // but we can verify the button exists and proper event handlers are attached
    cy.getByCy('download-button').should('not.be.disabled');
  });

  it('allows deleting a document', () => {
    // Count documents before deletion
    cy.getByCy('document-item').its('length').as('initialCount');
    
    // Click delete button on the first document
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('document-name').invoke('text').as('deletedDocName');
      cy.getByCy('delete-document-button').click();
    });
    
    // Confirm deletion in modal
    cy.getByCy('confirm-delete-button').click();
    
    // Verify success message
    cy.getByCy('success-message').should('contain', 'silindi');
    
    // Verify document count decreased
    cy.get('@initialCount').then(initialCount => {
      cy.getByCy('document-item').its('length').should('eq', initialCount - 1);
    });
    
    // Verify deleted document is not in the list
    cy.get('@deletedDocName').then(name => {
      cy.getByCy('document-name').each($el => {
        expect($el.text().trim()).not.to.eq(name.trim());
      });
    });
  });

  it('performs accessibility check on document list', () => {
    cy.checkA11y();
  });

  it('performs accessibility check on document viewer', () => {
    cy.getByCy('document-item').first().within(() => {
      cy.getByCy('view-document-button').click();
    });
    cy.checkA11y();
  });

  it('performs accessibility check on document uploader', () => {
    cy.getByCy('upload-document-button').click();
    cy.checkA11y();
  });
});