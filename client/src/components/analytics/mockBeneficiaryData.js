// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Mock data for beneficiary analytics
 */
// Sample beneficiaries for analytics
export const beneficiaries = [
{
  id: 1,
  name: "John Smith",
  email: "john.smith@example.com",
  program: "Web Development Bootcamp",
  programId: 1,
  progress: 65,
  assessmentScore: 78,
  status: "Active"
},
{
  id: 2,
  name: "Maria Garcia",
  email: "maria.garcia@example.com",
  program: "Digital Marketing Fundamentals",
  programId: 2,
  progress: 92,
  assessmentScore: 86,
  status: "Completed"
},
{
  id: 3,
  name: "David Lee",
  email: "david.lee@example.com",
  program: "Advanced Data Analytics",
  programId: 3,
  progress: 45,
  assessmentScore: 72,
  status: "Active"
},
{
  id: 4,
  name: "Sarah Johnson",
  email: "sarah.johnson@example.com",
  program: "Leadership Development",
  programId: 4,
  progress: 95,
  assessmentScore: 92,
  status: "Completed"
},
{
  id: 5,
  name: "Michael Brown",
  email: "michael.brown@example.com",
  program: "Cloud Computing Certification",
  programId: 5,
  progress: 52,
  assessmentScore: 68,
  status: "Active"
},
{
  id: 6,
  name: "Emily Wilson",
  email: "emily.wilson@example.com",
  program: "UX/UI Design Principles",
  programId: 6,
  progress: 78,
  assessmentScore: 84,
  status: "Active"
},
{
  id: 7,
  name: "James Taylor",
  email: "james.taylor@example.com",
  program: "Financial Literacy",
  programId: 7,
  progress: 33,
  assessmentScore: 65,
  status: "On Leave"
},
{
  id: 8,
  name: "Sofia Martinez",
  email: "sofia.martinez@example.com",
  program: "Web Development Bootcamp",
  programId: 1,
  progress: 48,
  assessmentScore: 75,
  status: "Active"
}];

// Detailed beneficiary analytics data
export const beneficiaryAnalytics = {
  1: { // John Smith
    overview: {
      programCompletion: 65,
      completionTrend: 12,
      attendanceRate: 88,
      attendanceTrend: 3,
      avgAssessmentScore: 78,
      assessmentTrend: 5,
      engagementScore: 4.2,
      engagementTrend: 8
    },
    attendance: {
      overall: 88,
      history: [
      { period: 'Week 1', rate: 100, avgRate: 90 },
      { period: 'Week 2', rate: 100, avgRate: 90 },
      { period: 'Week 3', rate: 75, avgRate: 88 },
      { period: 'Week 4', rate: 100, avgRate: 87 },
      { period: 'Week 5', rate: 75, avgRate: 86 },
      { period: 'Week 6', rate: 100, avgRate: 85 },
      { period: 'Week 7', rate: 75, avgRate: 84 },
      { period: 'Week 8', rate: 100, avgRate: 83 }],

      details: {
        onTime: 90,
        late: 6,
        absences: 4
      }
    },
    progression: {
      timeline: [
      { period: 'Week 1', completion: 10, expected: 8 },
      { period: 'Week 2', completion: 18, expected: 16 },
      { period: 'Week 3', completion: 25, expected: 25 },
      { period: 'Week 4', completion: 32, expected: 33 },
      { period: 'Week 5', completion: 40, expected: 41 },
      { period: 'Week 6', completion: 48, expected: 50 },
      { period: 'Week 7', completion: 56, expected: 58 },
      { period: 'Week 8', completion: 65, expected: 67 }],

      modules: [
      { name: 'HTML/CSS', completion: 90 },
      { name: 'JavaScript Basics', completion: 85 },
      { name: 'Advanced JS', completion: 70 },
      { name: 'React', completion: 50 },
      { name: 'Backend', completion: 30 },
      { name: 'Database', completion: 25 }]

    },
    skillsAssessment: {
      overall: 78,
      skills: [
      { name: 'HTML', initial: 25, current: 85, target: 90 },
      { name: 'CSS', initial: 30, current: 80, target: 90 },
      { name: 'JavaScript', initial: 20, current: 75, target: 85 },
      { name: 'React', initial: 5, current: 65, target: 80 },
      { name: 'Node.js', initial: 0, current: 45, target: 75 },
      { name: 'Git', initial: 15, current: 70, target: 80 }],

      strengths: [
      'Strong grasp of front-end fundamentals',
      'Quick problem-solving abilities',
      'Excellent design implementation'],

      areasForImprovement: [
      'Backend concepts need more focus',
      'Database design principles',
      'Testing and deployment workflows']

    },
    sessionEngagement: {
      overall: 4.2,
      byType: {
        'Lecture': 4.0,
        'Workshop': 4.5,
        'Project Work': 4.7,
        'Assessment': 3.8,
        'One-on-One': 4.3
      },
      participation: {
        questionAsking: 4.2,
        discussionContribution: 3.8,
        teamCollaboration: 4.5,
        problemSolving: 4.3
      }
    },
    outcomes: {
      projectCompletion: 8,
      certifications: 2,
      skillsProficiency: 78,
      jobReadiness: 65
    },
    trainers: [
    {
      id: 101,
      name: 'Sarah Johnson',
      email: 'sarah.j@bdctrainer.com',
      role: 'Lead Instructor',
      sessionsCount: 24,
      lastSession: '2023-06-10',
      rating: 4.8
    },
    {
      id: 102,
      name: 'David Chen',
      email: 'david.c@bdctrainer.com',
      role: 'Technical Mentor',
      sessionsCount: 12,
      lastSession: '2023-06-12',
      rating: 4.6
    },
    {
      id: 103,
      name: 'Lisa Taylor',
      email: 'lisa.t@bdctrainer.com',
      role: 'Career Coach',
      sessionsCount: 4,
      lastSession: '2023-05-30',
      rating: 4.5
    }],

    milestones: [
    {
      title: 'Program Onboarding',
      description: 'Completed orientation and initial skills assessment',
      status: 'completed',
      date: '2023-04-15',
      achievements: [
      'Completed baseline skills assessment',
      'Set up development environment',
      'Established learning goals']

    },
    {
      title: 'Front-end Fundamentals',
      description: 'HTML, CSS, and JavaScript basics',
      status: 'completed',
      date: '2023-05-10',
      achievements: [
      'Built responsive landing page',
      'Implemented interactive JavaScript components',
      'Scored 85% on front-end assessment']

    },
    {
      title: 'Advanced JavaScript',
      description: 'Modern JS features and frameworks',
      status: 'completed',
      date: '2023-05-28',
      achievements: [
      'Implemented async/await patterns',
      'Built data visualization components',
      'Created RESTful API client']

    },
    {
      title: 'React Fundamentals',
      description: 'Component-based UI development',
      status: 'in_progress',
      date: '2023-06-25',
      achievements: [
      'Created functional and class components',
      'Implemented state management']

    },
    {
      title: 'Backend Development',
      description: 'Server-side programming and APIs',
      status: 'upcoming',
      date: '2023-07-20'
    },
    {
      title: 'Database Integration',
      description: 'SQL, NoSQL, and ORM fundamentals',
      status: 'upcoming',
      date: '2023-08-10'
    },
    {
      title: 'Project Deployment',
      description: 'CI/CD pipelines and cloud hosting',
      status: 'upcoming',
      date: '2023-08-25'
    }],

    actionPlan: {
      objectives: [
      'Strengthen React skills through additional exercises and mini-projects',
      'Begin backend study ahead of module start date',
      'Improve pair programming and code review practices',
      'Develop portfolio project with both front-end and back-end elements'],

      shortTermGoals: [
      'Complete React module with 80% or higher assessment score',
      'Contribute to at least 3 group project components',
      'Attend 2 industry meetups or webinars'],

      longTermGoals: [
      'Achieve 85% overall program completion rate',
      'Develop full-stack portfolio with 3+ projects',
      'Pass final technical assessment with 80%+ score',
      'Prepare for junior developer interviews'],

      recommendations: [
      'Additional focus on React hooks and context API',
      'Explore TypeScript fundamentals alongside JavaScript',
      'Participate in code review sessions to improve code quality',
      'Consider AWS cloud practitioner certification after program'],

      nextReview: 'July 1, 2023'
    }
  },
  2: { // Maria Garcia
    overview: {
      programCompletion: 92,
      completionTrend: 8,
      attendanceRate: 95,
      attendanceTrend: 2,
      avgAssessmentScore: 86,
      assessmentTrend: 4,
      engagementScore: 4.7,
      engagementTrend: 5
    },
    attendance: {
      overall: 95,
      history: [
      { period: 'Week 1', rate: 100, avgRate: 90 },
      { period: 'Week 2', rate: 100, avgRate: 90 },
      { period: 'Week 3', rate: 100, avgRate: 88 },
      { period: 'Week 4', rate: 75, avgRate: 87 },
      { period: 'Week 5', rate: 100, avgRate: 86 },
      { period: 'Week 6', rate: 100, avgRate: 85 },
      { period: 'Week 7', rate: 100, avgRate: 84 },
      { period: 'Week 8', rate: 100, avgRate: 83 }],

      details: {
        onTime: 95,
        late: 5,
        absences: 0
      }
    },
    progression: {
      timeline: [
      { period: 'Week 1', completion: 15, expected: 12 },
      { period: 'Week 2', completion: 28, expected: 25 },
      { period: 'Week 3', completion: 42, expected: 38 },
      { period: 'Week 4', completion: 55, expected: 50 },
      { period: 'Week 5', completion: 68, expected: 62 },
      { period: 'Week 6', completion: 78, expected: 75 },
      { period: 'Week 7', completion: 88, expected: 88 },
      { period: 'Week 8', completion: 92, expected: 100 }],

      modules: [
      { name: 'Marketing Foundations', completion: 100 },
      { name: 'SEO', completion: 95 },
      { name: 'Content Marketing', completion: 100 },
      { name: 'Social Media', completion: 90 },
      { name: 'Analytics', completion: 85 },
      { name: 'Campaign Management', completion: 80 }]

    },
    skillsAssessment: {
      overall: 86,
      skills: [
      { name: 'SEO', initial: 20, current: 90, target: 85 },
      { name: 'Content Creation', initial: 40, current: 95, target: 90 },
      { name: 'Social Media', initial: 60, current: 95, target: 90 },
      { name: 'Analytics', initial: 15, current: 85, target: 80 },
      { name: 'PPC', initial: 5, current: 75, target: 80 },
      { name: 'CRM', initial: 10, current: 70, target: 75 }],

      strengths: [
      'Exceptional content creation skills',
      'Strong SEO knowledge',
      'Excellent social media strategy development'],

      areasForImprovement: [
      'PPC campaign optimization',
      'Marketing automation workflows',
      'Advanced analytics interpretation']

    },
    sessionEngagement: {
      overall: 4.7,
      byType: {
        'Lecture': 4.5,
        'Workshop': 4.8,
        'Project Work': 4.9,
        'Assessment': 4.6,
        'One-on-One': 4.7
      },
      participation: {
        questionAsking: 4.6,
        discussionContribution: 4.8,
        teamCollaboration: 4.7,
        problemSolving: 4.5
      }
    },
    outcomes: {
      projectCompletion: 12,
      certifications: 3,
      skillsProficiency: 86,
      jobReadiness: 90
    },
    trainers: [
    {
      id: 105,
      name: 'Emma Wilson',
      email: 'emma.w@bdctrainer.com',
      role: 'Marketing Lead',
      sessionsCount: 32,
      lastSession: '2023-06-14',
      rating: 4.9
    },
    {
      id: 106,
      name: 'Thomas Grant',
      email: 'thomas.g@bdctrainer.com',
      role: 'Social Media Specialist',
      sessionsCount: 18,
      lastSession: '2023-06-10',
      rating: 4.7
    }],

    milestones: [
    {
      title: 'Program Onboarding',
      description: 'Completed orientation and initial skills assessment',
      status: 'completed',
      date: '2023-03-05',
      achievements: [
      'Completed baseline marketing skills assessment',
      'Set up analytics tools and accounts',
      'Established learning goals']

    },
    {
      title: 'Digital Marketing Foundations',
      description: 'Core concepts and strategies',
      status: 'completed',
      date: '2023-03-20',
      achievements: [
      'Created comprehensive marketing strategy',
      'Completed customer persona development',
      'Scored 92% on foundations assessment']

    },
    {
      title: 'SEO & Content Marketing',
      description: 'Search optimization and content creation',
      status: 'completed',
      date: '2023-04-10',
      achievements: [
      'Performed full SEO audit of sample site',
      'Created content calendar and strategy',
      'Wrote 5 high-quality blog posts with SEO optimization']

    },
    {
      title: 'Social Media Marketing',
      description: 'Platform strategies and community management',
      status: 'completed',
      date: '2023-04-30',
      achievements: [
      'Developed cross-platform social strategy',
      'Created and scheduled content for multiple platforms',
      'Implemented engagement and growth tactics']

    },
    {
      title: 'Analytics & Reporting',
      description: 'Data-driven marketing decisions',
      status: 'completed',
      date: '2023-05-20',
      achievements: [
      'Set up comprehensive analytics dashboard',
      'Created performance reports with insights',
      'Implemented A/B testing methodology']

    },
    {
      title: 'Campaign Management',
      description: 'End-to-end campaign execution',
      status: 'completed',
      date: '2023-06-10',
      achievements: [
      'Designed multi-channel marketing campaign',
      'Implemented and monitored campaign performance',
      'Optimized based on real-time results']

    },
    {
      title: 'Final Project & Certification',
      description: 'Comprehensive marketing strategy implementation',
      status: 'in_progress',
      date: '2023-06-25',
      achievements: [
      'Developed client marketing strategy',
      'Presented campaign results and recommendations']

    }],

    actionPlan: {
      objectives: [
      'Complete final project with client presentation',
      'Finalize digital marketing portfolio',
      'Prepare for professional certification exams',
      'Develop specialized PPC campaign skills'],

      shortTermGoals: [
      'Submit final project by June 25',
      'Create portfolio website with case studies',
      'Register for Google Ads certification'],

      longTermGoals: [
      'Obtain 3 professional marketing certifications',
      'Develop specialized skills in marketing automation',
      'Prepare for digital marketing strategist roles'],

      recommendations: [
      'Consider Facebook Blueprint certification',
      'Develop deeper skills in marketing automation tools',
      'Join digital marketing professional networks',
      'Consider pursuing Google Analytics certification'],

      nextReview: 'June 20, 2023'
    }
  },
  3: { // David Lee
    overview: {
      programCompletion: 45,
      completionTrend: -2,
      attendanceRate: 75,
      attendanceTrend: -5,
      avgAssessmentScore: 72,
      assessmentTrend: 3,
      engagementScore: 3.8,
      engagementTrend: -4
    },
    attendance: {
      overall: 75,
      history: [
      { period: 'Week 1', rate: 100, avgRate: 90 },
      { period: 'Week 2', rate: 100, avgRate: 90 },
      { period: 'Week 3', rate: 75, avgRate: 88 },
      { period: 'Week 4', rate: 75, avgRate: 87 },
      { period: 'Week 5', rate: 50, avgRate: 86 },
      { period: 'Week 6', rate: 75, avgRate: 85 },
      { period: 'Week 7', rate: 50, avgRate: 84 },
      { period: 'Week 8', rate: 75, avgRate: 83 }],

      details: {
        onTime: 70,
        late: 20,
        absences: 10
      }
    },
    progression: {
      timeline: [
      { period: 'Week 1', completion: 8, expected: 6 },
      { period: 'Week 2', completion: 15, expected: 12 },
      { period: 'Week 3', completion: 20, expected: 19 },
      { period: 'Week 4', completion: 25, expected: 25 },
      { period: 'Week 5', completion: 30, expected: 31 },
      { period: 'Week 6', completion: 35, expected: 38 },
      { period: 'Week 7', completion: 39, expected: 44 },
      { period: 'Week 8', completion: 45, expected: 50 }],

      modules: [
      { name: 'Python Basics', completion: 90 },
      { name: 'Data Structures', completion: 85 },
      { name: 'SQL Fundamentals', completion: 75 },
      { name: 'Data Visualization', completion: 60 },
      { name: 'Statistical Analysis', completion: 35 },
      { name: 'Machine Learning', completion: 20 }]

    },
    skillsAssessment: {
      overall: 72,
      skills: [
      { name: 'Python', initial: 35, current: 85, target: 90 },
      { name: 'SQL', initial: 25, current: 75, target: 85 },
      { name: 'Data Analysis', initial: 30, current: 70, target: 85 },
      { name: 'Data Viz', initial: 20, current: 65, target: 80 },
      { name: 'Statistics', initial: 15, current: 50, target: 80 },
      { name: 'ML Basics', initial: 5, current: 35, target: 75 }],

      strengths: [
      'Strong programming fundamentals',
      'Good database query skills',
      'Solid problem decomposition ability'],

      areasForImprovement: [
      'Statistical analysis concepts',
      'Machine learning fundamentals',
      'Project time management',
      'Consistent attendance and engagement']

    },
    sessionEngagement: {
      overall: 3.8,
      byType: {
        'Lecture': 3.5,
        'Workshop': 4.0,
        'Project Work': 4.2,
        'Assessment': 3.6,
        'One-on-One': 3.9
      },
      participation: {
        questionAsking: 3.2,
        discussionContribution: 3.5,
        teamCollaboration: 4.0,
        problemSolving: 4.2
      }
    },
    outcomes: {
      projectCompletion: 5,
      certifications: 1,
      skillsProficiency: 72,
      jobReadiness: 60
    },
    trainers: [
    {
      id: 108,
      name: 'Robert Kim',
      email: 'robert.k@bdctrainer.com',
      role: 'Data Science Lead',
      sessionsCount: 28,
      lastSession: '2023-06-08',
      rating: 4.5
    },
    {
      id: 109,
      name: 'Anita Sharma',
      email: 'anita.s@bdctrainer.com',
      role: 'ML Engineer',
      sessionsCount: 12,
      lastSession: '2023-06-05',
      rating: 4.2
    }],

    milestones: [
    {
      title: 'Program Onboarding',
      description: 'Completed orientation and initial skills assessment',
      status: 'completed',
      date: '2023-04-10',
      achievements: [
      'Completed baseline technical skills assessment',
      'Set up data science environment and tools',
      'Established learning goals']

    },
    {
      title: 'Python Fundamentals',
      description: 'Core programming concepts',
      status: 'completed',
      date: '2023-04-30',
      achievements: [
      'Mastered Python syntax and data structures',
      'Completed programming challenges',
      'Built data processing utilities']

    },
    {
      title: 'Data Management',
      description: 'SQL and database concepts',
      status: 'completed',
      date: '2023-05-20',
      achievements: [
      'Designed database schemas',
      'Wrote complex SQL queries',
      'Implemented ETL processes']

    },
    {
      title: 'Data Visualization',
      description: 'Creating impactful data visualizations',
      status: 'in_progress',
      date: '2023-06-10',
      achievements: [
      'Created static visualizations with matplotlib',
      'Built interactive dashboards']

    },
    {
      title: 'Statistical Analysis',
      description: 'Statistical methods for data science',
      status: 'upcoming',
      date: '2023-07-01'
    },
    {
      title: 'Machine Learning',
      description: 'ML algorithms and applications',
      status: 'upcoming',
      date: '2023-07-20'
    },
    {
      title: 'Final Project',
      description: 'End-to-end data science project',
      status: 'upcoming',
      date: '2023-08-10'
    }],

    actionPlan: {
      objectives: [
      'Improve attendance and engagement in sessions',
      'Catch up on module completion targets',
      'Strengthen statistical analysis foundations',
      'Build consistent study habits'],

      shortTermGoals: [
      'Achieve 80% attendance for the next month',
      'Complete data visualization module by June 25',
      'Start statistics preparation ahead of module',
      'Attend weekly office hours for personalized support'],

      longTermGoals: [
      'Get back on track with program completion targets',
      'Improve assessment scores to 80%+ average',
      'Complete at least 2 portfolio-worthy projects',
      'Prepare for entry-level data analyst roles'],

      recommendations: [
      'Schedule bi-weekly check-ins with program mentor',
      'Join study group for mutual accountability',
      'Consider reduced work hours if possible to focus on program',
      'Utilize additional online resources for statistics fundamentals'],

      nextReview: 'June 25, 2023'
    }
  }
  // You could add more detailed analytics for other beneficiaries as needed
};
// Mock API function to get all beneficiaries
export const getBeneficiariesList = () => {
  return Promise.resolve(beneficiaries);
};
// Mock API function to get beneficiary analytics by ID
export const getBeneficiaryAnalytics = (id, dateRange = 'last30days') => {
  const analytics = beneficiaryAnalytics[id];
  if (!analytics) {
    return Promise.reject(new Error('Beneficiary analytics not found'));
  }
  // In a real scenario, you might filter data based on dateRange
  // For mock data, we'll just return the full analytics
  return Promise.resolve(analytics);
};
// Mock API function to export beneficiary analytics
export const exportBeneficiaryAnalytics = (id, format, dateRange = 'last30days') => {
  // In a real scenario, this would generate a file for download
  // For mock data, we'll just return a successful response
  return Promise.resolve({
    success: true,
    message: `Beneficiary analytics for beneficiary ${id} exported as ${format}`
  });
};