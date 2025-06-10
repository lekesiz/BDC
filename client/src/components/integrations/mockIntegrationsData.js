// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock Integrations Data
export const generateIntegrationsData = () => {
  return {
    available: [
    {
      id: "google-calendar",
      name: "Google Calendar",
      description: "Sync events and manage appointments with Google Calendar",
      category: "productivity",
      icon: "/api/placeholder/64/64",
      features: [
      "Two-way calendar sync",
      "Automatic event creation",
      "Google Meet integration",
      "Multiple calendar support"],

      status: "connected",
      connectionDetails: {
        email: "user@example.com",
        connectedAt: "2023-11-15T10:30:00Z",
        lastSync: new Date(Date.now() - 3600000).toISOString(),
        permissions: ["calendar.read", "calendar.write", "calendar.events"]
      },
      settings: {
        autoSync: true,
        syncInterval: 15,
        autoCreateMeetLinks: true
      }
    },
    {
      id: "microsoft-teams",
      name: "Microsoft Teams",
      description: "Create meetings and send notifications through Teams",
      category: "communication",
      icon: "/api/placeholder/64/64",
      features: [
      "Teams meeting creation",
      "Channel notifications",
      "Direct messaging",
      "File sharing"],

      status: "disconnected",
      connectionDetails: null,
      settings: {
        defaultTeam: "",
        notificationTypes: true,
        autoCreateMeetings: true
      }
    },
    {
      id: "slack",
      name: "Slack",
      description: "Receive notifications and updates in Slack",
      category: "communication",
      icon: "/api/placeholder/64/64",
      features: [
      "Real-time notifications",
      "Channel updates",
      "Direct messages",
      "File sharing"],

      status: "connected",
      connectionDetails: {
        workspace: "tech-academy",
        channel: "#general",
        connectedAt: "2023-12-01T14:20:00Z",
        lastActivity: new Date(Date.now() - 7200000).toISOString()
      },
      settings: {
        notifyGrades: true,
        notifyAssignments: true,
        notifyAnnouncements: true,
        directMessages: false
      }
    },
    {
      id: "zoom",
      name: "Zoom",
      description: "Host and join video meetings",
      category: "communication",
      icon: "/api/placeholder/64/64",
      features: [
      "Video conferencing",
      "Screen sharing",
      "Recording capabilities",
      "Webinar hosting"],

      status: "connected",
      connectionDetails: {
        email: "user@example.com",
        connectedAt: "2023-10-20T09:15:00Z",
        accountType: "Pro",
        meetingsHosted: 45
      },
      settings: {
        autoRecord: false,
        enableWaitingRoom: true,
        muteOnEntry: true,
        allowScreenShare: true
      }
    },
    {
      id: "google-drive",
      name: "Google Drive",
      description: "Store and share documents with Google Drive",
      category: "storage",
      icon: "/api/placeholder/64/64",
      features: [
      "File synchronization",
      "Folder management",
      "Sharing permissions",
      "Automatic backup"],

      status: "connected",
      connectionDetails: {
        email: "user@example.com",
        connectedAt: "2023-11-10T14:20:00Z",
        lastSync: new Date(Date.now() - 1800000).toISOString(),
        storageUsed: "45.2 GB",
        storageTotal: "100 GB"
      },
      settings: {
        autoSync: true,
        syncInterval: 30,
        preserveFolderStructure: true
      }
    },
    {
      id: "dropbox",
      name: "Dropbox",
      description: "Backup files and sync documents with Dropbox",
      category: "storage",
      icon: "/api/placeholder/64/64",
      features: [
      "Automatic backup",
      "Version control",
      "Team folders",
      "Smart sync"],

      status: "disconnected",
      connectionDetails: null,
      settings: {
        autoBackup: true,
        versioning: true,
        compression: true
      }
    },
    {
      id: "stripe",
      name: "Stripe",
      description: "Process payments and manage subscriptions",
      category: "payment",
      icon: "/api/placeholder/64/64",
      features: [
      "Payment processing",
      "Subscription management",
      "Invoice generation",
      "Financial reporting"],

      status: "connected",
      connectionDetails: {
        accountId: "acct_1234567890",
        connectedAt: "2023-09-01T11:00:00Z",
        mode: "live",
        currency: "EUR"
      },
      settings: {
        autoCharge: true,
        sendReceipts: true,
        webhooksEnabled: true
      }
    },
    {
      id: "mailchimp",
      name: "Mailchimp",
      description: "Email marketing and newsletter automation",
      category: "marketing",
      icon: "/api/placeholder/64/64",
      features: [
      "Email campaigns",
      "Newsletter automation",
      "Audience segmentation",
      "Performance analytics"],

      status: "disconnected",
      connectionDetails: null,
      settings: {
        autoSubscribe: false,
        segmentByRole: true,
        weeklyNewsletter: true
      }
    },
    {
      id: "webhooks",
      name: "Webhooks",
      description: "Send real-time updates to external services",
      category: "automation",
      icon: "/api/placeholder/64/64",
      features: [
      "Custom webhook endpoints",
      "Event filtering",
      "Retry logic",
      "Signature verification"],

      status: "connected",
      connectionDetails: {
        activeWebhooks: 3,
        totalCalls: 156789,
        successRate: 97.8
      },
      settings: {
        retryAttempts: 3,
        timeout: 30,
        enableLogging: true
      }
    },
    {
      id: "twilio",
      name: "Twilio",
      description: "SMS notifications and communications",
      category: "communication",
      icon: "/api/placeholder/64/64",
      features: [
      "SMS notifications",
      "Voice calls",
      "WhatsApp integration",
      "Programmable messaging"],

      status: "connected",
      connectionDetails: {
        accountSid: "AC1234567890abcdef",
        connectedAt: "2023-12-10T08:20:00Z",
        phoneNumber: "+33123456789",
        messagesSent: 1567
      },
      settings: {
        smsNotifications: true,
        urgentOnly: false,
        quietHours: { start: "22:00", end: "08:00" }
      }
    }],

    webhooks: [
    {
      id: 1,
      url: "https://api.example.com/webhooks/enrollment",
      events: ["enrollment.created", "enrollment.updated"],
      active: true,
      createdAt: "2023-10-01T12:00:00Z",
      lastTriggered: new Date(Date.now() - 3600000).toISOString(),
      successRate: 98.5
    },
    {
      id: 2,
      url: "https://api.example.com/webhooks/completion",
      events: ["course.completed", "certificate.issued"],
      active: true,
      createdAt: "2023-09-15T14:30:00Z",
      lastTriggered: new Date(Date.now() - 7200000).toISOString(),
      successRate: 99.2
    },
    {
      id: 3,
      url: "https://api.example.com/webhooks/payment",
      events: ["payment.success", "payment.failed", "subscription.updated"],
      active: false,
      createdAt: "2023-08-20T10:15:00Z",
      lastTriggered: new Date(Date.now() - 172800000).toISOString(),
      successRate: 95.7
    }],

    apiKeys: [
    {
      id: 1,
      name: "Production API Key",
      key: "sk_live_1234...abcd",
      permissions: ["read", "write"],
      createdAt: "2023-07-01T09:00:00Z",
      lastUsed: new Date(Date.now() - 300000).toISOString(),
      expiresAt: "2024-07-01T09:00:00Z",
      requestCount: 45678
    },
    {
      id: 2,
      name: "Development API Key",
      key: "sk_test_5678...efgh",
      permissions: ["read"],
      createdAt: "2023-11-15T11:30:00Z",
      lastUsed: new Date(Date.now() - 3600000).toISOString(),
      expiresAt: null,
      requestCount: 12345
    }]

  };
};
// Generate integration activity
export const generateIntegrationActivity = () => {
  return [
  {
    id: 1,
    integration: "Google Workspace",
    action: "Calendar event created",
    details: "New class session scheduled",
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    status: "success"
  },
  {
    id: 2,
    integration: "Slack",
    action: "Notification sent",
    details: "Grade update notification",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    status: "success"
  },
  {
    id: 3,
    integration: "Stripe",
    action: "Payment processed",
    details: "Monthly subscription renewal",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    status: "success"
  },
  {
    id: 4,
    integration: "Zapier",
    action: "Workflow triggered",
    details: "New student enrollment automation",
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    status: "success"
  },
  {
    id: 5,
    integration: "Zoom",
    action: "Meeting created",
    details: "Office hours session",
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    status: "success"
  },
  {
    id: 6,
    integration: "Twilio",
    action: "SMS sent",
    details: "Assignment reminder",
    timestamp: new Date(Date.now() - 18000000).toISOString(),
    status: "failed",
    error: "Invalid phone number"
  }];

};
// Generate integration statistics
export const generateIntegrationStats = () => {
  return {
    overview: {
      totalIntegrations: 11,
      activeIntegrations: 7,
      totalApiCalls: 156789,
      successRate: 98.2
    },
    byIntegration: {
      google: { calls: 45678, successRate: 99.5, lastSync: new Date(Date.now() - 3600000).toISOString() },
      slack: { calls: 23456, successRate: 98.7, lastSync: new Date(Date.now() - 7200000).toISOString() },
      stripe: { calls: 12345, successRate: 99.9, lastSync: new Date(Date.now() - 1800000).toISOString() },
      zapier: { calls: 34567, successRate: 97.3, lastSync: new Date(Date.now() - 10800000).toISOString() },
      zoom: { calls: 19876, successRate: 96.8, lastSync: new Date(Date.now() - 14400000).toISOString() }
    },
    usage: {
      daily: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        data: [2345, 2678, 2890, 3123, 2987, 1543, 1234]
      },
      monthly: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        data: [45678, 48902, 52341, 54678, 51234, 49876]
      }
    },
    topEndpoints: [
    { endpoint: "/api/calendar/sync", calls: 12345, avgResponseTime: 145 },
    { endpoint: "/api/notifications/send", calls: 9876, avgResponseTime: 78 },
    { endpoint: "/api/payments/process", calls: 5432, avgResponseTime: 234 },
    { endpoint: "/api/webhooks/trigger", calls: 8765, avgResponseTime: 167 }]

  };
};
// Generate OAuth configurations
export const generateOAuthConfigs = () => {
  return {
    google: {
      clientId: "1234567890-abcdefghijklmnop.apps.googleusercontent.com",
      scopes: [
      "https://www.googleapis.com/auth/calendar",
      "https://www.googleapis.com/auth/drive",
      "https://www.googleapis.com/auth/userinfo.email"],

      redirectUri: "https://app.example.com/auth/google/callback"
    },
    microsoft: {
      clientId: "12345678-1234-1234-1234-123456789012",
      tenantId: "common",
      scopes: ["User.Read", "Calendars.ReadWrite", "Files.Read"],
      redirectUri: "https://app.example.com/auth/microsoft/callback"
    },
    github: {
      clientId: "Iv1.1234567890abcdef",
      scopes: ["read:user", "repo", "notifications"],
      redirectUri: "https://app.example.com/auth/github/callback"
    }
  };
};