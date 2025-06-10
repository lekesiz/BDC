// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Mock data for program analytics
 */
// Sample programs for analytics
export const programs = [
{
  id: 1,
  name: "Web Development Bootcamp",
  description: "Intensive training program for full-stack web development skills",
  category: "Technical Skills",
  duration: "12 weeks",
  startDate: "2023-01-15",
  endDate: "2023-04-10",
  enrolledCount: 48,
  completionRate: 87,
  status: "Completed"
},
{
  id: 2,
  name: "Digital Marketing Fundamentals",
  description: "Essential digital marketing skills for beginners",
  category: "Marketing",
  duration: "8 weeks",
  startDate: "2023-02-01",
  endDate: "2023-03-29",
  enrolledCount: 35,
  completionRate: 92,
  status: "Completed"
},
{
  id: 3,
  name: "Advanced Data Analytics",
  description: "Data analysis and machine learning for business intelligence",
  category: "Technical Skills",
  duration: "16 weeks",
  startDate: "2023-03-10",
  endDate: "2023-06-30",
  enrolledCount: 28,
  completionRate: 78,
  status: "Active"
},
{
  id: 4,
  name: "Leadership Development",
  description: "Developing key leadership skills for career advancement",
  category: "Soft Skills",
  duration: "6 weeks",
  startDate: "2023-04-05",
  endDate: "2023-05-17",
  enrolledCount: 42,
  completionRate: 95,
  status: "Completed"
},
{
  id: 5,
  name: "Cloud Computing Certification",
  description: "AWS and Azure certification preparation",
  category: "Technical Skills",
  duration: "10 weeks",
  startDate: "2023-05-01",
  endDate: "2023-07-10",
  enrolledCount: 32,
  completionRate: 81,
  status: "Active"
},
{
  id: 6,
  name: "UX/UI Design Principles",
  description: "Human-centered design approaches for digital products",
  category: "Design",
  duration: "8 weeks",
  startDate: "2023-06-15",
  endDate: "2023-08-10",
  enrolledCount: 25,
  completionRate: 88,
  status: "Active"
},
{
  id: 7,
  name: "Financial Literacy",
  description: "Personal and business finance fundamentals",
  category: "Finance",
  duration: "4 weeks",
  startDate: "2023-07-01",
  endDate: "2023-07-29",
  enrolledCount: 50,
  completionRate: 90,
  status: "Active"
},
{
  id: 8,
  name: "Project Management Professional",
  description: "PMP certification preparation course",
  category: "Management",
  duration: "12 weeks",
  startDate: "2023-08-15",
  endDate: "2023-11-07",
  enrolledCount: 20,
  completionRate: 0,
  status: "Upcoming"
}];

// Detailed program analytics data
export const programAnalytics = {
  1: { // Web Development Bootcamp
    overview: {
      totalBeneficiaries: 48,
      beneficiaryGrowth: 12,
      totalSessions: 142,
      sessionGrowth: 8,
      completionRate: 87,
      completionRateGrowth: 5,
      avgSatisfaction: 4.3,
      satisfactionGrowth: 3
    },
    enrollmentTrends: [
    { period: 'Week 1', newEnrollments: 35, totalActive: 35 },
    { period: 'Week 2', newEnrollments: 8, totalActive: 43 },
    { period: 'Week 3', newEnrollments: 5, totalActive: 48 },
    { period: 'Week 4', newEnrollments: 0, totalActive: 48 },
    { period: 'Week 5', newEnrollments: 0, totalActive: 46 },
    { period: 'Week 6', newEnrollments: 0, totalActive: 45 },
    { period: 'Week 7', newEnrollments: 0, totalActive: 44 },
    { period: 'Week 8', newEnrollments: 0, totalActive: 44 },
    { period: 'Week 9', newEnrollments: 0, totalActive: 43 },
    { period: 'Week 10', newEnrollments: 0, totalActive: 43 },
    { period: 'Week 11', newEnrollments: 0, totalActive: 42 },
    { period: 'Week 12', newEnrollments: 0, totalActive: 42 }],

    completionRates: [
    { period: 'Week 2', rate: 95, benchmark: 90 },
    { period: 'Week 4', rate: 92, benchmark: 90 },
    { period: 'Week 6', rate: 90, benchmark: 90 },
    { period: 'Week 8', rate: 88, benchmark: 90 },
    { period: 'Week 10', rate: 88, benchmark: 90 },
    { period: 'Week 12', rate: 87, benchmark: 90 }],

    skillsProgress: [
    { name: 'HTML/CSS', baseline: 25, current: 82, target: 85 },
    { name: 'JavaScript', baseline: 15, current: 75, target: 80 },
    { name: 'React', baseline: 5, current: 68, target: 75 },
    { name: 'Node.js', baseline: 8, current: 70, target: 75 },
    { name: 'Databases', baseline: 10, current: 72, target: 70 },
    { name: 'Git/Version Control', baseline: 20, current: 85, target: 80 }],

    outcomes: {
      employmentRate: 72,
      skillCertificationRate: 88,
      roiScore: 8.5
    },
    satisfactionScores: {
      overall: 4.3,
      curriculum: 4.5,
      instructors: 4.7,
      support: 4.2,
      resources: 3.9,
      history: [
      { period: 'Week 2', score: 4.1, avgAllPrograms: 4.0 },
      { period: 'Week 4', score: 4.2, avgAllPrograms: 4.0 },
      { period: 'Week 6', score: 4.3, avgAllPrograms: 4.1 },
      { period: 'Week 8', score: 4.2, avgAllPrograms: 4.1 },
      { period: 'Week 10', score: 4.4, avgAllPrograms: 4.2 },
      { period: 'Week 12', score: 4.3, avgAllPrograms: 4.2 }]

    },
    sessionDistribution: {
      byType: {
        'Lecture': 45,
        'Workshop': 30,
        'Project Work': 15,
        'Assessment': 5,
        'Mentoring': 5
      },
      byWeek: [10, 12, 12, 11, 13, 12, 11, 13, 12, 13, 11, 12]
    },
    trainers: [
    {
      id: 101,
      name: 'Sarah Johnson',
      role: 'Lead Instructor',
      sessions: 58,
      beneficiaries: 48,
      rating: 4.8,
      status: 'Active'
    },
    {
      id: 102,
      name: 'David Chen',
      role: 'Technical Mentor',
      sessions: 42,
      beneficiaries: 32,
      rating: 4.6,
      status: 'Active'
    },
    {
      id: 103,
      name: 'Michael Rodriguez',
      role: 'Industry Expert',
      sessions: 22,
      beneficiaries: 48,
      rating: 4.3,
      status: 'Active'
    },
    {
      id: 104,
      name: 'Lisa Taylor',
      role: 'Career Coach',
      sessions: 20,
      beneficiaries: 45,
      rating: 4.5,
      status: 'Active'
    }],

    insights: [
    'Student retention was 6% higher than previous cohorts, likely due to the new project-based curriculum.',
    'The job placement rate of 72% exceeds industry average by 15% for similar programs.',
    'React module received lower satisfaction scores, indicating a need for curriculum revision.',
    'Students with prior programming experience showed 22% faster progress in the first 4 weeks.',
    'Project collaboration skills showed significant improvement, increasing 65% from baseline.']

  },
  2: { // Digital Marketing Fundamentals
    overview: {
      totalBeneficiaries: 35,
      beneficiaryGrowth: 8,
      totalSessions: 98,
      sessionGrowth: 5,
      completionRate: 92,
      completionRateGrowth: 7,
      avgSatisfaction: 4.5,
      satisfactionGrowth: 5
    },
    enrollmentTrends: [
    { period: 'Week 1', newEnrollments: 28, totalActive: 28 },
    { period: 'Week 2', newEnrollments: 7, totalActive: 35 },
    { period: 'Week 3', newEnrollments: 0, totalActive: 35 },
    { period: 'Week 4', newEnrollments: 0, totalActive: 35 },
    { period: 'Week 5', newEnrollments: 0, totalActive: 34 },
    { period: 'Week 6', newEnrollments: 0, totalActive: 34 },
    { period: 'Week 7', newEnrollments: 0, totalActive: 33 },
    { period: 'Week 8', newEnrollments: 0, totalActive: 33 }],

    completionRates: [
    { period: 'Week 2', rate: 98, benchmark: 90 },
    { period: 'Week 4', rate: 95, benchmark: 90 },
    { period: 'Week 6', rate: 94, benchmark: 90 },
    { period: 'Week 8', rate: 92, benchmark: 90 }],

    skillsProgress: [
    { name: 'SEO', baseline: 18, current: 85, target: 80 },
    { name: 'Social Media', baseline: 25, current: 90, target: 85 },
    { name: 'Content Marketing', baseline: 20, current: 82, target: 80 },
    { name: 'Analytics', baseline: 10, current: 75, target: 75 },
    { name: 'PPC Campaigns', baseline: 5, current: 70, target: 70 }],

    outcomes: {
      employmentRate: 68,
      skillCertificationRate: 95,
      roiScore: 8.2
    },
    satisfactionScores: {
      overall: 4.5,
      curriculum: 4.6,
      instructors: 4.7,
      support: 4.3,
      resources: 4.4,
      history: [
      { period: 'Week 2', score: 4.3, avgAllPrograms: 4.0 },
      { period: 'Week 4', score: 4.4, avgAllPrograms: 4.0 },
      { period: 'Week 6', score: 4.6, avgAllPrograms: 4.1 },
      { period: 'Week 8', score: 4.5, avgAllPrograms: 4.1 }]

    },
    sessionDistribution: {
      byType: {
        'Lecture': 40,
        'Workshop': 30,
        'Case Study': 20,
        'Assessment': 5,
        'Guest Speaker': 5
      },
      byWeek: [12, 13, 12, 13, 12, 12, 12, 12]
    },
    trainers: [
    {
      id: 105,
      name: 'Emma Wilson',
      role: 'Lead Instructor',
      sessions: 45,
      beneficiaries: 35,
      rating: 4.8,
      status: 'Active'
    },
    {
      id: 106,
      name: 'Thomas Grant',
      role: 'Social Media Specialist',
      sessions: 28,
      beneficiaries: 35,
      rating: 4.5,
      status: 'Active'
    },
    {
      id: 107,
      name: 'Jessica Patel',
      role: 'Content Marketing Expert',
      sessions: 25,
      beneficiaries: 35,
      rating: 4.4,
      status: 'Active'
    }],

    insights: [
    'Social media marketing module was the highest-rated component with a 97% satisfaction rate.',
    'Practical case studies led to 35% higher engagement compared to lecture-only sessions.',
    'Post-program surveys showed 89% of participants actively using new skills in their current roles.',
    'The Google Analytics component showed the steepest learning curve, suggesting a need for additional resources.',
    'Group projects resulted in 3 teams securing actual clients for their portfolio work.']

  },
  3: { // Advanced Data Analytics
    overview: {
      totalBeneficiaries: 28,
      beneficiaryGrowth: -5,
      totalSessions: 135,
      sessionGrowth: 0,
      completionRate: 78,
      completionRateGrowth: -3,
      avgSatisfaction: 4.1,
      satisfactionGrowth: -1
    },
    enrollmentTrends: [
    { period: 'Week 1', newEnrollments: 25, totalActive: 25 },
    { period: 'Week 2', newEnrollments: 3, totalActive: 28 },
    { period: 'Week 3', newEnrollments: 0, totalActive: 28 },
    { period: 'Week 4', newEnrollments: 0, totalActive: 27 },
    { period: 'Week 5', newEnrollments: 0, totalActive: 26 },
    { period: 'Week 6', newEnrollments: 0, totalActive: 26 },
    { period: 'Week 7', newEnrollments: 0, totalActive: 25 },
    { period: 'Week 8', newEnrollments: 0, totalActive: 24 },
    { period: 'Week 9', newEnrollments: 0, totalActive: 24 },
    { period: 'Week 10', newEnrollments: 0, totalActive: 23 },
    { period: 'Week 11', newEnrollments: 0, totalActive: 22 },
    { period: 'Week 12', newEnrollments: 0, totalActive: 22 },
    { period: 'Week 13', newEnrollments: 0, totalActive: 22 },
    { period: 'Week 14', newEnrollments: 0, totalActive: 22 },
    { period: 'Week 15', newEnrollments: 0, totalActive: 22 },
    { period: 'Week 16', newEnrollments: 0, totalActive: 22 }],

    completionRates: [
    { period: 'Week 4', rate: 96, benchmark: 90 },
    { period: 'Week 8', rate: 86, benchmark: 90 },
    { period: 'Week 12', rate: 80, benchmark: 90 },
    { period: 'Week 16', rate: 78, benchmark: 90 }],

    skillsProgress: [
    { name: 'Python', baseline: 30, current: 85, target: 90 },
    { name: 'SQL', baseline: 25, current: 80, target: 85 },
    { name: 'Data Visualization', baseline: 20, current: 75, target: 80 },
    { name: 'Statistical Analysis', baseline: 15, current: 70, target: 75 },
    { name: 'Machine Learning', baseline: 5, current: 60, target: 70 },
    { name: 'Big Data Tools', baseline: 10, current: 65, target: 75 }],

    outcomes: {
      employmentRate: 65,
      skillCertificationRate: 78,
      roiScore: 7.5
    },
    satisfactionScores: {
      overall: 4.1,
      curriculum: 4.3,
      instructors: 4.0,
      support: 3.8,
      resources: 4.2,
      history: [
      { period: 'Week 4', score: 4.3, avgAllPrograms: 4.0 },
      { period: 'Week 8', score: 4.2, avgAllPrograms: 4.1 },
      { period: 'Week 12', score: 4.0, avgAllPrograms: 4.1 },
      { period: 'Week 16', score: 4.1, avgAllPrograms: 4.2 }]

    },
    sessionDistribution: {
      byType: {
        'Lecture': 35,
        'Lab Work': 30,
        'Project Work': 25,
        'Assessment': 5,
        'Guest Lecture': 5
      },
      byWeek: [8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 8]
    },
    trainers: [
    {
      id: 108,
      name: 'Robert Kim',
      role: 'Data Science Lead',
      sessions: 70,
      beneficiaries: 28,
      rating: 4.2,
      status: 'Active'
    },
    {
      id: 109,
      name: 'Anita Sharma',
      role: 'ML Engineer',
      sessions: 40,
      beneficiaries: 28,
      rating: 4.0,
      status: 'Active'
    },
    {
      id: 110,
      name: 'James Wilson',
      role: 'Industry Consultant',
      sessions: 25,
      beneficiaries: 28,
      rating: 4.3,
      status: 'On Leave'
    }],

    insights: [
    'The advanced machine learning module had a 25% higher drop rate than other modules, indicating potential difficulty level issues.',
    'Students with prior programming experience showed 40% better retention and performance.',
    'Mid-program survey identified need for additional support resources for statistical concepts.',
    'Projects involving real business data showed 30% higher engagement than abstract exercises.',
    'Peer learning sessions initiated by students improved performance by an average of 15%.',
    'Recommendation to add prerequisite assessment to better prepare future cohorts.']

  }
  // You could add more detailed analytics for other programs as needed
};
// Mock API function to get all programs
export const getProgramsList = () => {
  return Promise.resolve(programs);
};
// Mock API function to get program analytics by ID
export const getProgramAnalytics = (id, dateRange = 'last30days') => {
  const analytics = programAnalytics[id];
  if (!analytics) {
    return Promise.reject(new Error('Program analytics not found'));
  }
  // In a real scenario, you might filter data based on dateRange
  // For mock data, we'll just return the full analytics
  return Promise.resolve(analytics);
};
// Mock API function to export program analytics
export const exportProgramAnalytics = (id, format, dateRange = 'last30days') => {
  // In a real scenario, this would generate a file for download
  // For mock data, we'll just return a successful response
  return Promise.resolve({
    success: true,
    message: `Program analytics for program ${id} exported as ${format}`
  });
};