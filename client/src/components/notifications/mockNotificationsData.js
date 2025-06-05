// Mock Notifications Data
export const generateNotificationsData = (userRole) => {
  const baseNotifications = [
    {
      id: 1,
      type: "course_update",
      title: "Course Material Updated",
      message: "New content has been added to 'Advanced JavaScript'",
      category: "education",
      priority: "medium",
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      read: false,
      actionable: true,
      actions: [
        { label: "View Course", action: "navigate", url: "/courses/javascript-advanced" },
        { label: "Dismiss", action: "dismiss" }
      ],
      metadata: {
        courseId: "course_123",
        instructorId: "instructor_456",
        updateType: "new_material"
      }
    },
    {
      id: 2,
      type: "assignment_reminder",
      title: "Assignment Due Soon",
      message: "Your React project is due in 2 days",
      category: "reminder",
      priority: "high",
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      read: false,
      actionable: true,
      actions: [
        { label: "Submit Assignment", action: "navigate", url: "/assignments/react-project" },
        { label: "Remind Later", action: "snooze", duration: 3600000 }
      ],
      metadata: {
        assignmentId: "assignment_789",
        courseId: "course_456",
        dueDate: new Date(Date.now() + 172800000).toISOString()
      }
    },
    {
      id: 3,
      type: "grade_posted",
      title: "Grade Posted",
      message: "Your grade for 'Python Basics Exam' has been posted: 92%",
      category: "academic",
      priority: "medium",
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      read: true,
      actionable: true,
      actions: [
        { label: "View Details", action: "navigate", url: "/grades/exam-python-basics" }
      ],
      metadata: {
        examId: "exam_321",
        courseId: "course_789",
        grade: 92,
        maxGrade: 100
      }
    },
    {
      id: 4,
      type: "system_update",
      title: "System Maintenance",
      message: "Scheduled maintenance on Sunday, 2:00 AM - 4:00 AM",
      category: "system",
      priority: "low",
      timestamp: new Date(Date.now() - 86400000).toISOString(),
      read: true,
      actionable: false,
      metadata: {
        maintenanceStart: new Date(Date.now() + 432000000).toISOString(),
        maintenanceEnd: new Date(Date.now() + 439200000).toISOString(),
        affectedServices: ["video_streaming", "file_uploads"]
      }
    },
    {
      id: 5,
      type: "message_received",
      title: "New Message from John Smith",
      message: "Hi, I have a question about the assignment...",
      category: "communication",
      priority: "medium",
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      read: false,
      actionable: true,
      actions: [
        { label: "Reply", action: "navigate", url: "/messages/conversation/123" },
        { label: "Mark as Read", action: "mark_read" }
      ],
      metadata: {
        conversationId: "conv_123",
        senderId: "user_456",
        senderName: "John Smith",
        messagePreview: "Hi, I have a question about the assignment..."
      }
    },
    {
      id: 6,
      type: "achievement_unlocked",
      title: "Achievement Unlocked!",
      message: "You've earned the 'Fast Learner' badge",
      category: "achievement",
      priority: "low",
      timestamp: new Date(Date.now() - 14400000).toISOString(),
      read: false,
      actionable: true,
      actions: [
        { label: "View Achievements", action: "navigate", url: "/profile/achievements" },
        { label: "Share", action: "share" }
      ],
      metadata: {
        achievementId: "achievement_123",
        badgeName: "Fast Learner",
        badgeImage: "/api/placeholder/64/64",
        points: 100
      }
    },
    {
      id: 7,
      type: "event_reminder",
      title: "Upcoming Live Session",
      message: "JavaScript Q&A Session starts in 1 hour",
      category: "event",
      priority: "high",
      timestamp: new Date(Date.now() - 600000).toISOString(),
      read: false,
      actionable: true,
      actions: [
        { label: "Join Session", action: "navigate", url: "/live/session-123" },
        { label: "Set Reminder", action: "remind", time: 300000 }
      ],
      metadata: {
        sessionId: "session_123",
        instructorId: "instructor_789",
        startTime: new Date(Date.now() + 3600000).toISOString(),
        duration: 3600000
      }
    },
    {
      id: 8,
      type: "certificate_ready",
      title: "Certificate Available",
      message: "Your certificate for 'Web Development Basics' is ready",
      category: "achievement",
      priority: "medium",
      timestamp: new Date(Date.now() - 172800000).toISOString(),
      read: true,
      actionable: true,
      actions: [
        { label: "Download Certificate", action: "download", url: "/certificates/web-dev-basics.pdf" },
        { label: "View All Certificates", action: "navigate", url: "/profile/certificates" }
      ],
      metadata: {
        certificateId: "cert_123",
        courseId: "course_111",
        issuedDate: new Date(Date.now() - 172800000).toISOString()
      }
    }
  ];
  // Add role-specific notifications
  if (userRole === "trainer") {
    const trainerNotifications = [
      {
        id: 9,
        type: "submission_received",
        title: "New Assignment Submission",
        message: "5 students have submitted their Python projects",
        category: "grading",
        priority: "high",
        timestamp: new Date(Date.now() - 5400000).toISOString(),
        read: false,
        actionable: true,
        actions: [
          { label: "Review Submissions", action: "navigate", url: "/submissions/pending" },
          { label: "Mark All Read", action: "mark_all_read" }
        ],
        metadata: {
          assignmentId: "assignment_456",
          submissionCount: 5,
          courseId: "course_123"
        }
      },
      {
        id: 10,
        type: "student_question",
        title: "Student Question",
        message: "Marie Martin asked a question in the discussion forum",
        category: "communication",
        priority: "medium",
        timestamp: new Date(Date.now() - 9000000).toISOString(),
        read: false,
        actionable: true,
        actions: [
          { label: "Answer Question", action: "navigate", url: "/forums/question-789" },
          { label: "Assign to TA", action: "assign" }
        ],
        metadata: {
          questionId: "question_789",
          studentId: "student_456",
          forumId: "forum_123"
        }
      },
      {
        id: 11,
        type: "class_scheduled",
        title: "New Class Scheduled",
        message: "React Advanced Topics scheduled for Monday, 2:00 PM",
        category: "schedule",
        priority: "medium",
        timestamp: new Date(Date.now() - 21600000).toISOString(),
        read: true,
        actionable: true,
        actions: [
          { label: "View Schedule", action: "navigate", url: "/schedule" },
          { label: "Prepare Materials", action: "navigate", url: "/courses/react-advanced/materials" }
        ],
        metadata: {
          classId: "class_123",
          courseId: "course_456",
          scheduledTime: new Date(Date.now() + 259200000).toISOString()
        }
      }
    ];
    return [...baseNotifications, ...trainerNotifications];
  }
  if (userRole === "admin" || userRole === "tenant_admin") {
    const adminNotifications = [
      {
        id: 12,
        type: "user_registration",
        title: "New User Registration",
        message: "15 new users registered today",
        category: "admin",
        priority: "low",
        timestamp: new Date(Date.now() - 18000000).toISOString(),
        read: false,
        actionable: true,
        actions: [
          { label: "View Users", action: "navigate", url: "/admin/users" },
          { label: "View Report", action: "navigate", url: "/admin/reports/registrations" }
        ],
        metadata: {
          registrationCount: 15,
          date: new Date().toISOString().split('T')[0]
        }
      },
      {
        id: 13,
        type: "system_alert",
        title: "High Server Load",
        message: "Server CPU usage exceeded 90% threshold",
        category: "system",
        priority: "critical",
        timestamp: new Date(Date.now() - 1200000).toISOString(),
        read: false,
        actionable: true,
        actions: [
          { label: "View Metrics", action: "navigate", url: "/admin/monitoring" },
          { label: "Scale Resources", action: "execute", command: "scale_up" }
        ],
        metadata: {
          metric: "cpu_usage",
          currentValue: 92,
          threshold: 90,
          serverId: "server_001"
        }
      },
      {
        id: 14,
        type: "compliance_update",
        title: "Compliance Report Ready",
        message: "Monthly GDPR compliance report is available",
        category: "compliance",
        priority: "medium",
        timestamp: new Date(Date.now() - 43200000).toISOString(),
        read: true,
        actionable: true,
        actions: [
          { label: "Download Report", action: "download", url: "/reports/gdpr-202401.pdf" },
          { label: "Schedule Review", action: "navigate", url: "/calendar/new-event" }
        ],
        metadata: {
          reportId: "report_123",
          reportType: "gdpr_compliance",
          period: "2024-01"
        }
      }
    ];
    return [...baseNotifications, ...adminNotifications];
  }
  return baseNotifications;
};
// Generate notification preferences
export const generateNotificationPreferences = () => {
  return {
    channels: {
      email: {
        enabled: true,
        frequency: "immediate",
        categories: {
          academic: true,
          reminder: true,
          system: false,
          communication: true,
          achievement: true,
          event: true
        }
      },
      push: {
        enabled: true,
        frequency: "immediate",
        categories: {
          academic: true,
          reminder: true,
          system: true,
          communication: true,
          achievement: false,
          event: true
        }
      },
      sms: {
        enabled: false,
        frequency: "urgent_only",
        categories: {
          academic: false,
          reminder: true,
          system: false,
          communication: false,
          achievement: false,
          event: false
        }
      },
      inApp: {
        enabled: true,
        frequency: "immediate",
        categories: {
          academic: true,
          reminder: true,
          system: true,
          communication: true,
          achievement: true,
          event: true
        }
      }
    },
    quietHours: {
      enabled: true,
      start: "22:00",
      end: "08:00",
      timezone: "Europe/Paris",
      allowUrgent: true
    },
    digest: {
      enabled: true,
      frequency: "weekly",
      day: "monday",
      time: "09:00",
      includeCategories: ["academic", "achievement", "event"]
    }
  };
};
// Generate notification statistics
export const generateNotificationStats = () => {
  return {
    overview: {
      total: 156,
      unread: 23,
      actionable: 45,
      snoozed: 5
    },
    byCategory: {
      academic: 45,
      reminder: 32,
      system: 12,
      communication: 38,
      achievement: 18,
      event: 11
    },
    byPriority: {
      critical: 2,
      high: 15,
      medium: 89,
      low: 50
    },
    trends: {
      daily: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        data: [23, 18, 25, 22, 30, 12, 8]
      },
      hourly: {
        labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
        data: [2, 1, 0, 0, 0, 0, 3, 8, 12, 15, 11, 9, 14, 16, 13, 10, 8, 11, 9, 7, 5, 4, 3, 2]
      }
    }
  };
};
// Generate notification templates
export const generateNotificationTemplates = () => {
  return [
    {
      id: 1,
      name: "Course Update",
      type: "course_update",
      subject: "{{courseName}} has been updated",
      body: "New content has been added to {{courseName}}. Check it out!",
      variables: ["courseName", "updateType", "instructorName"],
      channels: ["email", "push", "inApp"]
    },
    {
      id: 2,
      name: "Assignment Reminder",
      type: "assignment_reminder",
      subject: "Assignment Due: {{assignmentName}}",
      body: "Your assignment '{{assignmentName}}' is due in {{daysRemaining}} days.",
      variables: ["assignmentName", "daysRemaining", "courseName"],
      channels: ["email", "push", "sms", "inApp"]
    },
    {
      id: 3,
      name: "Grade Posted",
      type: "grade_posted",
      subject: "Grade Posted: {{assessmentName}}",
      body: "Your grade for '{{assessmentName}}' has been posted: {{grade}}%",
      variables: ["assessmentName", "grade", "courseName"],
      channels: ["email", "push", "inApp"]
    },
    {
      id: 4,
      name: "Welcome Email",
      type: "welcome",
      subject: "Welcome to {{platformName}}!",
      body: "Hi {{userName}}, welcome to {{platformName}}. Get started with your learning journey!",
      variables: ["userName", "platformName"],
      channels: ["email"]
    }
  ];
};