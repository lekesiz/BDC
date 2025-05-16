import { addDays, subDays, subHours, subMinutes } from 'date-fns';

// Generate dates
const now = new Date();
const yesterday = subDays(now, 1);
const twoDaysAgo = subDays(now, 2);
const lastWeek = subDays(now, 7);

// Mock conversations data
export const mockConversations = [
  {
    id: 1,
    title: null, // One-on-one conversation
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      { id: 2, name: 'Michael Chen' }
    ],
    is_group: false,
    created_at: lastWeek.toISOString(),
    updated_at: subHours(now, 1).toISOString(),
    last_message: {
      content: "I'll send you the updated training materials tomorrow.",
      created_at: subHours(now, 1).toISOString(),
      sender_id: 2,
      sender_name: 'Michael Chen'
    },
    unread_count: 2
  },
  {
    id: 2,
    title: 'Training Team',
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      { id: 2, name: 'Michael Chen' },
      { id: 3, name: 'Emily Davis' },
      { id: 4, name: 'Robert Wilson' }
    ],
    is_group: true,
    created_at: twoDaysAgo.toISOString(),
    updated_at: yesterday.toISOString(),
    last_message: {
      content: "Let's meet next Monday to discuss the new training modules.",
      created_at: yesterday.toISOString(),
      sender_id: 3,
      sender_name: 'Emily Davis'
    },
    unread_count: 0
  },
  {
    id: 3,
    title: null, // One-on-one conversation
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      { id: 3, name: 'Emily Davis' }
    ],
    is_group: false,
    created_at: twoDaysAgo.toISOString(),
    updated_at: twoDaysAgo.toISOString(),
    last_message: {
      content: "Thank you for helping with the workshop yesterday!",
      created_at: twoDaysAgo.toISOString(),
      sender_id: 1,
      sender_name: 'Sarah Johnson'
    },
    unread_count: 0
  },
  {
    id: 4,
    title: 'Software Development Course',
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      { id: 2, name: 'Michael Chen' },
      { id: 5, name: 'Jennifer Lopez' }
    ],
    is_group: true,
    created_at: lastWeek.toISOString(),
    updated_at: subDays(now, 3).toISOString(),
    last_message: {
      content: "I've uploaded the programming exercises to the shared folder.",
      created_at: subDays(now, 3).toISOString(),
      sender_id: 2,
      sender_name: 'Michael Chen'
    },
    unread_count: 0
  },
  {
    id: 5,
    title: null, // One-on-one conversation
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      { id: 4, name: 'Robert Wilson' }
    ],
    is_group: false,
    created_at: subDays(now, 4).toISOString(),
    updated_at: subDays(now, 4).toISOString(),
    last_message: {
      content: "Can we schedule a meeting to review the latest evaluation results?",
      created_at: subDays(now, 4).toISOString(),
      sender_id: 4,
      sender_name: 'Robert Wilson'
    },
    unread_count: 0
  }
];

// Mock messages data for each conversation
export const mockMessages = {
  // Conversation with Michael Chen
  1: [
    {
      id: 1,
      conversation_id: 1,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Hi Michael, how's the new training module coming along?",
      created_at: subDays(now, 1).toISOString(),
      is_read: true
    },
    {
      id: 2,
      conversation_id: 1,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "Hi Sarah, it's going well. I'm working on the final exercises now.",
      created_at: subDays(now, 1).toISOString(),
      is_read: true
    },
    {
      id: 3,
      conversation_id: 1,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Great! When do you think it will be ready for review?",
      created_at: subDays(now, 1).toISOString(),
      is_read: true
    },
    {
      id: 4,
      conversation_id: 1,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "I should have it ready by tomorrow afternoon. I just need to finalize the assessment questions.",
      created_at: subDays(now, 1).toISOString(),
      is_read: true
    },
    {
      id: 5,
      conversation_id: 1,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Perfect. We need to launch it by the end of the week.",
      created_at: subDays(now, 1).toISOString(),
      is_read: true
    },
    {
      id: 6,
      conversation_id: 1,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "No problem. Also, do you have the latest feedback from the last training session?",
      created_at: subHours(now, 2).toISOString(),
      is_read: true
    },
    {
      id: 7,
      conversation_id: 1,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Yes, I'll email it to you shortly.",
      created_at: subHours(now, 2).toISOString(),
      is_read: true
    },
    {
      id: 8,
      conversation_id: 1,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "Thanks! I'll incorporate that feedback into the new materials.",
      created_at: subHours(now, 1).toISOString(),
      is_read: false
    },
    {
      id: 9,
      conversation_id: 1,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "I'll send you the updated training materials tomorrow.",
      created_at: subHours(now, 1).toISOString(),
      is_read: false
    }
  ],
  
  // Training Team group
  2: [
    {
      id: 10,
      conversation_id: 2,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Hi team, I've created this group to coordinate our training efforts.",
      created_at: twoDaysAgo.toISOString(),
      is_read: true
    },
    {
      id: 11,
      conversation_id: 2,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "Great idea! This will make it easier to keep everyone in the loop.",
      created_at: twoDaysAgo.toISOString(),
      is_read: true
    },
    {
      id: 12,
      conversation_id: 2,
      sender_id: 3,
      sender_name: 'Emily Davis',
      content: "I agree. We should discuss the upcoming training schedule.",
      created_at: twoDaysAgo.toISOString(),
      is_read: true
    },
    {
      id: 13,
      conversation_id: 2,
      sender_id: 4,
      sender_name: 'Robert Wilson',
      content: "I've been working on some new assessment methods we could implement.",
      created_at: yesterday.toISOString(),
      is_read: true
    },
    {
      id: 14,
      conversation_id: 2,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "That sounds interesting, Robert. Can you share more details?",
      created_at: yesterday.toISOString(),
      is_read: true
    },
    {
      id: 15,
      conversation_id: 2,
      sender_id: 3,
      sender_name: 'Emily Davis',
      content: "Let's meet next Monday to discuss the new training modules.",
      created_at: yesterday.toISOString(),
      is_read: true
    }
  ],
  
  // Conversation with Emily Davis
  3: [
    {
      id: 16,
      conversation_id: 3,
      sender_id: 3,
      sender_name: 'Emily Davis',
      content: "Hi Sarah, great job with the workshop today!",
      created_at: subDays(twoDaysAgo, 1).toISOString(),
      is_read: true
    },
    {
      id: 17,
      conversation_id: 3,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Thanks Emily! The participants seemed really engaged.",
      created_at: subDays(twoDaysAgo, 1).toISOString(),
      is_read: true
    },
    {
      id: 18,
      conversation_id: 3,
      sender_id: 3,
      sender_name: 'Emily Davis',
      content: "Definitely. I think the hands-on exercises were particularly effective.",
      created_at: twoDaysAgo.toISOString(),
      is_read: true
    },
    {
      id: 19,
      conversation_id: 3,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Thank you for helping with the workshop yesterday!",
      created_at: twoDaysAgo.toISOString(),
      is_read: true
    }
  ],
  
  // Software Development Course group
  4: [
    {
      id: 20,
      conversation_id: 4,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Welcome to the Software Development Course group chat!",
      created_at: lastWeek.toISOString(),
      is_read: true
    },
    {
      id: 21,
      conversation_id: 4,
      sender_id: 5,
      sender_name: 'Jennifer Lopez',
      content: "Thanks for setting this up. When does the course start?",
      created_at: lastWeek.toISOString(),
      is_read: true
    },
    {
      id: 22,
      conversation_id: 4,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "We're planning to start next month. I'm finalizing the curriculum now.",
      created_at: lastWeek.toISOString(),
      is_read: true
    },
    {
      id: 23,
      conversation_id: 4,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Michael, can you share the draft syllabus when it's ready?",
      created_at: subDays(now, 4).toISOString(),
      is_read: true
    },
    {
      id: 24,
      conversation_id: 4,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "Sure thing. I'll have it ready by tomorrow.",
      created_at: subDays(now, 3).toISOString(),
      is_read: true
    },
    {
      id: 25,
      conversation_id: 4,
      sender_id: 2,
      sender_name: 'Michael Chen',
      content: "I've uploaded the programming exercises to the shared folder.",
      created_at: subDays(now, 3).toISOString(),
      is_read: true
    }
  ],
  
  // Conversation with Robert Wilson
  5: [
    {
      id: 26,
      conversation_id: 5,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Hi Robert, how are the evaluations coming along?",
      created_at: subDays(now, 5).toISOString(),
      is_read: true
    },
    {
      id: 27,
      conversation_id: 5,
      sender_id: 4,
      sender_name: 'Robert Wilson',
      content: "Hi Sarah, I've completed about 70% of them so far.",
      created_at: subDays(now, 5).toISOString(),
      is_read: true
    },
    {
      id: 28,
      conversation_id: 5,
      sender_id: 1,
      sender_name: 'Sarah Johnson',
      content: "Great progress! When do you expect to finish the rest?",
      created_at: subDays(now, 4).toISOString(),
      is_read: true
    },
    {
      id: 29,
      conversation_id: 5,
      sender_id: 4,
      sender_name: 'Robert Wilson',
      content: "I should be done by the end of the week. The results are looking promising.",
      created_at: subDays(now, 4).toISOString(),
      is_read: true
    },
    {
      id: 30,
      conversation_id: 5,
      sender_id: 4,
      sender_name: 'Robert Wilson',
      content: "Can we schedule a meeting to review the latest evaluation results?",
      created_at: subDays(now, 4).toISOString(),
      is_read: true
    }
  ]
};

// Mock notifications data
export const mockNotifications = [
  {
    id: 1,
    user_id: 1,
    title: 'New Message',
    content: 'Michael Chen sent you a message: "I\'ll send you the updated training materials tomorrow."',
    type: 'message',
    created_at: subHours(now, 1).toISOString(),
    is_read: false,
    link: '/messaging',
    action_text: 'Reply'
  },
  {
    id: 2,
    user_id: 1,
    title: 'Appointment Reminder',
    content: 'You have a training session with John Doe tomorrow at 10:00 AM',
    type: 'appointment',
    created_at: subHours(now, 2).toISOString(),
    is_read: false,
    link: '/calendar',
    action_text: 'View Calendar'
  },
  {
    id: 3,
    user_id: 1,
    title: 'Document Shared',
    content: 'Emily Davis shared a document with you: "Communication Skills Workshop.pptx"',
    type: 'document',
    created_at: yesterday.toISOString(),
    is_read: true,
    link: '/documents/3',
    action_text: 'View Document'
  },
  {
    id: 4,
    user_id: 1,
    title: 'New Comment',
    content: 'Michael Chen commented on "Beneficiary Progress Tracker.xlsx"',
    type: 'document',
    created_at: yesterday.toISOString(),
    is_read: true,
    link: '/documents/5',
    action_text: 'View Comments'
  },
  {
    id: 5,
    user_id: 1,
    title: 'Appointment Updated',
    content: 'Your appointment with Jane Smith has been rescheduled to Friday at 2:00 PM',
    type: 'appointment',
    created_at: twoDaysAgo.toISOString(),
    is_read: true,
    link: '/calendar',
    action_text: 'View Calendar'
  },
  {
    id: 6,
    user_id: 1,
    title: 'System Update',
    content: 'The system will be undergoing maintenance this weekend. Please save your work before Sunday at midnight.',
    type: 'system',
    created_at: twoDaysAgo.toISOString(),
    is_read: true,
    link: null
  },
  {
    id: 7,
    user_id: 1,
    title: 'New Beneficiary',
    content: 'A new beneficiary, James Brown, has been assigned to you',
    type: 'user',
    created_at: subDays(now, 3).toISOString(),
    is_read: true,
    link: '/beneficiaries/5',
    action_text: 'View Profile'
  },
  {
    id: 8,
    user_id: 1,
    title: 'Training Evaluation',
    content: 'Robert Wilson has completed a trainer evaluation for you',
    type: 'user',
    created_at: subDays(now, 4).toISOString(),
    is_read: true,
    link: '/evaluations/trainer-evaluations/7',
    action_text: 'View Evaluation'
  },
  {
    id: 9,
    user_id: 1,
    title: 'New Group Message',
    content: 'Emily Davis posted in "Training Team": "Let\'s meet next Monday to discuss the new training modules."',
    type: 'message',
    created_at: yesterday.toISOString(),
    is_read: true,
    link: '/messaging',
    action_text: 'View Conversation'
  },
  {
    id: 10,
    user_id: 1,
    title: 'Document Updated',
    content: 'Michael Chen updated "Programming Fundamentals.pdf"',
    type: 'document',
    created_at: subDays(now, 2).toISOString(),
    is_read: true,
    link: '/documents/2',
    action_text: 'View Document'
  }
];

// Mock notification settings data
export const mockNotificationSettings = {
  channels: {
    email: true,
    in_app: true,
    push: false,
  },
  categories: {
    appointments: {
      new_appointment: true,
      appointment_reminder: true,
      appointment_update: true,
      appointment_cancellation: true,
    },
    documents: {
      document_shared: true,
      document_updated: true,
      document_commented: true,
    },
    messages: {
      new_message: true,
      message_reply: true,
    },
    users: {
      new_user: false,
      user_update: false,
    },
    system: {
      system_announcement: true,
      maintenance_alert: true,
    },
  },
  preferences: {
    daily_digest: false,
    quiet_hours: {
      enabled: false,
      start: '22:00',
      end: '08:00',
    },
  },
};

// Mock API functions
export const fetchConversations = () => {
  return {
    status: 200,
    data: mockConversations
  };
};

export const fetchMessages = (conversationId) => {
  const messages = mockMessages[conversationId] || [];
  
  return {
    status: 200,
    data: messages
  };
};

export const sendMessage = (conversationId, message) => {
  const newMessage = {
    id: Math.floor(Math.random() * 1000) + 100, // Generate a random ID
    conversation_id: parseInt(conversationId),
    sender_id: 1, // Current user
    sender_name: 'Sarah Johnson', // Current user
    content: message.content,
    created_at: new Date().toISOString(),
    is_read: true
  };
  
  return {
    status: 201,
    data: newMessage
  };
};

export const markConversationAsRead = (conversationId) => {
  return {
    status: 200,
    data: {
      conversation_id: parseInt(conversationId),
      unread_count: 0
    }
  };
};

export const createConversation = (data) => {
  // Create a new conversation with the specified participants
  const newConversation = {
    id: Math.floor(Math.random() * 1000) + 100, // Generate a random ID
    title: data.title || null,
    participants: [
      { id: 1, name: 'Sarah Johnson' }, // Current user
      ...data.participant_ids.map(id => {
        const user = [
          { id: 2, name: 'Michael Chen' },
          { id: 3, name: 'Emily Davis' },
          { id: 4, name: 'Robert Wilson' },
          { id: 5, name: 'Jennifer Lopez' }
        ].find(u => u.id === id);
        
        return user || { id, name: `User ${id}` };
      })
    ],
    is_group: data.participant_ids.length > 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_message: null,
    unread_count: 0
  };
  
  return {
    status: 201,
    data: newConversation
  };
};

export const fetchNotifications = (params = {}) => {
  let notifications = [...mockNotifications];
  
  // Apply filters
  if (params.filter) {
    if (params.filter === 'unread') {
      notifications = notifications.filter(n => !n.is_read);
    } else {
      notifications = notifications.filter(n => n.type === params.filter);
    }
  }
  
  // Sort by created_at (newest first)
  notifications.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  
  // Apply pagination
  const page = params.page || 1;
  const limit = params.limit || 10;
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  const paginatedNotifications = notifications.slice(startIndex, endIndex);
  
  return {
    status: 200,
    data: {
      notifications: paginatedNotifications,
      total: notifications.length
    }
  };
};

export const markNotificationAsRead = (id) => {
  return {
    status: 200,
    data: {
      id: parseInt(id),
      is_read: true
    }
  };
};

export const markAllNotificationsAsRead = () => {
  return {
    status: 200,
    data: {
      success: true,
      message: 'All notifications marked as read'
    }
  };
};

export const fetchNotificationSettings = () => {
  return {
    status: 200,
    data: mockNotificationSettings
  };
};

export const updateNotificationSettings = (settings) => {
  return {
    status: 200,
    data: settings
  };
};