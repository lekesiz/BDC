/**
 * Mock data for trainer assessment management
 */

import { subDays, addDays } from 'date-fns';

const NOW = new Date();

// Sample assessment templates created by trainers
export const assessmentTemplates = {
  quizTemplates: [
    {
      id: "template-1",
      title: "Web Development Fundamentals",
      description: "Assessment covering HTML, CSS, and basic JavaScript concepts",
      created_by: "trainer-1",
      creator_name: "Sarah Johnson",
      created_at: subDays(NOW, 30).toISOString(),
      updated_at: subDays(NOW, 25).toISOString(),
      status: "active", // active, draft, archived
      type: "quiz",
      questions: [
        {
          id: "q1",
          type: "multipleChoice",
          question: "Which HTML element is used to define the main heading of a document?",
          options: ["<header>", "<heading>", "<h1>", "<main>"],
          correctAnswer: 2,
          points: 10,
          difficulty: "easy",
          tags: ["HTML", "elements"],
          explanation: "The <h1> element defines the most important heading on a page."
        },
        {
          id: "q2",
          type: "multipleChoice",
          question: "Which CSS property is used to change the text color of an element?",
          options: ["color", "text-color", "font-color", "background-color"],
          correctAnswer: 0,
          points: 10,
          difficulty: "easy",
          tags: ["CSS", "properties"],
          explanation: "The 'color' property sets the color of text."
        },
        {
          id: "q3",
          type: "trueFalse",
          question: "CSS stands for Cascading Style Sheets.",
          correctAnswer: true,
          points: 5,
          difficulty: "easy",
          tags: ["CSS", "fundamentals"],
          explanation: "CSS (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML."
        },
        {
          id: "q4",
          type: "shortAnswer",
          question: "What CSS property is used to add space between the border and the content of an element?",
          correctAnswer: "padding",
          points: 10,
          difficulty: "medium",
          tags: ["CSS", "box-model"],
          explanation: "Padding creates space inside the element between its content and its border."
        },
        {
          id: "q5", 
          type: "matching",
          question: "Match the HTML elements with their purposes:",
          items: [
            { id: 0, text: "<header>", match: "Container for introductory content" },
            { id: 1, text: "<footer>", match: "Container for footer content" },
            { id: 2, text: "<nav>", match: "Container for navigation links" },
            { id: 3, text: "<article>", match: "Container for independent, self-contained content" }
          ],
          correctMatches: { 0: 0, 1: 1, 2: 2, 3: 3 },
          points: 20,
          difficulty: "medium",
          tags: ["HTML", "elements", "semantics"]
        }
      ],
      settings: {
        timeLimit: 30, // in minutes
        passingScore: 70,
        randomizeQuestions: true,
        showResults: true,
        allowRetakes: true,
        maxRetakes: 2
      },
      skills: ["HTML", "CSS", "Web Development"],
      categories: ["Fundamentals", "Front-end"],
      averageCompletion: 25, // in minutes
      averageScore: 82,
      usageCount: 15
    },
    {
      id: "template-2",
      title: "JavaScript Advanced Concepts",
      description: "Test covering advanced JavaScript topics including closures, promises, and ES6 features",
      created_by: "trainer-2",
      creator_name: "Michael Rodriguez",
      created_at: subDays(NOW, 45).toISOString(),
      updated_at: subDays(NOW, 10).toISOString(),
      status: "active",
      type: "quiz",
      questions: [
        {
          id: "q6",
          type: "multipleChoice",
          question: "What is a closure in JavaScript?",
          options: [
            "A function that has no access to its outer scope variables",
            "A function along with its lexical environment",
            "A method to close browser windows",
            "A way to prevent memory leaks"
          ],
          correctAnswer: 1,
          points: 15,
          difficulty: "hard",
          tags: ["JavaScript", "closures"],
          explanation: "A closure is the combination of a function bundled together with references to its surrounding state (the lexical environment)."
        },
        {
          id: "q7",
          type: "trueFalse",
          question: "Promises in JavaScript are used for handling asynchronous operations.",
          correctAnswer: true,
          points: 10,
          difficulty: "medium",
          tags: ["JavaScript", "promises", "async"],
          explanation: "Promises provide a way to handle asynchronous operations more cleanly than callbacks."
        },
        {
          id: "q8",
          type: "multipleAnswer",
          question: "Which of the following are ES6 features?",
          options: [
            "let and const",
            "Arrow functions",
            "Template literals",
            "jQuery",
            "Class syntax"
          ],
          correctAnswers: [0, 1, 2, 4],
          points: 20,
          difficulty: "medium",
          tags: ["JavaScript", "ES6"]
        }
      ],
      settings: {
        timeLimit: 45,
        passingScore: 75,
        randomizeQuestions: false,
        showResults: true,
        allowRetakes: true,
        maxRetakes: 1
      },
      skills: ["JavaScript", "ES6", "Asynchronous Programming"],
      categories: ["Advanced", "Front-end"],
      averageCompletion: 38,
      averageScore: 74,
      usageCount: 8
    },
    {
      id: "template-3",
      title: "React Fundamentals",
      description: "Assessment covering React fundamentals including components, props, and state",
      created_by: "trainer-1",
      creator_name: "Sarah Johnson",
      created_at: subDays(NOW, 20).toISOString(),
      updated_at: subDays(NOW, 15).toISOString(),
      status: "draft",
      type: "quiz",
      questions: [
        {
          id: "q9",
          type: "multipleChoice",
          question: "What is JSX in React?",
          options: [
            "A templating engine",
            "A syntax extension for JavaScript that resembles HTML",
            "A JavaScript library",
            "A CSS framework for React"
          ],
          correctAnswer: 1,
          points: 10,
          difficulty: "medium",
          tags: ["React", "JSX"],
          explanation: "JSX is a syntax extension for JavaScript that resembles HTML and makes it easier to write and add HTML in React."
        }
      ],
      settings: {
        timeLimit: 40,
        passingScore: 70,
        randomizeQuestions: true,
        showResults: true,
        allowRetakes: true,
        maxRetakes: 2
      },
      skills: ["React", "JavaScript", "Front-end Development"],
      categories: ["Frameworks", "Front-end"],
      averageCompletion: null,
      averageScore: null,
      usageCount: 0
    }
  ],
  projectTemplates: [
    {
      id: "project-template-1",
      title: "Personal Portfolio Website",
      description: "Create a responsive personal portfolio website using HTML, CSS, and JavaScript",
      created_by: "trainer-1",
      creator_name: "Sarah Johnson",
      created_at: subDays(NOW, 60).toISOString(),
      updated_at: subDays(NOW, 58).toISOString(),
      status: "active",
      type: "project",
      requirements: [
        {
          id: "r1",
          description: "Create a responsive design that works on mobile, tablet, and desktop",
          points: 20
        },
        {
          id: "r2",
          description: "Include a hero section with your name and a brief introduction",
          points: 10
        },
        {
          id: "r3",
          description: "Create a skills section showcasing your technical abilities",
          points: 15
        },
        {
          id: "r4",
          description: "Include a projects section with at least 3 project examples",
          points: 20
        },
        {
          id: "r5",
          description: "Add a contact form with proper validation",
          points: 15
        },
        {
          id: "r6",
          description: "Write clean, well-commented code",
          points: 10
        },
        {
          id: "r7",
          description: "Deploy the website to GitHub Pages or a similar platform",
          points: 10
        }
      ],
      rubric: {
        design: {
          description: "Visual appeal and user experience",
          points: 25,
          criteria: [
            { description: "Professional appearance", points: 10 },
            { description: "Intuitive navigation", points: 10 },
            { description: "Consistent style throughout", points: 5 }
          ]
        },
        functionality: {
          description: "Working features and technical implementation",
          points: 35,
          criteria: [
            { description: "Responsive design works on all devices", points: 15 },
            { description: "All links and navigation work correctly", points: 10 },
            { description: "Contact form validates input properly", points: 10 }
          ]
        },
        code_quality: {
          description: "Code structure, organization, and best practices",
          points: 25,
          criteria: [
            { description: "Clean, readable code", points: 10 },
            { description: "Proper HTML semantics", points: 5 },
            { description: "CSS organization and efficiency", points: 5 },
            { description: "JavaScript implementation and performance", points: 5 }
          ]
        },
        deployment: {
          description: "Successful deployment and documentation",
          points: 15,
          criteria: [
            { description: "Successfully deployed and accessible online", points: 10 },
            { description: "Documentation of deployment process", points: 5 }
          ]
        }
      },
      settings: {
        dueDate: null, // Set when assigned
        submissionType: "url", // url, file, github
        allowLateSubmissions: true,
        latePenalty: 10, // percentage
        showRubric: true
      },
      skills: ["HTML", "CSS", "JavaScript", "Responsive Design"],
      categories: ["Front-end", "Portfolio"],
      averageScore: 87,
      usageCount: 25
    }
  ]
};

// Sample assessments assigned to cohorts/students
export const assignedAssessments = [
  {
    id: "assign-1",
    template_id: "template-1",
    title: "Web Development Fundamentals - Cohort A",
    description: "Assessment covering HTML, CSS, and basic JavaScript concepts",
    assigned_by: "trainer-1",
    assigner_name: "Sarah Johnson",
    assigned_at: subDays(NOW, 10).toISOString(),
    due_date: addDays(NOW, 5).toISOString(),
    status: "active", // active, scheduled, completed, canceled
    assigned_to: {
      type: "cohort", // cohort, individual, program
      id: "cohort-1",
      name: "Web Development Cohort A"
    },
    settings: {
      timeLimit: 30,
      passingScore: 70,
      randomizeQuestions: true,
      showResults: true,
      allowRetakes: true,
      maxRetakes: 2,
      notifyCompletion: true,
      reminderEnabled: true,
      reminderDays: 1
    },
    submissions: {
      total: 20,
      completed: 12,
      inProgress: 3,
      notStarted: 5,
      averageScore: 82
    }
  },
  {
    id: "assign-2",
    template_id: "template-2",
    title: "JavaScript Advanced Concepts - Cohort B",
    description: "Test covering advanced JavaScript topics including closures, promises, and ES6 features",
    assigned_by: "trainer-2",
    assigner_name: "Michael Rodriguez",
    assigned_at: subDays(NOW, 5).toISOString(),
    due_date: addDays(NOW, 7).toISOString(),
    status: "active",
    assigned_to: {
      type: "cohort",
      id: "cohort-2",
      name: "Web Development Cohort B"
    },
    settings: {
      timeLimit: 45,
      passingScore: 75,
      randomizeQuestions: false,
      showResults: true,
      allowRetakes: true,
      maxRetakes: 1,
      notifyCompletion: true,
      reminderEnabled: true,
      reminderDays: 2
    },
    submissions: {
      total: 18,
      completed: 8,
      inProgress: 5,
      notStarted: 5,
      averageScore: 74
    }
  },
  {
    id: "assign-3",
    template_id: "project-template-1",
    title: "Personal Portfolio Project - Cohort A",
    description: "Create a responsive personal portfolio website using HTML, CSS, and JavaScript",
    assigned_by: "trainer-1",
    assigner_name: "Sarah Johnson",
    assigned_at: subDays(NOW, 15).toISOString(),
    due_date: addDays(NOW, 10).toISOString(),
    status: "active",
    assigned_to: {
      type: "cohort",
      id: "cohort-1",
      name: "Web Development Cohort A"
    },
    settings: {
      dueDate: addDays(NOW, 10).toISOString(),
      submissionType: "url",
      allowLateSubmissions: true,
      latePenalty: 10,
      showRubric: true,
      notifyCompletion: true,
      reminderEnabled: true,
      reminderDays: 3
    },
    submissions: {
      total: 20,
      completed: 10,
      inProgress: 8,
      notStarted: 2,
      averageScore: 85
    }
  },
  {
    id: "assign-4",
    template_id: "template-1",
    title: "Web Development Fundamentals - Cohort C",
    description: "Assessment covering HTML, CSS, and basic JavaScript concepts",
    assigned_by: "trainer-1",
    assigner_name: "Sarah Johnson",
    assigned_at: subDays(NOW, 2).toISOString(),
    scheduled_date: addDays(NOW, 5).toISOString(),
    due_date: addDays(NOW, 12).toISOString(),
    status: "scheduled",
    assigned_to: {
      type: "cohort",
      id: "cohort-3",
      name: "Web Development Cohort C"
    },
    settings: {
      timeLimit: 30,
      passingScore: 70,
      randomizeQuestions: true,
      showResults: true,
      allowRetakes: true,
      maxRetakes: 2,
      notifyCompletion: true,
      reminderEnabled: true,
      reminderDays: 1
    },
    submissions: {
      total: 22,
      completed: 0,
      inProgress: 0,
      notStarted: 22,
      averageScore: null
    }
  }
];

// Sample student assessment submissions
export const assessmentSubmissions = {
  quizSubmissions: [
    {
      id: "submission-1",
      assessment_id: "assign-1",
      template_id: "template-1",
      student_id: "student-1",
      student_name: "John Smith",
      submitted_at: subDays(NOW, 7).toISOString(),
      completed: true,
      score: 90,
      percentage: 90,
      passed: true,
      time_spent: 22, // minutes
      answers: [
        {
          question_id: "q1",
          answer: 2, // multiple choice index
          correct: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          question_id: "q2",
          answer: 0,
          correct: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          question_id: "q3",
          answer: true,
          correct: true,
          points_earned: 5,
          points_possible: 5
        },
        {
          question_id: "q4",
          answer: "padding",
          correct: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          question_id: "q5",
          answer: { 0: 0, 1: 1, 2: 3, 3: 2 }, // matching item_id to match_id
          correct: false,
          points_earned: 10,
          points_possible: 20,
          feedback: "You mixed up the purpose of <nav> and <article>."
        }
      ],
      feedback: {
        general: "Great job overall! You demonstrated a strong understanding of HTML and CSS fundamentals.",
        strengths: ["Excellent understanding of HTML elements", "Good knowledge of CSS properties"],
        areas_for_improvement: ["Review semantic HTML elements and their purposes"]
      }
    },
    {
      id: "submission-2",
      assessment_id: "assign-1",
      template_id: "template-1",
      student_id: "student-2",
      student_name: "Emily Johnson",
      submitted_at: subDays(NOW, 8).toISOString(),
      completed: true,
      score: 75,
      percentage: 75,
      passed: true,
      time_spent: 28,
      answers: [
        {
          question_id: "q1",
          answer: 2,
          correct: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          question_id: "q2",
          answer: 2, // incorrect
          correct: false,
          points_earned: 0,
          points_possible: 10,
          feedback: "The correct property is 'color', not 'font-color'."
        },
        {
          question_id: "q3",
          answer: true,
          correct: true,
          points_earned: 5,
          points_possible: 5
        },
        {
          question_id: "q4",
          answer: "margin",
          correct: false,
          points_earned: 0,
          points_possible: 10,
          feedback: "Margin is the space outside the element, padding is inside."
        },
        {
          question_id: "q5",
          answer: { 0: 0, 1: 1, 2: 2, 3: 3 },
          correct: true,
          points_earned: 20,
          points_possible: 20
        }
      ],
      feedback: {
        general: "Good work, but you should review CSS properties more carefully.",
        strengths: ["Good understanding of HTML structure", "Strong on semantic elements"],
        areas_for_improvement: ["Review CSS properties", "Study box model concepts"]
      }
    },
    {
      id: "submission-3",
      assessment_id: "assign-2",
      template_id: "template-2",
      student_id: "student-3",
      student_name: "Miguel Lopez",
      submitted_at: subDays(NOW, 3).toISOString(),
      completed: true,
      score: 65,
      percentage: 65,
      passed: false,
      time_spent: 40,
      answers: [
        {
          question_id: "q6",
          answer: 0, // incorrect
          correct: false,
          points_earned: 0,
          points_possible: 15,
          feedback: "A closure is a function bundled with its lexical environment."
        },
        {
          question_id: "q7",
          answer: true,
          correct: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          question_id: "q8",
          answer: [0, 1, 3, 4], // incorrect (included jQuery)
          correct: false,
          points_earned: 10,
          points_possible: 20,
          feedback: "jQuery is not an ES6 feature. The correct options are 'let and const', 'Arrow functions', 'Template literals', and 'Class syntax'."
        }
      ],
      feedback: {
        general: "You need to review JavaScript advanced concepts, especially closures and ES6 features.",
        strengths: ["Good understanding of promises"],
        areas_for_improvement: ["Study closures more deeply", "Review ES6 features", "Practice with more examples"]
      }
    }
  ],
  projectSubmissions: [
    {
      id: "project-submission-1",
      assessment_id: "assign-3",
      template_id: "project-template-1",
      student_id: "student-1",
      student_name: "John Smith",
      submitted_at: subDays(NOW, 5).toISOString(),
      submission_url: "https://johnsmith-portfolio.netlify.app",
      repository_url: "https://github.com/johnsmith/portfolio",
      completed: true,
      status: "graded", // submitted, in_review, graded
      score: 92,
      percentage: 92,
      passed: true,
      requirements_met: [
        {
          requirement_id: "r1",
          met: true,
          points_earned: 20,
          points_possible: 20,
          feedback: "Excellent responsive design with smooth transitions between breakpoints."
        },
        {
          requirement_id: "r2",
          met: true,
          points_earned: 10,
          points_possible: 10
        },
        {
          requirement_id: "r3",
          met: true,
          points_earned: 15,
          points_possible: 15,
          feedback: "Creative visualization of skills with progress bars."
        },
        {
          requirement_id: "r4",
          met: true,
          points_earned: 20,
          points_possible: 20
        },
        {
          requirement_id: "r5",
          met: true,
          points_earned: 12,
          points_possible: 15,
          feedback: "Contact form works but could improve error messaging."
        },
        {
          requirement_id: "r6",
          met: true,
          points_earned: 8,
          points_possible: 10,
          feedback: "Code is clean but some sections could use more comments."
        },
        {
          requirement_id: "r7",
          met: true,
          points_earned: 10,
          points_possible: 10
        }
      ],
      rubric_scores: {
        design: {
          points_earned: 23,
          points_possible: 25,
          feedback: "Very professional design with minor inconsistencies in mobile view."
        },
        functionality: {
          points_earned: 32,
          points_possible: 35,
          feedback: "All features work well, contact form validation could be more robust."
        },
        code_quality: {
          points_earned: 22,
          points_possible: 25,
          feedback: "Good code organization, could use more consistent commenting."
        },
        deployment: {
          points_earned: 15,
          points_possible: 15,
          feedback: "Perfect deployment with clear documentation."
        }
      },
      feedback: {
        general: "Excellent portfolio site that showcases your skills well. The design is professional and the functionality is solid.",
        strengths: [
          "Strong visual design that maintains brand consistency",
          "Good project showcases with detailed descriptions",
          "Excellent responsive design implementation"
        ],
        areas_for_improvement: [
          "Enhance form validation with more descriptive error messages",
          "Add more detailed comments to JavaScript code",
          "Consider adding more interactive elements"
        ]
      }
    },
    {
      id: "project-submission-2",
      assessment_id: "assign-3",
      template_id: "project-template-1",
      student_id: "student-4",
      student_name: "Aisha Patel",
      submitted_at: subDays(NOW, 2).toISOString(),
      submission_url: "https://aisha-portfolio.netlify.app",
      repository_url: "https://github.com/aishap/portfolio-site",
      completed: true,
      status: "in_review",
      score: null,
      percentage: null,
      passed: null,
      grader_id: "trainer-1",
      grader_name: "Sarah Johnson",
      grader_notes: "Started reviewing - design looks good, need to check functionality more thoroughly.",
      requirements_met: null,
      rubric_scores: null,
      feedback: null
    }
  ]
};

// Sample assessment analytics
export const assessmentAnalytics = {
  // Overall analytics
  overall: {
    total_assessments: 4,
    total_submissions: 40,
    completion_rate: 75, // percentage
    average_score: 80,
    pass_rate: 85, // percentage
    skills_coverage: [
      { skill: "HTML", assessments: 3, average_score: 88 },
      { skill: "CSS", assessments: 3, average_score: 82 },
      { skill: "JavaScript", assessments: 2, average_score: 75 },
      { skill: "React", assessments: 1, average_score: null }, // not enough data
      { skill: "Responsive Design", assessments: 1, average_score: 92 }
    ],
    top_performing_skills: ["Responsive Design", "HTML", "CSS"],
    struggling_skills: ["JavaScript"]
  },
  
  // Analytics per assessment
  assessments: {
    "assign-1": {
      id: "assign-1",
      title: "Web Development Fundamentals - Cohort A",
      type: "quiz",
      total_students: 20,
      completion_rate: 60, // percentage
      average_score: 82,
      average_time: 25, // minutes
      score_distribution: [
        { range: "90-100", count: 4 },
        { range: "80-89", count: 6 },
        { range: "70-79", count: 2 },
        { range: "60-69", count: 0 },
        { range: "Below 60", count: 0 }
      ],
      pass_rate: 100,
      question_analysis: [
        {
          question_id: "q1",
          correct_rate: 92, // percentage
          average_time: 30, // seconds
          difficulty_rating: "easy"
        },
        {
          question_id: "q2",
          correct_rate: 75,
          average_time: 45,
          difficulty_rating: "medium"
        },
        {
          question_id: "q3",
          correct_rate: 100,
          average_time: 20,
          difficulty_rating: "easy"
        },
        {
          question_id: "q4",
          correct_rate: 58,
          average_time: 60,
          difficulty_rating: "hard"
        },
        {
          question_id: "q5",
          correct_rate: 67,
          average_time: 90,
          difficulty_rating: "medium"
        }
      ],
      common_mistakes: [
        {
          question_id: "q4",
          description: "Confusing padding with margin",
          frequency: 42 // percentage
        },
        {
          question_id: "q5",
          description: "Mixing up nav and article elements",
          frequency: 25
        }
      ]
    },
    "assign-2": {
      id: "assign-2",
      title: "JavaScript Advanced Concepts - Cohort B",
      type: "quiz",
      total_students: 18,
      completion_rate: 44,
      average_score: 74,
      average_time: 38,
      score_distribution: [
        { range: "90-100", count: 1 },
        { range: "80-89", count: 3 },
        { range: "70-79", count: 2 },
        { range: "60-69", count: 2 },
        { range: "Below 60", count: 0 }
      ],
      pass_rate: 75,
      question_analysis: [
        {
          question_id: "q6",
          correct_rate: 50,
          average_time: 90,
          difficulty_rating: "hard"
        },
        {
          question_id: "q7",
          correct_rate: 88,
          average_time: 30,
          difficulty_rating: "easy"
        },
        {
          question_id: "q8",
          correct_rate: 63,
          average_time: 85,
          difficulty_rating: "medium"
        }
      ],
      common_mistakes: [
        {
          question_id: "q6",
          description: "Misunderstanding closure concept",
          frequency: 50
        },
        {
          question_id: "q8",
          description: "Identifying jQuery as ES6 feature",
          frequency: 38
        }
      ]
    },
    "assign-3": {
      id: "assign-3",
      title: "Personal Portfolio Project - Cohort A",
      type: "project",
      total_students: 20,
      completion_rate: 50,
      average_score: 85,
      deadline_adherence: 90, // percentage submitted by deadline
      common_issues: [
        { description: "Inconsistent mobile responsiveness", frequency: 30 },
        { description: "Insufficient form validation", frequency: 40 },
        { description: "Poor code commenting", frequency: 60 }
      ],
      strength_areas: [
        { description: "Visual design", average_score: 88 },
        { description: "Project descriptions", average_score: 92 },
        { description: "Deployment", average_score: 95 }
      ],
      improvement_areas: [
        { description: "Form validation", average_score: 75 },
        { description: "Code quality", average_score: 80 },
        { description: "Mobile responsiveness", average_score: 82 }
      ]
    }
  },
  
  // Analytics per cohort
  cohorts: {
    "cohort-1": {
      id: "cohort-1",
      name: "Web Development Cohort A",
      students: 20,
      assessments_assigned: 2,
      average_completion_rate: 55,
      average_score: 84,
      pass_rate: 92,
      performance_by_category: [
        { category: "HTML", average_score: 90 },
        { category: "CSS", average_score: 85 },
        { category: "JavaScript", average_score: 78 },
        { category: "Responsive Design", average_score: 88 }
      ],
      top_performers: [
        { student_id: "student-1", student_name: "John Smith", average_score: 91 },
        { student_id: "student-5", student_name: "Olivia Williams", average_score: 89 }
      ],
      struggling_students: [
        { student_id: "student-8", student_name: "David Chen", average_score: 72 },
        { student_id: "student-12", student_name: "Sofia Martinez", average_score: 68 }
      ],
      progress_over_time: [
        { assessment_id: "assign-1", average_score: 82, completion_date: subDays(NOW, 7).toISOString() },
        { assessment_id: "assign-3", average_score: 85, completion_date: subDays(NOW, 2).toISOString() }
      ]
    },
    "cohort-2": {
      id: "cohort-2",
      name: "Web Development Cohort B",
      students: 18,
      assessments_assigned: 1,
      average_completion_rate: 44,
      average_score: 74,
      pass_rate: 75,
      performance_by_category: [
        { category: "JavaScript", average_score: 74 },
        { category: "ES6", average_score: 70 },
        { category: "Asynchronous Programming", average_score: 68 }
      ],
      top_performers: [
        { student_id: "student-21", student_name: "Emma Davis", average_score: 95 },
        { student_id: "student-24", student_name: "Jamal Wilson", average_score: 88 }
      ],
      struggling_students: [
        { student_id: "student-3", student_name: "Miguel Lopez", average_score: 65 },
        { student_id: "student-29", student_name: "Rebecca Taylor", average_score: 62 }
      ],
      progress_over_time: [
        { assessment_id: "assign-2", average_score: 74, completion_date: subDays(NOW, 3).toISOString() }
      ]
    }
  }
};

// Mock API functions

export const getAssessmentTemplates = (status = null) => {
  let templates = [
    ...assessmentTemplates.quizTemplates,
    ...assessmentTemplates.projectTemplates
  ];
  
  if (status) {
    templates = templates.filter(template => template.status === status);
  }
  
  return Promise.resolve(templates);
};

export const getAssessmentTemplateById = (id) => {
  const allTemplates = [
    ...assessmentTemplates.quizTemplates,
    ...assessmentTemplates.projectTemplates
  ];
  
  const template = allTemplates.find(t => t.id === id);
  
  if (!template) {
    return Promise.reject(new Error('Assessment template not found'));
  }
  
  return Promise.resolve(template);
};

export const createAssessmentTemplate = (templateData) => {
  // In a real implementation, this would add the template to the database
  // For our mock, we'll just simulate a successful creation
  const newTemplate = {
    id: `template-${Date.now()}`,
    created_by: "trainer-1", // In real app, this would be the logged-in user
    creator_name: "Sarah Johnson",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    status: "draft",
    ...templateData
  };
  
  return Promise.resolve(newTemplate);
};

export const updateAssessmentTemplate = (id, templateData) => {
  const allTemplates = [
    ...assessmentTemplates.quizTemplates,
    ...assessmentTemplates.projectTemplates
  ];
  
  const template = allTemplates.find(t => t.id === id);
  
  if (!template) {
    return Promise.reject(new Error('Assessment template not found'));
  }
  
  // In a real implementation, this would update the template in the database
  const updatedTemplate = {
    ...template,
    ...templateData,
    updated_at: new Date().toISOString()
  };
  
  return Promise.resolve(updatedTemplate);
};

export const getAssignedAssessments = (status = null) => {
  let assigned = [...assignedAssessments];
  
  if (status) {
    assigned = assigned.filter(a => a.status === status);
  }
  
  return Promise.resolve(assigned);
};

export const getAssignedAssessmentById = (id) => {
  const assessment = assignedAssessments.find(a => a.id === id);
  
  if (!assessment) {
    return Promise.reject(new Error('Assigned assessment not found'));
  }
  
  return Promise.resolve(assessment);
};

export const assignAssessment = (assignmentData) => {
  // In a real implementation, this would add the assignment to the database
  const newAssignment = {
    id: `assign-${Date.now()}`,
    assigned_by: "trainer-1", // In real app, this would be the logged-in user
    assigner_name: "Sarah Johnson",
    assigned_at: new Date().toISOString(),
    status: assignmentData.scheduled_date ? "scheduled" : "active",
    ...assignmentData
  };
  
  return Promise.resolve(newAssignment);
};

export const getSubmissionsByAssessment = (assessmentId) => {
  // Combine quiz and project submissions
  const allSubmissions = [
    ...assessmentSubmissions.quizSubmissions,
    ...assessmentSubmissions.projectSubmissions
  ];
  
  const submissions = allSubmissions.filter(s => s.assessment_id === assessmentId);
  
  return Promise.resolve(submissions);
};

export const getSubmissionById = (submissionId) => {
  // Check both quiz and project submissions
  const allSubmissions = [
    ...assessmentSubmissions.quizSubmissions,
    ...assessmentSubmissions.projectSubmissions
  ];
  
  const submission = allSubmissions.find(s => s.id === submissionId);
  
  if (!submission) {
    return Promise.reject(new Error('Submission not found'));
  }
  
  return Promise.resolve(submission);
};

export const gradeSubmission = (submissionId, gradingData) => {
  // Find the submission to update
  const allSubmissions = [
    ...assessmentSubmissions.quizSubmissions,
    ...assessmentSubmissions.projectSubmissions
  ];
  
  const submission = allSubmissions.find(s => s.id === submissionId);
  
  if (!submission) {
    return Promise.reject(new Error('Submission not found'));
  }
  
  // In a real implementation, this would update the submission in the database
  const updatedSubmission = {
    ...submission,
    status: "graded",
    graded_at: new Date().toISOString(),
    grader_id: "trainer-1", // In real app, this would be the logged-in user
    grader_name: "Sarah Johnson",
    ...gradingData
  };
  
  return Promise.resolve(updatedSubmission);
};

export const getAssessmentAnalytics = () => {
  return Promise.resolve(assessmentAnalytics.overall);
};

export const getAssessmentAnalyticsByAssessment = (assessmentId) => {
  const analytics = assessmentAnalytics.assessments[assessmentId];
  
  if (!analytics) {
    return Promise.reject(new Error('Assessment analytics not found'));
  }
  
  return Promise.resolve(analytics);
};

export const getAssessmentAnalyticsByCohort = (cohortId) => {
  const analytics = assessmentAnalytics.cohorts[cohortId];
  
  if (!analytics) {
    return Promise.reject(new Error('Cohort analytics not found'));
  }
  
  return Promise.resolve(analytics);
};