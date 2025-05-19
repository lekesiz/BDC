// Mock Compliance Data
export const generateComplianceData = () => {
  return {
    auditLogs: [
      {
        id: 1,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        user: "John Doe",
        userId: "user_123",
        action: "login",
        resource: "auth",
        details: "Successful login from IP 192.168.1.1",
        ipAddress: "192.168.1.1",
        userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        status: "success",
        risk: "low"
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        user: "Jane Smith",
        userId: "user_456",
        action: "update",
        resource: "user_profile",
        details: "Updated email address",
        ipAddress: "192.168.1.2",
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        status: "success",
        risk: "low"
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        user: "Admin User",
        userId: "admin_789",
        action: "delete",
        resource: "document",
        details: "Deleted document ID: doc_12345",
        ipAddress: "192.168.1.100",
        userAgent: "Mozilla/5.0 (X11; Linux x86_64)",
        status: "success",
        risk: "medium"
      },
      {
        id: 4,
        timestamp: new Date(Date.now() - 14400000).toISOString(),
        user: "System",
        userId: "system",
        action: "backup",
        resource: "database",
        details: "Automated daily backup completed",
        ipAddress: "127.0.0.1",
        userAgent: "System Process",
        status: "success",
        risk: "low"
      },
      {
        id: 5,
        timestamp: new Date(Date.now() - 18000000).toISOString(),
        user: "John Doe",
        userId: "user_123",
        action: "access",
        resource: "sensitive_data",
        details: "Accessed financial reports",
        ipAddress: "192.168.1.1",
        userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        status: "success",
        risk: "high"
      },
      {
        id: 6,
        timestamp: new Date(Date.now() - 21600000).toISOString(),
        user: "Unknown",
        userId: null,
        action: "login_attempt",
        resource: "auth",
        details: "Failed login attempt - incorrect password",
        ipAddress: "203.0.113.0",
        userAgent: "Mozilla/5.0 (compatible; bot)",
        status: "failed",
        risk: "high"
      }
    ],
    
    gdprCompliance: {
      status: "compliant",
      lastAudit: "2024-01-15",
      nextAudit: "2024-07-15",
      score: 92,
      requirements: [
        { id: 1, requirement: "Data Processing Agreements", status: "complete", lastUpdated: "2023-12-01" },
        { id: 2, requirement: "Privacy Policy", status: "complete", lastUpdated: "2024-01-10" },
        { id: 3, requirement: "Cookie Consent", status: "complete", lastUpdated: "2023-11-15" },
        { id: 4, requirement: "Data Retention Policy", status: "complete", lastUpdated: "2023-10-20" },
        { id: 5, requirement: "Right to Erasure Implementation", status: "complete", lastUpdated: "2023-09-25" },
        { id: 6, requirement: "Data Portability", status: "in_progress", lastUpdated: "2024-01-20" },
        { id: 7, requirement: "Breach Notification Process", status: "complete", lastUpdated: "2023-08-30" },
        { id: 8, requirement: "Data Protection Officer", status: "complete", lastUpdated: "2023-07-15" }
      ],
      dataCategories: [
        { category: "Personal Identification", sensitivity: "high", encrypted: true, retention: "5 years" },
        { category: "Contact Information", sensitivity: "medium", encrypted: true, retention: "3 years" },
        { category: "Educational Records", sensitivity: "high", encrypted: true, retention: "7 years" },
        { category: "Payment Information", sensitivity: "critical", encrypted: true, retention: "2 years" },
        { category: "Usage Analytics", sensitivity: "low", encrypted: false, retention: "1 year" }
      ]
    },
    
    securityHeaders: {
      status: "configured",
      headers: [
        { name: "Content-Security-Policy", value: "default-src 'self'", enabled: true, risk: "low" },
        { name: "X-Frame-Options", value: "DENY", enabled: true, risk: "low" },
        { name: "X-Content-Type-Options", value: "nosniff", enabled: true, risk: "low" },
        { name: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains", enabled: true, risk: "low" },
        { name: "X-XSS-Protection", value: "1; mode=block", enabled: true, risk: "low" },
        { name: "Referrer-Policy", value: "strict-origin-when-cross-origin", enabled: true, risk: "low" },
        { name: "Permissions-Policy", value: "geolocation=(), microphone=()", enabled: true, risk: "low" }
      ],
      score: 100,
      lastCheck: new Date(Date.now() - 86400000).toISOString()
    },
    
    dataBackup: {
      backups: [
        {
          id: 1,
          type: "full",
          status: "completed",
          size: "15.7 GB",
          duration: "2h 15m",
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          location: "AWS S3 - eu-west-1",
          encrypted: true,
          verified: true
        },
        {
          id: 2,
          type: "incremental",
          status: "completed",
          size: "2.3 GB",
          duration: "25m",
          timestamp: new Date(Date.now() - 43200000).toISOString(),
          location: "AWS S3 - eu-west-1",
          encrypted: true,
          verified: true
        },
        {
          id: 3,
          type: "incremental",
          status: "completed",
          size: "1.8 GB",
          duration: "20m",
          timestamp: new Date(Date.now() - 21600000).toISOString(),
          location: "AWS S3 - eu-west-1",
          encrypted: true,
          verified: true
        },
        {
          id: 4,
          type: "incremental",
          status: "in_progress",
          size: null,
          duration: null,
          timestamp: new Date().toISOString(),
          location: "AWS S3 - eu-west-1",
          encrypted: true,
          verified: false,
          progress: 67
        }
      ],
      schedule: {
        full: { frequency: "weekly", day: "sunday", time: "02:00" },
        incremental: { frequency: "daily", time: "02:00" },
        retention: { full: "30 days", incremental: "7 days" }
      },
      storage: {
        used: 124.5,
        available: 375.5,
        total: 500,
        unit: "GB"
      }
    },
    
    inputValidation: {
      rules: [
        {
          id: 1,
          field: "email",
          rule: "Email format validation",
          enabled: true,
          violations: 12,
          lastViolation: new Date(Date.now() - 7200000).toISOString()
        },
        {
          id: 2,
          field: "password",
          rule: "Minimum 8 characters, mixed case, numbers, special chars",
          enabled: true,
          violations: 45,
          lastViolation: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 3,
          field: "phone",
          rule: "International phone format",
          enabled: true,
          violations: 8,
          lastViolation: new Date(Date.now() - 14400000).toISOString()
        },
        {
          id: 4,
          field: "username",
          rule: "Alphanumeric, 3-20 characters",
          enabled: true,
          violations: 3,
          lastViolation: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 5,
          field: "credit_card",
          rule: "Valid card number format",
          enabled: true,
          violations: 0,
          lastViolation: null
        }
      ],
      statistics: {
        totalValidations: 156789,
        violations: 68,
        successRate: 99.96,
        mostViolatedField: "password"
      }
    },
    
    regulatoryCompliance: {
      frameworks: [
        {
          name: "GDPR",
          region: "European Union",
          status: "compliant",
          score: 92,
          lastAudit: "2024-01-15",
          nextAudit: "2024-07-15"
        },
        {
          name: "CCPA",
          region: "California, USA",
          status: "compliant",
          score: 88,
          lastAudit: "2023-12-01",
          nextAudit: "2024-06-01"
        },
        {
          name: "PIPEDA",
          region: "Canada",
          status: "compliant",
          score: 90,
          lastAudit: "2023-11-15",
          nextAudit: "2024-05-15"
        },
        {
          name: "LGPD",
          region: "Brazil",
          status: "in_progress",
          score: 75,
          lastAudit: "2023-10-01",
          nextAudit: "2024-04-01"
        }
      ],
      certifications: [
        {
          name: "ISO 27001",
          status: "active",
          issueDate: "2023-06-15",
          expiryDate: "2024-06-15",
          certificationBody: "TÜV SÜD"
        },
        {
          name: "SOC 2 Type II",
          status: "active",
          issueDate: "2023-09-01",
          expiryDate: "2024-09-01",
          certificationBody: "Deloitte"
        }
      ]
    },
    
    riskAssessment: {
      overallRisk: "medium",
      riskScore: 6.2,
      categories: [
        { category: "Data Security", risk: "low", score: 2.1, trend: "improving" },
        { category: "Access Control", risk: "medium", score: 5.8, trend: "stable" },
        { category: "Third-party Services", risk: "high", score: 8.2, trend: "worsening" },
        { category: "Employee Training", risk: "medium", score: 6.5, trend: "improving" },
        { category: "Incident Response", risk: "low", score: 3.2, trend: "stable" }
      ],
      recommendations: [
        "Implement multi-factor authentication for all administrative accounts",
        "Review and update third-party service agreements",
        "Conduct quarterly security awareness training",
        "Perform penetration testing on critical systems"
      ]
    }
  };
};

// Generate compliance metrics
export const generateComplianceMetrics = () => {
  return {
    overview: {
      complianceScore: 88,
      openIssues: 5,
      resolvedIssues: 123,
      upcomingAudits: 3,
      activePolicies: 45
    },
    trends: {
      monthly: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        scores: [82, 84, 86, 87, 88, 88],
        violations: [12, 10, 8, 7, 5, 5]
      },
      quarterly: {
        labels: ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "Q1 2024"],
        scores: [80, 83, 85, 87, 88]
      }
    },
    byCategory: {
      labels: ["GDPR", "Security", "Privacy", "Data Protection", "Access Control"],
      scores: [92, 88, 90, 85, 87]
    }
  };
};

// Generate compliance reports
export const generateComplianceReports = () => {
  return [
    {
      id: 1,
      title: "Q1 2024 Compliance Report",
      type: "quarterly",
      generatedAt: "2024-01-15",
      status: "completed",
      size: "2.4 MB",
      format: "PDF"
    },
    {
      id: 2,
      title: "GDPR Annual Assessment",
      type: "annual",
      generatedAt: "2024-01-01",
      status: "completed",
      size: "5.8 MB",
      format: "PDF"
    },
    {
      id: 3,
      title: "Security Audit Report",
      type: "audit",
      generatedAt: "2023-12-15",
      status: "completed",
      size: "3.2 MB",
      format: "PDF"
    },
    {
      id: 4,
      title: "Data Breach Response Test",
      type: "test",
      generatedAt: "2023-11-30",
      status: "completed",
      size: "1.7 MB",
      format: "PDF"
    }
  ];
};