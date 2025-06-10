// TODO: i18n - processed
/**
 * Mock data for student portal
 */
import { addDays, addHours, subDays, format } from 'date-fns';import { useTranslation } from "react-i18next";
const NOW = new Date();
const FILE_SIZES = {
  small: { min: 10 * 1024, max: 500 * 1024 }, // 10KB - 500KB
  medium: { min: 500 * 1024, max: 5 * 1024 * 1024 }, // 500KB - 5MB
  large: { min: 5 * 1024 * 1024, max: 20 * 1024 * 1024 } // 5MB - 20MB
};
// Sample dashboard data
export const dashboardData = {
  program: {
    id: 1,
    name: "Web Development Bootcamp",
    startDate: subDays(NOW, 30).toISOString(),
    expectedEndDate: addDays(NOW, 60).toISOString()
  },
  progress: 65,
  nextSession: {
    id: 101,
    title: "JavaScript Advanced Concepts",
    type: "lecture",
    date: addDays(NOW, 1).toISOString()
  },
  primaryTrainer: {
    id: 201,
    name: "Sarah Johnson",
    email: "sarah.j@bdctrainer.com"
  },
  modules: [
  {
    id: 1,
    name: "HTML/CSS Fundamentals",
    status: "completed",
    completion: 100
  },
  {
    id: 2,
    name: "JavaScript Basics",
    status: "completed",
    completion: 100
  },
  {
    id: 3,
    name: "JavaScript Advanced",
    status: "in_progress",
    completion: 60
  },
  {
    id: 4,
    name: "React Fundamentals",
    status: "not_started",
    completion: 0
  },
  {
    id: 5,
    name: "Backend Basics",
    status: "not_started",
    completion: 0
  }],

  skills: [
  {
    id: 1,
    name: "HTML",
    currentLevel: 4,
    maxLevel: 5
  },
  {
    id: 2,
    name: "CSS",
    currentLevel: 3,
    maxLevel: 5
  },
  {
    id: 3,
    name: "JavaScript",
    currentLevel: 3,
    maxLevel: 5
  },
  {
    id: 4,
    name: "React",
    currentLevel: 1,
    maxLevel: 5
  }],

  upcomingSessions: [
  {
    id: 101,
    title: "JavaScript Advanced Concepts",
    type: "lecture",
    date: addDays(NOW, 1).toISOString(),
    trainer: "Sarah Johnson"
  },
  {
    id: 102,
    title: "Pair Programming Workshop",
    type: "workshop",
    date: addDays(NOW, 3).toISOString(),
    trainer: "David Chen"
  },
  {
    id: 103,
    title: "Code Review Session",
    type: "discussion",
    date: addDays(NOW, 5).toISOString(),
    trainer: "Sarah Johnson"
  }],

  notifications: [
  {
    id: 1,
    type: "schedule",
    message: "New session scheduled: JavaScript Advanced Concepts on " + format(addDays(NOW, 1), 'MMMM d, yyyy'),
    timestamp: subDays(NOW, 1).toISOString()
  },
  {
    id: 2,
    type: "progress",
    message: "You've completed the JavaScript Basics module! Great job!",
    timestamp: subDays(NOW, 2).toISOString()
  },
  {
    id: 3,
    type: "message",
    message: "New message from Sarah Johnson: 'Great work on your last assignment!'",
    timestamp: subDays(NOW, 3).toISOString()
  },
  {
    id: 4,
    type: "reminder",
    message: "Don't forget to submit your project by this Friday",
    timestamp: subDays(NOW, 4).toISOString()
  }]

};
// Sample courses data
export const coursesData = [
{
  id: 1,
  title: "Web Development Bootcamp",
  description: "A comprehensive course covering front-end and back-end web development",
  status: "in_progress",
  totalDuration: 4800, // in minutes
  modules: [
  {
    id: 1,
    title: "HTML/CSS Fundamentals",
    description: "Learn the basics of HTML and CSS",
    status: "completed",
    duration: 600,
    lessonCount: 5
  },
  {
    id: 2,
    title: "JavaScript Basics",
    description: "Introduction to JavaScript programming",
    status: "completed",
    duration: 720,
    lessonCount: 6
  },
  {
    id: 3,
    title: "JavaScript Advanced",
    description: "Advanced JavaScript concepts and patterns",
    status: "in_progress",
    duration: 840,
    lessonCount: 7
  },
  {
    id: 4,
    title: "React Fundamentals",
    description: "Building user interfaces with React",
    status: "not_started",
    duration: 900,
    lessonCount: 8
  },
  {
    id: 5,
    title: "Backend Basics",
    description: "Introduction to server-side development",
    status: "not_started",
    duration: 780,
    lessonCount: 6
  },
  {
    id: 6,
    title: "Database Integration",
    description: "Working with databases and ORMs",
    status: "not_started",
    duration: 720,
    lessonCount: 6
  },
  {
    id: 7,
    title: "Final Project",
    description: "Building a complete web application",
    status: "not_started",
    duration: 240,
    lessonCount: 2
  }]

},
{
  id: 2,
  title: "Career Development",
  description: "Prepare for your career in tech with resume building, interview skills, and more",
  status: "not_started",
  totalDuration: 600,
  modules: [
  {
    id: 8,
    title: "Resume Building",
    description: "Create an effective technical resume",
    status: "not_started",
    duration: 120,
    lessonCount: 2
  },
  {
    id: 9,
    title: "Interview Preparation",
    description: "Techniques for technical interviews",
    status: "not_started",
    duration: 180,
    lessonCount: 3
  },
  {
    id: 10,
    title: "Portfolio Development",
    description: "Build a strong portfolio to showcase your skills",
    status: "not_started",
    duration: 120,
    lessonCount: 2
  },
  {
    id: 11,
    title: "Networking Strategies",
    description: "Effective networking in the tech industry",
    status: "not_started",
    duration: 180,
    lessonCount: 3
  }]

}];

// Sample module data (for module detail page)
export const moduleData = {
  1: { // HTML/CSS Fundamentals
    id: 1,
    title: "HTML/CSS Fundamentals",
    description: "Learn the basics of HTML and CSS to build the foundation of any web application",
    status: "completed",
    duration: 600,
    courseId: 1,
    course: "Web Development Bootcamp",
    instructor: "Sarah Johnson",
    instructorRole: "Lead Instructor",
    objectives: [
    "Understand HTML document structure",
    "Create semantic HTML markup",
    "Style web pages with CSS",
    "Implement responsive designs",
    "Build layouts with Flexbox and Grid"],

    prerequisites: [
    "Basic computer skills",
    "Familiarity with using a web browser"],

    lessons: [
    {
      id: 101,
      title: "Introduction to HTML",
      type: "video",
      duration: 45,
      status: "completed",
      videoUrl: "https://example.com/videos/intro-html",
      description: "An introduction to HTML, its history, and purpose",
      content: "<p>HTML (Hypertext Markup Language) is the standard markup language for documents designed to be displayed in a web browser. It defines the structure of web content.</p>",
      resources: [
      {
        id: 1001,
        name: "HTML Cheat Sheet.pdf",
        type: "PDF",
        size: "1.2 MB"
      },
      {
        id: 1002,
        name: "Lecture Slides.pptx",
        type: "PPTX",
        size: "2.5 MB"
      }]

    },
    {
      id: 102,
      title: "HTML Elements and Structure",
      type: "video",
      duration: 60,
      status: "completed",
      videoUrl: "https://example.com/videos/html-elements",
      description: "Learn about HTML elements and how to structure a webpage",
      content: "<p>In this lesson, we'll explore the various HTML elements and how they're used to create structured content.</p>",
      resources: [
      {
        id: 1003,
        name: "HTML Elements Reference.pdf",
        type: "PDF",
        size: "1.8 MB"
      }]

    },
    {
      id: 103,
      title: "Introduction to CSS",
      type: "video",
      duration: 45,
      status: "completed",
      videoUrl: "https://example.com/videos/intro-css",
      description: "An introduction to CSS and styling web pages",
      content: "<p>CSS (Cascading Style Sheets) is used to style and lay out web pages — for example, to alter the font, color, size, and spacing of your content.</p>",
      resources: [
      {
        id: 1004,
        name: "CSS Basics.pdf",
        type: "PDF",
        size: "1.5 MB"
      }]

    },
    {
      id: 104,
      title: "CSS Selectors and Properties",
      type: "video",
      duration: 60,
      status: "completed",
      videoUrl: "https://example.com/videos/css-selectors",
      description: "Learn about CSS selectors and properties for styling elements",
      content: "<p>CSS selectors are patterns used to select HTML elements. We'll explore different types of selectors and the properties you can apply to them.</p>",
      resources: [
      {
        id: 1005,
        name: "CSS Selectors Cheat Sheet.pdf",
        type: "PDF",
        size: "1.3 MB"
      }]

    },
    {
      id: 105,
      title: "Building Responsive Layouts",
      type: "presentation",
      duration: 90,
      status: "completed",
      description: "Learn to create responsive layouts with Flexbox and Grid",
      content: "<p>In modern web development, it's crucial to build websites that look good on all devices. In this lesson, we'll explore responsive design techniques.</p>",
      resources: [
      {
        id: 1006,
        name: "Responsive Design Guide.pdf",
        type: "PDF",
        size: "2.2 MB"
      },
      {
        id: 1007,
        name: "Flexbox and Grid Examples.zip",
        type: "ZIP",
        size: "3.5 MB"
      }]

    }],

    discussions: [
    {
      id: 201,
      author: "John Smith",
      timestamp: subDays(NOW, 15).toISOString(),
      message: "I'm having trouble with the flexbox alignment in the responsive layouts exercise. Can someone help?",
      replies: [
      {
        id: 301,
        author: "Sarah Johnson",
        timestamp: subDays(NOW, 15).toISOString(),
        message: "Make sure you're setting the correct 'justify-content' and 'align-items' properties. You might want to check the Flexbox guide in the resources."
      },
      {
        id: 302,
        author: "Maria Garcia",
        timestamp: subDays(NOW, 14).toISOString(),
        message: "I had the same issue! The trick is to understand the main axis vs cross axis concept."
      }]

    },
    {
      id: 202,
      author: "Emily Wilson",
      timestamp: subDays(NOW, 10).toISOString(),
      message: "The CSS Grid layout is amazing for complex layouts. I'm using it for my personal project already!",
      replies: []
    }]

  },
  3: { // JavaScript Advanced
    id: 3,
    title: "JavaScript Advanced",
    description: "Take your JavaScript skills to the next level with advanced concepts and patterns",
    status: "in_progress",
    duration: 840,
    courseId: 1,
    course: "Web Development Bootcamp",
    instructor: "David Chen",
    instructorRole: "Technical Mentor",
    objectives: [
    "Understand JavaScript closures and scope",
    "Work with advanced array methods",
    "Implement asynchronous programming with Promises",
    "Use modern JavaScript features (ES6+)",
    "Apply design patterns in JavaScript"],

    prerequisites: [
    "JavaScript Basics module",
    "Understanding of functions and objects"],

    lessons: [
    {
      id: 301,
      title: "Closures and Scope",
      type: "video",
      duration: 60,
      status: "completed",
      videoUrl: "https://example.com/videos/js-closures",
      description: "Understanding JavaScript closures and scope chains",
      content: "<p>Closures are a fundamental JavaScript concept. They happen when a function remembers and accesses variables from outside its own scope.</p>",
      resources: [
      {
        id: 3001,
        name: "Closures Explained.pdf",
        type: "PDF",
        size: "1.4 MB"
      }]

    },
    {
      id: 302,
      title: "Advanced Array Methods",
      type: "video",
      duration: 75,
      status: "completed",
      videoUrl: "https://example.com/videos/array-methods",
      description: "Master advanced array methods like map, filter, reduce, and more",
      content: "<p>Modern JavaScript provides powerful array methods that enable functional programming patterns and clean, readable code.</p>",
      resources: [
      {
        id: 3002,
        name: "Array Methods Reference.pdf",
        type: "PDF",
        size: "1.6 MB"
      },
      {
        id: 3003,
        name: "Practice Exercises.js",
        type: "JS",
        size: "8 KB"
      }]

    },
    {
      id: 303,
      title: "Asynchronous JavaScript",
      type: "video",
      duration: 90,
      status: "completed",
      videoUrl: "https://example.com/videos/async-js",
      description: "Learn about asynchronous programming with callbacks, promises, and async/await",
      content: "<p>Asynchronous programming is crucial for creating responsive web applications. We'll explore various techniques for handling asynchronous operations.</p>",
      resources: [
      {
        id: 3004,
        name: "Async JavaScript Guide.pdf",
        type: "PDF",
        size: "2.1 MB"
      }]

    },
    {
      id: 304,
      title: "Modern JavaScript Features",
      type: "video",
      duration: 75,
      status: "in_progress",
      videoUrl: "https://example.com/videos/modern-js",
      description: "Explore ES6+ features like arrow functions, destructuring, modules, and more",
      content: "<p>Modern JavaScript (ES6 and beyond) introduced many powerful features that make your code more expressive and maintainable.</p>",
      resources: [
      {
        id: 3005,
        name: "ES6+ Features Cheat Sheet.pdf",
        type: "PDF",
        size: "1.8 MB"
      }]

    },
    {
      id: 305,
      title: "JavaScript Design Patterns",
      type: "presentation",
      duration: 120,
      status: "not_started",
      description: "Common design patterns in JavaScript applications",
      content: "<p>Design patterns are reusable solutions to common programming problems. We'll explore patterns particularly useful in JavaScript applications.</p>",
      resources: [
      {
        id: 3006,
        name: "Design Patterns in JS.pdf",
        type: "PDF",
        size: "2.4 MB"
      },
      {
        id: 3007,
        name: "Pattern Examples.zip",
        type: "ZIP",
        size: "4.2 MB"
      }]

    },
    {
      id: 306,
      title: "Error Handling and Debugging",
      type: "video",
      duration: 60,
      status: "not_started",
      videoUrl: "https://example.com/videos/js-debugging",
      description: "Techniques for effective error handling and debugging in JavaScript",
      content: "<p>Every developer needs to know how to properly handle errors and debug their code. We'll explore tools and techniques for JavaScript debugging.</p>",
      resources: [
      {
        id: 3008,
        name: "Debugging Techniques.pdf",
        type: "PDF",
        size: "1.5 MB"
      }]

    },
    {
      id: 307,
      title: "JavaScript Performance Optimization",
      type: "video",
      duration: 60,
      status: "not_started",
      videoUrl: "https://example.com/videos/js-performance",
      description: "Learn how to optimize your JavaScript code for better performance",
      content: "<p>Performance matters! We'll explore techniques to make your JavaScript code faster and more efficient.</p>",
      resources: [
      {
        id: 3009,
        name: "Performance Optimization Guide.pdf",
        type: "PDF",
        size: "1.9 MB"
      }]

    }],

    discussions: [
    {
      id: 401,
      author: "Michael Brown",
      timestamp: subDays(NOW, 5).toISOString(),
      message: "I'm finding async/await much easier to work with than plain promises. Anyone else feel the same?",
      replies: [
      {
        id: 501,
        author: "David Chen",
        timestamp: subDays(NOW, 5).toISOString(),
        message: "Absolutely! Async/await makes asynchronous code much more readable and maintainable. Just remember that it's still using promises under the hood."
      }]

    },
    {
      id: 402,
      author: "Sarah Johnson",
      timestamp: subDays(NOW, 3).toISOString(),
      message: "For those who are struggling with closures, try thinking of them as functions that 'remember' their lexical scope, even when executed outside that scope.",
      replies: []
    }]

  }
};
// Sample calendar data
export const calendarData = {
  sessions: [
  {
    id: 101,
    title: "JavaScript Advanced Concepts",
    type: "lecture",
    date: addDays(NOW, 1).toISOString(),
    trainer: "Sarah Johnson",
    duration: 90,
    description: "Deep dive into closures, scopes, and the prototype chain"
  },
  {
    id: 102,
    title: "Pair Programming Workshop",
    type: "workshop",
    date: addDays(NOW, 3).toISOString(),
    trainer: "David Chen",
    duration: 120,
    description: "Practice collaborative coding techniques with a partner"
  },
  {
    id: 103,
    title: "Code Review Session",
    type: "discussion",
    date: addDays(NOW, 5).toISOString(),
    trainer: "Sarah Johnson",
    duration: 60,
    description: "Review and feedback on your latest project submission"
  },
  {
    id: 104,
    title: "Advanced Array Methods",
    type: "video",
    date: addDays(NOW, 8).toISOString(),
    duration: 75,
    description: "Learn about map, filter, reduce, and other powerful array methods"
  },
  {
    id: 105,
    title: "React Introduction",
    type: "lecture",
    date: addDays(NOW, 10).toISOString(),
    trainer: "Lisa Taylor",
    duration: 90,
    description: "Introduction to React and component-based architecture"
  },
  {
    id: 106,
    title: "Career Development Workshop",
    type: "workshop",
    date: addDays(NOW, 15).toISOString(),
    trainer: "Michael Rodriguez",
    duration: 120,
    description: "Resume building and interview preparation"
  },
  {
    id: 107,
    title: "Project Planning Session",
    type: "discussion",
    date: addDays(NOW, 17).toISOString(),
    trainer: "David Chen",
    duration: 60,
    description: "Plan your capstone project with guidance from mentors"
  }]

};
// Mock API functions
export const getPortalDashboard = () => {
  return Promise.resolve(dashboardData);
};
export const getPortalCourses = () => {
  return Promise.resolve(coursesData);
};
export const getPortalModuleDetail = (id) => {
  const module = moduleData[id];
  if (!module) {
    return Promise.reject(new Error('Module not found'));
  }
  return Promise.resolve(module);
};
export const completeLesson = (lessonId) => {
  // In a real implementation, this would update the lesson status in the database
  return Promise.resolve({ success: true });
};
export const getPortalCalendar = (month, year) => {
  // In a real implementation, this would filter sessions by month and year
  return Promise.resolve(calendarData.sessions);
};
// First definition removed - using the more complete one below
export const getSessionDetail = (sessionId) => {
  const session = calendarData.sessions.find((s) => s.id.toString() === sessionId);
  if (!session) {
    return Promise.reject(new Error('Session not found'));
  }
  return Promise.resolve(session);
};
// Sample resources data
export const resourcesData = {
  resources: [
  // HTML/CSS Fundamentals resources
  {
    id: 1001,
    name: "HTML5 Cheat Sheet",
    description: "Quick reference guide for HTML5 elements and attributes",
    fileType: "pdf",
    fileSize: 1.2 * 1024 * 1024, // 1.2MB
    category: "Reference",
    moduleName: "HTML/CSS Fundamentals",
    moduleId: 1,
    uploadDate: subDays(NOW, 45).toISOString()
  },
  {
    id: 1002,
    name: "CSS3 Properties Reference",
    description: "Complete list of CSS3 properties with examples",
    fileType: "pdf",
    fileSize: 2.5 * 1024 * 1024, // 2.5MB
    category: "Reference",
    moduleName: "HTML/CSS Fundamentals",
    moduleId: 1,
    uploadDate: subDays(NOW, 45).toISOString()
  },
  {
    id: 1003,
    name: "HTML/CSS Course Slides",
    description: "Lecture slides for the HTML/CSS module",
    fileType: "pptx",
    fileSize: 8.7 * 1024 * 1024, // 8.7MB
    category: "Slides",
    moduleName: "HTML/CSS Fundamentals",
    moduleId: 1,
    uploadDate: subDays(NOW, 44).toISOString()
  },
  {
    id: 1004,
    name: "Responsive Design Examples",
    description: "Sample code for responsive layouts using Flexbox and Grid",
    fileType: "zip",
    fileSize: 3.4 * 1024 * 1024, // 3.4MB
    category: "Code Samples",
    moduleName: "HTML/CSS Fundamentals",
    moduleId: 1,
    uploadDate: subDays(NOW, 42).toISOString()
  },
  // JavaScript Basics resources
  {
    id: 1005,
    name: "JavaScript Basics Handbook",
    description: "Comprehensive guide to JavaScript fundamentals",
    fileType: "pdf",
    fileSize: 4.8 * 1024 * 1024, // 4.8MB
    category: "Books",
    moduleName: "JavaScript Basics",
    moduleId: 2,
    uploadDate: subDays(NOW, 30).toISOString()
  },
  {
    id: 1006,
    name: "JavaScript Basics Course Slides",
    description: "Lecture slides for the JavaScript Basics module",
    fileType: "pptx",
    fileSize: 6.2 * 1024 * 1024, // 6.2MB
    category: "Slides",
    moduleName: "JavaScript Basics",
    moduleId: 2,
    uploadDate: subDays(NOW, 29).toISOString()
  },
  {
    id: 1007,
    name: "Practice Exercises - Variables and Data Types",
    description: "Practice exercises for JavaScript variables and data types",
    fileType: "js",
    fileSize: 22 * 1024, // 22KB
    category: "Exercises",
    moduleName: "JavaScript Basics",
    moduleId: 2,
    uploadDate: subDays(NOW, 28).toISOString()
  },
  {
    id: 1008,
    name: "Practice Exercises - Functions and Scope",
    description: "Practice exercises for JavaScript functions and scope",
    fileType: "js",
    fileSize: 18 * 1024, // 18KB
    category: "Exercises",
    moduleName: "JavaScript Basics",
    moduleId: 2,
    uploadDate: subDays(NOW, 27).toISOString()
  },
  // JavaScript Advanced resources
  {
    id: 1009,
    name: "Advanced JavaScript Concepts",
    description: "In-depth guide to advanced JavaScript concepts",
    fileType: "pdf",
    fileSize: 5.7 * 1024 * 1024, // 5.7MB
    category: "Books",
    moduleName: "JavaScript Advanced",
    moduleId: 3,
    uploadDate: subDays(NOW, 15).toISOString()
  },
  {
    id: 1010,
    name: "JavaScript Design Patterns",
    description: "Common JavaScript design patterns with examples",
    fileType: "pdf",
    fileSize: 3.2 * 1024 * 1024, // 3.2MB
    category: "Reference",
    moduleName: "JavaScript Advanced",
    moduleId: 3,
    uploadDate: subDays(NOW, 14).toISOString()
  },
  {
    id: 1011,
    name: "Asynchronous JavaScript Demo",
    description: "Sample code demonstrating promises, async/await, and callbacks",
    fileType: "js",
    fileSize: 45 * 1024, // 45KB
    category: "Code Samples",
    moduleName: "JavaScript Advanced",
    moduleId: 3,
    uploadDate: subDays(NOW, 12).toISOString()
  },
  {
    id: 1012,
    name: "JavaScript Testing Examples",
    description: "Examples of unit tests with Jest",
    fileType: "zip",
    fileSize: 1.8 * 1024 * 1024, // 1.8MB
    category: "Code Samples",
    moduleName: "JavaScript Advanced",
    moduleId: 3,
    uploadDate: subDays(NOW, 10).toISOString()
  },
  // React Fundamentals resources
  {
    id: 1013,
    name: "Introduction to React",
    description: "Overview of React and its core concepts",
    fileType: "pdf",
    fileSize: 2.1 * 1024 * 1024, // 2.1MB
    category: "Books",
    moduleName: "React Fundamentals",
    moduleId: 4,
    uploadDate: subDays(NOW, 5).toISOString()
  },
  {
    id: 1014,
    name: "React Component Lifecycle",
    description: "Diagram of React component lifecycle",
    fileType: "png",
    fileSize: 420 * 1024, // 420KB
    category: "Reference",
    moduleName: "React Fundamentals",
    moduleId: 4,
    uploadDate: subDays(NOW, 5).toISOString()
  },
  // Career Development resources
  {
    id: 1015,
    name: "Resume Writing Guide",
    description: "Guide to creating an effective technical resume",
    fileType: "pdf",
    fileSize: 1.4 * 1024 * 1024, // 1.4MB
    category: "Career",
    moduleName: "Career Development",
    moduleId: 8,
    uploadDate: subDays(NOW, 3).toISOString()
  },
  {
    id: 1016,
    name: "Technical Interview Preparation",
    description: "Guide to preparing for technical interviews",
    fileType: "pdf",
    fileSize: 2.8 * 1024 * 1024, // 2.8MB
    category: "Career",
    moduleName: "Career Development",
    moduleId: 8,
    uploadDate: subDays(NOW, 3).toISOString()
  },
  {
    id: 1017,
    name: "Sample Resume Templates",
    description: "Collection of resume templates for tech jobs",
    fileType: "docx",
    fileSize: 780 * 1024, // 780KB
    category: "Templates",
    moduleName: "Career Development",
    moduleId: 8,
    uploadDate: subDays(NOW, 2).toISOString()
  }],

  categories: [
  { id: 1, name: "Reference", count: 4, icon: "FileText", colorClass: "bg-blue-500" },
  { id: 2, name: "Books", count: 3, icon: "BookOpen", colorClass: "bg-green-500" },
  { id: 3, name: "Slides", count: 2, icon: "FileText", colorClass: "bg-yellow-500" },
  { id: 4, name: "Code Samples", count: 3, icon: "FileCode", colorClass: "bg-purple-500" },
  { id: 5, name: "Exercises", count: 2, icon: "FileText", colorClass: "bg-pink-500" },
  { id: 6, name: "Templates", count: 1, icon: "Folder", colorClass: "bg-indigo-500" },
  { id: 7, name: "Career", count: 2, icon: "Folder", colorClass: "bg-orange-500" }]

};
// Mock API function for resources
export const getPortalResources = () => {
  return Promise.resolve(resourcesData);
};
// Mock API function for downloading a resource
export const downloadResource = (resourceId) => {
  const resource = resourcesData.resources.find((r) => r.id.toString() === resourceId);
  if (!resource) {
    return Promise.reject(new Error('Resource not found'));
  }
  // In a real implementation, this would return the resource file
  return Promise.resolve({ success: true, resource });
};
// Sample achievements data
export const achievementsData = {
  highlights: [
  {
    id: 1,
    label: "Modules Completed",
    value: "2/7",
    type: "completion"
  },
  {
    id: 2,
    label: "Badges Earned",
    value: "5",
    type: "badge"
  },
  {
    id: 3,
    label: "Certificates",
    value: "1",
    type: "certificate"
  },
  {
    id: 4,
    label: "Skills Mastered",
    value: "3",
    type: "skill"
  }],

  recentAchievements: [
  {
    id: 101,
    name: "JavaScript Foundations",
    description: "Successfully completed JavaScript Basics module with a score of 95%",
    type: "completion",
    dateEarned: subDays(NOW, 7).toISOString()
  },
  {
    id: 102,
    name: "Problem Solver",
    description: "Solved 10 complex programming challenges",
    type: "badge",
    dateEarned: subDays(NOW, 10).toISOString()
  },
  {
    id: 103,
    name: "HTML & CSS Fundamentals",
    description: "Certificate of completion for HTML & CSS Fundamentals module",
    type: "certificate",
    dateEarned: subDays(NOW, 15).toISOString()
  }],

  badges: [
  {
    id: 201,
    name: "Problem Solver",
    description: "Solved 10 complex programming challenges",
    type: "badge",
    isEarned: true,
    dateEarned: subDays(NOW, 10).toISOString()
  },
  {
    id: 202,
    name: "Code Quality",
    description: "Maintained high code quality standards across 5 projects",
    type: "badge",
    isEarned: true,
    dateEarned: subDays(NOW, 20).toISOString()
  },
  {
    id: 203,
    name: "Team Player",
    description: "Successfully completed 3 collaborative coding projects",
    type: "badge",
    isEarned: true,
    dateEarned: subDays(NOW, 25).toISOString()
  },
  {
    id: 204,
    name: "Quick Learner",
    description: "Demonstrated exceptional learning pace on new technologies",
    type: "badge",
    isEarned: true,
    dateEarned: subDays(NOW, 18).toISOString()
  },
  {
    id: 205,
    name: "Bug Hunter",
    description: "Found and fixed 15 critical bugs in various projects",
    type: "badge",
    isEarned: true,
    dateEarned: subDays(NOW, 12).toISOString()
  },
  {
    id: 206,
    name: "Performance Guru",
    description: "Optimized application performance by at least 30%",
    type: "badge",
    isEarned: false
  },
  {
    id: 207,
    name: "Accessibility Champion",
    description: "Implemented WCAG standards across all projects",
    type: "badge",
    isEarned: false
  },
  {
    id: 208,
    name: "Security Expert",
    description: "Applied security best practices in all code submissions",
    type: "badge",
    isEarned: false
  }],

  certificates: [
  {
    id: 301,
    name: "HTML & CSS Fundamentals",
    description: "Certificate of completion for HTML & CSS Fundamentals module",
    type: "certificate",
    isEarned: true,
    dateEarned: subDays(NOW, 15).toISOString()
  },
  {
    id: 302,
    name: "JavaScript Basics",
    description: "Certificate of completion for JavaScript Basics module",
    type: "certificate",
    isEarned: false,
    progress: 75
  },
  {
    id: 303,
    name: "Advanced JavaScript",
    description: "Certificate of completion for Advanced JavaScript module",
    type: "certificate",
    isEarned: false,
    progress: 35
  },
  {
    id: 304,
    name: "Web Development Fundamentals",
    description: "Comprehensive certificate for completing the Web Development Fundamentals track",
    type: "certificate",
    isEarned: false,
    progress: 40
  }]

};
// Mock API function for achievements
export const getPortalAchievements = () => {
  return Promise.resolve(achievementsData);
};
// Mock API function for downloading a certificate
export const downloadCertificate = (certificateId) => {
  const certificate = achievementsData.certificates.find((c) => c.id.toString() === certificateId);
  if (!certificate) {
    return Promise.reject(new Error('Certificate not found'));
  }
  if (!certificate.isEarned) {
    return Promise.reject(new Error('Certificate not yet earned'));
  }
  // In a real implementation, this would return the certificate file
  return Promise.resolve({ success: true, certificate });
};
// Sample profile data
export const profileData = {
  id: 1001,
  name: "John Smith",
  avatar: null, // URL to avatar image
  role: "Student",
  contact: {
    email: "john.smith@example.com",
    phone: "+1 (555) 123-4567",
    address: "123 Main St, San Francisco, CA 94105"
  },
  dateJoined: subDays(NOW, 60).toISOString(),
  program: {
    id: 1,
    name: "Web Development Bootcamp",
    startDate: subDays(NOW, 30).toISOString(),
    expectedEndDate: addDays(NOW, 60).toISOString(),
    progress: 65
  },
  bio: "I'm a career switcher with a background in marketing, now pursuing web development. I have a passion for creating user-friendly interfaces and solving problems through code. Previously worked for 5 years in digital marketing before deciding to transition to a more technical role.",
  education: "Bachelor of Arts in Communications, University of California (2015-2019)\nDigital Marketing Certificate, Google (2020)\nIntroduction to Web Development, Online Course (2022)",
  skills: [
  {
    id: 1,
    name: "HTML",
    currentLevel: 4,
    maxLevel: 5
  },
  {
    id: 2,
    name: "CSS",
    currentLevel: 3,
    maxLevel: 5
  },
  {
    id: 3,
    name: "JavaScript",
    currentLevel: 3,
    maxLevel: 5
  },
  {
    id: 4,
    name: "React",
    currentLevel: 1,
    maxLevel: 5
  }],

  interests: "Front-end development, UX/UI design, data visualization, mobile app development, and digital accessibility.",
  goals: "My primary goal is to transition from marketing to a full-time role as a front-end developer within the next 6 months. I aim to master React and become proficient with modern JavaScript frameworks. Long-term, I'd like to specialize in creating accessible web applications and potentially explore opportunities in technical leadership."
};
// Mock API function for profile
export const getPortalProfile = () => {
  return Promise.resolve(profileData);
};
// Mock API function for updating profile
export const updatePortalProfile = (updatedData) => {
  // In a real implementation, this would update the profile in the database
  Object.assign(profileData, {
    contact: {
      ...profileData.contact,
      phone: updatedData.phone || profileData.contact.phone,
      address: updatedData.address || profileData.contact.address
    },
    bio: updatedData.bio || profileData.bio,
    education: updatedData.education || profileData.education,
    interests: updatedData.interests || profileData.interests,
    goals: updatedData.goals || profileData.goals
  });
  return Promise.resolve({ success: true, profile: profileData });
};
// Sample skills data
export const skillsData = {
  highlightMetrics: [
  {
    id: 1,
    label: "Avg. Skill Level",
    value: "2.8/5",
    type: "average"
  },
  {
    id: 2,
    label: "Skills Mastered",
    value: "3",
    type: "mastered"
  },
  {
    id: 3,
    label: "Skills Improved",
    value: "7",
    type: "improved"
  },
  {
    id: 4,
    label: "Focus Areas",
    value: "4",
    type: "focus"
  }],

  skillGrowth: [
  {
    id: 1,
    name: "HTML",
    previousLevel: 3,
    currentLevel: 4,
    maxLevel: 5,
    growthPercentage: 20
  },
  {
    id: 2,
    name: "CSS",
    previousLevel: 2,
    currentLevel: 3,
    maxLevel: 5,
    growthPercentage: 20
  },
  {
    id: 3,
    name: "JavaScript",
    previousLevel: 2,
    currentLevel: 3,
    maxLevel: 5,
    growthPercentage: 20
  },
  {
    id: 4,
    name: "Problem Solving",
    previousLevel: 2,
    currentLevel: 3,
    maxLevel: 5,
    growthPercentage: 20
  }],

  technicalSkills: [
  {
    id: 101,
    name: "HTML",
    description: "Creating structured content with HTML5 elements",
    type: "technical",
    category: "Front-end Development",
    currentLevel: 4,
    maxLevel: 5,
    lastImproved: subDays(NOW, 15).toISOString(),
    subskills: [
    { id: 1001, name: "Semantic HTML", level: 4 },
    { id: 1002, name: "Forms & Validation", level: 4 },
    { id: 1003, name: "Accessibility", level: 3 },
    { id: 1004, name: "SEO Principles", level: 3 }],

    learningPath: [
    {
      title: "Complete HTML Basics",
      description: "Introduction to HTML elements and structure",
      completed: true,
      resource: "module-1"
    },
    {
      title: "HTML Forms Mastery",
      description: "Create and validate complex forms",
      completed: true,
      resource: "module-2"
    },
    {
      title: "Accessibility Standards",
      description: "Implement WCAG guidelines in your HTML",
      completed: false,
      resource: "module-3"
    }]

  },
  {
    id: 102,
    name: "CSS",
    description: "Styling web pages with modern CSS techniques",
    type: "technical",
    category: "Front-end Development",
    currentLevel: 3,
    maxLevel: 5,
    lastImproved: subDays(NOW, 20).toISOString(),
    subskills: [
    { id: 1005, name: "Selectors & Properties", level: 4 },
    { id: 1006, name: "Layout (Flexbox/Grid)", level: 3 },
    { id: 1007, name: "Animations & Transitions", level: 2 },
    { id: 1008, name: "Responsive Design", level: 3 }],

    learningPath: [
    {
      title: "CSS Fundamentals",
      description: "Master CSS selectors and basic properties",
      completed: true,
      resource: "module-4"
    },
    {
      title: "Modern Layouts",
      description: "Learn Flexbox and Grid for complex layouts",
      completed: true,
      resource: "module-5"
    },
    {
      title: "Advanced CSS Techniques",
      description: "Animations, transitions, and advanced effects",
      completed: false,
      resource: "module-6"
    }]

  },
  {
    id: 103,
    name: "JavaScript",
    description: "Programming interactive web applications with JavaScript",
    type: "technical",
    category: "Front-end Development",
    currentLevel: 3,
    maxLevel: 5,
    lastImproved: subDays(NOW, 10).toISOString(),
    subskills: [
    { id: 1009, name: "Core Concepts", level: 3 },
    { id: 1010, name: "DOM Manipulation", level: 3 },
    { id: 1011, name: "Async Programming", level: 2 },
    { id: 1012, name: "ES6+ Features", level: 2 }],

    learningPath: [
    {
      title: "JavaScript Fundamentals",
      description: "Core concepts and language features",
      completed: true,
      resource: "module-7"
    },
    {
      title: "DOM Manipulation",
      description: "Interact with web page elements",
      completed: true,
      resource: "module-8"
    },
    {
      title: "Asynchronous JavaScript",
      description: "Promises, async/await, and fetch API",
      completed: false,
      resource: "module-9"
    }]

  },
  {
    id: 104,
    name: "React",
    description: "Building user interfaces with React components",
    type: "technical",
    category: "Front-end Frameworks",
    currentLevel: 1,
    maxLevel: 5,
    lastImproved: subDays(NOW, 5).toISOString(),
    subskills: [
    { id: 1013, name: "Component Architecture", level: 2 },
    { id: 1014, name: "State Management", level: 1 },
    { id: 1015, name: "Hooks", level: 1 },
    { id: 1016, name: "React Router", level: 1 }],

    learningPath: [
    {
      title: "React Fundamentals",
      description: "Introduction to components and props",
      completed: false,
      resource: "module-10"
    },
    {
      title: "State & Lifecycle",
      description: "Managing component state and lifecycle",
      completed: false,
      resource: "module-11"
    },
    {
      title: "React Hooks",
      description: "Using hooks for state and side effects",
      completed: false,
      resource: "module-12"
    }]

  },
  {
    id: 105,
    name: "Git & Version Control",
    description: "Managing code with Git and GitHub",
    type: "technical",
    category: "Development Tools",
    currentLevel: 2,
    maxLevel: 5,
    lastImproved: subDays(NOW, 25).toISOString(),
    subskills: [
    { id: 1017, name: "Basic Git Commands", level: 3 },
    { id: 1018, name: "Branching & Merging", level: 2 },
    { id: 1019, name: "Pull Requests", level: 2 },
    { id: 1020, name: "Resolving Conflicts", level: 1 }],

    learningPath: [
    {
      title: "Git Basics",
      description: "Essential commands and workflow",
      completed: true,
      resource: "module-13"
    },
    {
      title: "Collaborative Git",
      description: "Branching, merging and team workflows",
      completed: false,
      resource: "module-14"
    }]

  }],

  softSkills: [
  {
    id: 201,
    name: "Problem Solving",
    description: "Analyzing problems and developing effective solutions",
    type: "soft",
    category: "Cognitive Skills",
    currentLevel: 3,
    maxLevel: 5,
    lastImproved: subDays(NOW, 12).toISOString(),
    subskills: [
    { id: 2001, name: "Analytical Thinking", level: 3 },
    { id: 2002, name: "Debugging", level: 3 },
    { id: 2003, name: "Creative Solutions", level: 2 },
    { id: 2004, name: "Decision Making", level: 3 }],

    learningPath: [
    {
      title: "Analytical Problem Solving",
      description: "Structured approach to identifying and solving problems",
      completed: true,
      resource: null
    },
    {
      title: "Debugging Strategies",
      description: "Effective techniques for finding and fixing bugs",
      completed: false,
      resource: null
    }]

  },
  {
    id: 202,
    name: "Communication",
    description: "Clearly expressing ideas and collaborating effectively",
    type: "soft",
    category: "Interpersonal Skills",
    currentLevel: 3,
    maxLevel: 5,
    lastImproved: subDays(NOW, 18).toISOString(),
    subskills: [
    { id: 2005, name: "Written Communication", level: 4 },
    { id: 2006, name: "Verbal Communication", level: 3 },
    { id: 2007, name: "Active Listening", level: 3 },
    { id: 2008, name: "Technical Documentation", level: 2 }],

    learningPath: [
    {
      title: "Communication Fundamentals",
      description: "Principles of effective communication",
      completed: true,
      resource: null
    },
    {
      title: "Technical Communication",
      description: "Explaining complex concepts clearly",
      completed: false,
      resource: null
    }]

  },
  {
    id: 203,
    name: "Time Management",
    description: "Efficiently organizing tasks and meeting deadlines",
    type: "soft",
    category: "Productivity Skills",
    currentLevel: 2,
    maxLevel: 5,
    lastImproved: subDays(NOW, 30).toISOString(),
    subskills: [
    { id: 2009, name: "Prioritization", level: 3 },
    { id: 2010, name: "Goal Setting", level: 2 },
    { id: 2011, name: "Focus & Concentration", level: 2 },
    { id: 2012, name: "Work-Life Balance", level: 2 }],

    learningPath: [
    {
      title: "Effective Prioritization",
      description: "Identifying what matters most and focusing efforts",
      completed: false,
      resource: null
    },
    {
      title: "Productive Habits",
      description: "Building routines that maximize productivity",
      completed: false,
      resource: null
    }]

  },
  {
    id: 204,
    name: "Teamwork",
    description: "Collaborating effectively in group settings",
    type: "soft",
    category: "Interpersonal Skills",
    currentLevel: 3,
    maxLevel: 5,
    lastImproved: subDays(NOW, 22).toISOString(),
    subskills: [
    { id: 2013, name: "Collaboration", level: 4 },
    { id: 2014, name: "Conflict Resolution", level: 3 },
    { id: 2015, name: "Feedback Exchange", level: 2 },
    { id: 2016, name: "Shared Responsibility", level: 3 }],

    learningPath: [
    {
      title: "Collaborative Development",
      description: "Working effectively in development teams",
      completed: true,
      resource: null
    },
    {
      title: "Peer Code Reviews",
      description: "Giving and receiving constructive feedback",
      completed: false,
      resource: null
    }]

  }],

  recommendedFocus: [
  {
    skillId: 104,
    reason: "React is essential for the upcoming project work and your current level is beginner. Focusing here will have the most impact on your overall progress."
  },
  {
    skillId: 103,
    reason: "Strengthening your JavaScript skills will provide a solid foundation for learning React and other front-end frameworks."
  },
  {
    skillId: 105,
    reason: "Improving your Git skills will be important for collaborative project work in the upcoming modules."
  },
  {
    skillId: 203,
    reason: "Better time management will help you balance your learning across multiple skill areas more effectively."
  }]

};
// Mock API function for skills
export const getPortalSkills = () => {
  return Promise.resolve(skillsData);
};
// Sample progress data
export const progressData = {
  program: {
    id: 1,
    name: "Web Development Bootcamp",
    startDate: subDays(NOW, 30).toISOString(),
    expectedEndDate: addDays(NOW, 60).toISOString(),
    progress: 65
  },
  moduleStats: {
    total: 7,
    completed: 2,
    inProgress: 1,
    notStarted: 4,
    completedPercentage: 29
  },
  timeStats: {
    spent: 2160, // in minutes (36 hours)
    total: 4800, // in minutes (80 hours)
    remaining: 2640, // in minutes (44 hours)
    onTrack: true,
    behindSchedule: false
  },
  modules: [
  {
    id: 1,
    name: "HTML/CSS Fundamentals",
    description: "Learn the basics of HTML and CSS to build the foundation of any web application",
    status: "completed",
    progress: 100,
    lessonsCompleted: 5,
    totalLessons: 5,
    timeSpent: 600, // in minutes (10 hours)
    lessons: [
    {
      id: 101,
      title: "Introduction to HTML",
      description: "An introduction to HTML, its history, and purpose",
      status: "completed",
      duration: 45,
      completedDate: subDays(NOW, 28).toISOString(),
      lastAccessed: subDays(NOW, 28).toISOString()
    },
    {
      id: 102,
      title: "HTML Elements and Structure",
      description: "Learn about HTML elements and how to structure a webpage",
      status: "completed",
      duration: 60,
      completedDate: subDays(NOW, 27).toISOString(),
      lastAccessed: subDays(NOW, 27).toISOString()
    },
    {
      id: 103,
      title: "Introduction to CSS",
      description: "An introduction to CSS and styling web pages",
      status: "completed",
      duration: 45,
      completedDate: subDays(NOW, 26).toISOString(),
      lastAccessed: subDays(NOW, 26).toISOString()
    },
    {
      id: 104,
      title: "CSS Selectors and Properties",
      description: "Learn about CSS selectors and properties for styling elements",
      status: "completed",
      duration: 60,
      completedDate: subDays(NOW, 25).toISOString(),
      lastAccessed: subDays(NOW, 25).toISOString()
    },
    {
      id: 105,
      title: "Building Responsive Layouts",
      description: "Learn to create responsive layouts with Flexbox and Grid",
      status: "completed",
      duration: 90,
      completedDate: subDays(NOW, 24).toISOString(),
      lastAccessed: subDays(NOW, 24).toISOString()
    }],

    resources: [
    {
      id: 1001,
      name: "HTML5 Cheat Sheet",
      type: "PDF",
      size: "1.2 MB"
    },
    {
      id: 1002,
      name: "CSS3 Properties Reference",
      type: "PDF",
      size: "2.5 MB"
    },
    {
      id: 1003,
      name: "Responsive Design Examples",
      type: "ZIP",
      size: "3.4 MB"
    }]

  },
  {
    id: 2,
    name: "JavaScript Basics",
    description: "Introduction to JavaScript programming for web development",
    status: "completed",
    progress: 100,
    lessonsCompleted: 6,
    totalLessons: 6,
    timeSpent: 720, // in minutes (12 hours)
    lessons: [
    {
      id: 201,
      title: "Introduction to JavaScript",
      description: "An introduction to JavaScript and its role in web development",
      status: "completed",
      duration: 45,
      completedDate: subDays(NOW, 22).toISOString(),
      lastAccessed: subDays(NOW, 22).toISOString()
    },
    {
      id: 202,
      title: "Variables and Data Types",
      description: "Understanding JavaScript variables, primitives, and objects",
      status: "completed",
      duration: 60,
      completedDate: subDays(NOW, 21).toISOString(),
      lastAccessed: subDays(NOW, 21).toISOString()
    },
    {
      id: 203,
      title: "Control Flow",
      description: "Using conditions and loops to control program flow",
      status: "completed",
      duration: 60,
      completedDate: subDays(NOW, 20).toISOString(),
      lastAccessed: subDays(NOW, 20).toISOString()
    },
    {
      id: 204,
      title: "Functions",
      description: "Creating and using functions in JavaScript",
      status: "completed",
      duration: 75,
      completedDate: subDays(NOW, 19).toISOString(),
      lastAccessed: subDays(NOW, 19).toISOString()
    },
    {
      id: 205,
      title: "Arrays and Objects",
      description: "Working with complex data structures in JavaScript",
      status: "completed",
      duration: 75,
      completedDate: subDays(NOW, 18).toISOString(),
      lastAccessed: subDays(NOW, 18).toISOString()
    },
    {
      id: 206,
      title: "DOM Manipulation",
      description: "Interacting with HTML using JavaScript and the DOM API",
      status: "completed",
      duration: 90,
      completedDate: subDays(NOW, 17).toISOString(),
      lastAccessed: subDays(NOW, 17).toISOString()
    }],

    resources: [
    {
      id: 2001,
      name: "JavaScript Basics Handbook",
      type: "PDF",
      size: "4.8 MB"
    },
    {
      id: 2002,
      name: "Practice Exercises - Variables and Data Types",
      type: "JS",
      size: "22 KB"
    },
    {
      id: 2003,
      name: "Practice Exercises - Functions and Scope",
      type: "JS",
      size: "18 KB"
    }]

  },
  {
    id: 3,
    name: "JavaScript Advanced",
    description: "Advanced JavaScript concepts and patterns for professional development",
    status: "in_progress",
    progress: 60,
    lessonsCompleted: 4,
    totalLessons: 7,
    timeSpent: 300, // in minutes (5 hours)
    lessons: [
    {
      id: 301,
      title: "Closures and Scope",
      description: "Understanding JavaScript closures and scope chains",
      status: "completed",
      duration: 60,
      completedDate: subDays(NOW, 15).toISOString(),
      lastAccessed: subDays(NOW, 15).toISOString()
    },
    {
      id: 302,
      title: "Advanced Array Methods",
      description: "Master advanced array methods like map, filter, reduce, and more",
      status: "completed",
      duration: 75,
      completedDate: subDays(NOW, 14).toISOString(),
      lastAccessed: subDays(NOW, 14).toISOString()
    },
    {
      id: 303,
      title: "Asynchronous JavaScript",
      description: "Learn about asynchronous programming with callbacks, promises, and async/await",
      status: "completed",
      duration: 90,
      completedDate: subDays(NOW, 12).toISOString(),
      lastAccessed: subDays(NOW, 12).toISOString()
    },
    {
      id: 304,
      title: "Modern JavaScript Features",
      description: "Explore ES6+ features like arrow functions, destructuring, modules, and more",
      status: "completed",
      duration: 75,
      completedDate: subDays(NOW, 9).toISOString(),
      lastAccessed: subDays(NOW, 9).toISOString()
    },
    {
      id: 305,
      title: "JavaScript Design Patterns",
      description: "Common design patterns in JavaScript applications",
      status: "not_started",
      duration: 120,
      lastAccessed: null
    },
    {
      id: 306,
      title: "Error Handling and Debugging",
      description: "Techniques for effective error handling and debugging in JavaScript",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    },
    {
      id: 307,
      title: "JavaScript Performance Optimization",
      description: "Learn how to optimize your JavaScript code for better performance",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    }],

    resources: [
    {
      id: 3001,
      name: "Advanced JavaScript Concepts",
      type: "PDF",
      size: "5.7 MB"
    },
    {
      id: 3002,
      name: "JavaScript Design Patterns",
      type: "PDF",
      size: "3.2 MB"
    },
    {
      id: 3003,
      name: "Asynchronous JavaScript Demo",
      type: "JS",
      size: "45 KB"
    }]

  },
  {
    id: 4,
    name: "React Fundamentals",
    description: "Building user interfaces with React components",
    status: "not_started",
    progress: 0,
    lessonsCompleted: 0,
    totalLessons: 8,
    timeSpent: 0,
    lessons: [
    {
      id: 401,
      title: "Introduction to React",
      description: "An overview of React and its component-based architecture",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    },
    {
      id: 402,
      title: "Components and Props",
      description: "Creating and using React components with props",
      status: "not_started",
      duration: 75,
      lastAccessed: null
    },
    {
      id: 403,
      title: "State and Lifecycle",
      description: "Managing component state and lifecycle methods",
      status: "not_started",
      duration: 75,
      lastAccessed: null
    },
    {
      id: 404,
      title: "Event Handling",
      description: "Handling user events in React components",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    },
    {
      id: 405,
      title: "Conditional Rendering",
      description: "Techniques for conditional rendering in React",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    },
    {
      id: 406,
      title: "Lists and Keys",
      description: "Rendering lists of items with keys in React",
      status: "not_started",
      duration: 60,
      lastAccessed: null
    },
    {
      id: 407,
      title: "Forms in React",
      description: "Working with forms and controlled components",
      status: "not_started",
      duration: 75,
      lastAccessed: null
    },
    {
      id: 408,
      title: "React Hooks",
      description: "Using hooks for state and side effects in functional components",
      status: "not_started",
      duration: 90,
      lastAccessed: null
    }],

    resources: [
    {
      id: 4001,
      name: "Introduction to React",
      type: "PDF",
      size: "2.1 MB"
    },
    {
      id: 4002,
      name: "React Component Lifecycle",
      type: "PNG",
      size: "420 KB"
    }]

  },
  {
    id: 5,
    name: "Backend Basics",
    description: "Introduction to server-side development",
    status: "not_started",
    progress: 0,
    lessonsCompleted: 0,
    totalLessons: 6,
    timeSpent: 0,
    lessons: [
      // Lesson data would be similar to above
      // Omitted for brevity
    ],
    resources: []
  },
  {
    id: 6,
    name: "Database Integration",
    description: "Working with databases and ORMs",
    status: "not_started",
    progress: 0,
    lessonsCompleted: 0,
    totalLessons: 6,
    timeSpent: 0,
    lessons: [],
    resources: []
  },
  {
    id: 7,
    name: "Final Project",
    description: "Building a complete web application",
    status: "not_started",
    progress: 0,
    lessonsCompleted: 0,
    totalLessons: 2,
    timeSpent: 0,
    lessons: [],
    resources: []
  }],

  recentAchievements: [
  {
    id: 101,
    name: "JavaScript Foundations",
    description: "Successfully completed JavaScript Basics module with a score of 95%",
    type: "completion",
    dateEarned: subDays(NOW, 7).toISOString()
  },
  {
    id: 102,
    name: "Problem Solver",
    description: "Solved 10 complex programming challenges",
    type: "badge",
    dateEarned: subDays(NOW, 10).toISOString()
  },
  {
    id: 103,
    name: "HTML & CSS Fundamentals",
    description: "Certificate of completion for HTML & CSS Fundamentals module",
    type: "completion",
    dateEarned: subDays(NOW, 15).toISOString()
  }],

  programCertificate: {
    isEarned: false,
    requiredCompletion: 7, // All modules need to be completed
    currentCompletion: 2, // 2 modules completed so far
    completionPercentage: 29 // (2/7) * 100
  },
  recommendations: [
  {
    id: 1,
    type: "module",
    moduleId: 3,
    title: "Complete JavaScript Advanced Module",
    description: "You're making good progress! Finish the JavaScript Advanced module to unlock React content."
  },
  {
    id: 2,
    type: "resource",
    title: "Advanced JavaScript Concepts Guide",
    description: "This comprehensive guide will help you master the concepts in your current module."
  },
  {
    id: 3,
    type: "skill",
    title: "Improve Problem Solving Skills",
    description: "Practice algorithmic thinking to prepare for more complex programming challenges."
  }]

};
// Mock API function for progress
export const getPortalProgress = () => {
  return Promise.resolve(progressData);
};
// Sample notifications data
export const notificationsData = {
  unreadCount: 4,
  notifications: [
  {
    id: 1,
    type: "schedule",
    message: "New session scheduled: JavaScript Advanced Concepts on " + format(addDays(NOW, 1), 'MMMM d, yyyy'),
    timestamp: subDays(NOW, 1).toISOString(),
    isRead: false,
    link: "/portal/calendar",
    linkText: "View Calendar"
  },
  {
    id: 2,
    type: "progress",
    title: "Module Completed",
    message: "You've completed the JavaScript Basics module! Great job!",
    timestamp: subDays(NOW, 2).toISOString(),
    isRead: false,
    link: "/portal/progress",
    linkText: "View Progress"
  },
  {
    id: 3,
    type: "message",
    title: "New Message",
    message: "Sarah Johnson: 'Great work on your last assignment! I particularly liked your implementation of the array methods.'",
    timestamp: subDays(NOW, 3).toISOString(),
    isRead: false
  },
  {
    id: 4,
    type: "reminder",
    message: "Don't forget to submit your project by this Friday",
    timestamp: subDays(NOW, 4).toISOString(),
    isRead: false,
    link: "/portal/courses",
    linkText: "Go to Courses"
  },
  {
    id: 5,
    type: "alert",
    title: "Important Announcement",
    message: "The schedule for next week has been updated due to a holiday. Please check the calendar for the new session times.",
    timestamp: subDays(NOW, 5).toISOString(),
    isRead: true,
    link: "/portal/calendar",
    linkText: "View Calendar"
  },
  {
    id: 6,
    type: "success",
    title: "Badge Earned",
    message: "You've earned the 'Problem Solver' badge for completing 10 complex coding challenges!",
    timestamp: subDays(NOW, 7).toISOString(),
    isRead: true,
    link: "/portal/achievements",
    linkText: "View Achievements"
  },
  {
    id: 7,
    type: "schedule",
    message: "Reminder: Pair Programming Workshop tomorrow at " + format(addHours(NOW, 26), 'h:mm a'),
    timestamp: subDays(NOW, 8).toISOString(),
    isRead: true,
    link: "/portal/calendar",
    linkText: "View Calendar"
  },
  {
    id: 8,
    type: "progress",
    message: "You've made significant progress in HTML skills! Your proficiency level has increased to 4/5.",
    timestamp: subDays(NOW, 10).toISOString(),
    isRead: true,
    link: "/portal/skills",
    linkText: "View Skills"
  },
  {
    id: 9,
    type: "warning",
    title: "Approaching Deadline",
    message: "You have 3 days left to complete the current module exercises before the next section unlocks.",
    timestamp: subDays(NOW, 12).toISOString(),
    isRead: true
  },
  {
    id: 10,
    type: "message",
    title: "Group Message",
    message: "David Chen: 'I've shared some useful resources for the upcoming React module in the resources section.'",
    timestamp: subDays(NOW, 15).toISOString(),
    isRead: true,
    link: "/portal/resources",
    linkText: "View Resources"
  }]

};
// Mock API function for notifications
export const getPortalNotifications = () => {
  return Promise.resolve(notificationsData);
};
// Mock API function for marking a notification as read
export const markNotificationAsRead = (id) => {
  // Find the notification
  const notification = notificationsData.notifications.find((n) => n.id.toString() === id);
  if (!notification) {
    return Promise.reject(new Error('Notification not found'));
  }
  // Update the notification's read status
  if (!notification.isRead) {
    notification.isRead = true;
    notificationsData.unreadCount = Math.max(0, notificationsData.unreadCount - 1);
  }
  return Promise.resolve({ success: true, notification });
};
// Mock API function for marking all notifications as read
export const markAllNotificationsAsRead = () => {
  // Update all notifications to read
  notificationsData.notifications.forEach((notification) => {
    notification.isRead = true;
  });
  // Reset unread count
  notificationsData.unreadCount = 0;
  return Promise.resolve({ success: true });
};
// Mock API function for deleting a notification
export const deleteNotification = (id) => {
  // Find the notification index
  const index = notificationsData.notifications.findIndex((n) => n.id.toString() === id);
  if (index === -1) {
    return Promise.reject(new Error('Notification not found'));
  }
  // Check if it was unread
  const wasUnread = !notificationsData.notifications[index].isRead;
  // Remove the notification
  notificationsData.notifications.splice(index, 1);
  // Update unread count if needed
  if (wasUnread) {
    notificationsData.unreadCount = Math.max(0, notificationsData.unreadCount - 1);
  }
  return Promise.resolve({ success: true });
};
// Mock API function for updating notification settings
export const updateNotificationSettings = (settings) => {
  // In a real implementation, this would update the user's notification preferences
  return Promise.resolve({ success: true, settings });
};