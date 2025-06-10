// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Integration Templates - Pre-configured settings for common use cases
export const integrationTemplates = {
  'google-calendar': {
    educational: {
      name: 'Educational Institution Setup',
      description: 'Optimized for schools and training centers',
      settings: {
        syncInterval: 15,
        syncDirection: 'bidirectional',
        autoCreateMeetLinks: true,
        eventTypes: ['classes', 'meetings', 'appointments'],
        defaultEventDuration: 60,
        defaultReminder: 15,
        workingHours: {
          start: '08:00',
          end: '18:00',
          days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        }
      }
    },
    corporate: {
      name: 'Corporate Training Setup',
      description: 'Best for corporate training programs',
      settings: {
        syncInterval: 30,
        syncDirection: 'bidirectional',
        autoCreateMeetLinks: true,
        eventTypes: ['training', 'meetings', 'workshops'],
        defaultEventDuration: 90,
        defaultReminder: 30,
        requiresApproval: true
      }
    }
  },
  'slack': {
    smallTeam: {
      name: 'Small Team Setup',
      description: 'For teams under 50 members',
      settings: {
        channels: ['#general', '#announcements'],
        notificationTypes: {
          newEnrollment: true,
          assignmentSubmission: true,
          gradePosted: true,
          appointmentReminder: true,
          systemAlerts: false
        },
        quietHours: {
          enabled: true,
          start: '18:00',
          end: '09:00'
        },
        mentionUsers: false
      }
    },
    largeOrganization: {
      name: 'Large Organization Setup',
      description: 'For organizations with multiple departments',
      settings: {
        channels: ['#general', '#training-updates', '#tech-support'],
        notificationTypes: {
          newEnrollment: false,
          assignmentSubmission: false,
          gradePosted: true,
          appointmentReminder: true,
          systemAlerts: true
        },
        useThreads: true,
        channelPrefix: 'bdc-',
        departmentChannels: true
      }
    }
  },
  'zoom': {
    virtualClassroom: {
      name: 'Virtual Classroom Setup',
      description: 'Optimized for online teaching',
      settings: {
        defaultMeetingType: 'scheduled',
        enableWaitingRoom: true,
        muteOnEntry: true,
        allowScreenShare: true,
        autoRecording: 'cloud',
        breakoutRooms: true,
        maxParticipants: 100,
        meetingDefaults: {
          duration: 60,
          passcode: true,
          video: {
            host: true,
            participants: false
          }
        }
      }
    },
    webinar: {
      name: 'Webinar Setup',
      description: 'For large presentations and lectures',
      settings: {
        defaultMeetingType: 'webinar',
        enableRegistration: true,
        autoRecording: 'cloud',
        panelists: true,
        qa: true,
        polling: true,
        maxParticipants: 500,
        practiceSession: true
      }
    }
  },
  'stripe': {
    subscription: {
      name: 'Subscription Business',
      description: 'Monthly or annual subscription model',
      settings: {
        paymentMethods: ['card', 'sepa'],
        subscriptionPlans: [
        { name: 'Basic', price: 29, interval: 'month' },
        { name: 'Pro', price: 59, interval: 'month' },
        { name: 'Enterprise', custom: true }],

        trialPeriod: 14,
        automaticTax: true,
        invoicing: true,
        dunning: {
          enabled: true,
          maxAttempts: 4
        }
      }
    },
    oneTime: {
      name: 'One-time Payments',
      description: 'Single course or product purchases',
      settings: {
        paymentMethods: ['card', 'ideal', 'bancontact'],
        statementDescriptor: 'BDC ACADEMY',
        captureMethod: 'automatic',
        automaticTax: true,
        savePaymentMethod: false
      }
    }
  },
  'twilio': {
    notifications: {
      name: 'Notification System',
      description: 'SMS notifications for important updates',
      settings: {
        channels: ['sms'],
        notificationTypes: {
          appointmentReminders: true,
          assignmentDeadlines: true,
          gradeNotifications: true,
          emergencyAlerts: true,
          marketingMessages: false
        },
        quietHours: {
          enabled: true,
          start: '21:00',
          end: '09:00'
        },
        templates: {
          appointmentReminder: 'Hi {name}, reminder: You have {subject} tomorrow at {time}',
          assignmentDue: 'Hi {name}, your assignment for {course} is due in {days} days',
          gradePosted: 'Hi {name}, your grade for {assignment} has been posted'
        }
      }
    },
    marketing: {
      name: 'Marketing Campaigns',
      description: 'SMS marketing and promotional messages',
      settings: {
        channels: ['sms', 'whatsapp'],
        requiresOptIn: true,
        includeUnsubscribe: true,
        campaignTracking: true,
        linkShortening: true,
        scheduling: {
          enabled: true,
          timezone: 'Europe/Paris'
        }
      }
    }
  },
  'mailchimp': {
    newsletter: {
      name: 'Newsletter Setup',
      description: 'Regular newsletters and updates',
      settings: {
        lists: ['All Subscribers', 'Active Students'],
        campaignDefaults: {
          fromName: 'BDC Academy',
          replyTo: 'info@bdcacademy.com',
          frequency: 'weekly'
        },
        segments: {
          byProgram: true,
          byEngagement: true,
          byLocation: false
        },
        automations: [
        'Welcome Series',
        'Course Completion',
        'Re-engagement']

      }
    },
    automated: {
      name: 'Automated Campaigns',
      description: 'Behavior-triggered email sequences',
      settings: {
        triggers: {
          enrollment: 'Welcome Series',
          completion: 'Certificate + Next Steps',
          inactivity: 'Re-engagement Campaign'
        },
        personalization: {
          dynamicContent: true,
          recommendedCourses: true,
          achievementBadges: true
        }
      }
    }
  },
  'google-drive': {
    documentManagement: {
      name: 'Document Management',
      description: 'Centralized document storage',
      settings: {
        folderStructure: {
          root: 'BDC Academy',
          subfolders: ['Courses', 'Students', 'Resources', 'Admin']
        },
        permissions: {
          studentsCanView: true,
          studentsCanComment: true,
          studentsCanEdit: false
        },
        fileNaming: {
          convention: '{course}_{type}_{date}',
          autoRename: true
        },
        backup: {
          enabled: true,
          frequency: 'daily'
        }
      }
    },
    collaboration: {
      name: 'Collaborative Workspace',
      description: 'Shared workspace for teams',
      settings: {
        sharedDrives: true,
        realTimeCollaboration: true,
        versionControl: true,
        commentNotifications: true,
        fileTypes: ['docs', 'sheets', 'slides', 'forms'],
        templates: {
          enabled: true,
          customTemplates: ['Assignment', 'Report', 'Presentation']
        }
      }
    }
  },
  'webhooks': {
    basic: {
      name: 'Basic Webhook Setup',
      description: 'Essential events only',
      settings: {
        events: [
        'user.enrolled',
        'course.completed',
        'payment.success'],

        security: {
          signatureVerification: true,
          ipWhitelist: false
        },
        retry: {
          enabled: true,
          maxAttempts: 3,
          backoffMultiplier: 2
        }
      }
    },
    advanced: {
      name: 'Advanced Integration',
      description: 'All events with custom filtering',
      settings: {
        events: 'all',
        filters: {
          byProgram: true,
          byUserType: true,
          byTimeRange: true
        },
        security: {
          signatureVerification: true,
          ipWhitelist: true,
          apiKeyRotation: true
        },
        payload: {
          includeMetadata: true,
          customFields: true,
          compression: true
        }
      }
    }
  }
};
// Helper function to apply template
export const applyTemplate = (integrationId, templateName) => {
  const templates = integrationTemplates[integrationId];
  if (!templates || !templates[templateName]) {
    return null;
  }
  return templates[templateName].settings;
};
// Get all templates for an integration
export const getTemplatesForIntegration = (integrationId) => {
  const templates = integrationTemplates[integrationId];
  if (!templates) return [];
  return Object.entries(templates).map(([key, template]) => ({
    id: key,
    name: template.name,
    description: template.description
  }));
};
// Validate settings against template
export const validateSettings = (integrationId, settings, templateName) => {
  const templates = integrationTemplates[integrationId];
  if (!templates || !templates[templateName]) {
    return { valid: true }; // No template to validate against
  }
  const template = templates[templateName].settings;
  const missing = [];
  // Check for missing required fields
  for (const key of Object.keys(template)) {
    if (!(key in settings)) {
      missing.push(key);
    }
  }
  return {
    valid: missing.length === 0,
    missing
  };
};