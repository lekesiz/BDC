// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock data for assessment statistics
export const generateMockStatistics = (startDate, endDate) => {
  const days = Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24));
  return {
    overview: {
      totalAssessments: 127,
      activeStudents: 342,
      averageScore: 78,
      completionRate: 82,
      totalSubmissions: 1543,
      pendingSubmissions: 89,
      averageTimeToComplete: 45 // minutes
    },
    performance: {
      scoreDistribution: [
      { range: '0-20%', count: 12 },
      { range: '21-40%', count: 28 },
      { range: '41-60%', count: 65 },
      { range: '61-80%', count: 142 },
      { range: '81-100%', count: 95 }],

      timeToComplete: [
      { type: 'Quick Quiz', minutes: 15 },
      { type: 'Standard Quiz', minutes: 35 },
      { type: 'Project', minutes: 120 }],

      byCourse: [
      { id: 1, name: 'Python Programming', assessmentCount: 24, averageScore: 82, passRate: 85 },
      { id: 2, name: 'Web Development', assessmentCount: 18, averageScore: 75, passRate: 78 },
      { id: 3, name: 'Data Science', assessmentCount: 31, averageScore: 79, passRate: 82 },
      { id: 4, name: 'Mobile Development', assessmentCount: 15, averageScore: 71, passRate: 72 },
      { id: 5, name: 'Cloud Computing', assessmentCount: 22, averageScore: 84, passRate: 88 }],

      byTrainer: [
      { id: 1, name: 'John Smith', studentCount: 45, averageScore: 79, completionRate: 88 },
      { id: 2, name: 'Sarah Johnson', studentCount: 52, averageScore: 82, completionRate: 91 },
      { id: 3, name: 'Mike Chen', studentCount: 38, averageScore: 77, completionRate: 85 },
      { id: 4, name: 'Emily Davis', studentCount: 41, averageScore: 80, completionRate: 87 }],

      passRateTrends: generateTrendData(days, ['quiz', 'project', 'overall'])
    },
    completion: {
      trends: generateCompletionTrends(days)
    },
    assessmentStats: {
      typeDistribution: [
      { name: 'Quiz', value: 78 },
      { name: 'Project', value: 49 }],

      topAssessments: [
      {
        id: 1,
        title: 'Python Basics Quiz',
        type: 'quiz',
        completions: 234,
        averageScore: 85,
        passRate: 88
      },
      {
        id: 2,
        title: 'JavaScript Fundamentals',
        type: 'quiz',
        completions: 189,
        averageScore: 78,
        passRate: 82
      },
      {
        id: 3,
        title: 'React Project',
        type: 'project',
        completions: 67,
        averageScore: 73,
        passRate: 75
      },
      {
        id: 4,
        title: 'Database Design Quiz',
        type: 'quiz',
        completions: 156,
        averageScore: 81,
        passRate: 84
      },
      {
        id: 5,
        title: 'API Development Project',
        type: 'project',
        completions: 89,
        averageScore: 76,
        passRate: 78
      }]

    },
    studentStats: {
      topStudents: [
      {
        id: 1,
        name: 'Alice Johnson',
        email: 'alice@example.com',
        assessmentCount: 15,
        averageScore: 92,
        badges: ['🏆', '⭐', '🎯']
      },
      {
        id: 2,
        name: 'Bob Wilson',
        email: 'bob@example.com',
        assessmentCount: 12,
        averageScore: 88,
        badges: ['🏆', '⭐']
      },
      {
        id: 3,
        name: 'Carol Martinez',
        email: 'carol@example.com',
        assessmentCount: 18,
        averageScore: 86,
        badges: ['⭐', '🎯']
      },
      {
        id: 4,
        name: 'David Lee',
        email: 'david@example.com',
        assessmentCount: 11,
        averageScore: 85,
        badges: ['⭐']
      }],

      needingSupport: [
      {
        id: 5,
        name: 'Eve Brown',
        email: 'eve@example.com',
        failedCount: 4,
        averageScore: 42
      },
      {
        id: 6,
        name: 'Frank Davis',
        email: 'frank@example.com',
        failedCount: 3,
        averageScore: 48
      },
      {
        id: 7,
        name: 'Grace Wilson',
        email: 'grace@example.com',
        failedCount: 5,
        averageScore: 38
      }],

      engagementTrends: generateEngagementTrends(days)
    },
    questionStats: {
      mostChallenging: [
      {
        id: 1,
        text: 'What is the time complexity of binary search?',
        assessmentTitle: 'Algorithms Quiz',
        attempts: 234,
        successRate: 42,
        avgTime: 120
      },
      {
        id: 2,
        text: 'Explain the difference between SQL JOIN types',
        assessmentTitle: 'Database Quiz',
        attempts: 189,
        successRate: 38,
        avgTime: 180
      },
      {
        id: 3,
        text: 'Implement a recursive function for factorial',
        assessmentTitle: 'Programming Basics',
        attempts: 156,
        successRate: 45,
        avgTime: 150
      },
      {
        id: 4,
        text: 'What is closure in JavaScript?',
        assessmentTitle: 'JavaScript Advanced',
        attempts: 145,
        successRate: 35,
        avgTime: 200
      }]

    }
  };
};
// Helper function to generate trend data
function generateTrendData(days, metrics) {
  const data = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dataPoint = {
      date: date.toISOString().split('T')[0]
    };
    metrics.forEach((metric) => {
      dataPoint[metric] = Math.floor(Math.random() * 20) + 70; // Random value between 70-90
    });
    data.push(dataPoint);
  }
  return data;
}
// Helper function to generate completion trends
function generateCompletionTrends(days) {
  const data = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    data.push({
      date: date.toISOString().split('T')[0],
      completed: Math.floor(Math.random() * 50) + 100,
      pending: Math.floor(Math.random() * 20) + 10,
      overdue: Math.floor(Math.random() * 10) + 5
    });
  }
  return data;
}
// Helper function to generate engagement trends
function generateEngagementTrends(days) {
  const data = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    data.push({
      date: date.toISOString().split('T')[0],
      active: Math.floor(Math.random() * 100) + 200,
      inactive: Math.floor(Math.random() * 50) + 50,
      new: Math.floor(Math.random() * 20) + 10
    });
  }
  return data;
}
export const statisticsEndpoints = {
  overview: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.overview), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  },
  performance: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.performance), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  },
  completion: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.completion), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  },
  assessments: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.assessmentStats), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  },
  students: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.studentStats), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  },
  questions: (req) => {
    const url = new URL(req.url);
    const start = url.searchParams.get('start');
    const end = url.searchParams.get('end');
    const stats = generateMockStatistics(start, end);
    return new Response(JSON.stringify(stats.questionStats), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};