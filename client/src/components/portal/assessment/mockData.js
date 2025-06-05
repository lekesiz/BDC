/**
 * Mock data for assessments and quizzes
 */
import { subDays, addDays } from 'date-fns';
const NOW = new Date();
// Sample assessment data
export const assessmentsData = {
  moduleAssessments: [
    {
      id: "m1-assessment",
      title: "HTML/CSS Fundamentals Assessment",
      moduleId: 1,
      moduleName: "HTML/CSS Fundamentals",
      description: "Test your understanding of HTML and CSS concepts covered in this module",
      duration: 20, // in minutes
      questionCount: 10,
      attempts: {
        allowed: 2,
        completed: 1,
        bestScore: 90
      },
      status: "completed",
      dueDate: subDays(NOW, 5).toISOString(),
      completedDate: subDays(NOW, 7).toISOString(),
      passingScore: 70,
      type: "quiz"
    },
    {
      id: "m2-assessment",
      title: "JavaScript Basics Assessment",
      moduleId: 2,
      moduleName: "JavaScript Basics",
      description: "Test your understanding of JavaScript fundamentals covered in this module",
      duration: 30, // in minutes
      questionCount: 15,
      attempts: {
        allowed: 2,
        completed: 1,
        bestScore: 85
      },
      status: "completed",
      dueDate: subDays(NOW, 2).toISOString(),
      completedDate: subDays(NOW, 3).toISOString(),
      passingScore: 70,
      type: "quiz"
    },
    {
      id: "m3-assessment",
      title: "JavaScript Advanced Assessment",
      moduleId: 3,
      moduleName: "JavaScript Advanced",
      description: "Test your understanding of advanced JavaScript concepts covered in this module",
      duration: 45, // in minutes
      questionCount: 20,
      attempts: {
        allowed: 3,
        completed: 0,
        bestScore: null
      },
      status: "available",
      dueDate: addDays(NOW, 5).toISOString(),
      completedDate: null,
      passingScore: 75,
      type: "quiz"
    },
    {
      id: "m3-project",
      title: "JavaScript Advanced Project",
      moduleId: 3,
      moduleName: "JavaScript Advanced",
      description: "Apply advanced JavaScript concepts to build a small application",
      duration: null, // No time limit for projects
      submissions: {
        allowed: 2,
        completed: 0,
        bestScore: null
      },
      status: "available",
      dueDate: addDays(NOW, 10).toISOString(),
      completedDate: null,
      passingScore: 70,
      type: "project",
      requirements: [
        "Implement at least 3 advanced JavaScript concepts (closures, promises, etc.)",
        "Create a responsive user interface",
        "Include proper error handling",
        "Add comprehensive documentation"
      ]
    }
  ],
  programAssessments: [
    {
      id: "p1-midterm",
      title: "Web Development Midterm Exam",
      description: "Comprehensive assessment covering HTML, CSS, and JavaScript fundamentals",
      duration: 90, // in minutes
      questionCount: 50,
      attempts: {
        allowed: 1,
        completed: 0,
        bestScore: null
      },
      status: "upcoming",
      availableDate: addDays(NOW, 15).toISOString(),
      dueDate: addDays(NOW, 20).toISOString(),
      completedDate: null,
      passingScore: 75,
      type: "exam"
    }
  ],
  skillAssessments: [
    {
      id: "s1-html",
      title: "HTML Proficiency Assessment",
      skillId: 1,
      skillName: "HTML",
      description: "Evaluate your HTML knowledge and identify areas for improvement",
      duration: 15, // in minutes
      questionCount: 10,
      attempts: {
        allowed: 999, // Unlimited
        completed: 2,
        scores: [70, 85],
        bestScore: 85
      },
      status: "available",
      dueDate: null, // No due date for skill assessments
      completedDate: subDays(NOW, 10).toISOString(),
      passingScore: 0, // No passing score, just for evaluation
      type: "evaluation"
    },
    {
      id: "s2-css",
      title: "CSS Proficiency Assessment",
      skillId: 2,
      skillName: "CSS",
      description: "Evaluate your CSS knowledge and identify areas for improvement",
      duration: 15, // in minutes
      questionCount: 10,
      attempts: {
        allowed: 999, // Unlimited
        completed: 1,
        scores: [75],
        bestScore: 75
      },
      status: "available",
      dueDate: null, // No due date for skill assessments
      completedDate: subDays(NOW, 8).toISOString(),
      passingScore: 0, // No passing score, just for evaluation
      type: "evaluation"
    },
    {
      id: "s3-js",
      title: "JavaScript Proficiency Assessment",
      skillId: 3,
      skillName: "JavaScript",
      description: "Evaluate your JavaScript knowledge and identify areas for improvement",
      duration: 20, // in minutes
      questionCount: 15,
      attempts: {
        allowed: 999, // Unlimited
        completed: 0,
        scores: [],
        bestScore: null
      },
      status: "available",
      dueDate: null, // No due date for skill assessments
      completedDate: null,
      passingScore: 0, // No passing score, just for evaluation
      type: "evaluation"
    }
  ]
};
// Sample quiz data
export const quizzes = {
  "m1-assessment": {
    id: "m1-assessment",
    title: "HTML/CSS Fundamentals Assessment",
    description: "Test your understanding of HTML and CSS concepts covered in this module",
    timeLimit: 20 * 60, // in seconds
    passingScore: 70,
    questions: [
      {
        type: "multipleChoice",
        question: "Which HTML element is used to define the main heading of a document?",
        options: ["<header>", "<heading>", "<h1>", "<main>"],
        correctAnswer: 2
      },
      {
        type: "multipleChoice",
        question: "Which CSS property is used to change the text color of an element?",
        options: ["color", "text-color", "font-color", "background-color"],
        correctAnswer: 0
      },
      {
        type: "trueFalse",
        question: "CSS stands for Cascading Style Sheets.",
        correctAnswer: true,
        explanation: "CSS (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML."
      },
      {
        type: "trueFalse",
        question: "The HTML <section> element represents a generic section of a document, typically with a heading.",
        correctAnswer: true
      },
      {
        type: "shortAnswer",
        question: "What CSS property is used to add space between the border and the content of an element?",
        correctAnswer: "padding",
        explanation: "Padding creates space inside the element between its content and its border."
      },
      {
        type: "matching",
        question: "Match the HTML elements with their purposes:",
        items: [
          { id: 0, text: "<header>", match: "Container for introductory content" },
          { id: 1, text: "<footer>", match: "Container for footer content" },
          { id: 2, text: "<nav>", match: "Container for navigation links" },
          { id: 3, text: "<article>", match: "Container for independent, self-contained content" }
        ],
        correctMatches: { 0: 0, 1: 1, 2: 2, 3: 3 }
      },
      {
        type: "multipleAnswer",
        question: "Which of the following are valid CSS selectors?",
        options: [
          "#header",
          ".container",
          "div > p",
          "div p",
          "div[class]",
          "div:class"
        ],
        correctAnswers: [0, 1, 2, 3, 4]
      },
      {
        type: "multipleChoice",
        question: "Which CSS property is used to make text bold?",
        options: ["font-style", "text-decoration", "font-weight", "font-variant"],
        correctAnswer: 2
      },
      {
        type: "shortAnswer",
        question: "What property do you use to create space between elements?",
        correctAnswer: ["margin", "margin-top", "margin-bottom", "margin-left", "margin-right"],
        explanation: "Margin creates space outside the element, separating it from other elements."
      },
      {
        type: "multipleChoice",
        question: "Which HTML tag is used to define an unordered list?",
        options: ["<ol>", "<li>", "<ul>", "<list>"],
        correctAnswer: 2
      }
    ]
  },
  "m2-assessment": {
    id: "m2-assessment",
    title: "JavaScript Basics Assessment",
    description: "Test your understanding of JavaScript fundamentals covered in this module",
    timeLimit: 30 * 60, // in seconds
    passingScore: 70,
    questions: [
      {
        type: "multipleChoice",
        question: "Which of the following is NOT a JavaScript data type?",
        options: ["String", "Boolean", "Integer", "Object"],
        correctAnswer: 2,
        explanation: "JavaScript does not have an Integer type. Numbers in JavaScript are represented by the Number type."
      },
      {
        type: "trueFalse",
        question: "JavaScript is a case-sensitive language.",
        correctAnswer: true,
        explanation: "In JavaScript, variables, function names, and operators are all case sensitive."
      },
      {
        type: "shortAnswer",
        question: "What keyword is used to declare a variable in JavaScript that cannot be reassigned?",
        correctAnswer: "const",
        explanation: "The 'const' keyword declares a variable that cannot be reassigned after initialization."
      },
      // More questions would be added here...
    ]
  },
  "m3-assessment": {
    id: "m3-assessment",
    title: "JavaScript Advanced Assessment",
    description: "Test your understanding of advanced JavaScript concepts covered in this module",
    timeLimit: 45 * 60, // in seconds
    passingScore: 75,
    questions: [
      {
        type: "multipleChoice",
        question: "What is a closure in JavaScript?",
        options: [
          "A function that has no access to its outer scope variables",
          "A function along with its lexical environment",
          "A method to close browser windows",
          "A way to prevent memory leaks"
        ],
        correctAnswer: 1,
        explanation: "A closure is the combination of a function bundled together with references to its surrounding state (the lexical environment)."
      },
      {
        type: "trueFalse",
        question: "Promises in JavaScript are used for handling asynchronous operations.",
        correctAnswer: true,
        explanation: "Promises provide a way to handle asynchronous operations more cleanly than callbacks."
      },
      {
        type: "shortAnswer",
        question: "What is the method in JavaScript that creates a new array with the results of calling a provided function on every element in the calling array?",
        correctAnswer: "map",
        explanation: "The map() method creates a new array populated with the results of calling a provided function on every element in the calling array."
      },
      // More questions would be added here...
    ]
  },
  "s1-html": {
    id: "s1-html",
    title: "HTML Proficiency Assessment",
    description: "Evaluate your HTML knowledge and identify areas for improvement",
    timeLimit: 15 * 60, // in seconds
    passingScore: 0, // No passing score for evaluation
    questions: [
      {
        type: "multipleChoice",
        question: "Which attribute is used to provide alternative text for an image?",
        options: ["title", "alt", "src", "href"],
        correctAnswer: 1
      },
      {
        type: "trueFalse",
        question: "The <div> element is a semantic HTML element.",
        correctAnswer: false,
        explanation: "The <div> element is a non-semantic element. Semantic elements like <article>, <section>, <nav> clearly describe their purpose."
      },
      {
        type: "multipleAnswer",
        question: "Which of the following are valid HTML5 form input types?",
        options: ["date", "color", "range", "slider", "password", "toggle"],
        correctAnswers: [0, 1, 2, 4]
      },
      // More questions would be added here...
    ]
  }
};
// Sample assessment results
export const assessmentResults = {
  "m1-assessment": {
    id: "m1-assessment",
    assessmentId: "m1-assessment",
    score: 90,
    answers: {
      0: 2,
      1: 0,
      2: true,
      3: true,
      4: "padding",
      5: { 0: 0, 1: 1, 2: 2, 3: 3 },
      6: [0, 1, 2, 3, 4],
      7: 2,
      8: "margin",
      9: 2
    },
    correctCount: 9,
    totalQuestions: 10,
    timeSpent: 15 * 60, // 15 minutes in seconds
    completedAt: subDays(NOW, 7).toISOString(),
    feedback: "Excellent understanding of HTML and CSS fundamentals! You might want to review CSS selectors a bit more."
  }
};
// Mock API functions
export const getAssessments = () => {
  return Promise.resolve(assessmentsData);
};
export const getAssessmentById = (id) => {
  // Find the assessment in all categories
  const allAssessments = [
    ...assessmentsData.moduleAssessments,
    ...assessmentsData.programAssessments,
    ...assessmentsData.skillAssessments
  ];
  const assessment = allAssessments.find(a => a.id === id);
  if (!assessment) {
    return Promise.reject(new Error('Assessment not found'));
  }
  return Promise.resolve(assessment);
};
export const getQuizById = (id) => {
  const quiz = quizzes[id];
  if (!quiz) {
    return Promise.reject(new Error('Quiz not found'));
  }
  return Promise.resolve(quiz);
};
export const getAssessmentResult = (assessmentId) => {
  const result = assessmentResults[assessmentId];
  if (!result) {
    return Promise.reject(new Error('Assessment result not found'));
  }
  return Promise.resolve(result);
};
export const submitQuizResults = (assessmentId, results) => {
  // In a real implementation, this would store the results in the database
  // For our mock, we'll just simulate a successful submission
  return Promise.resolve({
    success: true,
    message: "Quiz results submitted successfully",
    results
  });
};