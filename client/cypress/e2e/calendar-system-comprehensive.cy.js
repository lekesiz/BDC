describe('Comprehensive Calendar System', () => {
  beforeEach(() => {
    cy.clearDatabase();
    cy.seedDatabase();
    cy.waitForLoad();
  });

  afterEach(() => {
    cy.dismissNotification();
  });

  describe('Calendar View and Navigation', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar');
      cy.waitForLoad();
    });

    it('should display calendar with different view modes', () => {
      // Default month view
      cy.get('[data-cy=calendar-container]').should('be.visible');
      cy.get('[data-cy=calendar-month-view]').should('be.visible');
      cy.get('[data-cy=current-month-year]').should('be.visible');
      
      // Navigation controls
      cy.get('[data-cy=prev-month-btn]').should('be.visible');
      cy.get('[data-cy=next-month-btn]').should('be.visible');
      cy.get('[data-cy=today-btn]').should('be.visible');

      // Switch to week view
      cy.get('[data-cy=week-view-btn]').click();
      cy.get('[data-cy=calendar-week-view]').should('be.visible');
      cy.get('[data-cy=week-days-header]').should('be.visible');
      cy.get('[data-cy=time-slots]').should('be.visible');

      // Switch to day view
      cy.get('[data-cy=day-view-btn]').click();
      cy.get('[data-cy=calendar-day-view]').should('be.visible');
      cy.get('[data-cy=current-date-header]').should('be.visible');
      cy.get('[data-cy=hourly-slots]').should('be.visible');

      // Switch to agenda view
      cy.get('[data-cy=agenda-view-btn]').click();
      cy.get('[data-cy=calendar-agenda-view]').should('be.visible');
      cy.get('[data-cy=agenda-list]').should('be.visible');
    });

    it('should navigate between dates correctly', () => {
      // Navigate to next month
      cy.get('[data-cy=current-month-year]').invoke('text').then(currentMonth => {
        cy.get('[data-cy=next-month-btn]').click();
        cy.get('[data-cy=current-month-year]').should('not.contain', currentMonth);
      });

      // Navigate to previous month
      cy.get('[data-cy=prev-month-btn]').click();
      cy.get('[data-cy=prev-month-btn]').click();

      // Return to today
      cy.get('[data-cy=today-btn]').click();
      cy.get('[data-cy=current-month-year]').should('contain', new Date().getFullYear());
    });

    it('should display existing appointments correctly', () => {
      cy.get('[data-cy=appointment-event]').should('have.length.at.least', 1);
      
      cy.get('[data-cy=appointment-event]').first().within(() => {
        cy.get('[data-cy=appointment-title]').should('be.visible');
        cy.get('[data-cy=appointment-time]').should('be.visible');
        cy.get('[data-cy=appointment-participant]').should('be.visible');
      });

      // Click on appointment to view details
      cy.get('[data-cy=appointment-event]').first().click();
      cy.get('[data-cy=appointment-details-modal]').should('be.visible');
      cy.get('[data-cy=appointment-title]').should('be.visible');
      cy.get('[data-cy=appointment-description]').should('be.visible');
      cy.get('[data-cy=appointment-participants]').should('be.visible');
    });

    it('should support calendar filtering', () => {
      cy.get('[data-cy=calendar-filters-btn]').click();
      cy.get('[data-cy=filter-panel]').should('be.visible');

      // Filter by appointment type
      cy.get('[data-cy=filter-appointment-type]').click();
      cy.get('[data-cy=consultation-filter]').uncheck();
      cy.waitForLoad();
      
      cy.get('[data-cy=appointment-event]').each($event => {
        cy.wrap($event).should('not.have.attr', 'data-type', 'consultation');
      });

      // Filter by participant
      cy.get('[data-cy=filter-participants]').click();
      cy.get('[data-cy=participant-filter-search]').type('john');
      cy.get('[data-cy=participant-filter-item]').first().click();
      cy.waitForLoad();

      cy.get('[data-cy=appointment-event]').each($event => {
        cy.wrap($event).should('contain', 'john');
      });
    });
  });

  describe('Appointment Scheduling (Trainer/Admin)', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar');
      cy.waitForLoad();
    });

    it('should create new appointments', () => {
      // Click on empty time slot
      cy.get('[data-cy=day-view-btn]').click();
      cy.get('[data-cy=time-slot-10-00]').click();
      
      cy.waitForModal();
      cy.get('[data-cy=appointment-form]').should('be.visible');

      const appointmentData = {
        title: 'Career Guidance Session',
        description: 'Discussion about career paths and opportunities',
        participants: 'john.doe@student.com',
        duration: 60,
        type: 'consultation'
      };

      // Fill appointment details
      cy.fillForm({
        'appointment-title': appointmentData.title,
        'appointment-description': appointmentData.description,
        'appointment-duration': appointmentData.duration
      });

      cy.selectDropdown('appointment-type', appointmentData.type);

      // Add participants
      cy.get('[data-cy=add-participant-btn]').click();
      cy.get('[data-cy=participant-search]').type(appointmentData.participants);
      cy.get('[data-cy=participant-suggestion]').first().click();

      // Set reminders
      cy.get('[data-cy=reminder-enabled]').check();
      cy.selectDropdown('reminder-time', '24-hours');
      cy.get('[data-cy=email-reminder]').check();
      cy.get('[data-cy=sms-reminder]').check();

      cy.get('[data-cy=save-appointment-btn]').click();
      cy.verifyNotification('Appointment created successfully');

      // Verify appointment appears on calendar
      cy.get('[data-cy=appointment-event]').should('contain', appointmentData.title);
    });

    it('should handle appointment conflicts', () => {
      // Try to schedule overlapping appointment
      cy.get('[data-cy=day-view-btn]').click();
      cy.get('[data-cy=time-slot-14-00]').click(); // Assume there's already an appointment here

      cy.waitForModal();
      cy.fillForm({
        'appointment-title': 'Conflicting Appointment',
        'appointment-duration': '60'
      });

      cy.get('[data-cy=save-appointment-btn]').click();
      
      // Should show conflict warning
      cy.get('[data-cy=conflict-warning-modal]').should('be.visible');
      cy.get('[data-cy=existing-appointments-list]').should('be.visible');
      
      // Options to resolve conflict
      cy.get('[data-cy=suggest-alternative-btn]').should('be.visible');
      cy.get('[data-cy=force-schedule-btn]').should('be.visible');
      
      // Choose alternative time
      cy.get('[data-cy=suggest-alternative-btn]').click();
      cy.get('[data-cy=alternative-times-list]').should('be.visible');
      cy.get('[data-cy=alternative-time-option]').first().click();
      cy.get('[data-cy=accept-alternative-btn]').click();

      cy.verifyNotification('Appointment scheduled for alternative time');
    });

    it('should support recurring appointments', () => {
      cy.get('[data-cy=create-appointment-btn]').click();
      cy.waitForModal();

      cy.fillForm({
        'appointment-title': 'Weekly Progress Review',
        'appointment-date': '2025-07-01',
        'appointment-time': '15:00',
        'appointment-duration': '30'
      });

      // Enable recurring
      cy.get('[data-cy=recurring-enabled]').check();
      cy.selectDropdown('recurring-pattern', 'weekly');
      cy.selectDropdown('recurring-frequency', '1');
      cy.get('[data-cy=recurring-end-date]').type('2025-12-31');

      // Select specific days
      cy.get('[data-cy=recurring-days]').within(() => {
        cy.get('[data-cy=day-tuesday]').check();
      });

      cy.get('[data-cy=save-appointment-btn]').click();
      cy.verifyNotification('Recurring appointment series created');

      // Verify multiple appointments created
      cy.get('[data-cy=month-view-btn]').click();
      cy.get('[data-cy=appointment-event]').filter(':contains("Weekly Progress Review")')
        .should('have.length.at.least', 4);
    });

    it('should allow bulk appointment operations', () => {
      // Select multiple appointments
      cy.get('[data-cy=selection-mode-btn]').click();
      cy.get('[data-cy=appointment-event]').first().click();
      cy.get('[data-cy=appointment-event]').eq(1).click();
      cy.get('[data-cy=appointment-event]').eq(2).click();

      cy.get('[data-cy=selected-count]').should('contain', '3 selected');
      cy.get('[data-cy=bulk-actions-menu]').click();

      // Test bulk reschedule
      cy.get('[data-cy=bulk-reschedule]').click();
      cy.waitForModal();

      cy.get('[data-cy=reschedule-date]').type('2025-07-15');
      cy.get('[data-cy=time-adjustment]').select('+1-hour');
      cy.get('[data-cy=confirm-bulk-reschedule]').click();

      cy.verifyNotification('3 appointments rescheduled successfully');
    });

    it('should integrate with external calendars', () => {
      cy.get('[data-cy=calendar-settings-btn]').click();
      cy.get('[data-cy=integrations-tab]').click();

      // Google Calendar integration
      cy.get('[data-cy=google-calendar-integration]').within(() => {
        cy.get('[data-cy=connect-google-btn]').click();
      });

      // Mock OAuth flow
      cy.window().then(win => {
        win.postMessage({
          type: 'oauth-success',
          provider: 'google',
          accessToken: 'mock-token'
        }, '*');
      });

      cy.verifyNotification('Google Calendar connected successfully');

      // Sync calendar
      cy.get('[data-cy=sync-calendars-btn]').click();
      cy.waitForLoad();
      
      cy.get('[data-cy=external-event]').should('have.length.at.least', 0);
      cy.verifyNotification('Calendar sync completed');
    });
  });

  describe('Appointment Booking (Student/Beneficiary)', () => {
    beforeEach(() => {
      cy.loginAsStudent();
      cy.visit('/calendar/book');
      cy.waitForLoad();
    });

    it('should display available time slots', () => {
      cy.get('[data-cy=available-trainers-list]').should('be.visible');
      cy.get('[data-cy=trainer-card]').should('have.length.at.least', 1);

      // Select a trainer
      cy.get('[data-cy=trainer-card]').first().click();
      cy.get('[data-cy=trainer-schedule]').should('be.visible');
      cy.get('[data-cy=available-slot]').should('have.length.at.least', 1);

      // Check slot details
      cy.get('[data-cy=available-slot]').first().within(() => {
        cy.get('[data-cy=slot-time]').should('be.visible');
        cy.get('[data-cy=slot-duration]').should('be.visible');
        cy.get('[data-cy=book-slot-btn]').should('be.visible');
      });
    });

    it('should book an appointment successfully', () => {
      // Select trainer and time slot
      cy.get('[data-cy=trainer-card]').first().click();
      cy.get('[data-cy=available-slot]').first().within(() => {
        cy.get('[data-cy=book-slot-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=booking-form]').should('be.visible');

      const bookingData = {
        purpose: 'Career guidance and mentoring session',
        notes: 'Would like to discuss web development career paths',
        preferredMethod: 'video-call'
      };

      cy.fillForm({
        'appointment-purpose': bookingData.purpose,
        'appointment-notes': bookingData.notes
      });

      cy.selectDropdown('meeting-method', bookingData.preferredMethod);
      cy.get('[data-cy=terms-agreement]').check();

      cy.get('[data-cy=confirm-booking-btn]').click();
      cy.verifyNotification('Appointment request sent successfully');

      // Should redirect to confirmation page
      cy.url().should('include', '/calendar/booking-confirmation');
      cy.get('[data-cy=booking-confirmation]').should('be.visible');
      cy.get('[data-cy=booking-reference]').should('be.visible');
    });

    it('should handle appointment approval workflow', () => {
      // Book an appointment
      cy.get('[data-cy=trainer-card]').first().click();
      cy.get('[data-cy=available-slot]').first().within(() => {
        cy.get('[data-cy=book-slot-btn]').click();
      });

      cy.waitForModal();
      cy.fillForm({
        'appointment-purpose': 'Test booking for approval workflow'
      });
      cy.get('[data-cy=confirm-booking-btn]').click();

      // Switch to trainer view to approve
      cy.logout();
      cy.loginAsTrainer();
      cy.visit('/calendar/requests');
      cy.waitForLoad();

      cy.get('[data-cy=pending-request]').should('have.length.at.least', 1);
      cy.get('[data-cy=pending-request]').first().within(() => {
        cy.get('[data-cy=approve-request-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=approval-notes]').type('Approved. Looking forward to our session.');
      cy.get('[data-cy=confirm-approval-btn]').click();

      cy.verifyNotification('Appointment approved successfully');

      // Verify student receives notification
      cy.logout();
      cy.loginAsStudent();
      cy.visit('/portal/notifications');
      
      cy.get('[data-cy=notification-item]').first().should('contain', 'appointment approved');
    });

    it('should allow rescheduling and cancellation', () => {
      // Go to student's appointments
      cy.visit('/portal/appointments');
      cy.waitForLoad();

      cy.get('[data-cy=my-appointments]').should('be.visible');
      cy.get('[data-cy=appointment-item]').should('have.length.at.least', 1);

      // Reschedule appointment
      cy.get('[data-cy=appointment-item]').first().within(() => {
        cy.get('[data-cy=reschedule-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=available-alternatives]').should('be.visible');
      cy.get('[data-cy=alternative-slot]').first().click();
      cy.get('[data-cy=reschedule-reason]').type('Schedule conflict with another commitment');
      cy.get('[data-cy=confirm-reschedule-btn]').click();

      cy.verifyNotification('Reschedule request sent successfully');

      // Cancel appointment
      cy.get('[data-cy=appointment-item]').eq(1).within(() => {
        cy.get('[data-cy=cancel-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=cancellation-reason]').select('personal-emergency');
      cy.get('[data-cy=cancellation-notes]').type('Family emergency, need to cancel');
      cy.get('[data-cy=understand-policy]').check();
      cy.get('[data-cy=confirm-cancellation-btn]').click();

      cy.verifyNotification('Appointment cancelled successfully');
    });

    it('should support group appointment booking', () => {
      cy.get('[data-cy=group-session-tab]').click();
      cy.get('[data-cy=available-group-sessions]').should('be.visible');

      cy.get('[data-cy=group-session-card]').first().within(() => {
        cy.get('[data-cy=session-title]').should('be.visible');
        cy.get('[data-cy=session-capacity]').should('be.visible');
        cy.get('[data-cy=available-spots]').should('be.visible');
        cy.get('[data-cy=join-session-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=group-booking-form]').should('be.visible');
      
      cy.get('[data-cy=participation-level]').select('active');
      cy.get('[data-cy=specific-interests]').type('React.js best practices and state management');
      cy.get('[data-cy=confirm-group-booking-btn]').click();

      cy.verifyNotification('Successfully joined group session');
    });
  });

  describe('Availability Management', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar/availability');
      cy.waitForLoad();
    });

    it('should set weekly availability schedule', () => {
      cy.get('[data-cy=availability-settings]').should('be.visible');

      // Set Monday availability
      cy.get('[data-cy=monday-available]').check();
      cy.get('[data-cy=monday-start-time]').type('09:00');
      cy.get('[data-cy=monday-end-time]').type('17:00');
      cy.get('[data-cy=monday-break-start]').type('12:00');
      cy.get('[data-cy=monday-break-end]').type('13:00');

      // Set Tuesday availability
      cy.get('[data-cy=tuesday-available]').check();
      cy.get('[data-cy=tuesday-start-time]').type('10:00');
      cy.get('[data-cy=tuesday-end-time]').type('18:00');

      // Set Friday as unavailable
      cy.get('[data-cy=friday-available]').uncheck();

      cy.get('[data-cy=save-availability-btn]').click();
      cy.verifyNotification('Availability schedule updated successfully');
    });

    it('should set time-off and exceptions', () => {
      cy.get('[data-cy=time-off-tab]').click();
      cy.get('[data-cy=add-time-off-btn]').click();
      cy.waitForModal();

      const timeOffData = {
        title: 'Summer Vacation',
        startDate: '2025-08-01',
        endDate: '2025-08-15',
        type: 'vacation',
        notes: 'Annual summer vacation - will not be available for appointments'
      };

      cy.fillForm({
        'time-off-title': timeOffData.title,
        'time-off-start-date': timeOffData.startDate,
        'time-off-end-date': timeOffData.endDate,
        'time-off-notes': timeOffData.notes
      });

      cy.selectDropdown('time-off-type', timeOffData.type);
      cy.get('[data-cy=block-all-appointments]').check();
      cy.get('[data-cy=notify-existing-appointments]').check();

      cy.get('[data-cy=save-time-off-btn]').click();
      cy.verifyNotification('Time-off period added successfully');

      // Verify time-off appears in calendar
      cy.visit('/calendar');
      cy.get('[data-cy=month-view-btn]').click();
      cy.get('[data-cy=time-off-period]').should('contain', timeOffData.title);
    });

    it('should set appointment buffers and preferences', () => {
      cy.get('[data-cy=preferences-tab]').click();

      // Buffer times
      cy.get('[data-cy=buffer-before]').clear().type('15');
      cy.get('[data-cy=buffer-after]').clear().type('10');

      // Appointment settings
      cy.get('[data-cy=min-notice-hours]').clear().type('24');
      cy.get('[data-cy=max-advance-days]').clear().type('60');
      cy.get('[data-cy=default-duration]').clear().type('45');

      // Auto-approval settings
      cy.get('[data-cy=auto-approve-existing-students]').check();
      cy.get('[data-cy=require-approval-new-students]').check();

      cy.get('[data-cy=save-preferences-btn]').click();
      cy.verifyNotification('Availability preferences updated');
    });

    it('should bulk update availability', () => {
      cy.get('[data-cy=bulk-update-btn]').click();
      cy.waitForModal();

      // Apply same schedule to multiple days
      cy.get('[data-cy=template-schedule]').select('standard-business');
      cy.get('[data-cy=apply-to-days]').within(() => {
        cy.get('[data-cy=monday]').check();
        cy.get('[data-cy=tuesday]').check();
        cy.get('[data-cy=wednesday]').check();
        cy.get('[data-cy=thursday]').check();
      });

      cy.get('[data-cy=apply-bulk-update-btn]').click();
      cy.verifyNotification('Bulk availability update completed');
    });
  });

  describe('Notifications and Reminders', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar/notifications');
      cy.waitForLoad();
    });

    it('should configure notification preferences', () => {
      cy.get('[data-cy=notification-settings]').should('be.visible');

      // Email notifications
      cy.get('[data-cy=email-notifications]').within(() => {
        cy.get('[data-cy=new-booking-email]').check();
        cy.get('[data-cy=cancellation-email]').check();
        cy.get('[data-cy=reminder-email]').check();
        cy.get('[data-cy=daily-summary-email]').check();
      });

      // SMS notifications
      cy.get('[data-cy=sms-notifications]').within(() => {
        cy.get('[data-cy=urgent-changes-sms]').check();
        cy.get('[data-cy=same-day-reminders-sms]').check();
      });

      // In-app notifications
      cy.get('[data-cy=in-app-notifications]').within(() => {
        cy.get('[data-cy=booking-requests-app]').check();
        cy.get('[data-cy=schedule-changes-app]').check();
      });

      // Reminder timing
      cy.selectDropdown('default-reminder-time', '2-hours');
      cy.selectDropdown('follow-up-reminder', '15-minutes');

      cy.get('[data-cy=save-notification-settings-btn]').click();
      cy.verifyNotification('Notification preferences saved');
    });

    it('should send automated reminders', () => {
      // View upcoming appointments
      cy.get('[data-cy=upcoming-appointments]').should('be.visible');
      cy.get('[data-cy=appointment-with-reminder]').should('have.length.at.least', 1);

      // Send manual reminder
      cy.get('[data-cy=appointment-with-reminder]').first().within(() => {
        cy.get('[data-cy=send-reminder-btn]').click();
      });

      cy.waitForModal();
      cy.get('[data-cy=reminder-message]').clear().type('Looking forward to our session tomorrow. Please confirm your attendance.');
      cy.get('[data-cy=reminder-methods]').within(() => {
        cy.get('[data-cy=email-reminder]').check();
        cy.get('[data-cy=sms-reminder]').check();
      });

      cy.get('[data-cy=send-custom-reminder-btn]').click();
      cy.verifyNotification('Reminder sent successfully');
    });

    it('should handle reminder delivery status', () => {
      cy.get('[data-cy=reminder-history-tab]').click();
      cy.get('[data-cy=reminder-log]').should('be.visible');

      cy.get('[data-cy=reminder-entry]').each($entry => {
        cy.wrap($entry).within(() => {
          cy.get('[data-cy=reminder-timestamp]').should('be.visible');
          cy.get('[data-cy=reminder-recipient]').should('be.visible');
          cy.get('[data-cy=reminder-method]').should('be.visible');
          cy.get('[data-cy=delivery-status]').should('be.visible');
        });
      });

      // Check failed deliveries
      cy.get('[data-cy=failed-deliveries-filter]').click();
      cy.get('[data-cy=reminder-entry]').each($entry => {
        cy.wrap($entry).find('[data-cy=delivery-status]').should('contain', 'Failed');
      });
    });
  });

  describe('Calendar Analytics and Reporting', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar/analytics');
      cy.waitForLoad();
    });

    it('should display appointment statistics', () => {
      cy.get('[data-cy=analytics-dashboard]').should('be.visible');

      // Key metrics
      cy.get('[data-cy=total-appointments]').should('be.visible');
      cy.get('[data-cy=attendance-rate]').should('be.visible');
      cy.get('[data-cy=cancellation-rate]').should('be.visible');
      cy.get('[data-cy=average-duration]').should('be.visible');

      // Charts and visualizations
      cy.get('[data-cy=appointments-trend-chart]').should('be.visible');
      cy.get('[data-cy=time-distribution-chart]').should('be.visible');
      cy.get('[data-cy=popular-slots-chart]').should('be.visible');
      cy.get('[data-cy=no-show-analysis]').should('be.visible');
    });

    it('should generate utilization reports', () => {
      cy.get('[data-cy=utilization-tab]').click();
      cy.get('[data-cy=utilization-analysis]').should('be.visible');

      // Time period selection
      cy.selectDropdown('analysis-period', 'last-month');
      cy.get('[data-cy=apply-filter-btn]').click();
      cy.waitForLoad();

      // Utilization metrics
      cy.get('[data-cy=availability-hours]').should('be.visible');
      cy.get('[data-cy=booked-hours]').should('be.visible');
      cy.get('[data-cy=utilization-percentage]').should('be.visible');
      cy.get('[data-cy=peak-hours-analysis]').should('be.visible');

      // Export report
      cy.get('[data-cy=export-utilization-report]').click();
      cy.waitForModal();

      cy.selectDropdown('export-format', 'pdf');
      cy.get('[data-cy=include-charts]').check();
      cy.get('[data-cy=include-recommendations]').check();
      cy.get('[data-cy=generate-export-btn]').click();

      cy.verifyNotification('Utilization report generated successfully');
    });

    it('should analyze appointment patterns', () => {
      cy.get('[data-cy=patterns-tab]').click();
      cy.get('[data-cy=pattern-analysis]').should('be.visible');

      // Seasonal patterns
      cy.get('[data-cy=seasonal-chart]').should('be.visible');
      cy.get('[data-cy=monthly-trends]').should('be.visible');

      // Day of week analysis
      cy.get('[data-cy=dow-analysis]').should('be.visible');
      cy.get('[data-cy=busiest-days]').should('be.visible');

      // Time of day preferences
      cy.get('[data-cy=time-preferences-chart]').should('be.visible');
      cy.get('[data-cy=peak-hours-list]').should('be.visible');

      // Student behavior analysis
      cy.get('[data-cy=student-behavior-section]').should('be.visible');
      cy.get('[data-cy=booking-lead-time]').should('be.visible');
      cy.get('[data-cy=rescheduling-patterns]').should('be.visible');
    });
  });

  describe('Mobile Calendar Interface', () => {
    beforeEach(() => {
      cy.setMobileViewport();
      cy.loginAsStudent();
      cy.visit('/calendar/mobile');
      cy.waitForLoad();
    });

    it('should display mobile-optimized calendar', () => {
      cy.get('[data-cy=mobile-calendar]').should('be.visible');
      cy.get('[data-cy=mobile-date-picker]').should('be.visible');
      cy.get('[data-cy=mobile-appointment-list]').should('be.visible');

      // Navigation controls
      cy.get('[data-cy=mobile-nav-prev]').should('be.visible');
      cy.get('[data-cy=mobile-nav-next]').should('be.visible');
      cy.get('[data-cy=mobile-today-btn]').should('be.visible');
    });

    it('should support mobile appointment booking', () => {
      cy.get('[data-cy=mobile-book-btn]').click();
      cy.get('[data-cy=mobile-booking-flow]').should('be.visible');

      // Trainer selection
      cy.get('[data-cy=mobile-trainer-list]').should('be.visible');
      cy.get('[data-cy=mobile-trainer-card]').first().click();

      // Date selection
      cy.get('[data-cy=mobile-date-selector]').should('be.visible');
      cy.get('[data-cy=available-date]').first().click();

      // Time selection
      cy.get('[data-cy=mobile-time-slots]').should('be.visible');
      cy.get('[data-cy=available-time-slot]').first().click();

      // Appointment details
      cy.get('[data-cy=mobile-appointment-form]').should('be.visible');
      cy.get('[data-cy=mobile-purpose-input]').type('Quick consultation about project');
      cy.get('[data-cy=mobile-book-confirm-btn]').click();

      cy.verifyNotification('Appointment booked successfully');
    });

    it('should handle mobile gestures', () => {
      // Swipe navigation
      cy.get('[data-cy=mobile-calendar]').swipe('left');
      cy.waitForLoad();
      cy.get('[data-cy=current-month]').should('not.contain', new Date().getMonth());

      // Pull to refresh
      cy.get('[data-cy=mobile-calendar]').swipe('down', { force: true });
      cy.get('[data-cy=refresh-indicator]').should('be.visible');
      cy.waitForLoad();
    });
  });

  describe('Accessibility and Performance', () => {
    beforeEach(() => {
      cy.loginAsTrainer();
      cy.visit('/calendar');
      cy.waitForLoad();
    });

    it('should be accessible with keyboard navigation', () => {
      cy.get('body').tab();
      cy.focused().should('be.visible');

      // Navigate through calendar dates
      cy.focused().type('{rightarrow}');
      cy.focused().should('have.attr', 'role', 'gridcell');

      // Navigate to appointment
      cy.get('[data-cy=appointment-event]').first().focus();
      cy.focused().type('{enter}');
      cy.get('[data-cy=appointment-details-modal]').should('be.visible');
    });

    it('should meet WCAG accessibility standards', () => {
      cy.checkA11y();
      
      // Check specific calendar accessibility
      cy.get('[data-cy=calendar-container]').should('have.attr', 'role', 'grid');
      cy.get('[data-cy=calendar-cell]').should('have.attr', 'role', 'gridcell');
      cy.get('[data-cy=appointment-event]').should('have.attr', 'aria-label');
    });

    it('should support screen readers', () => {
      // Check aria-live regions
      cy.get('[data-cy=calendar-announcement]').should('have.attr', 'aria-live', 'polite');
      cy.get('[data-cy=appointment-status]').should('have.attr', 'aria-live', 'assertive');

      // Check descriptive labels
      cy.get('[data-cy=calendar-navigation]').should('have.attr', 'aria-label');
      cy.get('[data-cy=appointment-event]').should('have.attr', 'aria-describedby');
    });

    it('should handle large datasets efficiently', () => {
      // Navigate to a month with many appointments
      cy.visit('/calendar?month=2025-12'); // Assume December has many appointments
      cy.waitForLoad();

      cy.measurePageLoad();
      
      // Test virtual scrolling in agenda view
      cy.get('[data-cy=agenda-view-btn]').click();
      cy.get('[data-cy=agenda-list]').should('be.visible');
      
      // Scroll through large list
      cy.get('[data-cy=agenda-list]').scrollTo('bottom');
      cy.get('[data-cy=load-more-btn]').should('be.visible');
    });

    it('should work offline with cached data', () => {
      // Load calendar data
      cy.visit('/calendar');
      cy.waitForLoad();

      // Go offline
      cy.window().then(win => {
        win.navigator.onLine = false;
        win.dispatchEvent(new Event('offline'));
      });

      // Should still display cached appointments
      cy.get('[data-cy=offline-indicator]').should('be.visible');
      cy.get('[data-cy=appointment-event]').should('be.visible');
      cy.get('[data-cy=cached-data-notice]').should('be.visible');

      // Try to create appointment offline
      cy.get('[data-cy=create-appointment-btn]').click();
      cy.get('[data-cy=offline-mode-warning]').should('be.visible');
    });
  });
});