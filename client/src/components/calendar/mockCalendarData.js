// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock Calendar Data
export const generateCalendarData = (userRole) => {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const day = currentDate.getDate();
  const baseEvents = [
  {
    id: 1,
    title: "JavaScript Fundamentals",
    start: new Date(year, month, day, 9, 0).toISOString(),
    end: new Date(year, month, day, 10, 30).toISOString(),
    type: "class",
    description: "Introduction to JavaScript programming",
    location: "Room 101",
    attendees: 15,
    color: "#3B82F6",
    instructor: "John Smith"
  },
  {
    id: 2,
    title: "Team Meeting",
    start: new Date(year, month, day, 14, 0).toISOString(),
    end: new Date(year, month, day, 15, 0).toISOString(),
    type: "meeting",
    description: "Weekly team sync",
    location: "Conference Room A",
    attendees: 8,
    color: "#10B981",
    organizer: "Sarah Johnson"
  },
  {
    id: 3,
    title: "Python Workshop",
    start: new Date(year, month, day + 1, 10, 0).toISOString(),
    end: new Date(year, month, day + 1, 12, 0).toISOString(),
    type: "workshop",
    description: "Advanced Python techniques",
    location: "Lab 2",
    attendees: 20,
    color: "#8B5CF6",
    instructor: "Dr. Emily Chen"
  },
  {
    id: 4,
    title: "Code Review Session",
    start: new Date(year, month, day + 2, 13, 0).toISOString(),
    end: new Date(year, month, day + 2, 14, 30).toISOString(),
    type: "review",
    description: "Reviewing recent project submissions",
    location: "Online",
    attendees: 5,
    color: "#F59E0B",
    reviewer: "Mike Wilson"
  },
  {
    id: 5,
    title: "React Advanced Topics",
    start: new Date(year, month, day + 3, 9, 0).toISOString(),
    end: new Date(year, month, day + 3, 11, 0).toISOString(),
    type: "class",
    description: "State management and optimization",
    location: "Room 202",
    attendees: 12,
    color: "#3B82F6",
    instructor: "Lisa Brown"
  },
  {
    id: 6,
    title: "Career Counseling",
    start: new Date(year, month, day + 4, 15, 0).toISOString(),
    end: new Date(year, month, day + 4, 16, 0).toISOString(),
    type: "appointment",
    description: "One-on-one career guidance",
    location: "Office 305",
    attendees: 1,
    color: "#EC4899",
    counselor: "Mark Davis"
  },
  {
    id: 7,
    title: "Hackathon",
    start: new Date(year, month, day + 7, 9, 0).toISOString(),
    end: new Date(year, month, day + 7, 18, 0).toISOString(),
    type: "event",
    description: "24-hour coding challenge",
    location: "Main Hall",
    attendees: 50,
    color: "#10B981",
    organizer: "Tech Club"
  },
  {
    id: 8,
    title: "Database Design Workshop",
    start: new Date(year, month, day + 14, 14, 0).toISOString(),
    end: new Date(year, month, day + 14, 17, 0).toISOString(),
    type: "workshop",
    description: "SQL and NoSQL fundamentals",
    location: "Lab 3",
    attendees: 18,
    color: "#8B5CF6",
    instructor: "Prof. Robert Lee"
  }];

  // Customize events based on role
  if (userRole === 'trainer') {
    return {
      events: [
      ...baseEvents,
      {
        id: 9,
        title: "Faculty Meeting",
        start: new Date(year, month, day + 5, 16, 0).toISOString(),
        end: new Date(year, month, day + 5, 17, 30).toISOString(),
        type: "meeting",
        description: "Monthly faculty discussion",
        location: "Faculty Lounge",
        attendees: 15,
        color: "#6B7280",
        organizer: "Dean Smith"
      },
      {
        id: 10,
        title: "Curriculum Planning",
        start: new Date(year, month, day + 10, 10, 0).toISOString(),
        end: new Date(year, month, day + 10, 12, 0).toISOString(),
        type: "planning",
        description: "Next semester course planning",
        location: "Room 401",
        attendees: 6,
        color: "#F59E0B",
        lead: "Academic Director"
      }],

      availableSlots: generateAvailableSlots(),
      teachingSchedule: generateTeachingSchedule()
    };
  } else if (userRole === 'student') {
    return {
      events: baseEvents.filter((event) =>
      ['class', 'workshop', 'event', 'appointment'].includes(event.type)
      ),
      upcomingDeadlines: generateUpcomingDeadlines(),
      studyGroups: generateStudyGroups()
    };
  } else if (userRole === 'admin' || userRole === 'tenant_admin') {
    return {
      events: [
      ...baseEvents,
      {
        id: 11,
        title: "Board Meeting",
        start: new Date(year, month, day + 15, 15, 0).toISOString(),
        end: new Date(year, month, day + 15, 17, 0).toISOString(),
        type: "meeting",
        description: "Quarterly review meeting",
        location: "Board Room",
        attendees: 10,
        color: "#DC2626",
        organizer: "CEO"
      },
      {
        id: 12,
        title: "Budget Review",
        start: new Date(year, month, day + 20, 10, 0).toISOString(),
        end: new Date(year, month, day + 20, 12, 0).toISOString(),
        type: "review",
        description: "Annual budget planning",
        location: "Finance Dept",
        attendees: 5,
        color: "#F59E0B",
        lead: "CFO"
      }],

      resourceUtilization: generateResourceUtilization(),
      facilityBookings: generateFacilityBookings()
    };
  }
  return { events: baseEvents };
};
// Generate available time slots for trainers
export const generateAvailableSlots = () => {
  const slots = [];
  const currentDate = new Date();
  for (let i = 0; i < 14; i++) {
    const date = new Date(currentDate);
    date.setDate(currentDate.getDate() + i);
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    // Morning slots
    slots.push({
      id: `slot-${i}-1`,
      date: date.toISOString().split('T')[0],
      start: "09:00",
      end: "10:00",
      available: Math.random() > 0.3,
      type: "consultation"
    });
    // Afternoon slots
    slots.push({
      id: `slot-${i}-2`,
      date: date.toISOString().split('T')[0],
      start: "14:00",
      end: "15:00",
      available: Math.random() > 0.4,
      type: "consultation"
    });
    // Evening slots
    slots.push({
      id: `slot-${i}-3`,
      date: date.toISOString().split('T')[0],
      start: "16:00",
      end: "17:00",
      available: Math.random() > 0.5,
      type: "consultation"
    });
  }
  return slots;
};
// Generate teaching schedule
export const generateTeachingSchedule = () => {
  return {
    monday: [
    { time: "09:00-10:30", subject: "JavaScript Basics", room: "Lab A", students: 25 },
    { time: "14:00-15:30", subject: "React Development", room: "Lab B", students: 20 }],

    tuesday: [
    { time: "10:00-12:00", subject: "Python Programming", room: "Lab C", students: 22 },
    { time: "14:00-16:00", subject: "Database Design", room: "Room 201", students: 18 }],

    wednesday: [
    { time: "09:00-10:30", subject: "Web APIs", room: "Lab A", students: 24 },
    { time: "13:00-14:30", subject: "Git & Version Control", room: "Lab D", students: 30 }],

    thursday: [
    { time: "10:00-12:00", subject: "Advanced JavaScript", room: "Lab B", students: 15 },
    { time: "14:00-16:00", subject: "Mobile Development", room: "Lab C", students: 19 }],

    friday: [
    { time: "09:00-11:00", subject: "Project Workshop", room: "Main Lab", students: 35 },
    { time: "13:00-15:00", subject: "Code Review", room: "Room 301", students: 12 }]

  };
};
// Generate upcoming deadlines for students
export const generateUpcomingDeadlines = () => {
  const currentDate = new Date();
  return [
  {
    id: 1,
    title: "JavaScript Final Project",
    dueDate: new Date(currentDate.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    course: "JavaScript Fundamentals",
    type: "project",
    priority: "high"
  },
  {
    id: 2,
    title: "React Component Assignment",
    dueDate: new Date(currentDate.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    course: "React Development",
    type: "assignment",
    priority: "medium"
  },
  {
    id: 3,
    title: "Database Design Quiz",
    dueDate: new Date(currentDate.getTime() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    course: "Database Fundamentals",
    type: "quiz",
    priority: "medium"
  },
  {
    id: 4,
    title: "Python Lab Report",
    dueDate: new Date(currentDate.getTime() + 10 * 24 * 60 * 60 * 1000).toISOString(),
    course: "Python Programming",
    type: "report",
    priority: "low"
  }];

};
// Generate study groups
export const generateStudyGroups = () => {
  return [
  {
    id: 1,
    name: "JavaScript Study Group",
    members: 8,
    nextMeeting: "Monday, 4:00 PM",
    location: "Library Room 2A",
    topic: "Async/Await patterns"
  },
  {
    id: 2,
    name: "React Developers",
    members: 6,
    nextMeeting: "Wednesday, 5:00 PM",
    location: "Student Center",
    topic: "State management"
  },
  {
    id: 3,
    name: "Python Enthusiasts",
    members: 10,
    nextMeeting: "Friday, 3:00 PM",
    location: "Lab 5",
    topic: "Machine Learning basics"
  }];

};
// Generate resource utilization data
export const generateResourceUtilization = () => {
  return {
    rooms: [
    { name: "Lab A", utilization: 85, capacity: 30 },
    { name: "Lab B", utilization: 72, capacity: 25 },
    { name: "Lab C", utilization: 90, capacity: 35 },
    { name: "Conference Room A", utilization: 65, capacity: 15 },
    { name: "Main Hall", utilization: 45, capacity: 100 }],

    equipment: [
    { name: "Projectors", available: 8, total: 10 },
    { name: "Laptops", available: 25, total: 40 },
    { name: "Whiteboards", available: 15, total: 20 }]

  };
};
// Generate facility bookings
export const generateFacilityBookings = () => {
  const currentDate = new Date();
  return [
  {
    id: 1,
    facility: "Conference Room A",
    bookedBy: "Marketing Team",
    date: new Date(currentDate.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    time: "10:00-12:00",
    purpose: "Product Launch Meeting"
  },
  {
    id: 2,
    facility: "Main Hall",
    bookedBy: "Student Association",
    date: new Date(currentDate.getTime() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    time: "14:00-18:00",
    purpose: "Annual Tech Fest"
  },
  {
    id: 3,
    facility: "Lab C",
    bookedBy: "External Training",
    date: new Date(currentDate.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    time: "09:00-17:00",
    purpose: "Corporate Workshop"
  }];

};
// Generate appointment types
export const generateAppointmentTypes = () => {
  return [
  { id: 1, name: "Academic Counseling", duration: 30, color: "#3B82F6" },
  { id: 2, name: "Career Guidance", duration: 45, color: "#10B981" },
  { id: 3, name: "Technical Support", duration: 20, color: "#F59E0B" },
  { id: 4, name: "Project Review", duration: 60, color: "#8B5CF6" },
  { id: 5, name: "Exam Preparation", duration: 45, color: "#EC4899" },
  { id: 6, name: "Course Registration", duration: 15, color: "#6B7280" }];

};