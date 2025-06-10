// TODO: i18n - processed
/**
 * Mock data for reports system
 */
import { format, subDays, addDays } from 'date-fns';
// Sample reports
import { useTranslation } from "react-i18next";export const reports = [
{
  id: 1,
  name: "Beneficiary Progress Report",
  description: "Detailed progress tracking for all beneficiaries",
  type: "beneficiary",
  format: "pdf",
  fields: ["id", "name", "program", "progress", "assessment_score", "attendance_rate", "status"],
  filters: {
    status: "Active",
    progress_min: 0,
    progress_max: 100
  },
  groupBy: ["program"],
  sortBy: [{ field: "progress", direction: "desc" }],
  dateRange: "30days",
  createdBy: {
    id: 1,
    name: "Admin User"
  },
  lastRun: subDays(new Date(), 2).toISOString(),
  runCount: 12,
  generated_at: subDays(new Date(), 2).toISOString()
},
{
  id: 2,
  name: "Program Performance Analysis",
  description: "Analytics on program effectiveness and outcomes",
  type: "program",
  format: "xlsx",
  fields: ["id", "name", "description", "enrolled_count", "completion_rate", "avg_satisfaction", "status"],
  filters: {
    status: ["Active", "Completed"]
  },
  groupBy: [],
  sortBy: [{ field: "completion_rate", direction: "desc" }],
  dateRange: "90days",
  createdBy: {
    id: 1,
    name: "Admin User"
  },
  lastRun: subDays(new Date(), 5).toISOString(),
  runCount: 8,
  generated_at: subDays(new Date(), 5).toISOString()
},
{
  id: 3,
  name: "Trainer Evaluation Summary",
  description: "Summary of trainer performance evaluations",
  type: "trainer",
  format: "pdf",
  fields: ["id", "name", "role", "sessions_count", "beneficiaries_count", "avg_rating", "success_rate"],
  filters: {},
  groupBy: ["role"],
  sortBy: [{ field: "avg_rating", direction: "desc" }],
  dateRange: "30days",
  createdBy: {
    id: 2,
    name: "Manager User"
  },
  lastRun: subDays(new Date(), 1).toISOString(),
  runCount: 5,
  generated_at: subDays(new Date(), 1).toISOString()
},
{
  id: 4,
  name: "Monthly Attendance Report",
  description: "Detailed attendance tracking for all sessions",
  type: "analytics",
  format: "xlsx",
  fields: ["date", "program", "trainer", "total_beneficiaries", "present_count", "absent_count", "attendance_rate"],
  filters: {
    attendance_rate_min: 0,
    attendance_rate_max: 100
  },
  groupBy: ["program", "trainer"],
  sortBy: [{ field: "date", direction: "asc" }],
  dateRange: "30days",
  createdBy: {
    id: 1,
    name: "Admin User"
  },
  lastRun: subDays(new Date(), 10).toISOString(),
  runCount: 3,
  generated_at: subDays(new Date(), 10).toISOString()
},
{
  id: 5,
  name: "Skills Assessment Report",
  description: "Analysis of skills acquisition and progress",
  type: "beneficiary",
  format: "pdf",
  fields: ["skill_name", "initial_level", "current_level", "target_level", "improvement_percentage", "time_to_target"],
  filters: {
    improvement_percentage_min: 0
  },
  groupBy: ["skill_name"],
  sortBy: [{ field: "improvement_percentage", direction: "desc" }],
  dateRange: "90days",
  createdBy: {
    id: 3,
    name: "Trainer User"
  },
  lastRun: subDays(new Date(), 7).toISOString(),
  runCount: 6,
  generated_at: subDays(new Date(), 7).toISOString()
},
{
  id: 6,
  name: "Quarterly Performance Review",
  description: "Comprehensive quarterly performance metrics",
  type: "performance",
  format: "pdf",
  fields: ["metric_name", "target", "actual", "variance", "trend"],
  filters: {},
  groupBy: [],
  sortBy: [{ field: "variance", direction: "asc" }],
  dateRange: "90days",
  createdBy: {
    id: 1,
    name: "Admin User"
  },
  lastRun: subDays(new Date(), 15).toISOString(),
  runCount: 4,
  generated_at: subDays(new Date(), 15).toISOString()
}];

// Scheduled reports
export const scheduledReports = [
{
  id: 1,
  name: "Weekly Beneficiary Progress",
  description: "Automatic weekly report of beneficiary progress",
  report: {
    id: 1,
    name: "Beneficiary Progress Report",
    type: "beneficiary"
  },
  frequency: "weekly",
  dayOfWeek: "1", // Monday
  time: "08:00",
  formats: ["pdf", "xlsx"],
  recipients: [
  { id: 1, name: "Admin User", email: "admin@example.com" },
  { id: 2, name: "Manager User", email: "manager@example.com" }],

  recipients_count: 2,
  status: "active",
  next_run: addDays(new Date(), 3).toISOString(),
  last_run: subDays(new Date(), 4).toISOString()
},
{
  id: 2,
  name: "Monthly Program Performance",
  description: "End of month program performance metrics",
  report: {
    id: 2,
    name: "Program Performance Analysis",
    type: "program"
  },
  frequency: "monthly",
  dayOfMonth: "1",
  time: "09:00",
  formats: ["pdf", "xlsx", "csv"],
  recipients: [
  { id: 1, name: "Admin User", email: "admin@example.com" },
  { id: 4, name: "Director User", email: "director@example.com" }],

  recipients_count: 2,
  status: "active",
  next_run: addDays(new Date(), 15).toISOString(),
  last_run: subDays(new Date(), 15).toISOString()
},
{
  id: 3,
  name: "Daily Attendance Summary",
  description: "Daily attendance report for all sessions",
  report: {
    id: 4,
    name: "Monthly Attendance Report",
    type: "analytics"
  },
  frequency: "daily",
  time: "17:00",
  formats: ["pdf"],
  recipients: [
  { id: 1, name: "Admin User", email: "admin@example.com" },
  { id: 2, name: "Manager User", email: "manager@example.com" },
  { id: 3, name: "Trainer User", email: "trainer@example.com" }],

  recipients_count: 3,
  status: "inactive",
  next_run: null,
  last_run: subDays(new Date(), 1).toISOString()
}];

// Available fields for report types
export const reportFields = {
  beneficiary: [
  { id: "id", name: "Beneficiary ID", description: "Unique identifier" },
  { id: "name", name: "Name", description: "Beneficiary's full name" },
  { id: "email", name: "Email", description: "Contact email address" },
  { id: "program", name: "Program", description: "Enrolled training program" },
  { id: "progress", name: "Progress", description: "Overall completion percentage" },
  { id: "assessment_score", name: "Assessment Score", description: "Latest assessment score" },
  { id: "attendance_rate", name: "Attendance Rate", description: "Session attendance percentage" },
  { id: "status", name: "Status", description: "Current enrollment status" },
  { id: "enrollment_date", name: "Enrollment Date", description: "When the beneficiary joined" },
  { id: "expected_completion", name: "Expected Completion", description: "Projected completion date" },
  { id: "trainers", name: "Assigned Trainers", description: "List of assigned trainers" },
  { id: "skills", name: "Skills", description: "Skills being developed" }],

  program: [
  { id: "id", name: "Program ID", description: "Unique identifier" },
  { id: "name", name: "Name", description: "Program name" },
  { id: "description", name: "Description", description: "Program description" },
  { id: "category", name: "Category", description: "Program category" },
  { id: "duration", name: "Duration", description: "Program length" },
  { id: "start_date", name: "Start Date", description: "When the program began" },
  { id: "end_date", name: "End Date", description: "When the program ends" },
  { id: "enrolled_count", name: "Enrolled Count", description: "Number of active beneficiaries" },
  { id: "completion_rate", name: "Completion Rate", description: "Percentage of beneficiaries who complete" },
  { id: "avg_satisfaction", name: "Average Satisfaction", description: "Satisfaction rating out of 5" },
  { id: "status", name: "Status", description: "Program status" }],

  trainer: [
  { id: "id", name: "Trainer ID", description: "Unique identifier" },
  { id: "name", name: "Name", description: "Trainer's full name" },
  { id: "email", name: "Email", description: "Contact email address" },
  { id: "role", name: "Role", description: "Trainer's role" },
  { id: "specialization", name: "Specialization", description: "Area of expertise" },
  { id: "sessions_count", name: "Sessions Count", description: "Number of sessions conducted" },
  { id: "beneficiaries_count", name: "Beneficiaries Count", description: "Number of assigned beneficiaries" },
  { id: "avg_rating", name: "Average Rating", description: "Rating given by beneficiaries" },
  { id: "success_rate", name: "Success Rate", description: "Percentage of beneficiaries who achieve goals" },
  { id: "status", name: "Status", description: "Current status" }],

  analytics: [
  { id: "date", name: "Date", description: "Date of data point" },
  { id: "program", name: "Program", description: "Training program" },
  { id: "trainer", name: "Trainer", description: "Trainer name" },
  { id: "total_beneficiaries", name: "Total Beneficiaries", description: "Total number of beneficiaries" },
  { id: "present_count", name: "Present Count", description: "Number of beneficiaries present" },
  { id: "absent_count", name: "Absent Count", description: "Number of beneficiaries absent" },
  { id: "attendance_rate", name: "Attendance Rate", description: "Percentage of beneficiaries attending" },
  { id: "satisfaction_score", name: "Satisfaction Score", description: "Average satisfaction rating" },
  { id: "session_type", name: "Session Type", description: "Type of session" },
  { id: "session_duration", name: "Session Duration", description: "Length of session in minutes" }],

  performance: [
  { id: "metric_name", name: "Metric Name", description: "Name of the performance metric" },
  { id: "category", name: "Category", description: "Metric category" },
  { id: "target", name: "Target", description: "Target value" },
  { id: "actual", name: "Actual", description: "Actual achieved value" },
  { id: "variance", name: "Variance", description: "Difference between target and actual" },
  { id: "trend", name: "Trend", description: "Direction of change" },
  { id: "previous_period", name: "Previous Period", description: "Value from previous period" },
  { id: "change_percentage", name: "Change Percentage", description: "Percentage change from previous period" }]

};
// Available filters for report types
export const reportFilters = {
  beneficiary: [
  { id: "status", name: "Status", type: "select", options: [
    { value: "Active", label: "Active" },
    { value: "Completed", label: "Completed" },
    { value: "On Leave", label: "On Leave" },
    { value: "Withdrawn", label: "Withdrawn" }]
  },
  { id: "program", name: "Program", type: "multiselect", options: [
    { value: "1", label: "Web Development Bootcamp" },
    { value: "2", label: "Digital Marketing Fundamentals" },
    { value: "3", label: "Advanced Data Analytics" },
    { value: "4", label: "Leadership Development" },
    { value: "5", label: "Cloud Computing Certification" }]
  },
  { id: "progress", name: "Progress", type: "range", min: 0, max: 100 },
  { id: "assessment_score", name: "Assessment Score", type: "range", min: 0, max: 100 },
  { id: "enrollment_date", name: "Enrollment Date", type: "date" }],

  program: [
  { id: "status", name: "Status", type: "select", options: [
    { value: "Active", label: "Active" },
    { value: "Completed", label: "Completed" },
    { value: "Upcoming", label: "Upcoming" }]
  },
  { id: "category", name: "Category", type: "multiselect", options: [
    { value: "Technical Skills", label: "Technical Skills" },
    { value: "Soft Skills", label: "Soft Skills" },
    { value: "Marketing", label: "Marketing" },
    { value: "Design", label: "Design" },
    { value: "Finance", label: "Finance" },
    { value: "Management", label: "Management" }]
  },
  { id: "completion_rate", name: "Completion Rate", type: "range", min: 0, max: 100 },
  { id: "avg_satisfaction", name: "Average Satisfaction", type: "range", min: 0, max: 5 },
  { id: "date_range", name: "Date Range", type: "date" }],

  trainer: [
  { id: "role", name: "Role", type: "multiselect", options: [
    { value: "Lead Instructor", label: "Lead Instructor" },
    { value: "Technical Mentor", label: "Technical Mentor" },
    { value: "Career Coach", label: "Career Coach" },
    { value: "Industry Expert", label: "Industry Expert" }]
  },
  { id: "specialization", name: "Specialization", type: "text" },
  { id: "avg_rating", name: "Average Rating", type: "range", min: 0, max: 5 },
  { id: "status", name: "Status", type: "select", options: [
    { value: "Active", label: "Active" },
    { value: "On Leave", label: "On Leave" },
    { value: "Inactive", label: "Inactive" }]
  }],

  analytics: [
  { id: "program", name: "Program", type: "multiselect", options: [
    { value: "1", label: "Web Development Bootcamp" },
    { value: "2", label: "Digital Marketing Fundamentals" },
    { value: "3", label: "Advanced Data Analytics" },
    { value: "4", label: "Leadership Development" },
    { value: "5", label: "Cloud Computing Certification" }]
  },
  { id: "trainer", name: "Trainer", type: "multiselect", options: [
    { value: "1", label: "Sarah Johnson" },
    { value: "2", label: "David Chen" },
    { value: "3", label: "Lisa Taylor" },
    { value: "4", label: "Michael Rodriguez" }]
  },
  { id: "session_type", name: "Session Type", type: "multiselect", options: [
    { value: "Lecture", label: "Lecture" },
    { value: "Workshop", label: "Workshop" },
    { value: "Project Work", label: "Project Work" },
    { value: "Assessment", label: "Assessment" },
    { value: "One-on-One", label: "One-on-One" }]
  },
  { id: "attendance_rate", name: "Attendance Rate", type: "range", min: 0, max: 100 },
  { id: "date_range", name: "Date Range", type: "date" }],

  performance: [
  { id: "category", name: "Category", type: "multiselect", options: [
    { value: "Enrollment", label: "Enrollment" },
    { value: "Completion", label: "Completion" },
    { value: "Satisfaction", label: "Satisfaction" },
    { value: "Placement", label: "Placement" },
    { value: "Financial", label: "Financial" }]
  },
  { id: "variance", name: "Variance", type: "range" },
  { id: "trend", name: "Trend", type: "select", options: [
    { value: "Positive", label: "Positive" },
    { value: "Negative", label: "Negative" },
    { value: "Stable", label: "Stable" }]
  },
  { id: "date_range", name: "Date Range", type: "date" }]

};
// Sample report preview data
export const sampleReportPreview = {
  sections: [
  {
    title: "Beneficiary Statistics Summary",
    type: "summary",
    metrics: [
    { id: "total", name: "Total Beneficiaries", value: 148, change: 12 },
    { id: "active", name: "Active Beneficiaries", value: 112, change: 8 },
    { id: "graduated", name: "Graduated Beneficiaries", value: 36, change: 4 }]

  },
  {
    title: "Beneficiary Progress Details",
    type: "table",
    columns: [
    { id: "name", name: "Name" },
    { id: "program", name: "Program" },
    { id: "progress", name: "Progress" },
    { id: "assessment_score", name: "Assessment Score" },
    { id: "status", name: "Status" }],

    data: [
    { name: "John Smith", program: "Web Development Bootcamp", progress: "65%", assessment_score: "78%", status: "Active" },
    { name: "Maria Garcia", program: "Digital Marketing Fundamentals", progress: "92%", assessment_score: "86%", status: "Completed" },
    { name: "David Lee", program: "Advanced Data Analytics", progress: "45%", assessment_score: "72%", status: "Active" },
    { name: "Sarah Johnson", program: "Leadership Development", progress: "95%", assessment_score: "92%", status: "Completed" },
    { name: "Michael Brown", program: "Cloud Computing Certification", progress: "52%", assessment_score: "68%", status: "Active" }]

  },
  {
    title: "Progress Distribution by Program",
    type: "chart",
    chartType: "Bar Chart",
    data: [
    { program: "Web Development Bootcamp", avgProgress: 58 },
    { program: "Digital Marketing Fundamentals", avgProgress: 75 },
    { program: "Advanced Data Analytics", avgProgress: 42 },
    { program: "Leadership Development", avgProgress: 88 },
    { program: "Cloud Computing Certification", avgProgress: 63 }]

  }]

};
// List of users for recipients
export const users = [
{ id: 1, name: "Admin User", email: "admin@example.com", role: "admin" },
{ id: 2, name: "Manager User", email: "manager@example.com", role: "manager" },
{ id: 3, name: "Trainer User", email: "trainer@example.com", role: "trainer" },
{ id: 4, name: "Director User", email: "director@example.com", role: "director" },
{ id: 5, name: "Coordinator User", email: "coordinator@example.com", role: "coordinator" }];

// Mock API function to get recent reports
export const getRecentReports = () => {
  return Promise.resolve(reports.slice(0, 3));
};
// Mock API function to get saved reports
export const getSavedReports = () => {
  return Promise.resolve(reports);
};
// Mock API function to get scheduled reports
export const getScheduledReports = () => {
  return Promise.resolve(scheduledReports);
};
// Mock API function to get report fields
export const getReportFields = (type) => {
  return Promise.resolve(reportFields[type] || []);
};
// Mock API function to get report filters
export const getReportFilters = (type) => {
  return Promise.resolve(reportFilters[type] || []);
};
// Mock API function to get report preview
export const getReportPreview = (reportData) => {
  return Promise.resolve(sampleReportPreview);
};
// Mock API function to save report
export const saveReport = (reportData) => {
  const newReport = {
    id: reports.length + 1,
    ...reportData,
    createdBy: {
      id: 1,
      name: "Admin User"
    },
    lastRun: null,
    runCount: 0,
    generated_at: new Date().toISOString()
  };
  reports.push(newReport);
  return Promise.resolve(newReport);
};
// Mock API function to get scheduled report
export const getScheduledReport = (id) => {
  const schedule = scheduledReports.find((s) => s.id.toString() === id);
  if (!schedule) {
    return Promise.reject(new Error('Schedule not found'));
  }
  return Promise.resolve(schedule);
};
// Mock API function to save scheduled report
export const saveScheduledReport = (scheduleData) => {
  const newSchedule = {
    id: scheduledReports.length + 1,
    ...scheduleData,
    recipients_count: scheduleData.recipients.length,
    next_run: calculateNextRun(scheduleData),
    last_run: null
  };
  scheduledReports.push(newSchedule);
  return Promise.resolve(newSchedule);
};
// Helper function to calculate next run date
const calculateNextRun = (schedule) => {
  const now = new Date();
  let nextRun = new Date();
  if (!schedule.active) {
    return null;
  }
  if (schedule.frequency === 'daily') {
    nextRun.setDate(now.getDate() + 1);
  } else if (schedule.frequency === 'weekly') {
    const dayOfWeek = parseInt(schedule.dayOfWeek);
    const currentDay = now.getDay();
    const daysToAdd = (dayOfWeek + 7 - currentDay) % 7;
    nextRun.setDate(now.getDate() + (daysToAdd === 0 ? 7 : daysToAdd));
  } else if (schedule.frequency === 'monthly') {
    const dayOfMonth = parseInt(schedule.dayOfMonth);
    nextRun = new Date(now.getFullYear(), now.getMonth() + 1, dayOfMonth);
  } else if (schedule.frequency === 'quarterly') {
    const dayOfMonth = parseInt(schedule.dayOfMonth);
    nextRun = new Date(now.getFullYear(), now.getMonth() + 3, dayOfMonth);
  }
  // Set the time
  if (schedule.time) {
    const [hours, minutes] = schedule.time.split(':').map(Number);
    nextRun.setHours(hours, minutes, 0, 0);
  }
  return nextRun.toISOString();
};