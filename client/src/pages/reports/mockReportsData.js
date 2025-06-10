// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock data for reports testing
export const mockReports = {
  recent: [
  {
    id: 1,
    name: "Monthly Beneficiary Summary",
    description: "Comprehensive overview of all beneficiaries for this month",
    type: "beneficiary",
    format: "pdf",
    status: "completed",
    generated_at: new Date().toISOString(),
    file_size: 1024000,
    created_by: "Admin User"
  },
  {
    id: 2,
    name: "Program Performance Report",
    description: "Analysis of program completion rates and attendance",
    type: "program",
    format: "xlsx",
    status: "completed",
    generated_at: new Date(Date.now() - 86400000).toISOString(),
    file_size: 512000,
    created_by: "Admin User"
  },
  {
    id: 3,
    name: "Test Score Analysis",
    description: "Detailed analysis of test scores across all programs",
    type: "performance",
    format: "pdf",
    status: "generating",
    generated_at: new Date(Date.now() - 172800000).toISOString(),
    file_size: 0,
    created_by: "Admin User"
  }],

  saved: [
  {
    id: 4,
    name: "Quarterly Analytics Report",
    description: "KPI metrics and trends for the quarter",
    type: "analytics",
    format: "pdf",
    status: "completed",
    created_by: "Admin User",
    last_generated: new Date(Date.now() - 604800000).toISOString(),
    run_count: 5
  },
  {
    id: 5,
    name: "Trainer Performance Summary",
    description: "Performance metrics for all active trainers",
    type: "trainer",
    format: "csv",
    status: "completed",
    created_by: "Manager User",
    last_generated: new Date(Date.now() - 1209600000).toISOString(),
    run_count: 3
  },
  {
    id: 6,
    name: "Annual Beneficiary Progress Report",
    description: "Year-over-year progress tracking for beneficiaries",
    type: "beneficiary",
    format: "xlsx",
    status: "completed",
    created_by: "Admin User",
    last_generated: new Date(Date.now() - 2419200000).toISOString(),
    run_count: 12
  }],

  scheduled: [
  {
    id: 1,
    report: {
      id: 4,
      name: "Quarterly Analytics Report",
      type: "analytics"
    },
    frequency: "monthly",
    recipients_count: 3,
    next_run: new Date(Date.now() + 86400000).toISOString(),
    status: "active"
  },
  {
    id: 2,
    report: {
      id: 5,
      name: "Trainer Performance Summary",
      type: "trainer"
    },
    frequency: "weekly",
    recipients_count: 2,
    next_run: new Date(Date.now() + 604800000).toISOString(),
    status: "active"
  },
  {
    id: 3,
    report: {
      id: 6,
      name: "Annual Beneficiary Progress Report",
      type: "beneficiary"
    },
    frequency: "daily",
    recipients_count: 1,
    next_run: new Date(Date.now() + 43200000).toISOString(),
    status: "paused"
  }],

  fields: {
    beneficiary: [
    { id: 'name', name: 'Full Name', description: 'Beneficiary full name' },
    { id: 'email', name: 'Email', description: 'Beneficiary email address' },
    { id: 'status', name: 'Status', description: 'Current beneficiary status' },
    { id: 'trainer', name: 'Assigned Trainer', description: 'Trainer assigned to beneficiary' },
    { id: 'created_date', name: 'Created Date', description: 'Date beneficiary was added' },
    { id: 'test_score', name: 'Average Test Score', description: 'Average score across all tests' },
    { id: 'progress', name: 'Progress', description: 'Overall progress percentage' },
    { id: 'department', name: 'Department', description: 'Department classification' },
    { id: 'notes', name: 'Notes', description: 'Additional notes and comments' }],

    program: [
    { id: 'name', name: 'Program Name', description: 'Name of the training program' },
    { id: 'code', name: 'Program Code', description: 'Unique program identifier' },
    { id: 'status', name: 'Status', description: 'Current program status' },
    { id: 'start_date', name: 'Start Date', description: 'Program start date' },
    { id: 'end_date', name: 'End Date', description: 'Program end date' },
    { id: 'enrollment_count', name: 'Enrollment Count', description: 'Number of enrolled beneficiaries' },
    { id: 'completion_rate', name: 'Completion Rate', description: 'Program completion percentage' },
    { id: 'attendance_rate', name: 'Attendance Rate', description: 'Average attendance rate' },
    { id: 'description', name: 'Description', description: 'Program description' }],

    trainer: [
    { id: 'name', name: 'Trainer Name', description: 'Full name of the trainer' },
    { id: 'email', name: 'Email', description: 'Trainer email address' },
    { id: 'beneficiary_count', name: 'Beneficiary Count', description: 'Number of assigned beneficiaries' },
    { id: 'active_status', name: 'Active Status', description: 'Whether trainer is active' },
    { id: 'last_login', name: 'Last Login', description: 'Last login timestamp' },
    { id: 'specialization', name: 'Specialization', description: 'Areas of expertise' },
    { id: 'programs', name: 'Assigned Programs', description: 'Programs trainer is involved in' },
    { id: 'performance_rating', name: 'Performance Rating', description: 'Average performance rating' }],

    analytics: [
    { id: 'metric_name', name: 'Metric Name', description: 'Name of the metric' },
    { id: 'value', name: 'Value', description: 'Metric value' },
    { id: 'change', name: 'Change', description: 'Change from previous period' },
    { id: 'trend', name: 'Trend', description: 'Trend direction' },
    { id: 'date', name: 'Date', description: 'Date of the metric' },
    { id: 'category', name: 'Category', description: 'Metric category' }],

    performance: [
    { id: 'beneficiary_name', name: 'Beneficiary Name', description: 'Full name of the beneficiary' },
    { id: 'test_name', name: 'Test Name', description: 'Name of the test' },
    { id: 'score', name: 'Score', description: 'Test score' },
    { id: 'date', name: 'Date', description: 'Test completion date' },
    { id: 'duration', name: 'Duration', description: 'Time taken to complete' },
    { id: 'status', name: 'Status', description: 'Test completion status' },
    { id: 'feedback', name: 'Feedback', description: 'Test feedback and comments' },
    { id: 'improvement', name: 'Improvement', description: 'Improvement from previous test' }]

  },
  filters: {
    beneficiary: [
    {
      id: 'status',
      name: 'Status',
      type: 'select',
      options: [
      { value: 'active', label: 'Active' },
      { value: 'inactive', label: 'Inactive' },
      { value: 'completed', label: 'Completed' },
      { value: 'pending', label: 'Pending' }]

    },
    {
      id: 'trainer',
      name: 'Trainer',
      type: 'multiselect',
      options: [
      { value: '1', label: 'John Smith' },
      { value: '2', label: 'Sarah Johnson' },
      { value: '3', label: 'Mike Wilson' }]

    },
    {
      id: 'test_score_range',
      name: 'Test Score Range',
      type: 'range',
      options: { min: 0, max: 100 }
    },
    {
      id: 'created_date',
      name: 'Created Date',
      type: 'date',
      options: {}
    }],

    program: [
    {
      id: 'status',
      name: 'Status',
      type: 'select',
      options: [
      { value: 'active', label: 'Active' },
      { value: 'completed', label: 'Completed' },
      { value: 'upcoming', label: 'Upcoming' },
      { value: 'cancelled', label: 'Cancelled' }]

    },
    {
      id: 'enrollment_range',
      name: 'Enrollment Count',
      type: 'range',
      options: { min: 0, max: 100 }
    },
    {
      id: 'date_range',
      name: 'Date Range',
      type: 'date',
      options: {}
    }],

    trainer: [
    {
      id: 'active_status',
      name: 'Active Status',
      type: 'select',
      options: [
      { value: 'active', label: 'Active' },
      { value: 'inactive', label: 'Inactive' }]

    },
    {
      id: 'beneficiary_count',
      name: 'Beneficiary Count',
      type: 'range',
      options: { min: 0, max: 50 }
    },
    {
      id: 'programs',
      name: 'Programs',
      type: 'multiselect',
      options: [
      { value: '1', label: 'Leadership Training' },
      { value: '2', label: 'Technical Skills' },
      { value: '3', label: 'Communication Skills' }]

    }],

    analytics: [
    {
      id: 'metric_category',
      name: 'Metric Category',
      type: 'multiselect',
      options: [
      { value: 'engagement', label: 'Engagement' },
      { value: 'performance', label: 'Performance' },
      { value: 'completion', label: 'Completion' },
      { value: 'satisfaction', label: 'Satisfaction' }]

    },
    {
      id: 'date_range',
      name: 'Date Range',
      type: 'date',
      options: {}
    }],

    performance: [
    {
      id: 'test_name',
      name: 'Test Name',
      type: 'multiselect',
      options: [
      { value: '1', label: 'Basic Assessment' },
      { value: '2', label: 'Advanced Assessment' },
      { value: '3', label: 'Final Evaluation' }]

    },
    {
      id: 'score_range',
      name: 'Score Range',
      type: 'range',
      options: { min: 0, max: 100 }
    },
    {
      id: 'status',
      name: 'Status',
      type: 'select',
      options: [
      { value: 'completed', label: 'Completed' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'abandoned', label: 'Abandoned' }]

    },
    {
      id: 'date_range',
      name: 'Date Range',
      type: 'date',
      options: {}
    }]

  },
  previewData: {
    beneficiary: {
      sections: [
      {
        title: 'Summary',
        type: 'summary',
        metrics: [
        { id: 'total', name: 'Total Beneficiaries', value: '125', change: 12 },
        { id: 'active', name: 'Active', value: '98', change: 5 },
        { id: 'avg_score', name: 'Average Score', value: '82.5%', change: 3 }]

      },
      {
        title: 'Beneficiary Details',
        type: 'table',
        columns: [
        { id: 'name', name: 'Name' },
        { id: 'email', name: 'Email' },
        { id: 'status', name: 'Status' },
        { id: 'test_score', name: 'Avg Score' },
        { id: 'trainer', name: 'Trainer' }],

        data: [
        {
          name: 'John Doe',
          email: 'john.doe@example.com',
          status: 'Active',
          test_score: '85%',
          trainer: 'Sarah Johnson'
        },
        {
          name: 'Jane Smith',
          email: 'jane.smith@example.com',
          status: 'Active',
          test_score: '92%',
          trainer: 'Mike Wilson'
        },
        {
          name: 'Robert Brown',
          email: 'robert.brown@example.com',
          status: 'Completed',
          test_score: '78%',
          trainer: 'John Smith'
        }]

      }]

    },
    program: {
      sections: [
      {
        title: 'Program Overview',
        type: 'summary',
        metrics: [
        { id: 'total', name: 'Total Programs', value: '15', change: 3 },
        { id: 'active', name: 'Active Programs', value: '8', change: -1 },
        { id: 'completion', name: 'Avg Completion', value: '76%', change: 5 }]

      },
      {
        title: 'Program Details',
        type: 'table',
        columns: [
        { id: 'name', name: 'Program' },
        { id: 'enrollment', name: 'Enrollments' },
        { id: 'completion', name: 'Completion Rate' },
        { id: 'attendance', name: 'Attendance' }],

        data: [
        {
          name: 'Leadership Training',
          enrollment: '25',
          completion: '88%',
          attendance: '94%'
        },
        {
          name: 'Technical Skills',
          enrollment: '40',
          completion: '76%',
          attendance: '89%'
        },
        {
          name: 'Communication Skills',
          enrollment: '35',
          completion: '82%',
          attendance: '91%'
        }]

      }]

    }
  }
};