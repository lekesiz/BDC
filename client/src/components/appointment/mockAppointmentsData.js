import { addDays, setHours, setMinutes, subDays } from 'date-fns';

// Generate today's date
const today = new Date();

// Generate dates for different appointments
const yesterday = subDays(today, 1);
const tomorrow = addDays(today, 1);
const nextWeek = addDays(today, 7);
const twoWeeksFromNow = addDays(today, 14);

// Helper function to create ISO string for a specific date, hour, minute
const dateTime = (date, hour, minute = 0) => {
  return setMinutes(setHours(date, hour), minute).toISOString();
};

// Mock appointments data for testing the calendar
export const mockAppointments = [
  {
    id: 1,
    title: 'Initial Assessment Session',
    description: 'First evaluation session with the beneficiary to assess current skills and needs',
    start_time: dateTime(today, 10, 0),
    end_time: dateTime(today, 11, 30),
    location: 'Main Office, Room 102',
    type: 'evaluation',
    status: 'confirmed',
    color: 'purple',
    beneficiary_id: 1,
    beneficiary: {
      id: 1,
      name: 'John Doe',
      email: 'john.doe@example.com'
    },
    trainer_id: 1,
    trainer: {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah.johnson@example.com'
    },
    notes: 'Prepare assessment materials and review previous records before the meeting',
    is_google_synced: true,
    google_event_id: 'abc123'
  },
  {
    id: 2,
    title: 'Technical Skills Training',
    description: 'Focus on programming fundamentals and problem-solving techniques',
    start_time: dateTime(today, 14, 0),
    end_time: dateTime(today, 16, 0),
    location: 'Training Lab, Building B',
    type: 'session',
    status: 'confirmed',
    color: 'blue',
    beneficiary_id: 2,
    beneficiary: {
      id: 2,
      name: 'Jane Smith',
      email: 'jane.smith@example.com'
    },
    trainer_id: 2,
    trainer: {
      id: 2,
      name: 'Michael Chen',
      email: 'michael.chen@example.com'
    },
    notes: 'Bring coding examples and exercises for SQL and database concepts',
    is_google_synced: false
  },
  {
    id: 3,
    title: 'Career Development Meeting',
    description: 'Discussion about career goals and development plan',
    start_time: dateTime(yesterday, 9, 0),
    end_time: dateTime(yesterday, 10, 0),
    location: 'Virtual (Zoom)',
    type: 'meeting',
    status: 'completed',
    color: 'green',
    beneficiary_id: 3,
    beneficiary: {
      id: 3,
      name: 'Robert Johnson',
      email: 'robert.johnson@example.com'
    },
    trainer_id: 3,
    trainer: {
      id: 3,
      name: 'Emily Davis',
      email: 'emily.davis@example.com'
    },
    notes: 'Follow up on job search progress and resume updates',
    is_google_synced: true,
    google_event_id: 'def456'
  },
  {
    id: 4,
    title: 'Communication Skills Workshop',
    description: 'Group workshop focusing on presentation and interpersonal communication',
    start_time: dateTime(tomorrow, 13, 0),
    end_time: dateTime(tomorrow, 16, 0),
    location: 'Conference Room A',
    type: 'session',
    status: 'confirmed',
    color: 'blue',
    beneficiary_id: null, // Group session with multiple beneficiaries
    trainer_id: 1,
    trainer: {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah.johnson@example.com'
    },
    notes: 'Prepare presentation materials and group exercises',
    is_google_synced: true,
    google_event_id: 'ghi789'
  },
  {
    id: 5,
    title: 'Mock Interview Session',
    description: 'Practice interview with feedback for upcoming job applications',
    start_time: dateTime(tomorrow, 11, 0),
    end_time: dateTime(tomorrow, 12, 0),
    location: 'Interview Room 3',
    type: 'session',
    status: 'confirmed',
    color: 'blue',
    beneficiary_id: 1,
    beneficiary: {
      id: 1,
      name: 'John Doe',
      email: 'john.doe@example.com'
    },
    trainer_id: 3,
    trainer: {
      id: 3,
      name: 'Emily Davis',
      email: 'emily.davis@example.com'
    },
    notes: 'Review common interview questions for software developer roles',
    is_google_synced: false
  },
  {
    id: 6,
    title: 'Progress Review Meeting',
    description: 'Monthly review of progress and adjustment of development plan',
    start_time: dateTime(nextWeek, 14, 30),
    end_time: dateTime(nextWeek, 15, 30),
    location: 'Office 205',
    type: 'evaluation',
    status: 'confirmed',
    color: 'purple',
    beneficiary_id: 2,
    beneficiary: {
      id: 2,
      name: 'Jane Smith',
      email: 'jane.smith@example.com'
    },
    trainer_id: 2,
    trainer: {
      id: 2,
      name: 'Michael Chen',
      email: 'michael.chen@example.com'
    },
    notes: 'Prepare progress reports and updated development plan',
    is_google_synced: true,
    google_event_id: 'jkl012'
  },
  {
    id: 7,
    title: 'Team Project Work Session',
    description: 'Collaborative work on the final group project',
    start_time: dateTime(twoWeeksFromNow, 10, 0),
    end_time: dateTime(twoWeeksFromNow, 15, 0),
    location: 'Project Space, Floor 2',
    type: 'session',
    status: 'confirmed',
    color: 'blue',
    beneficiary_id: 3,
    beneficiary: {
      id: 3,
      name: 'Robert Johnson',
      email: 'robert.johnson@example.com'
    },
    trainer_id: 1,
    trainer: {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah.johnson@example.com'
    },
    notes: 'Bring project materials and documentation',
    is_google_synced: false
  },
  {
    id: 8,
    title: 'Final Evaluation Session',
    description: 'Final assessment before program completion',
    start_time: dateTime(twoWeeksFromNow, 9, 0),
    end_time: dateTime(twoWeeksFromNow, 11, 0),
    location: 'Assessment Center',
    type: 'evaluation',
    status: 'confirmed',
    color: 'purple',
    beneficiary_id: 1,
    beneficiary: {
      id: 1,
      name: 'John Doe',
      email: 'john.doe@example.com'
    },
    trainer_id: 2,
    trainer: {
      id: 2,
      name: 'Michael Chen',
      email: 'michael.chen@example.com'
    },
    notes: 'Prepare final evaluation forms and certification documents',
    is_google_synced: true,
    google_event_id: 'mno345'
  },
  {
    id: 9,
    title: 'Canceled: Group Discussion',
    description: 'Team discussion about industry trends and opportunities',
    start_time: dateTime(yesterday, 15, 0),
    end_time: dateTime(yesterday, 16, 30),
    location: 'Meeting Room B',
    type: 'meeting',
    status: 'canceled',
    color: 'green',
    beneficiary_id: null,
    trainer_id: 3,
    trainer: {
      id: 3,
      name: 'Emily Davis',
      email: 'emily.davis@example.com'
    },
    notes: 'Canceled due to trainer illness',
    is_google_synced: false
  },
  {
    id: 10,
    title: 'Job Search Strategy Session',
    description: 'Review job search progress and refine strategies',
    start_time: dateTime(nextWeek, 9, 0),
    end_time: dateTime(nextWeek, 10, 30),
    location: 'Career Center',
    type: 'session',
    status: 'confirmed',
    color: 'blue',
    beneficiary_id: 3,
    beneficiary: {
      id: 3,
      name: 'Robert Johnson',
      email: 'robert.johnson@example.com'
    },
    trainer_id: 3,
    trainer: {
      id: 3,
      name: 'Emily Davis',
      email: 'emily.davis@example.com'
    },
    notes: 'Review current job listings and application status',
    is_google_synced: true,
    google_event_id: 'pqr678'
  }
];

// Mock API responses
export const fetchMockAppointments = (startDate, endDate) => {
  // In a real app, you would filter by date range
  // For simplicity, we'll return all appointments in the mock data
  return {
    status: 200,
    data: mockAppointments
  };
};

export const fetchMockAppointment = (id) => {
  const appointment = mockAppointments.find(appt => appt.id.toString() === id.toString());
  
  if (appointment) {
    return {
      status: 200,
      data: appointment
    };
  }
  
  return {
    status: 404,
    data: { message: 'Appointment not found' }
  };
};

export const createMockAppointment = (data) => {
  // In a real app, this would create a new appointment in the database
  return {
    status: 201,
    data: {
      id: mockAppointments.length + 1,
      ...data,
      created_at: new Date().toISOString()
    }
  };
};

export const updateMockAppointment = (id, data) => {
  // In a real app, this would update an appointment in the database
  return {
    status: 200,
    data: {
      id: parseInt(id),
      ...data,
      updated_at: new Date().toISOString()
    }
  };
};

export const deleteMockAppointment = (id) => {
  // In a real app, this would delete an appointment from the database
  return {
    status: 204,
    data: null
  };
};

export const notifyMockParticipants = (id) => {
  // In a real app, this would send notifications to participants
  return {
    status: 200,
    data: { message: 'Notifications sent successfully' }
  };
};

// Mock availability data
export const mockAvailabilitySettings = {
  regular_schedule: [
    { day: 0, is_available: false, time_slots: [] }, // Sunday
    { day: 1, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Monday
    { day: 2, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Tuesday
    { day: 3, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Wednesday
    { day: 4, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Thursday
    { day: 5, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Friday
    { day: 6, is_available: false, time_slots: [] }, // Saturday
  ],
  exceptions: [
    {
      date: addDays(today, 5).toISOString().split('T')[0],
      is_available: false,
      time_slots: []
    },
    {
      date: addDays(today, 10).toISOString().split('T')[0],
      is_available: true,
      time_slots: [{ start: '10:00', end: '15:00' }]
    }
  ],
  buffer_time: 15,
  appointment_duration: 60,
  advance_notice: 24,
  max_appointments_per_day: 8,
  auto_confirm: true,
  working_hours: {
    start: '09:00',
    end: '17:00',
  },
  break_time: {
    enabled: true,
    start: '12:00',
    end: '13:00',
  },
  sync_with_google: true,
};

// Mock Google Calendar sync settings
export const mockGoogleCalendarSyncSettings = {
  is_connected: true,
  last_synced: new Date().toISOString(),
  calendars: [
    { id: 'primary', name: 'Primary Calendar', color: '#039BE5' },
    { id: 'work', name: 'Work Calendar', color: '#33B679' },
    { id: 'personal', name: 'Personal Calendar', color: '#8E24AA' },
  ],
  selected_calendars: ['primary', 'work'],
  sync_options: {
    two_way_sync: true,
    sync_past_events: false,
    days_to_sync_in_past: 30,
    days_to_sync_in_future: 90,
    avoid_conflicts: true,
    auto_sync_frequency: 'hourly', // 'manual', 'hourly', 'daily'
  },
  conflict_resolution: {
    strategy: 'prompt', // 'bdc_overrides', 'google_overrides', 'prompt'
    auto_resolve_simple_conflicts: true,
  },
  sync_status: {
    total_events_synced: 42,
    last_sync_errors: [],
    last_sync_success: true,
  }
};

export const fetchMockAvailability = () => {
  return {
    status: 200,
    data: mockAvailabilitySettings
  };
};

export const updateMockAvailability = (data) => {
  return {
    status: 200,
    data: {
      ...data,
      updated_at: new Date().toISOString()
    }
  };
};

export const fetchMockGoogleCalendarSync = () => {
  return {
    status: 200,
    data: mockGoogleCalendarSyncSettings
  };
};

export const updateMockGoogleCalendarSync = (data) => {
  return {
    status: 200,
    data: {
      ...data,
      updated_at: new Date().toISOString()
    }
  };
};