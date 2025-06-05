// Mock Programs Data
export const generateProgramsData = (userRole) => {
  const basePrograms = [
    {
      id: 1,
      title: "Full Stack Web Development",
      description: "Complete web development course covering frontend, backend, and deployment",
      duration: "6 months",
      status: "active",
      startDate: "2024-01-15",
      endDate: "2024-07-15",
      enrolled: 45,
      capacity: 50,
      level: "Intermediate",
      categories: ["Web Development", "Programming"],
      instructor: {
        id: 1,
        name: "John Smith",
        avatar: "/api/placeholder/32/32",
        expertise: ["JavaScript", "React", "Node.js"]
      },
      modules: [
        {
          id: 1,
          title: "HTML & CSS Fundamentals",
          duration: "2 weeks",
          status: "completed",
          topics: ["HTML5", "CSS3", "Responsive Design", "Flexbox", "Grid"]
        },
        {
          id: 2,
          title: "JavaScript Essentials",
          duration: "3 weeks",
          status: "completed",
          topics: ["Variables", "Functions", "Objects", "Arrays", "DOM"]
        },
        {
          id: 3,
          title: "React Development",
          duration: "4 weeks",
          status: "in_progress",
          topics: ["Components", "State", "Props", "Hooks", "Router"]
        },
        {
          id: 4,
          title: "Backend with Node.js",
          duration: "4 weeks",
          status: "upcoming",
          topics: ["Express", "APIs", "MongoDB", "Authentication"]
        },
        {
          id: 5,
          title: "Deployment & DevOps",
          duration: "2 weeks",
          status: "upcoming",
          topics: ["Docker", "CI/CD", "Cloud Deployment", "Monitoring"]
        }
      ],
      skills: ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB"],
      prerequisites: ["Basic programming knowledge", "Understanding of web technologies"],
      outcomes: [
        "Build full-stack web applications",
        "Deploy applications to cloud platforms",
        "Work with modern development tools"
      ],
      price: 2500,
      rating: 4.7,
      reviews: 234
    },
    {
      id: 2,
      title: "Data Science with Python",
      description: "Comprehensive data science program from basics to advanced machine learning",
      duration: "4 months",
      status: "active",
      startDate: "2024-02-01",
      endDate: "2024-06-01",
      enrolled: 38,
      capacity: 40,
      level: "Advanced",
      categories: ["Data Science", "Python", "Machine Learning"],
      instructor: {
        id: 2,
        name: "Dr. Emily Chen",
        avatar: "/api/placeholder/32/32",
        expertise: ["Python", "Machine Learning", "Statistics"]
      },
      modules: [
        {
          id: 1,
          title: "Python Fundamentals",
          duration: "2 weeks",
          status: "completed",
          topics: ["Syntax", "Data Types", "Functions", "OOP"]
        },
        {
          id: 2,
          title: "Data Analysis with Pandas",
          duration: "3 weeks",
          status: "in_progress",
          topics: ["DataFrames", "Data Cleaning", "Merging", "Grouping"]
        },
        {
          id: 3,
          title: "Statistical Analysis",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["Descriptive Stats", "Hypothesis Testing", "Regression"]
        },
        {
          id: 4,
          title: "Machine Learning",
          duration: "4 weeks",
          status: "upcoming",
          topics: ["Supervised Learning", "Unsupervised Learning", "Deep Learning"]
        },
        {
          id: 5,
          title: "Real World Projects",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["Project Planning", "Implementation", "Deployment"]
        }
      ],
      skills: ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
      prerequisites: ["Basic Python knowledge", "Mathematics fundamentals"],
      outcomes: [
        "Analyze complex datasets",
        "Build machine learning models",
        "Create data visualizations"
      ],
      price: 3000,
      rating: 4.8,
      reviews: 189
    },
    {
      id: 3,
      title: "Mobile App Development",
      description: "Build native and cross-platform mobile applications",
      duration: "5 months",
      status: "active",
      startDate: "2024-01-01",
      endDate: "2024-06-01",
      enrolled: 32,
      capacity: 35,
      level: "Intermediate",
      categories: ["Mobile Development", "React Native", "Flutter"],
      instructor: {
        id: 3,
        name: "Sarah Johnson",
        avatar: "/api/placeholder/32/32",
        expertise: ["React Native", "Flutter", "Swift"]
      },
      modules: [
        {
          id: 1,
          title: "Mobile Development Basics",
          duration: "2 weeks",
          status: "completed",
          topics: ["Mobile UX", "Platform Guidelines", "Development Tools"]
        },
        {
          id: 2,
          title: "React Native",
          duration: "5 weeks",
          status: "in_progress",
          topics: ["Components", "Navigation", "State Management", "APIs"]
        },
        {
          id: 3,
          title: "Flutter Development",
          duration: "5 weeks",
          status: "upcoming",
          topics: ["Dart", "Widgets", "State", "Animations"]
        },
        {
          id: 4,
          title: "App Publishing",
          duration: "2 weeks",
          status: "upcoming",
          topics: ["App Store", "Google Play", "Testing", "Marketing"]
        }
      ],
      skills: ["React Native", "Flutter", "JavaScript", "Dart"],
      prerequisites: ["JavaScript knowledge", "Basic React understanding"],
      outcomes: [
        "Create cross-platform mobile apps",
        "Publish apps to app stores",
        "Implement mobile UI/UX best practices"
      ],
      price: 2800,
      rating: 4.6,
      reviews: 156
    },
    {
      id: 4,
      title: "UI/UX Design Bootcamp",
      description: "Master user interface and experience design principles",
      duration: "3 months",
      status: "active",
      startDate: "2024-03-01",
      endDate: "2024-06-01",
      enrolled: 28,
      capacity: 30,
      level: "Beginner",
      categories: ["Design", "UI/UX", "Product Design"],
      instructor: {
        id: 4,
        name: "Lisa Brown",
        avatar: "/api/placeholder/32/32",
        expertise: ["UI Design", "UX Research", "Prototyping"]
      },
      modules: [
        {
          id: 1,
          title: "Design Fundamentals",
          duration: "2 weeks",
          status: "in_progress",
          topics: ["Color Theory", "Typography", "Layout", "Composition"]
        },
        {
          id: 2,
          title: "UX Research",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["User Research", "Personas", "Journey Mapping", "Testing"]
        },
        {
          id: 3,
          title: "UI Design",
          duration: "4 weeks",
          status: "upcoming",
          topics: ["Figma", "Sketch", "Components", "Design Systems"]
        },
        {
          id: 4,
          title: "Prototyping",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["Interactive Prototypes", "Animation", "Handoff"]
        }
      ],
      skills: ["Figma", "Sketch", "Adobe XD", "Prototyping", "User Research"],
      prerequisites: ["Basic computer skills", "Interest in design"],
      outcomes: [
        "Design user-centered interfaces",
        "Conduct UX research",
        "Create interactive prototypes"
      ],
      price: 2200,
      rating: 4.7,
      reviews: 201
    },
    {
      id: 5,
      title: "DevOps Engineering",
      description: "Learn modern DevOps practices and tools",
      duration: "4 months",
      status: "upcoming",
      startDate: "2024-04-01",
      endDate: "2024-08-01",
      enrolled: 15,
      capacity: 40,
      level: "Advanced",
      categories: ["DevOps", "Cloud", "Infrastructure"],
      instructor: {
        id: 5,
        name: "Mike Wilson",
        avatar: "/api/placeholder/32/32",
        expertise: ["Docker", "Kubernetes", "AWS", "CI/CD"]
      },
      modules: [
        {
          id: 1,
          title: "Linux & Shell Scripting",
          duration: "2 weeks",
          status: "upcoming",
          topics: ["Linux Commands", "Bash Scripting", "System Administration"]
        },
        {
          id: 2,
          title: "Containerization",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["Docker", "Container Orchestration", "Microservices"]
        },
        {
          id: 3,
          title: "Kubernetes",
          duration: "4 weeks",
          status: "upcoming",
          topics: ["Clusters", "Deployments", "Services", "Scaling"]
        },
        {
          id: 4,
          title: "CI/CD Pipelines",
          duration: "3 weeks",
          status: "upcoming",
          topics: ["Jenkins", "GitLab CI", "GitHub Actions", "ArgoCD"]
        },
        {
          id: 5,
          title: "Cloud Platforms",
          duration: "4 weeks",
          status: "upcoming",
          topics: ["AWS", "Azure", "GCP", "Terraform"]
        }
      ],
      skills: ["Docker", "Kubernetes", "CI/CD", "Cloud Platforms", "Infrastructure as Code"],
      prerequisites: ["Linux knowledge", "Basic programming", "Networking basics"],
      outcomes: [
        "Design scalable infrastructure",
        "Implement CI/CD pipelines",
        "Manage cloud resources"
      ],
      price: 3500,
      rating: 4.9,
      reviews: 98
    }
  ];
  // Filter programs based on user role
  if (userRole === "student") {
    // Students see their enrolled programs and available programs
    return {
      enrolledPrograms: basePrograms.filter(p => p.enrolled > 30),
      availablePrograms: basePrograms.filter(p => p.enrolled < p.capacity),
      recommendedPrograms: basePrograms.slice(0, 3),
      recentlyViewed: basePrograms.slice(2, 4)
    };
  } else if (userRole === "trainer") {
    // Trainers see programs they teach
    return {
      myPrograms: basePrograms.filter(p => p.instructor.id <= 3),
      allPrograms: basePrograms,
      upcomingPrograms: basePrograms.filter(p => p.status === "upcoming"),
      programRequests: generateProgramRequests()
    };
  } else {
    // Admin and tenant_admin see all programs with additional metrics
    return {
      allPrograms: basePrograms,
      programStats: generateProgramStats(),
      programsByCategory: groupProgramsByCategory(basePrograms),
      performanceMetrics: generateProgramPerformance()
    };
  }
};
// Generate program requests for trainers
export const generateProgramRequests = () => {
  return [
    {
      id: 1,
      title: "Advanced React Patterns",
      requestedBy: "Tech Department",
      priority: "high",
      estimatedStudents: 25,
      preferredStart: "2024-05-01",
      status: "pending"
    },
    {
      id: 2,
      title: "Cybersecurity Fundamentals",
      requestedBy: "IT Security Team",
      priority: "medium",
      estimatedStudents: 30,
      preferredStart: "2024-06-01",
      status: "approved"
    }
  ];
};
// Generate program statistics
export const generateProgramStats = () => {
  return {
    totalPrograms: 45,
    activePrograms: 38,
    completedPrograms: 125,
    totalEnrollments: 1234,
    averageCompletion: 78,
    revenueGenerated: 458900,
    topCategories: [
      { category: "Web Development", count: 12, revenue: 125000 },
      { category: "Data Science", count: 8, revenue: 98000 },
      { category: "Mobile Development", count: 6, revenue: 75000 }
    ]
  };
};
// Group programs by category
export const groupProgramsByCategory = (programs) => {
  const grouped = {};
  programs.forEach(program => {
    program.categories.forEach(category => {
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(program);
    });
  });
  return grouped;
};
// Generate program performance metrics
export const generateProgramPerformance = () => {
  return {
    completionRates: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [{
        label: "Completion Rate (%)",
        data: [72, 75, 78, 80, 82, 85],
        borderColor: "rgb(34, 197, 94)",
        tension: 0.4
      }]
    },
    enrollmentTrends: {
      labels: ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "Q1 2024"],
      datasets: [{
        label: "New Enrollments",
        data: [234, 289, 312, 345, 389],
        backgroundColor: "rgba(59, 130, 246, 0.8)"
      }]
    },
    satisfactionScores: {
      labels: ["Content", "Instruction", "Support", "Platform", "Value"],
      datasets: [{
        label: "Satisfaction Score",
        data: [4.5, 4.7, 4.3, 4.6, 4.4],
        backgroundColor: "rgba(168, 85, 247, 0.8)"
      }]
    }
  };
};
// Generate program resources
export const generateProgramResources = (programId) => {
  return {
    videos: [
      { id: 1, title: "Introduction to the Course", duration: "15:30", views: 234 },
      { id: 2, title: "Setting Up Development Environment", duration: "22:45", views: 189 },
      { id: 3, title: "First Project Walkthrough", duration: "45:20", views: 156 }
    ],
    documents: [
      { id: 1, title: "Course Syllabus", type: "pdf", size: "2.3 MB", downloads: 89 },
      { id: 2, title: "Resources and References", type: "pdf", size: "1.8 MB", downloads: 67 },
      { id: 3, title: "Project Guidelines", type: "docx", size: "856 KB", downloads: 123 }
    ],
    assignments: [
      { id: 1, title: "Module 1 Assignment", dueDate: "2024-02-15", submissions: 32 },
      { id: 2, title: "Mid-term Project", dueDate: "2024-03-01", submissions: 28 },
      { id: 3, title: "Final Project", dueDate: "2024-04-15", submissions: 0 }
    ],
    quizzes: [
      { id: 1, title: "Module 1 Quiz", questions: 20, attempts: 45, avgScore: 85 },
      { id: 2, title: "Module 2 Quiz", questions: 25, attempts: 38, avgScore: 78 }
    ]
  };
};
// Generate program schedule
export const generateProgramSchedule = (programId) => {
  const schedule = [];
  const startDate = new Date('2024-01-15');
  for (let week = 0; week < 24; week++) {
    const weekStart = new Date(startDate);
    weekStart.setDate(startDate.getDate() + (week * 7));
    schedule.push({
      week: week + 1,
      startDate: weekStart.toISOString().split('T')[0],
      module: Math.floor(week / 5) + 1,
      topics: [
        `Topic ${week * 3 + 1}`,
        `Topic ${week * 3 + 2}`,
        `Topic ${week * 3 + 3}`
      ],
      assignments: week % 3 === 2 ? [`Assignment ${Math.floor(week / 3) + 1}`] : [],
      liveSession: week % 2 === 0 ? {
        date: new Date(weekStart.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        duration: "2 hours",
        topic: `Live Q&A Session ${Math.floor(week / 2) + 1}`
      } : null
    });
  }
  return schedule;
};