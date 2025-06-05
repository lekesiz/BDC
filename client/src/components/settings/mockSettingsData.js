// Mock Settings Data
export const generateSettingsData = (userRole) => {
  const baseSettings = {
    profile: {
      firstName: "John",
      lastName: "Doe",
      email: "john.doe@example.com",
      phone: "+33 6 12 34 56 78",
      avatar: "/api/placeholder/150/150",
      bio: "Passionate about technology and continuous learning",
      department: "Engineering",
      role: userRole,
      joinDate: "2023-06-15",
      language: "en",
      timezone: "Europe/Paris",
      address: {
        street: "123 Rue de la Paix",
        city: "Paris",
        postalCode: "75001",
        country: "France"
      }
    },
    notifications: {
      email: {
        courseUpdates: true,
        assignmentReminders: true,
        gradeNotifications: true,
        systemAlerts: true,
        marketingEmails: false,
        weeklyDigest: true
      },
      push: {
        courseUpdates: true,
        assignmentReminders: true,
        gradeNotifications: true,
        systemAlerts: true,
        liveSessionReminders: true
      },
      sms: {
        urgentAlerts: true,
        appointmentReminders: true,
        enabled: false
      }
    },
    privacy: {
      profileVisibility: "public",
      showEmail: false,
      showPhone: false,
      showProgress: true,
      allowDataAnalytics: true,
      shareWithPartners: false,
      cookieConsent: true,
      dataRetention: "1_year"
    },
    security: {
      twoFactorEnabled: false,
      lastPasswordChange: "2023-12-01",
      activeSessions: [
        {
          id: 1,
          device: "Chrome on Windows",
          location: "Paris, France",
          lastActive: new Date().toISOString(),
          current: true
        },
        {
          id: 2,
          device: "Mobile App - iOS",
          location: "Lyon, France",
          lastActive: new Date(Date.now() - 86400000).toISOString(),
          current: false
        }
      ],
      loginHistory: [
        {
          id: 1,
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          device: "Chrome on Windows",
          location: "Paris, France",
          status: "success"
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          device: "Firefox on Mac",
          location: "London, UK",
          status: "success"
        }
      ]
    },
    appearance: {
      theme: "light",
      primaryColor: "#3B82F6",
      fontSize: "medium",
      compactMode: false,
      animations: true,
      highContrast: false,
      colorBlindMode: null
    },
    integrations: {
      google: {
        connected: true,
        email: "john.doe@gmail.com",
        calendarSync: true,
        driveSync: false,
        lastSync: new Date(Date.now() - 3600000).toISOString()
      },
      microsoft: {
        connected: false,
        email: null,
        calendarSync: false,
        teamsIntegration: false
      },
      slack: {
        connected: false,
        workspace: null,
        notifications: false
      },
      zoom: {
        connected: true,
        email: "john.doe@example.com",
        autoJoin: true
      }
    }
  };
  // Role-specific settings
  if (userRole === "admin" || userRole === "tenant_admin") {
    return {
      ...baseSettings,
      organization: {
        name: "Tech Academy",
        logo: "/api/placeholder/200/60",
        website: "https://techacademy.example.com",
        primaryColor: "#3B82F6",
        secondaryColor: "#10B981",
        customDomain: "learn.techacademy.com",
        supportEmail: "support@techacademy.com",
        timezone: "Europe/Paris",
        defaultLanguage: "en",
        allowedDomains: ["techacademy.com", "example.com"],
        features: {
          customBranding: true,
          ssoEnabled: true,
          apiAccess: true,
          advancedAnalytics: true,
          whiteLabeling: false
        }
      },
      billing: {
        plan: "Professional",
        status: "active",
        nextBillingDate: "2024-02-15",
        amount: 499,
        currency: "EUR",
        paymentMethod: {
          type: "card",
          last4: "4242",
          brand: "Visa",
          expiryDate: "12/25"
        },
        invoices: [
          {
            id: 1,
            date: "2024-01-15",
            amount: 499,
            status: "paid",
            downloadUrl: "/api/invoices/2024-01-15.pdf"
          },
          {
            id: 2,
            date: "2023-12-15",
            amount: 499,
            status: "paid",
            downloadUrl: "/api/invoices/2023-12-15.pdf"
          }
        ],
        usage: {
          users: { current: 234, limit: 500 },
          storage: { current: 45.2, limit: 100, unit: "GB" },
          bandwidth: { current: 120.5, limit: 500, unit: "GB" },
          apiCalls: { current: 45230, limit: 100000 }
        }
      },
      security: {
        ...baseSettings.security,
        passwordPolicy: {
          minLength: 8,
          requireUppercase: true,
          requireLowercase: true,
          requireNumbers: true,
          requireSpecialChars: true,
          expiryDays: 90,
          preventReuse: 5
        },
        ipWhitelist: [
          "192.168.1.0/24",
          "10.0.0.0/16"
        ],
        ssoConfig: {
          enabled: true,
          provider: "SAML",
          entityId: "https://techacademy.com",
          ssoUrl: "https://sso.techacademy.com",
          certificate: "-----BEGIN CERTIFICATE-----..."
        }
      },
      emailTemplates: {
        welcome: {
          subject: "Welcome to Tech Academy!",
          enabled: true,
          lastModified: "2023-11-15"
        },
        courseEnrollment: {
          subject: "You've been enrolled in {{courseName}}",
          enabled: true,
          lastModified: "2023-10-20"
        },
        certificateCompletion: {
          subject: "Congratulations! Your certificate is ready",
          enabled: true,
          lastModified: "2023-09-10"
        }
      },
      apiSettings: {
        apiKey: "ta_live_key_xxxxxxxxxxxxxxxx",
        webhookUrl: "https://techacademy.com/webhooks",
        allowedOrigins: ["https://techacademy.com", "https://app.techacademy.com"],
        rateLimits: {
          perMinute: 60,
          perHour: 1000,
          perDay: 10000
        }
      }
    };
  }
  if (userRole === "trainer") {
    return {
      ...baseSettings,
      teaching: {
        availability: {
          monday: { start: "09:00", end: "17:00", available: true },
          tuesday: { start: "09:00", end: "17:00", available: true },
          wednesday: { start: "09:00", end: "17:00", available: true },
          thursday: { start: "09:00", end: "17:00", available: true },
          friday: { start: "09:00", end: "15:00", available: true },
          saturday: { start: null, end: null, available: false },
          sunday: { start: null, end: null, available: false }
        },
        specializations: ["JavaScript", "React", "Node.js", "Python"],
        certifications: [
          { name: "AWS Certified Developer", issueDate: "2023-03-15", expiryDate: "2026-03-15" },
          { name: "Google Cloud Professional", issueDate: "2023-06-20", expiryDate: "2025-06-20" }
        ],
        preferredClassSize: 20,
        teachingStyle: "interactive",
        bio: "10+ years of experience in web development and teaching",
        ratingSettings: {
          allowStudentRatings: true,
          publicProfile: true,
          displayBadges: true
        }
      },
      courseDefaults: {
        duration: 60,
        maxStudents: 25,
        requirePrerequisites: true,
        allowRecording: true,
        enableChat: true,
        enableQA: true,
        defaultMeetingPlatform: "zoom"
      },
      grading: {
        defaultGradingScale: "percentage",
        passingGrade: 70,
        lateSubmissionPolicy: "deduct_10_percent",
        allowResubmissions: true,
        maxResubmissions: 2,
        rubricTemplates: [
          { id: 1, name: "Standard Assignment", criteria: 5 },
          { id: 2, name: "Project Evaluation", criteria: 8 },
          { id: 3, name: "Presentation", criteria: 6 }
        ]
      }
    };
  }
  if (userRole === "student") {
    return {
      ...baseSettings,
      learning: {
        preferences: {
          learningStyle: "visual",
          preferredLanguage: "en",
          subtitles: true,
          playbackSpeed: 1.0,
          autoplay: false,
          downloadForOffline: true
        },
        goals: [
          { id: 1, title: "Complete JavaScript course", deadline: "2024-03-01", progress: 65 },
          { id: 2, title: "Learn React", deadline: "2024-04-15", progress: 30 },
          { id: 3, title: "Build portfolio project", deadline: "2024-05-01", progress: 10 }
        ],
        studySchedule: {
          monday: { start: "18:00", end: "20:00" },
          tuesday: { start: "18:00", end: "20:00" },
          wednesday: { start: null, end: null },
          thursday: { start: "18:00", end: "21:00" },
          friday: { start: null, end: null },
          saturday: { start: "10:00", end: "14:00" },
          sunday: { start: "10:00", end: "12:00" }
        },
        interests: ["Web Development", "Mobile Apps", "AI/ML", "Cloud Computing"],
        skillLevel: "intermediate"
      },
      achievements: {
        badges: [
          { id: 1, name: "Fast Learner", earnedDate: "2023-10-15", description: "Complete 5 courses in 30 days" },
          { id: 2, name: "Perfect Score", earnedDate: "2023-11-20", description: "Score 100% on an assessment" },
          { id: 3, name: "Consistent Learner", earnedDate: "2023-12-01", description: "Study for 30 consecutive days" }
        ],
        certificates: [
          { id: 1, courseName: "HTML & CSS Fundamentals", issueDate: "2023-09-15", verificationCode: "CERT-2023-HTML-001" },
          { id: 2, courseName: "JavaScript Basics", issueDate: "2023-11-01", verificationCode: "CERT-2023-JS-045" }
        ],
        points: 2450,
        rank: 15,
        totalStudents: 234
      },
      subscription: {
        plan: "Student Plus",
        status: "active",
        startDate: "2023-06-15",
        endDate: "2024-06-15",
        features: [
          "Unlimited course access",
          "Offline downloads",
          "Priority support",
          "Certificates of completion"
        ],
        autoRenew: true,
        nextBillingAmount: 29.99,
        currency: "EUR"
      }
    };
  }
  return baseSettings;
};
// Generate available settings options
export const generateSettingsOptions = () => {
  return {
    languages: [
      { code: "en", name: "English" },
      { code: "fr", name: "Français" },
      { code: "es", name: "Español" },
      { code: "de", name: "Deutsch" },
      { code: "it", name: "Italiano" }
    ],
    timezones: [
      { value: "Europe/Paris", label: "Paris (GMT+1)" },
      { value: "Europe/London", label: "London (GMT)" },
      { value: "America/New_York", label: "New York (GMT-5)" },
      { value: "America/Los_Angeles", label: "Los Angeles (GMT-8)" },
      { value: "Asia/Tokyo", label: "Tokyo (GMT+9)" }
    ],
    themes: [
      { value: "light", label: "Light" },
      { value: "dark", label: "Dark" },
      { value: "auto", label: "Auto (System)" }
    ],
    fontSizes: [
      { value: "small", label: "Small" },
      { value: "medium", label: "Medium" },
      { value: "large", label: "Large" }
    ],
    gradingScales: [
      { value: "percentage", label: "Percentage (0-100%)" },
      { value: "letter", label: "Letter Grade (A-F)" },
      { value: "points", label: "Points" },
      { value: "passfail", label: "Pass/Fail" }
    ],
    learningStyles: [
      { value: "visual", label: "Visual" },
      { value: "auditory", label: "Auditory" },
      { value: "reading", label: "Reading/Writing" },
      { value: "kinesthetic", label: "Kinesthetic" }
    ],
    playbackSpeeds: [
      { value: 0.5, label: "0.5x" },
      { value: 0.75, label: "0.75x" },
      { value: 1.0, label: "1x (Normal)" },
      { value: 1.25, label: "1.25x" },
      { value: 1.5, label: "1.5x" },
      { value: 2.0, label: "2x" }
    ]
  };
};
// Generate data export options
export const generateDataExportOptions = () => {
  return {
    formats: [
      { value: "json", label: "JSON", icon: "file-code" },
      { value: "csv", label: "CSV", icon: "file-csv" },
      { value: "pdf", label: "PDF", icon: "file-pdf" },
      { value: "xlsx", label: "Excel", icon: "file-excel" }
    ],
    dataTypes: [
      { value: "profile", label: "Profile Information" },
      { value: "courses", label: "Course Progress" },
      { value: "certificates", label: "Certificates" },
      { value: "grades", label: "Grades & Assessments" },
      { value: "all", label: "All Data" }
    ]
  };
};