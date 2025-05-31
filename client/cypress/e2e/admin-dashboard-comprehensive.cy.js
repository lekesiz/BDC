describe('Comprehensive Admin Dashboard', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.loginAsAdmin();
    cy.waitForLoad();
  });

  afterEach(() => {
    cy.dismissNotification();
  });

  describe('Dashboard Overview', () => {
    beforeEach(() => {
      cy.visit('/admin/dashboard');
      cy.waitForLoad();
    });

    it('should display admin dashboard with all key metrics', () => {
      // Verify main dashboard elements
      cy.get('[data-cy=admin-dashboard-title]').should('contain', 'Admin Dashboard');
      
      // Check key metrics widgets
      cy.get('[data-cy=total-users-widget]').should('be.visible');
      cy.get('[data-cy=active-programs-widget]').should('be.visible');
      cy.get('[data-cy=total-beneficiaries-widget]').should('be.visible');
      cy.get('[data-cy=system-health-widget]').should('be.visible');
      
      // Verify metrics have actual values
      cy.get('[data-cy=total-users-count]').should('not.contain', '0');
      cy.get('[data-cy=active-programs-count]').should('not.contain', '0');
    });

    it('should display recent activity timeline', () => {
      cy.get('[data-cy=recent-activity-section]').should('be.visible');
      cy.get('[data-cy=activity-timeline]').should('be.visible');
      cy.get('[data-cy=activity-item]').should('have.length.at.least', 1);
      
      // Check activity item structure
      cy.get('[data-cy=activity-item]').first().within(() => {
        cy.get('[data-cy=activity-timestamp]').should('be.visible');
        cy.get('[data-cy=activity-description]').should('be.visible');
        cy.get('[data-cy=activity-user]').should('be.visible');
      });
    });

    it('should display system alerts and notifications', () => {
      cy.get('[data-cy=system-alerts-section]').should('be.visible');
      
      // Check for different alert types
      cy.get('[data-cy=alert-item]').each($alert => {
        cy.wrap($alert).should('have.attr', 'data-alert-type');
        cy.wrap($alert).find('[data-cy=alert-message]').should('be.visible');
        cy.wrap($alert).find('[data-cy=alert-timestamp]').should('be.visible');
      });
    });

    it('should allow filtering dashboard data by date range', () => {
      cy.get('[data-cy=date-filter-toggle]').click();
      cy.get('[data-cy=date-range-start]').type('2025-01-01');
      cy.get('[data-cy=date-range-end]').type('2025-12-31');
      cy.get('[data-cy=apply-date-filter]').click();

      cy.waitForLoad();
      cy.get('[data-cy=filtered-results-indicator]').should('be.visible');
    });

    it('should refresh dashboard data automatically', () => {
      const initialValue = cy.get('[data-cy=total-users-count]').invoke('text');
      
      // Wait for auto-refresh (simulate time passing)
      cy.wait(30000);
      
      cy.get('[data-cy=total-users-count]').invoke('text').should('not.equal', initialValue);
    });

    it('should be responsive on different screen sizes', () => {
      // Test mobile view
      cy.setMobileViewport();
      cy.get('[data-cy=admin-dashboard]').should('be.visible');
      cy.get('[data-cy=mobile-menu-toggle]').should('be.visible');
      
      // Test tablet view
      cy.setTabletViewport();
      cy.get('[data-cy=admin-dashboard]').should('be.visible');
      
      // Test desktop view
      cy.setDesktopViewport();
      cy.get('[data-cy=admin-dashboard]').should('be.visible');
    });
  });

  describe('User Management', () => {
    beforeEach(() => {
      cy.visit('/admin/users');
      cy.waitForLoad();
    });

    it('should display users list with proper information', () => {
      cy.get('[data-cy=users-table]').should('be.visible');
      cy.get('[data-cy=user-row]').should('have.length.at.least', 1);
      
      // Check table headers
      cy.get('[data-cy=users-table-header]').within(() => {
        cy.contains('Name').should('be.visible');
        cy.contains('Email').should('be.visible');
        cy.contains('Role').should('be.visible');
        cy.contains('Status').should('be.visible');
        cy.contains('Actions').should('be.visible');
      });
    });

    it('should allow creating new users', () => {
      cy.get('[data-cy=create-user-btn]').click();
      cy.waitForModal();

      const newUser = {
        username: `admin_test_${Date.now()}`,
        email: `admin_test_${Date.now()}@test.com`,
        firstName: 'Admin',
        lastName: 'Test',
        role: 'trainer'
      };

      cy.fillForm({
        'user-username': newUser.username,
        'user-email': newUser.email,
        'user-first-name': newUser.firstName,
        'user-last-name': newUser.lastName,
        'user-password': 'TempPassword123!',
        'user-confirm-password': 'TempPassword123!'
      });

      cy.selectDropdown('user-role', newUser.role);
      cy.get('[data-cy=save-user-btn]').click();

      cy.verifyNotification('User created successfully');
      cy.get('[data-cy=users-table]').should('contain', newUser.email);
    });

    it('should allow editing existing users', () => {
      cy.get('[data-cy=user-row]').first().within(() => {
        cy.get('[data-cy=edit-user-btn]').click();
      });

      cy.waitForModal();
      
      // Update user information
      cy.get('[data-cy=user-first-name]').clear().type('Updated Name');
      cy.get('[data-cy=save-user-btn]').click();

      cy.verifyNotification('User updated successfully');
    });

    it('should allow deactivating/activating users', () => {
      cy.get('[data-cy=user-row]').first().within(() => {
        cy.get('[data-cy=user-status]').then($status => {
          const currentStatus = $status.text();
          cy.get('[data-cy=toggle-user-status-btn]').click();
          
          // Verify status changed
          cy.get('[data-cy=user-status]').should('not.contain', currentStatus);
        });
      });

      cy.verifyNotification('User status updated');
    });

    it('should allow bulk user operations', () => {
      // Select multiple users
      cy.get('[data-cy=user-checkbox]').first().check();
      cy.get('[data-cy=user-checkbox]').eq(1).check();

      cy.get('[data-cy=bulk-actions-dropdown]').click();
      cy.get('[data-cy=bulk-deactivate]').click();

      cy.get('[data-cy=confirm-bulk-action]').click();
      cy.verifyNotification('Bulk operation completed');
    });

    it('should allow searching and filtering users', () => {
      cy.get('[data-cy=user-search]').type('trainer');
      cy.waitForLoad();
      
      cy.get('[data-cy=user-row]').each($row => {
        cy.wrap($row).should('contain', 'trainer');
      });

      // Test role filter
      cy.get('[data-cy=role-filter]').select('admin');
      cy.waitForLoad();
      
      cy.get('[data-cy=user-row]').each($row => {
        cy.wrap($row).find('[data-cy=user-role]').should('contain', 'admin');
      });
    });

    it('should handle user deletion with confirmation', () => {
      cy.get('[data-cy=user-row]').first().within(() => {
        cy.get('[data-cy=delete-user-btn]').click();
      });

      cy.get('[data-cy=delete-confirmation-modal]').should('be.visible');
      cy.get('[data-cy=confirm-delete-btn]').click();

      cy.verifyNotification('User deleted successfully');
    });
  });

  describe('System Settings', () => {
    beforeEach(() => {
      cy.visit('/admin/settings');
      cy.waitForLoad();
    });

    it('should display system configuration options', () => {
      cy.get('[data-cy=system-settings-form]').should('be.visible');
      
      // Check different setting categories
      cy.get('[data-cy=general-settings-section]').should('be.visible');
      cy.get('[data-cy=security-settings-section]').should('be.visible');
      cy.get('[data-cy=notification-settings-section]').should('be.visible');
      cy.get('[data-cy=integration-settings-section]').should('be.visible');
    });

    it('should allow updating general system settings', () => {
      cy.get('[data-cy=system-name]').clear().type('BDC Test System');
      cy.get('[data-cy=system-timezone]').select('UTC');
      cy.get('[data-cy=default-language]').select('en');
      
      cy.get('[data-cy=save-general-settings]').click();
      cy.verifyNotification('General settings updated');
    });

    it('should allow configuring security settings', () => {
      cy.get('[data-cy=password-min-length]').clear().type('10');
      cy.get('[data-cy=session-timeout]').clear().type('30');
      cy.get('[data-cy=two-factor-required]').check();
      
      cy.get('[data-cy=save-security-settings]').click();
      cy.verifyNotification('Security settings updated');
    });

    it('should allow managing integrations', () => {
      cy.get('[data-cy=integration-settings-section]').within(() => {
        cy.get('[data-cy=email-integration-enabled]').check();
        cy.get('[data-cy=sms-integration-enabled]').check();
        cy.get('[data-cy=calendar-integration-enabled]').check();
      });

      cy.get('[data-cy=save-integration-settings]').click();
      cy.verifyNotification('Integration settings updated');
    });
  });

  describe('Analytics and Reporting', () => {
    beforeEach(() => {
      cy.visit('/admin/analytics');
      cy.waitForLoad();
    });

    it('should display comprehensive analytics dashboard', () => {
      // User analytics
      cy.get('[data-cy=user-analytics-chart]').should('be.visible');
      cy.get('[data-cy=user-growth-chart]').should('be.visible');
      
      // Program analytics
      cy.get('[data-cy=program-completion-chart]').should('be.visible');
      cy.get('[data-cy=program-enrollment-chart]').should('be.visible');
      
      // System performance
      cy.get('[data-cy=system-performance-chart]').should('be.visible');
    });

    it('should allow generating custom reports', () => {
      cy.get('[data-cy=create-report-btn]').click();
      cy.waitForModal();

      cy.fillForm({
        'report-name': 'Monthly User Activity Report',
        'report-description': 'Detailed analysis of user activity for the month'
      });

      cy.selectDropdown('report-type', 'user-activity');
      cy.selectDropdown('report-period', 'last-month');
      
      // Select report components
      cy.get('[data-cy=include-charts]').check();
      cy.get('[data-cy=include-tables]').check();
      cy.get('[data-cy=include-export]').check();

      cy.get('[data-cy=generate-report-btn]').click();
      cy.verifyNotification('Report generated successfully');
    });

    it('should allow exporting analytics data', () => {
      cy.get('[data-cy=export-analytics-btn]').click();
      cy.get('[data-cy=export-format-dropdown]').select('csv');
      cy.get('[data-cy=export-date-range]').type('2025-01-01 to 2025-12-31');
      cy.get('[data-cy=confirm-export-btn]').click();

      cy.verifyNotification('Export started. You will receive an email when ready.');
    });
  });

  describe('Tenant Management', () => {
    beforeEach(() => {
      cy.visit('/admin/tenants');
      cy.waitForLoad();
    });

    it('should display tenants list with management options', () => {
      cy.get('[data-cy=tenants-table]').should('be.visible');
      cy.get('[data-cy=tenant-row]').should('have.length.at.least', 1);
      
      cy.get('[data-cy=tenant-row]').first().within(() => {
        cy.get('[data-cy=tenant-name]').should('be.visible');
        cy.get('[data-cy=tenant-status]').should('be.visible');
        cy.get('[data-cy=tenant-subscription]').should('be.visible');
        cy.get('[data-cy=tenant-actions]').should('be.visible');
      });
    });

    it('should allow creating new tenants', () => {
      cy.get('[data-cy=create-tenant-btn]').click();
      cy.waitForModal();

      const newTenant = {
        name: `Test Tenant ${Date.now()}`,
        domain: `test-tenant-${Date.now()}`,
        adminEmail: `admin-${Date.now()}@test-tenant.com`,
        subscriptionPlan: 'premium'
      };

      cy.fillForm({
        'tenant-name': newTenant.name,
        'tenant-domain': newTenant.domain,
        'tenant-admin-email': newTenant.adminEmail
      });

      cy.selectDropdown('tenant-subscription-plan', newTenant.subscriptionPlan);
      cy.get('[data-cy=create-tenant-btn]').click();

      cy.verifyNotification('Tenant created successfully');
    });

    it('should allow managing tenant subscriptions', () => {
      cy.get('[data-cy=tenant-row]').first().within(() => {
        cy.get('[data-cy=manage-subscription-btn]').click();
      });

      cy.waitForModal();
      cy.selectDropdown('subscription-plan', 'enterprise');
      cy.get('[data-cy=subscription-start-date]').type('2025-06-01');
      cy.get('[data-cy=update-subscription-btn]').click();

      cy.verifyNotification('Subscription updated successfully');
    });

    it('should allow viewing tenant analytics', () => {
      cy.get('[data-cy=tenant-row]').first().within(() => {
        cy.get('[data-cy=view-analytics-btn]').click();
      });

      cy.url().should('include', '/admin/tenants/');
      cy.get('[data-cy=tenant-analytics-dashboard]').should('be.visible');
      cy.get('[data-cy=tenant-user-count]').should('be.visible');
      cy.get('[data-cy=tenant-program-count]').should('be.visible');
    });
  });

  describe('System Monitoring', () => {
    beforeEach(() => {
      cy.visit('/admin/monitoring');
      cy.waitForLoad();
    });

    it('should display system health metrics', () => {
      cy.get('[data-cy=system-health-dashboard]').should('be.visible');
      
      // Server metrics
      cy.get('[data-cy=server-uptime]').should('be.visible');
      cy.get('[data-cy=server-cpu-usage]').should('be.visible');
      cy.get('[data-cy=server-memory-usage]').should('be.visible');
      
      // Database metrics
      cy.get('[data-cy=database-status]').should('contain', 'Connected');
      cy.get('[data-cy=database-response-time]').should('be.visible');
      
      // Application metrics
      cy.get('[data-cy=active-users-count]').should('be.visible');
      cy.get('[data-cy=error-rate]').should('be.visible');
    });

    it('should display error logs and system logs', () => {
      cy.get('[data-cy=logs-section]').should('be.visible');
      cy.get('[data-cy=error-logs-tab]').click();
      
      cy.get('[data-cy=log-entries]').should('be.visible');
      cy.get('[data-cy=log-entry]').first().within(() => {
        cy.get('[data-cy=log-timestamp]').should('be.visible');
        cy.get('[data-cy=log-level]').should('be.visible');
        cy.get('[data-cy=log-message]').should('be.visible');
      });
    });

    it('should allow configuring system alerts', () => {
      cy.get('[data-cy=configure-alerts-btn]').click();
      cy.waitForModal();

      cy.get('[data-cy=cpu-threshold]').clear().type('80');
      cy.get('[data-cy=memory-threshold]').clear().type('85');
      cy.get('[data-cy=error-rate-threshold]').clear().type('5');
      
      cy.get('[data-cy=alert-email]').clear().type('admin@bdc.com');
      cy.get('[data-cy=save-alert-config]').click();

      cy.verifyNotification('Alert configuration saved');
    });
  });

  describe('Backup and Maintenance', () => {
    beforeEach(() => {
      cy.visit('/admin/maintenance');
      cy.waitForLoad();
    });

    it('should allow creating system backups', () => {
      cy.get('[data-cy=create-backup-btn]').click();
      cy.get('[data-cy=backup-type]').select('full');
      cy.get('[data-cy=backup-description]').type('Manual backup before system update');
      cy.get('[data-cy=start-backup-btn]').click();

      cy.verifyNotification('Backup started successfully');
      cy.get('[data-cy=backup-progress]').should('be.visible');
    });

    it('should display backup history', () => {
      cy.get('[data-cy=backup-history-table]').should('be.visible');
      cy.get('[data-cy=backup-entry]').should('have.length.at.least', 1);
      
      cy.get('[data-cy=backup-entry]').first().within(() => {
        cy.get('[data-cy=backup-date]').should('be.visible');
        cy.get('[data-cy=backup-size]').should('be.visible');
        cy.get('[data-cy=backup-status]').should('be.visible');
        cy.get('[data-cy=backup-actions]').should('be.visible');
      });
    });

    it('should allow scheduling maintenance windows', () => {
      cy.get('[data-cy=schedule-maintenance-btn]').click();
      cy.waitForModal();

      cy.fillForm({
        'maintenance-title': 'System Update Maintenance',
        'maintenance-description': 'Scheduled system update and security patches',
        'maintenance-start': '2025-06-15T02:00',
        'maintenance-end': '2025-06-15T04:00'
      });

      cy.get('[data-cy=maintenance-notification-enabled]').check();
      cy.get('[data-cy=schedule-maintenance-submit]').click();

      cy.verifyNotification('Maintenance window scheduled');
    });
  });

  describe('Accessibility in Admin Dashboard', () => {
    it('should meet WCAG accessibility standards', () => {
      cy.visit('/admin/dashboard');
      cy.checkA11y();
    });

    it('should support keyboard navigation', () => {
      cy.visit('/admin/users');
      cy.get('body').tab();
      cy.focused().should('be.visible');
      
      // Navigate through table
      cy.focused().tab();
      cy.focused().should('be.visible');
    });

    it('should have proper focus management in modals', () => {
      cy.visit('/admin/users');
      cy.get('[data-cy=create-user-btn]').click();
      cy.waitForModal();
      
      // Focus should be on first input in modal
      cy.focused().should('have.attr', 'data-cy', 'user-username');
    });
  });

  describe('Performance and Error Handling', () => {
    it('should handle large datasets efficiently', () => {
      cy.visit('/admin/users');
      
      // Test pagination with large user list
      cy.get('[data-cy=pagination-info]').should('be.visible');
      cy.get('[data-cy=next-page-btn]').click();
      cy.waitForLoad();
      
      cy.measurePageLoad();
    });

    it('should handle API errors gracefully', () => {
      cy.intercept('GET', '**/api/admin/users', { statusCode: 500 }).as('usersError');
      
      cy.visit('/admin/users');
      cy.wait('@usersError');
      
      cy.get('[data-cy=error-message]').should('contain', 'Failed to load users');
      cy.get('[data-cy=retry-btn]').should('be.visible');
    });

    it('should handle concurrent admin operations', () => {
      cy.visit('/admin/users');
      
      // Simulate multiple admins making changes
      cy.get('[data-cy=user-row]').first().within(() => {
        cy.get('[data-cy=edit-user-btn]').click();
      });
      
      cy.waitForModal();
      
      // Simulate conflict scenario
      cy.intercept('PUT', '**/api/admin/users/**', {
        statusCode: 409,
        body: { message: 'User was modified by another admin' }
      }).as('userConflict');
      
      cy.get('[data-cy=save-user-btn]').click();
      cy.wait('@userConflict');
      
      cy.get('[data-cy=conflict-resolution-modal]').should('be.visible');
    });
  });
});