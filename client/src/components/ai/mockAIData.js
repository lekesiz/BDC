// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock AI Features Data
export const generateAIData = (userRole) => {
  const baseAIData = {
    recommendations: {
      courses: [
      {
        id: 1,
        title: "Advanced React Patterns",
        reason: "Based on your completion of React Basics",
        matchScore: 92,
        difficulty: "Advanced",
        estimatedDuration: "4 weeks",
        skills: ["React", "Design Patterns", "Performance"],
        thumbnail: "/api/placeholder/200/150"
      },
      {
        id: 2,
        title: "Node.js Masterclass",
        reason: "Complements your frontend skills",
        matchScore: 87,
        difficulty: "Intermediate",
        estimatedDuration: "6 weeks",
        skills: ["Node.js", "Express", "MongoDB"],
        thumbnail: "/api/placeholder/200/150"
      },
      {
        id: 3,
        title: "Machine Learning with Python",
        reason: "Trending topic in your field",
        matchScore: 75,
        difficulty: "Advanced",
        estimatedDuration: "8 weeks",
        skills: ["Python", "TensorFlow", "Data Science"],
        thumbnail: "/api/placeholder/200/150"
      }],

      learningPaths: [
      {
        id: 1,
        title: "Full Stack Developer Path",
        description: "Complete pathway to become a full stack developer",
        courses: 12,
        estimatedDuration: "6 months",
        completionRate: 35,
        nextStep: "Complete JavaScript Advanced Topics"
      },
      {
        id: 2,
        title: "Data Science Specialist",
        description: "Master data science and machine learning",
        courses: 15,
        estimatedDuration: "8 months",
        completionRate: 10,
        nextStep: "Start Python Fundamentals"
      }],

      skills: [
      { name: "GraphQL", relevance: 85, demand: "High" },
      { name: "TypeScript", relevance: 82, demand: "Very High" },
      { name: "Docker", relevance: 78, demand: "High" },
      { name: "Kubernetes", relevance: 72, demand: "Medium" }]

    },
    insights: {
      learningAnalytics: {
        strongAreas: ["Problem Solving", "Code Quality", "Time Management"],
        improvementAreas: ["Algorithm Optimization", "System Design", "Testing"],
        learningStyle: "Visual Learner",
        optimalStudyTime: "Evening (6 PM - 9 PM)",
        retentionRate: 78,
        engagementScore: 85
      },
      progressPrediction: {
        currentPace: "Slightly Above Average",
        estimatedCompletion: "2024-05-15",
        predictedGrade: "B+",
        riskFactors: ["Decreasing engagement in last week"],
        recommendations: ["Review fundamental concepts", "Join study group"]
      },
      peerComparison: {
        rank: 15,
        totalPeers: 234,
        percentile: 94,
        strengths: ["Consistent submissions", "High accuracy"],
        opportunities: ["Participate more in discussions", "Help other students"]
      }
    },
    contentGeneration: {
      studyPlans: [
      {
        id: 1,
        title: "JavaScript Mastery Plan",
        duration: "4 weeks",
        customized: true,
        topics: [
        { week: 1, topic: "ES6+ Features", hours: 10 },
        { week: 2, topic: "Async Programming", hours: 12 },
        { week: 3, topic: "Modern Frameworks", hours: 15 },
        { week: 4, topic: "Testing & Deployment", hours: 8 }]

      }],

      quizzes: [
      {
        id: 1,
        topic: "React Hooks",
        difficulty: "Intermediate",
        questions: 20,
        generatedAt: new Date().toISOString(),
        averageScore: 82
      }],

      summaries: [
      {
        id: 1,
        course: "Python Basics",
        chapter: "Data Structures",
        keyPoints: [
        "Lists are mutable, ordered collections",
        "Dictionaries store key-value pairs",
        "Sets contain unique elements only"],

        examples: 3,
        exercises: 5
      }]

    },
    chatbot: {
      recentConversations: [
      {
        id: 1,
        topic: "JavaScript Arrays",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        resolved: true,
        satisfaction: 5
      },
      {
        id: 2,
        topic: "React State Management",
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        resolved: true,
        satisfaction: 4
      }],

      commonQuestions: [
      "How do I implement authentication in React?",
      "What's the difference between let and const?",
      "How do I deploy a Node.js application?",
      "What are React Hooks?"],

      capabilities: [
      "Code explanation",
      "Debugging assistance",
      "Concept clarification",
      "Best practices guidance",
      "Resource recommendations"]

    },
    feedback: {
      automated: {
        recentFeedback: [
        {
          id: 1,
          assignment: "React Todo App",
          score: 88,
          strengths: ["Clean code structure", "Good component separation"],
          improvements: ["Add error handling", "Implement loading states"],
          timestamp: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 2,
          assignment: "API Integration Project",
          score: 92,
          strengths: ["Excellent error handling", "Well-documented code"],
          improvements: ["Consider caching strategy", "Add rate limiting"],
          timestamp: new Date(Date.now() - 172800000).toISOString()
        }],

        averageResponseTime: "2 minutes",
        accuracyRate: 94
      }
    }
  };
  // Role-specific AI features
  if (userRole === "trainer") {
    return {
      ...baseAIData,
      teachingAssistant: {
        studentInsights: [
        {
          studentId: 1,
          name: "John Doe",
          riskLevel: "Low",
          engagement: 85,
          performance: 88,
          recommendations: ["Challenge with advanced topics", "Consider leadership role"]
        },
        {
          studentId: 2,
          name: "Jane Smith",
          riskLevel: "Medium",
          engagement: 65,
          performance: 72,
          recommendations: ["Provide additional support", "Schedule one-on-one session"]
        }],

        contentSuggestions: [
        {
          topic: "Async/Await",
          reason: "30% of students struggling with concept",
          resources: ["Video tutorial", "Interactive exercise", "Code examples"]
        },
        {
          topic: "State Management",
          reason: "Common question in office hours",
          resources: ["Comparison guide", "Best practices", "Live demo"]
        }],

        gradingAssistance: {
          pendingSubmissions: 15,
          averageGradingTime: "5 minutes",
          suggestedGrades: [
          { studentId: 1, assignment: "Final Project", suggestedGrade: 92, confidence: 0.95 },
          { studentId: 2, assignment: "Final Project", suggestedGrade: 78, confidence: 0.88 }]

        }
      },
      curriculumOptimization: {
        insights: [
        "Module 3 has 25% higher dropout rate",
        "Students prefer video content over text",
        "Lab exercises improve retention by 40%"],

        recommendations: [
        "Restructure Module 3 for better flow",
        "Add more interactive elements",
        "Introduce peer review sessions"]

      }
    };
  }
  if (userRole === "admin" || userRole === "tenant_admin") {
    return {
      ...baseAIData,
      performancePredictions: {
        enrollment: {
          nextMonth: 156,
          nextQuarter: 489,
          trend: "increasing",
          factors: ["Seasonal pattern", "Marketing campaign", "New course launches"]
        },
        revenue: {
          nextMonth: 45600,
          nextQuarter: 142800,
          trend: "stable",
          opportunities: ["Upsell premium features", "Launch corporate training"]
        },
        retention: {
          currentRate: 78,
          predictedRate: 82,
          improvements: ["Personalized learning paths", "Mentorship program"]
        }
      },
      operationalInsights: {
        resourceUtilization: {
          servers: 72,
          bandwidth: 68,
          storage: 45,
          recommendations: ["Scale up before peak season", "Optimize video delivery"]
        },
        costOptimization: [
        { area: "Cloud Infrastructure", potential: 15, effort: "Medium" },
        { area: "Software Licenses", potential: 8, effort: "Low" },
        { area: "Content Delivery", potential: 20, effort: "High" }]

      },
      aiUsageMetrics: {
        totalRequests: 15678,
        averageResponseTime: 250,
        satisfactionRate: 92,
        topFeatures: [
        { feature: "Content Recommendations", usage: 4532 },
        { feature: "Automated Grading", usage: 3215 },
        { feature: "Chatbot Support", usage: 2876 }]

      }
    };
  }
  return baseAIData;
};
// Generate AI model performance metrics
export const generateAIModelMetrics = () => {
  return {
    models: [
    {
      name: "Content Recommendation Engine",
      version: "2.3.1",
      accuracy: 92.5,
      latency: 45,
      requests: 5432,
      lastUpdated: "2024-01-15"
    },
    {
      name: "Automated Feedback System",
      version: "1.8.0",
      accuracy: 89.3,
      latency: 120,
      requests: 3215,
      lastUpdated: "2024-01-10"
    },
    {
      name: "Learning Path Optimizer",
      version: "3.0.0",
      accuracy: 94.7,
      latency: 85,
      requests: 2876,
      lastUpdated: "2024-01-20"
    }],

    overall: {
      uptime: 99.97,
      averageAccuracy: 92.2,
      averageLatency: 83.3,
      totalRequests: 15432
    }
  };
};
// Generate AI training history
export const generateAITrainingHistory = () => {
  return [
  {
    id: 1,
    model: "Content Recommendation Engine",
    version: "2.3.1",
    startDate: "2024-01-10",
    endDate: "2024-01-12",
    datasetSize: 125000,
    accuracy: 92.5,
    status: "completed"
  },
  {
    id: 2,
    model: "Automated Feedback System",
    version: "1.8.0",
    startDate: "2024-01-05",
    endDate: "2024-01-07",
    datasetSize: 85000,
    accuracy: 89.3,
    status: "completed"
  },
  {
    id: 3,
    model: "Chatbot NLU",
    version: "4.1.0",
    startDate: "2024-01-20",
    endDate: null,
    datasetSize: 200000,
    accuracy: null,
    status: "in_progress",
    progress: 67
  }];

};
// Generate AI configuration options
export const generateAIConfigOptions = () => {
  return {
    features: {
      recommendations: {
        enabled: true,
        updateFrequency: "daily",
        minConfidence: 0.75,
        maxResults: 10
      },
      chatbot: {
        enabled: true,
        availableHours: "24/7",
        maxTokens: 2048,
        temperature: 0.7
      },
      automatedGrading: {
        enabled: true,
        subjects: ["programming", "mathematics"],
        requireReview: true,
        minConfidence: 0.85
      },
      contentGeneration: {
        enabled: true,
        allowedTypes: ["summaries", "quizzes", "flashcards"],
        reviewRequired: false
      }
    },
    privacy: {
      dataRetention: "90_days",
      anonymization: true,
      optOut: false,
      dataSharing: "internal_only"
    },
    limits: {
      requestsPerMinute: 60,
      requestsPerHour: 1000,
      maxTokensPerRequest: 4096,
      maxFileSize: "10MB"
    }
  };
};