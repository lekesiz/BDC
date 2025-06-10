// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock Dashboard Data for different user types
export const generateDashboardData = (userRole) => {
  const baseData = {
    overview: {
      totalUsers: 456,
      activePrograms: 23,
      completedCourses: 189,
      averageProgress: 73,
      upcomingAppointments: 5,
      unreadNotifications: 8,
      pendingReports: 3,
      activeStudents: 234
    },
    recentActivity: [
    {
      id: 1,
      type: "course_completed",
      title: "Jean Dupont completed Advanced JavaScript",
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      icon: "check-circle",
      color: "green"
    },
    {
      id: 2,
      type: "evaluation_submitted",
      title: "Marie Martin submitted Python Basics evaluation",
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      icon: "document",
      color: "blue"
    },
    {
      id: 3,
      type: "appointment_scheduled",
      title: "New appointment scheduled with Pierre Bernard",
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      icon: "calendar",
      color: "purple"
    },
    {
      id: 4,
      type: "program_enrolled",
      title: "Sophie Laurent enrolled in Web Development Program",
      timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
      icon: "user-plus",
      color: "teal"
    },
    {
      id: 5,
      type: "achievement_unlocked",
      title: "Lucas Petit earned 'JavaScript Expert' badge",
      timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
      icon: "trophy",
      color: "yellow"
    }],

    performanceMetrics: {
      monthlyGrowth: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [
        {
          label: "New Students",
          data: [23, 31, 28, 45, 52, 61],
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)"
        },
        {
          label: "Course Completions",
          data: [15, 22, 19, 34, 41, 48],
          borderColor: "rgb(34, 197, 94)",
          backgroundColor: "rgba(34, 197, 94, 0.1)"
        }]

      },
      skillDistribution: {
        labels: ["JavaScript", "Python", "React", "Node.js", "Data Science", "UI/UX"],
        datasets: [{
          data: [85, 72, 78, 65, 45, 52],
          backgroundColor: [
          "rgba(59, 130, 246, 0.8)",
          "rgba(34, 197, 94, 0.8)",
          "rgba(168, 85, 247, 0.8)",
          "rgba(251, 146, 60, 0.8)",
          "rgba(236, 72, 153, 0.8)",
          "rgba(20, 184, 166, 0.8)"]

        }]
      },
      completionRate: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
        datasets: [{
          label: "Completion Rate (%)",
          data: [68, 72, 75, 78],
          backgroundColor: "rgba(34, 197, 94, 0.8)"
        }]
      }
    },
    quickStats: [
    { label: "Active Students", value: 234, change: 12, trend: "up", color: "blue" },
    { label: "Course Completion Rate", value: "78%", change: 5, trend: "up", color: "green" },
    { label: "Average Score", value: "85%", change: -2, trend: "down", color: "purple" },
    { label: "Student Satisfaction", value: "4.8/5", change: 0.2, trend: "up", color: "orange" }]

  };
  // Customize data based on user role
  if (userRole === "admin") {
    return {
      ...baseData,
      tenantOverview: {
        totalTenants: 12,
        activeTenants: 10,
        revenue: {
          monthly: 45250,
          quarterly: 132800,
          yearly: 512400
        },
        systemHealth: {
          uptime: "99.97%",
          responseTime: "128ms",
          errorRate: "0.03%",
          activeUsers: 1234
        }
      },
      adminSpecificMetrics: {
        userGrowth: {
          labels: ["Q1", "Q2", "Q3", "Q4"],
          datasets: [{
            label: "User Growth",
            data: [450, 680, 890, 1234],
            borderColor: "rgb(59, 130, 246)",
            tension: 0.4
          }]
        },
        revenueByTenant: {
          labels: ["Tenant A", "Tenant B", "Tenant C", "Tenant D", "Tenant E"],
          datasets: [{
            label: "Revenue",
            data: [12000, 8500, 15600, 9800, 11200],
            backgroundColor: "rgba(59, 130, 246, 0.8)"
          }]
        }
      }
    };
  } else if (userRole === "tenant_admin") {
    return {
      ...baseData,
      tenantSpecific: {
        totalStaff: 28,
        activePrograms: 12,
        studentCapacity: 85,
        resourceUtilization: 78,
        budgetUsed: 65
      },
      departmentMetrics: {
        byDepartment: {
          labels: ["IT", "Marketing", "HR", "Sales", "Operations"],
          datasets: [{
            label: "Active Students",
            data: [45, 32, 28, 51, 34],
            backgroundColor: "rgba(59, 130, 246, 0.8)"
          }]
        },
        programEffectiveness: {
          labels: ["Program A", "Program B", "Program C", "Program D"],
          datasets: [{
            label: "Effectiveness Score",
            data: [85, 72, 78, 91],
            backgroundColor: "rgba(34, 197, 94, 0.8)"
          }]
        }
      }
    };
  } else if (userRole === "trainer") {
    return {
      ...baseData,
      trainerSpecific: {
        myStudents: 34,
        pendingEvaluations: 12,
        upcomingClasses: 8,
        averageStudentScore: 82,
        completedSessions: 156
      },
      classMetrics: {
        attendanceRate: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
          datasets: [{
            label: "Attendance (%)",
            data: [92, 88, 95, 85, 90],
            borderColor: "rgb(59, 130, 246)",
            tension: 0.4
          }]
        },
        performanceByClass: {
          labels: ["Class A", "Class B", "Class C", "Class D"],
          datasets: [{
            label: "Average Score",
            data: [82, 78, 85, 79],
            backgroundColor: "rgba(34, 197, 94, 0.8)"
          }]
        }
      },
      upcomingSchedule: [
      {
        id: 1,
        title: "JavaScript Fundamentals",
        time: "09:00 - 10:30",
        date: "2024-01-22",
        students: 15,
        room: "Lab A"
      },
      {
        id: 2,
        title: "React Advanced Concepts",
        time: "14:00 - 16:00",
        date: "2024-01-22",
        students: 12,
        room: "Lab B"
      },
      {
        id: 3,
        title: "Python Basics",
        time: "10:00 - 12:00",
        date: "2024-01-23",
        students: 18,
        room: "Lab C"
      }]

    };
  } else {// student
    return {
      ...baseData,
      studentSpecific: {
        myProgress: 73,
        completedCourses: 12,
        upcomingDeadlines: 5,
        currentStreak: 15,
        rankInClass: 5,
        totalPoints: 2450
      },
      learningPath: {
        currentCourse: {
          name: "Advanced React Development",
          progress: 65,
          nextLesson: "State Management with Redux",
          estimatedTime: "2 hours"
        },
        upcomingCourses: [
        { name: "Node.js Backend Development", startDate: "2024-02-01" },
        { name: "Mobile Development with React Native", startDate: "2024-03-15" }],

        recentAchievements: [
        { name: "JavaScript Expert", earnedDate: "2024-01-15", points: 500 },
        { name: "Quick Learner", earnedDate: "2024-01-10", points: 250 }]

      },
      performanceChart: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
        datasets: [{
          label: "My Progress",
          data: [65, 70, 72, 73],
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)"
        }, {
          label: "Class Average",
          data: [60, 65, 68, 70],
          borderColor: "rgb(156, 163, 175)",
          backgroundColor: "rgba(156, 163, 175, 0.1)"
        }]
      }
    };
  }
};
// Generate notifications for dashboard
export const generateDashboardNotifications = (userRole) => {
  const baseNotifications = [
  {
    id: 1,
    type: "info",
    title: "System Update",
    message: "New features have been added to the platform",
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    read: false
  },
  {
    id: 2,
    type: "success",
    title: "Achievement Unlocked",
    message: "You've completed 10 courses this month!",
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    read: false
  }];

  if (userRole === "trainer") {
    return [
    ...baseNotifications,
    {
      id: 3,
      type: "warning",
      title: "Pending Evaluations",
      message: "You have 5 evaluations waiting for review",
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      read: false
    },
    {
      id: 4,
      type: "info",
      title: "Class Reminder",
      message: "JavaScript class starts in 2 hours",
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      read: true
    }];

  }
  if (userRole === "student") {
    return [
    ...baseNotifications,
    {
      id: 3,
      type: "warning",
      title: "Assignment Due",
      message: "React project due tomorrow at 11:59 PM",
      timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
      read: false
    },
    {
      id: 4,
      type: "success",
      title: "Grade Posted",
      message: "Your Python exam has been graded: 92%",
      timestamp: new Date(Date.now() - 1000 * 60 * 150).toISOString(),
      read: true
    }];

  }
  return baseNotifications;
};
// Generate quick actions for dashboard
export const generateQuickActions = (userRole) => {
  const baseActions = [
  { icon: "calendar", label: "Schedule", path: "/calendar", color: "blue" },
  { icon: "document", label: "Documents", path: "/documents", color: "green" },
  { icon: "message", label: "Messages", path: "/messages", color: "purple" }];

  if (userRole === "admin") {
    return [
    { icon: "users", label: "Manage Users", path: "/users", color: "blue" },
    { icon: "chart", label: "Analytics", path: "/analytics", color: "green" },
    { icon: "settings", label: "Settings", path: "/settings", color: "gray" },
    ...baseActions];

  } else if (userRole === "tenant_admin") {
    return [
    { icon: "users", label: "Staff", path: "/users", color: "blue" },
    { icon: "book", label: "Programs", path: "/programs", color: "green" },
    { icon: "chart", label: "Reports", path: "/reports", color: "purple" },
    ...baseActions];

  } else if (userRole === "trainer") {
    return [
    { icon: "users", label: "My Students", path: "/beneficiaries", color: "blue" },
    { icon: "clipboard", label: "Evaluations", path: "/evaluations", color: "green" },
    { icon: "calendar", label: "Schedule", path: "/calendar", color: "purple" },
    ...baseActions];

  } else {
    return [
    { icon: "book", label: "My Courses", path: "/portal/courses", color: "blue" },
    { icon: "chart", label: "Progress", path: "/portal/progress", color: "green" },
    { icon: "trophy", label: "Achievements", path: "/portal/achievements", color: "yellow" },
    ...baseActions];

  }
};