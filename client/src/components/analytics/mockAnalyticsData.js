// Mock Analytics Data
export const generateAnalyticsData = (userRole) => {
  const baseAnalytics = {
    overview: {
      totalUsers: 1234,
      activeUsers: 956,
      totalCourses: 45,
      completionRate: 78.5,
      averageScore: 84.2,
      totalRevenue: 245600,
      monthlyGrowth: 12.3,
      quarterlyGrowth: 34.7
    },
    userMetrics: {
      byRole: {
        labels: ["Students", "Trainers", "Admins", "Staff"],
        data: [890, 67, 12, 31],
        colors: ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]
      },
      byStatus: {
        labels: ["Active", "Inactive", "Suspended", "Pending"],
        data: [956, 234, 23, 21],
        colors: ["#10B981", "#6B7280", "#EF4444", "#F59E0B"]
      },
      growth: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [
          {
            label: "New Users",
            data: [45, 52, 61, 72, 89, 103],
            borderColor: "#3B82F6",
            backgroundColor: "rgba(59, 130, 246, 0.1)"
          },
          {
            label: "Active Users",
            data: [780, 810, 845, 890, 920, 956],
            borderColor: "#10B981",
            backgroundColor: "rgba(16, 185, 129, 0.1)"
          }
        ]
      }
    },
    courseMetrics: {
      popular: [
        { name: "JavaScript Fundamentals", enrollments: 342, completion: 82, rating: 4.8 },
        { name: "React Development", enrollments: 289, completion: 75, rating: 4.7 },
        { name: "Python Basics", enrollments: 265, completion: 88, rating: 4.9 },
        { name: "Data Science Intro", enrollments: 198, completion: 72, rating: 4.6 },
        { name: "UI/UX Design", enrollments: 176, completion: 85, rating: 4.8 }
      ],
      completionByCategory: {
        labels: ["Programming", "Design", "Data Science", "Business", "Marketing"],
        data: [78, 82, 74, 85, 80],
        colors: ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EC4899"]
      },
      averageCompletionTime: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
        data: [15, 28, 42, 58, 72, 85],
        idealData: [17, 33, 50, 67, 83, 100]
      }
    },
    revenueMetrics: {
      monthly: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        revenue: [38500, 42300, 45600, 48900, 52400, 58900],
        expenses: [15200, 16800, 17500, 18200, 19100, 20500],
        profit: [23300, 25500, 28100, 30700, 33300, 38400]
      },
      bySource: {
        labels: ["Subscriptions", "One-time", "Corporate", "Partnerships"],
        data: [145600, 45300, 38900, 15800],
        percentages: [59.3, 18.5, 15.9, 6.3]
      },
      topPlans: [
        { plan: "Professional", subscribers: 234, revenue: 58500, growth: 12.3 },
        { plan: "Standard", subscribers: 456, revenue: 45600, growth: 8.7 },
        { plan: "Basic", subscribers: 789, revenue: 31560, growth: 15.2 },
        { plan: "Enterprise", subscribers: 12, revenue: 48000, growth: 25.6 }
      ]
    },
    performanceMetrics: {
      systemHealth: {
        uptime: 99.97,
        responseTime: 142,
        errorRate: 0.03,
        activeConnections: 2341
      },
      apiUsage: {
        labels: ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        requests: [5432, 3210, 8976, 12453, 14567, 9876],
        errors: [12, 8, 23, 45, 67, 34]
      },
      resourceUtilization: {
        cpu: 68.5,
        memory: 72.3,
        storage: 45.8,
        bandwidth: 82.1
      }
    },
    learningAnalytics: {
      engagementScore: {
        overall: 7.8,
        byCategory: {
          "Video Watching": 8.2,
          "Assignment Submission": 7.5,
          "Forum Participation": 6.9,
          "Quiz Completion": 8.5,
          "Live Sessions": 7.3
        }
      },
      skillProgress: {
        labels: ["JavaScript", "Python", "React", "Data Analysis", "UI Design"],
        current: [85, 72, 78, 65, 82],
        target: [90, 85, 90, 80, 85]
      },
      learningPaths: [
        { path: "Web Developer", students: 234, avgProgress: 67, completion: 45 },
        { path: "Data Scientist", students: 189, avgProgress: 54, completion: 32 },
        { path: "UI/UX Designer", students: 156, avgProgress: 72, completion: 58 },
        { path: "Mobile Developer", students: 123, avgProgress: 48, completion: 28 }
      ]
    }
  };
  // Add role-specific analytics
  if (userRole === "trainer") {
    return {
      ...baseAnalytics,
      trainerAnalytics: {
        myStudents: {
          total: 67,
          active: 58,
          averageProgress: 73.5,
          averageScore: 81.2
        },
        coursePerformance: [
          { course: "JavaScript Advanced", students: 23, avgScore: 84.5, completion: 78 },
          { course: "React Basics", students: 31, avgScore: 79.2, completion: 82 },
          { course: "Node.js Backend", students: 13, avgScore: 86.7, completion: 69 }
        ],
        studentEngagement: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          attendance: [92, 88, 95, 86, 91, 72, 45],
          participation: [78, 82, 85, 75, 80, 65, 40]
        },
        feedback: {
          overall: 4.7,
          categories: {
            "Content Quality": 4.8,
            "Teaching Style": 4.6,
            "Responsiveness": 4.9,
            "Course Structure": 4.5
          },
          recentReviews: [
            { student: "John Doe", rating: 5, comment: "Excellent explanations!", date: "2024-01-20" },
            { student: "Jane Smith", rating: 4, comment: "Very helpful instructor", date: "2024-01-19" },
            { student: "Mike Johnson", rating: 5, comment: "Great course structure", date: "2024-01-18" }
          ]
        }
      }
    };
  }
  if (userRole === "student") {
    return {
      ...baseAnalytics,
      studentAnalytics: {
        myProgress: {
          overall: 73,
          byCategory: {
            "Programming": 82,
            "Theory": 68,
            "Projects": 75,
            "Assessments": 71
          },
          weeklyHours: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            hours: [2.5, 1.8, 3.2, 2.1, 2.8, 4.5, 3.0]
          }
        },
        achievements: {
          earned: 23,
          points: 2340,
          rank: 45,
          recentBadges: [
            { name: "Quick Learner", earned: "2024-01-20", points: 100 },
            { name: "Perfect Score", earned: "2024-01-18", points: 200 },
            { name: "Consistent", earned: "2024-01-15", points: 150 }
          ]
        },
        comparison: {
          vsClassAverage: {
            labels: ["Quiz 1", "Quiz 2", "Project 1", "Midterm", "Quiz 3"],
            myScores: [85, 92, 78, 88, 90],
            classAverage: [78, 82, 75, 80, 85]
          },
          percentile: 85,
          strongAreas: ["Problem Solving", "Code Quality", "Creativity"],
          improvementAreas: ["Time Management", "Documentation", "Testing"]
        }
      }
    };
  }
  return baseAnalytics;
};
// Generate detailed analytics reports
export const generateAnalyticsReports = () => {
  return [
    {
      id: 1,
      title: "Monthly Performance Report - January 2024",
      type: "monthly",
      generatedAt: "2024-02-01",
      sections: [
        "Executive Summary",
        "User Growth",
        "Course Performance",
        "Revenue Analysis",
        "System Performance"
      ],
      format: "PDF",
      size: "3.2 MB"
    },
    {
      id: 2,
      title: "Q4 2023 Analytics Report",
      type: "quarterly",
      generatedAt: "2024-01-15",
      sections: [
        "Quarter Overview",
        "Key Metrics",
        "Trends Analysis",
        "Recommendations"
      ],
      format: "PDF",
      size: "5.8 MB"
    },
    {
      id: 3,
      title: "Annual Report 2023",
      type: "annual",
      generatedAt: "2024-01-01",
      sections: [
        "Year in Review",
        "Growth Metrics",
        "Financial Summary",
        "Future Outlook"
      ],
      format: "PDF",
      size: "12.4 MB"
    }
  ];
};
// Generate analytics filters
export const generateAnalyticsFilters = () => {
  return {
    dateRanges: [
      { value: "today", label: "Today" },
      { value: "yesterday", label: "Yesterday" },
      { value: "last7days", label: "Last 7 Days" },
      { value: "last30days", label: "Last 30 Days" },
      { value: "last3months", label: "Last 3 Months" },
      { value: "last6months", label: "Last 6 Months" },
      { value: "lastyear", label: "Last Year" },
      { value: "custom", label: "Custom Range" }
    ],
    metrics: [
      { value: "users", label: "User Metrics" },
      { value: "courses", label: "Course Metrics" },
      { value: "revenue", label: "Revenue Metrics" },
      { value: "performance", label: "Performance Metrics" },
      { value: "engagement", label: "Engagement Metrics" }
    ],
    segments: [
      { value: "all", label: "All Users" },
      { value: "students", label: "Students Only" },
      { value: "trainers", label: "Trainers Only" },
      { value: "newusers", label: "New Users" },
      { value: "premium", label: "Premium Users" }
    ],
    comparisons: [
      { value: "none", label: "No Comparison" },
      { value: "previous_period", label: "Previous Period" },
      { value: "previous_year", label: "Previous Year" },
      { value: "target", label: "vs Target" }
    ]
  };
};
// Generate real-time analytics data
export const generateRealTimeAnalytics = () => {
  return {
    activeUsers: Math.floor(Math.random() * 50) + 200,
    currentSessions: Math.floor(Math.random() * 100) + 150,
    liveClasses: Math.floor(Math.random() * 10) + 5,
    recentActivity: [
      { type: "login", user: "user123", timestamp: new Date(Date.now() - 30000).toISOString() },
      { type: "course_start", user: "user456", course: "JavaScript", timestamp: new Date(Date.now() - 60000).toISOString() },
      { type: "quiz_complete", user: "user789", score: 92, timestamp: new Date(Date.now() - 120000).toISOString() },
      { type: "video_watch", user: "user234", video: "React Hooks", timestamp: new Date(Date.now() - 180000).toISOString() },
      { type: "assignment_submit", user: "user567", assignment: "Project 1", timestamp: new Date(Date.now() - 240000).toISOString() }
    ],
    systemStatus: {
      cpu: Math.floor(Math.random() * 30) + 40,
      memory: Math.floor(Math.random() * 20) + 60,
      requests: Math.floor(Math.random() * 1000) + 5000,
      responseTime: Math.floor(Math.random() * 50) + 100
    }
  };
};