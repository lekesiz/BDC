// Database seeding utilities for consistent test data
const axios = require('axios');

const API_BASE_URL = process.env.CYPRESS_apiUrl || 'http://localhost:5001/api';

class DatabaseSeeder {
  constructor() {
    this.adminToken = null;
    this.seededData = {
      users: [],
      beneficiaries: [],
      programs: [],
      evaluations: [],
      appointments: [],
      documents: []
    };
  }

  async authenticate() {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: 'admin@bdc.test',
        password: 'Admin123!Test'
      });
      this.adminToken = response.data.token;
      return this.adminToken;
    } catch (error) {
      console.error('Authentication failed:', error.message);
      throw error;
    }
  }

  getAuthHeaders() {
    return {
      Authorization: `Bearer ${this.adminToken}`,
      'Content-Type': 'application/json'
    };
  }

  async clearDatabase() {
    try {
      if (!this.adminToken) await this.authenticate();

      // Clear in reverse dependency order
      await axios.delete(`${API_BASE_URL}/test/appointments`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/evaluations`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/documents`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/program-assignments`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/programs`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/beneficiaries`, { headers: this.getAuthHeaders() });
      await axios.delete(`${API_BASE_URL}/test/users`, { headers: this.getAuthHeaders() });

      // Reset seeded data tracking
      this.seededData = {
        users: [],
        beneficiaries: [],
        programs: [],
        evaluations: [],
        appointments: [],
        documents: []
      };

      console.log('Database cleared successfully');
    } catch (error) {
      console.error('Database clear failed:', error.message);
      throw error;
    }
  }

  async seedUsers() {
    try {
      if (!this.adminToken) await this.authenticate();

      const users = [
        // Admin user
        {
          username: 'admin_test',
          email: 'admin@bdc.test',
          password: 'Admin123!Test',
          firstName: 'Admin',
          lastName: 'User',
          role: 'admin',
          isActive: true
        },
        // Tenant user
        {
          username: 'tenant_test',
          email: 'tenant@bdc.test',
          password: 'Tenant123!Test',
          firstName: 'Tenant',
          lastName: 'Manager',
          role: 'tenant',
          isActive: true,
          tenantId: 'tenant-001'
        },
        // Trainer users
        {
          username: 'trainer_john',
          email: 'trainer@bdc.test',
          password: 'Trainer123!Test',
          firstName: 'John',
          lastName: 'Trainer',
          role: 'trainer',
          isActive: true,
          specializations: ['Web Development', 'Data Science']
        },
        {
          username: 'trainer_jane',
          email: 'jane.trainer@bdc.test',
          password: 'Trainer123!Test',
          firstName: 'Jane',
          lastName: 'Smith',
          role: 'trainer',
          isActive: true,
          specializations: ['Mobile Development', 'UI/UX Design']
        },
        // Student/Beneficiary users
        {
          username: 'student_user',
          email: 'student@bdc.test',
          password: 'Student123!Test',
          firstName: 'Student',
          lastName: 'User',
          role: 'student',
          isActive: true
        },
        {
          username: 'john_doe',
          email: 'john.doe@student.test',
          password: 'Student123!Test',
          firstName: 'John',
          lastName: 'Doe',
          role: 'student',
          isActive: true
        },
        {
          username: 'jane_doe',
          email: 'jane.doe@student.test',
          password: 'Student123!Test',
          firstName: 'Jane',
          lastName: 'Doe',
          role: 'student',
          isActive: true
        }
      ];

      for (const user of users) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/users`, user, {
            headers: this.getAuthHeaders()
          });
          this.seededData.users.push(response.data);
        } catch (error) {
          console.warn(`Failed to create user ${user.email}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.users.length} users`);
    } catch (error) {
      console.error('User seeding failed:', error.message);
      throw error;
    }
  }

  async seedBeneficiaries() {
    try {
      if (!this.adminToken) await this.authenticate();

      const beneficiaries = [
        {
          firstName: 'Alice',
          lastName: 'Johnson',
          email: 'alice.johnson@beneficiary.test',
          phone: '+1234567001',
          dateOfBirth: '1995-03-15',
          address: '123 Main St',
          city: 'New York',
          state: 'NY',
          zipCode: '10001',
          emergencyContactName: 'Bob Johnson',
          emergencyContactPhone: '+1234567002',
          educationLevel: 'bachelor',
          employmentStatus: 'unemployed',
          interests: 'Web Development, Data Analysis',
          status: 'active'
        },
        {
          firstName: 'Bob',
          lastName: 'Smith',
          email: 'bob.smith@beneficiary.test',
          phone: '+1234567003',
          dateOfBirth: '1988-07-22',
          address: '456 Oak Ave',
          city: 'Los Angeles',
          state: 'CA',
          zipCode: '90210',
          emergencyContactName: 'Sarah Smith',
          emergencyContactPhone: '+1234567004',
          educationLevel: 'highschool',
          employmentStatus: 'parttime',
          interests: 'Mobile Development, UI Design',
          status: 'active'
        },
        {
          firstName: 'Carol',
          lastName: 'Williams',
          email: 'carol.williams@beneficiary.test',
          phone: '+1234567005',
          dateOfBirth: '1992-11-08',
          address: '789 Pine Rd',
          city: 'Chicago',
          state: 'IL',
          zipCode: '60601',
          emergencyContactName: 'David Williams',
          emergencyContactPhone: '+1234567006',
          educationLevel: 'masters',
          employmentStatus: 'unemployed',
          interests: 'Data Science, Machine Learning',
          status: 'active'
        },
        {
          firstName: 'David',
          lastName: 'Brown',
          email: 'david.brown@beneficiary.test',
          phone: '+1234567007',
          dateOfBirth: '1990-01-30',
          address: '321 Elm St',
          city: 'Houston',
          state: 'TX',
          zipCode: '77001',
          emergencyContactName: 'Lisa Brown',
          emergencyContactPhone: '+1234567008',
          educationLevel: 'bachelor',
          employmentStatus: 'unemployed',
          interests: 'Cybersecurity, Network Administration',
          status: 'active'
        },
        {
          firstName: 'Emma',
          lastName: 'Davis',
          email: 'emma.davis@beneficiary.test',
          phone: '+1234567009',
          dateOfBirth: '1994-05-12',
          address: '654 Maple Dr',
          city: 'Phoenix',
          state: 'AZ',
          zipCode: '85001',
          emergencyContactName: 'Michael Davis',
          emergencyContactPhone: '+1234567010',
          educationLevel: 'associate',
          employmentStatus: 'unemployed',
          interests: 'Cloud Computing, DevOps',
          status: 'inactive'
        }
      ];

      for (const beneficiary of beneficiaries) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/beneficiaries`, beneficiary, {
            headers: this.getAuthHeaders()
          });
          this.seededData.beneficiaries.push(response.data);
        } catch (error) {
          console.warn(`Failed to create beneficiary ${beneficiary.email}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.beneficiaries.length} beneficiaries`);
    } catch (error) {
      console.error('Beneficiary seeding failed:', error.message);
      throw error;
    }
  }

  async seedPrograms() {
    try {
      if (!this.adminToken) await this.authenticate();

      const programs = [
        {
          name: 'Web Development Bootcamp',
          description: 'Comprehensive full-stack web development training program covering HTML, CSS, JavaScript, React, Node.js, and database management.',
          startDate: '2025-07-01',
          endDate: '2025-09-30',
          duration: 12, // weeks
          category: 'Technology',
          level: 'Beginner to Intermediate',
          maxParticipants: 25,
          status: 'active',
          objectives: [
            'Master HTML5 and CSS3 fundamentals',
            'Learn JavaScript ES6+ features',
            'Build responsive web applications',
            'Understand React.js ecosystem',
            'Develop REST APIs with Node.js',
            'Work with databases (MongoDB, PostgreSQL)'
          ],
          schedule: {
            daysPerWeek: 5,
            hoursPerDay: 6,
            startTime: '09:00',
            endTime: '15:00'
          }
        },
        {
          name: 'Data Science Fundamentals',
          description: 'Introduction to data science concepts, tools, and techniques including Python programming, statistics, and machine learning basics.',
          startDate: '2025-08-15',
          endDate: '2025-11-15',
          duration: 14, // weeks
          category: 'Data Science',
          level: 'Beginner',
          maxParticipants: 20,
          status: 'active',
          objectives: [
            'Learn Python for data analysis',
            'Understand statistical concepts',
            'Master pandas and numpy libraries',
            'Create data visualizations',
            'Introduction to machine learning',
            'Work with real datasets'
          ],
          schedule: {
            daysPerWeek: 3,
            hoursPerDay: 4,
            startTime: '14:00',
            endTime: '18:00'
          }
        },
        {
          name: 'Mobile App Development',
          description: 'Learn to build native and cross-platform mobile applications using React Native and Flutter frameworks.',
          startDate: '2025-09-01',
          endDate: '2025-12-01',
          duration: 13, // weeks
          category: 'Mobile Development',
          level: 'Intermediate',
          maxParticipants: 15,
          status: 'planning',
          objectives: [
            'Understand mobile development principles',
            'Master React Native framework',
            'Learn Flutter development',
            'Implement native device features',
            'Publish apps to app stores',
            'Optimize for performance'
          ],
          schedule: {
            daysPerWeek: 4,
            hoursPerDay: 5,
            startTime: '10:00',
            endTime: '15:00'
          }
        },
        {
          name: 'Cybersecurity Essentials',
          description: 'Comprehensive cybersecurity training covering network security, ethical hacking, and security best practices.',
          startDate: '2025-10-01',
          endDate: '2025-12-31',
          duration: 13, // weeks
          category: 'Cybersecurity',
          level: 'Intermediate to Advanced',
          maxParticipants: 12,
          status: 'planning',
          objectives: [
            'Understand security fundamentals',
            'Learn ethical hacking techniques',
            'Master network security protocols',
            'Implement security frameworks',
            'Conduct security assessments',
            'Respond to security incidents'
          ],
          schedule: {
            daysPerWeek: 3,
            hoursPerDay: 6,
            startTime: '09:00',
            endTime: '15:00'
          }
        },
        {
          name: 'UI/UX Design Workshop',
          description: 'Hands-on design workshop focusing on user interface and user experience design principles and tools.',
          startDate: '2025-06-15',
          endDate: '2025-08-15',
          duration: 8, // weeks
          category: 'Design',
          level: 'Beginner to Intermediate',
          maxParticipants: 18,
          status: 'completed',
          objectives: [
            'Understand design principles',
            'Master design tools (Figma, Adobe XD)',
            'Create user personas and journeys',
            'Design responsive interfaces',
            'Conduct usability testing',
            'Build design systems'
          ],
          schedule: {
            daysPerWeek: 2,
            hoursPerDay: 4,
            startTime: '18:00',
            endTime: '22:00'
          }
        }
      ];

      for (const program of programs) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/programs`, program, {
            headers: this.getAuthHeaders()
          });
          this.seededData.programs.push(response.data);
        } catch (error) {
          console.warn(`Failed to create program ${program.name}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.programs.length} programs`);
    } catch (error) {
      console.error('Program seeding failed:', error.message);
      throw error;
    }
  }

  async seedEvaluations() {
    try {
      if (!this.adminToken) await this.authenticate();

      const evaluations = [
        {
          title: 'JavaScript Fundamentals Quiz',
          description: 'Test your knowledge of JavaScript basics including variables, functions, and control structures.',
          duration: 30, // minutes
          passingScore: 70,
          maxAttempts: 3,
          category: 'Programming',
          difficulty: 'beginner',
          randomizeQuestions: true,
          showResultsImmediately: true,
          questions: [
            {
              type: 'multiple_choice',
              text: 'What is the correct way to declare a variable in JavaScript?',
              points: 5,
              options: [
                { text: 'var myVar = 5;', isCorrect: true },
                { text: 'variable myVar = 5;', isCorrect: false },
                { text: 'v myVar = 5;', isCorrect: false },
                { text: 'declare myVar = 5;', isCorrect: false }
              ],
              explanation: 'Variables in JavaScript can be declared using var, let, or const keywords.'
            },
            {
              type: 'true_false',
              text: 'JavaScript is a compiled language.',
              points: 3,
              correctAnswer: false,
              explanation: 'JavaScript is an interpreted language, not compiled.'
            },
            {
              type: 'short_answer',
              text: 'What does DOM stand for?',
              points: 4,
              correctAnswers: ['Document Object Model'],
              explanation: 'DOM stands for Document Object Model, which represents the HTML document structure.'
            }
          ]
        },
        {
          title: 'HTML & CSS Assessment',
          description: 'Comprehensive test covering HTML structure and CSS styling concepts.',
          duration: 45, // minutes
          passingScore: 75,
          maxAttempts: 2,
          category: 'Web Development',
          difficulty: 'beginner',
          randomizeQuestions: false,
          showResultsImmediately: false,
          questions: [
            {
              type: 'multiple_choice',
              text: 'Which HTML tag is used to create a hyperlink?',
              points: 3,
              options: [
                { text: '<link>', isCorrect: false },
                { text: '<a>', isCorrect: true },
                { text: '<href>', isCorrect: false },
                { text: '<url>', isCorrect: false }
              ]
            },
            {
              type: 'multiple_choice',
              text: 'Which CSS property is used to change the text color?',
              points: 3,
              options: [
                { text: 'font-color', isCorrect: false },
                { text: 'text-color', isCorrect: false },
                { text: 'color', isCorrect: true },
                { text: 'foreground-color', isCorrect: false }
              ]
            },
            {
              type: 'essay',
              text: 'Explain the difference between block and inline elements in HTML. Provide examples of each.',
              points: 10,
              wordLimit: 200,
              rubric: [
                { criteria: 'Understanding of block elements', points: 3 },
                { criteria: 'Understanding of inline elements', points: 3 },
                { criteria: 'Provides accurate examples', points: 2 },
                { criteria: 'Clear explanation', points: 2 }
              ]
            }
          ]
        },
        {
          title: 'Data Science Concepts',
          description: 'Test your understanding of basic data science concepts and Python programming.',
          duration: 60, // minutes
          passingScore: 80,
          maxAttempts: 2,
          category: 'Data Science',
          difficulty: 'intermediate',
          randomizeQuestions: true,
          showResultsImmediately: true,
          questions: [
            {
              type: 'multiple_choice',
              text: 'Which Python library is primarily used for data manipulation and analysis?',
              points: 5,
              options: [
                { text: 'NumPy', isCorrect: false },
                { text: 'Pandas', isCorrect: true },
                { text: 'Matplotlib', isCorrect: false },
                { text: 'Scikit-learn', isCorrect: false }
              ]
            },
            {
              type: 'short_answer',
              text: 'What does SQL stand for?',
              points: 3,
              correctAnswers: ['Structured Query Language'],
              explanation: 'SQL stands for Structured Query Language, used for managing relational databases.'
            }
          ]
        }
      ];

      for (const evaluation of evaluations) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/evaluations`, evaluation, {
            headers: this.getAuthHeaders()
          });
          this.seededData.evaluations.push(response.data);
        } catch (error) {
          console.warn(`Failed to create evaluation ${evaluation.title}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.evaluations.length} evaluations`);
    } catch (error) {
      console.error('Evaluation seeding failed:', error.message);
      throw error;
    }
  }

  async seedAppointments() {
    try {
      if (!this.adminToken) await this.authenticate();

      const appointments = [
        {
          title: 'Career Guidance Session',
          description: 'Discussion about career paths in web development',
          startTime: '2025-07-15T10:00:00Z',
          endTime: '2025-07-15T11:00:00Z',
          type: 'consultation',
          status: 'scheduled',
          trainerEmail: 'trainer@bdc.test',
          studentEmail: 'john.doe@student.test',
          meetingMethod: 'video-call',
          notes: 'Student interested in frontend development career paths'
        },
        {
          title: 'Technical Interview Prep',
          description: 'Mock technical interview practice session',
          startTime: '2025-07-16T14:00:00Z',
          endTime: '2025-07-16T15:30:00Z',
          type: 'interview-prep',
          status: 'scheduled',
          trainerEmail: 'jane.trainer@bdc.test',
          studentEmail: 'jane.doe@student.test',
          meetingMethod: 'in-person',
          notes: 'Focus on JavaScript and React questions'
        },
        {
          title: 'Project Review',
          description: 'Review of final capstone project',
          startTime: '2025-07-17T09:00:00Z',
          endTime: '2025-07-17T10:00:00Z',
          type: 'project-review',
          status: 'completed',
          trainerEmail: 'trainer@bdc.test',
          studentEmail: 'alice.johnson@beneficiary.test',
          meetingMethod: 'video-call',
          notes: 'Excellent work on the e-commerce project',
          rating: 5,
          feedback: 'Great implementation of React best practices'
        },
        {
          title: 'One-on-One Mentoring',
          description: 'Personal mentoring session for skill development',
          startTime: '2025-07-18T16:00:00Z',
          endTime: '2025-07-18T17:00:00Z',
          type: 'mentoring',
          status: 'scheduled',
          trainerEmail: 'jane.trainer@bdc.test',
          studentEmail: 'bob.smith@beneficiary.test',
          meetingMethod: 'video-call',
          notes: 'Focus on mobile development concepts'
        },
        {
          title: 'Group Study Session',
          description: 'Collaborative learning session on data structures',
          startTime: '2025-07-19T13:00:00Z',
          endTime: '2025-07-19T15:00:00Z',
          type: 'group-session',
          status: 'scheduled',
          trainerEmail: 'trainer@bdc.test',
          participants: [
            'carol.williams@beneficiary.test',
            'david.brown@beneficiary.test',
            'emma.davis@beneficiary.test'
          ],
          meetingMethod: 'in-person',
          maxParticipants: 5,
          notes: 'Covering algorithms and data structures'
        }
      ];

      for (const appointment of appointments) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/appointments`, appointment, {
            headers: this.getAuthHeaders()
          });
          this.seededData.appointments.push(response.data);
        } catch (error) {
          console.warn(`Failed to create appointment ${appointment.title}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.appointments.length} appointments`);
    } catch (error) {
      console.error('Appointment seeding failed:', error.message);
      throw error;
    }
  }

  async seedDocuments() {
    try {
      if (!this.adminToken) await this.authenticate();

      const documents = [
        {
          title: 'JavaScript Cheat Sheet',
          description: 'Quick reference guide for JavaScript syntax and methods',
          category: 'Reference Material',
          type: 'pdf',
          size: 245760, // 240 KB
          uploadedBy: 'trainer@bdc.test',
          sharedWith: ['Web Development Bootcamp'],
          permissions: 'read',
          tags: ['javascript', 'reference', 'programming'],
          version: '1.0',
          isPublic: false
        },
        {
          title: 'React Best Practices Guide',
          description: 'Comprehensive guide to React.js development best practices',
          category: 'Training Material',
          type: 'pdf',
          size: 512000, // 500 KB
          uploadedBy: 'jane.trainer@bdc.test',
          sharedWith: ['Web Development Bootcamp'],
          permissions: 'read',
          tags: ['react', 'best-practices', 'frontend'],
          version: '2.1',
          isPublic: true
        },
        {
          title: 'Data Science Resources',
          description: 'Collection of useful links and resources for data science learning',
          category: 'Resource List',
          type: 'docx',
          size: 156780, // 153 KB
          uploadedBy: 'trainer@bdc.test',
          sharedWith: ['Data Science Fundamentals'],
          permissions: 'read-write',
          tags: ['data-science', 'resources', 'learning'],
          version: '1.3',
          isPublic: false
        },
        {
          title: 'Project Requirements Template',
          description: 'Template for documenting project requirements and specifications',
          category: 'Template',
          type: 'docx',
          size: 89432, // 87 KB
          uploadedBy: 'admin@bdc.test',
          sharedWith: ['all'],
          permissions: 'read-write',
          tags: ['template', 'project-management', 'documentation'],
          version: '1.0',
          isPublic: true
        },
        {
          title: 'Capstone Project Examples',
          description: 'Examples of successful capstone projects from previous cohorts',
          category: 'Examples',
          type: 'zip',
          size: 2048000, // 2 MB
          uploadedBy: 'trainer@bdc.test',
          sharedWith: ['Web Development Bootcamp', 'Mobile App Development'],
          permissions: 'read',
          tags: ['capstone', 'examples', 'projects'],
          version: '1.0',
          isPublic: false
        },
        {
          title: 'Career Development Workbook',
          description: 'Interactive workbook for career planning and development',
          category: 'Career Resources',
          type: 'pdf',
          size: 1024000, // 1 MB
          uploadedBy: 'admin@bdc.test',
          sharedWith: ['all'],
          permissions: 'read',
          tags: ['career', 'development', 'planning'],
          version: '3.0',
          isPublic: true
        }
      ];

      for (const document of documents) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/documents`, document, {
            headers: this.getAuthHeaders()
          });
          this.seededData.documents.push(response.data);
        } catch (error) {
          console.warn(`Failed to create document ${document.title}:`, error.message);
        }
      }

      console.log(`Seeded ${this.seededData.documents.length} documents`);
    } catch (error) {
      console.error('Document seeding failed:', error.message);
      throw error;
    }
  }

  async seedProgramAssignments() {
    try {
      if (!this.adminToken) await this.authenticate();

      // Assign beneficiaries to programs
      const assignments = [
        {
          programName: 'Web Development Bootcamp',
          beneficiaryEmails: [
            'alice.johnson@beneficiary.test',
            'bob.smith@beneficiary.test',
            'john.doe@student.test'
          ]
        },
        {
          programName: 'Data Science Fundamentals',
          beneficiaryEmails: [
            'carol.williams@beneficiary.test',
            'jane.doe@student.test'
          ]
        },
        {
          programName: 'Mobile App Development',
          beneficiaryEmails: [
            'bob.smith@beneficiary.test',
            'david.brown@beneficiary.test'
          ]
        },
        {
          programName: 'UI/UX Design Workshop',
          beneficiaryEmails: [
            'alice.johnson@beneficiary.test',
            'emma.davis@beneficiary.test',
            'jane.doe@student.test'
          ]
        }
      ];

      for (const assignment of assignments) {
        try {
          const response = await axios.post(`${API_BASE_URL}/test/program-assignments`, assignment, {
            headers: this.getAuthHeaders()
          });
          console.log(`Assigned beneficiaries to ${assignment.programName}`);
        } catch (error) {
          console.warn(`Failed to assign beneficiaries to ${assignment.programName}:`, error.message);
        }
      }

      console.log('Program assignments completed');
    } catch (error) {
      console.error('Program assignment seeding failed:', error.message);
      throw error;
    }
  }

  async seedAll() {
    try {
      console.log('Starting database seeding...');
      
      await this.authenticate();
      await this.clearDatabase();
      
      // Seed in dependency order
      await this.seedUsers();
      await this.seedBeneficiaries();
      await this.seedPrograms();
      await this.seedEvaluations();
      await this.seedAppointments();
      await this.seedDocuments();
      await this.seedProgramAssignments();
      
      console.log('Database seeding completed successfully!');
      console.log('Seeded data summary:', {
        users: this.seededData.users.length,
        beneficiaries: this.seededData.beneficiaries.length,
        programs: this.seededData.programs.length,
        evaluations: this.seededData.evaluations.length,
        appointments: this.seededData.appointments.length,
        documents: this.seededData.documents.length
      });
      
      return this.seededData;
    } catch (error) {
      console.error('Database seeding failed:', error.message);
      throw error;
    }
  }

  async createTestUser(userData) {
    try {
      if (!this.adminToken) await this.authenticate();
      
      const response = await axios.post(`${API_BASE_URL}/test/users`, userData, {
        headers: this.getAuthHeaders()
      });
      
      this.seededData.users.push(response.data);
      return response.data;
    } catch (error) {
      console.error('Test user creation failed:', error.message);
      throw error;
    }
  }

  getSeededData() {
    return this.seededData;
  }
}

module.exports = DatabaseSeeder;