import { 
  generateProgramsData, 
  generateProgramResources, 
  generateProgramSchedule,
  generateProgramStats 
} from './mockProgramsData';

export const setupProgramsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };

  // Programs list endpoint
  api.get = function(url, ...args) {
    if (url === '/api/programs' || url.startsWith('/api/programs?')) {
      console.log('Mock API: Programs list request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const programsData = generateProgramsData(userRole);
      
      // Parse query parameters
      const urlObj = new URL(url, 'http://localhost');
      const category = urlObj.searchParams.get('category');
      const status = urlObj.searchParams.get('status');
      const search = urlObj.searchParams.get('search');
      
      let programs = programsData.allPrograms || programsData.availablePrograms || [];
      
      // Filter by category
      if (category) {
        programs = programs.filter(p => 
          p.categories.includes(category)
        );
      }
      
      // Filter by status
      if (status) {
        programs = programs.filter(p => p.status === status);
      }
      
      // Search filter
      if (search) {
        const searchLower = search.toLowerCase();
        programs = programs.filter(p => 
          p.title.toLowerCase().includes(searchLower) ||
          p.description.toLowerCase().includes(searchLower)
        );
      }
      
      return Promise.resolve({
        status: 200,
        data: {
          programs,
          total: programs.length,
          enrolled: programsData.enrolledPrograms,
          recommended: programsData.recommendedPrograms
        }
      });
    }
    
    // My programs endpoint (for trainers and students)
    if (url === '/api/programs/my') {
      console.log('Mock API: My programs request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const programsData = generateProgramsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: {
          programs: programsData.myPrograms || programsData.enrolledPrograms || [],
          total: (programsData.myPrograms || programsData.enrolledPrograms || []).length
        }
      });
    }
    
    // Program statistics endpoint
    if (url === '/api/programs/statistics') {
      console.log('Mock API: Program statistics request');
      const stats = generateProgramStats();
      
      return Promise.resolve({
        status: 200,
        data: stats
      });
    }
    
    // Specific program endpoint
    if (url.match(/^\/api\/programs\/\d+$/)) {
      console.log('Mock API: Specific program request');
      const programId = parseInt(url.split('/').pop());
      const userRole = localStorage.getItem('userRole') || 'student';
      const programsData = generateProgramsData(userRole);
      const allPrograms = programsData.allPrograms || programsData.availablePrograms || [];
      const program = allPrograms.find(p => p.id === programId);
      
      if (program) {
        return Promise.resolve({
          status: 200,
          data: program
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Program not found' }
        });
      }
    }
    
    // Program modules endpoint
    if (url.match(/^\/api\/programs\/\d+\/modules$/)) {
      console.log('Mock API: Program modules request');
      const programId = parseInt(url.split('/')[3]);
      const userRole = localStorage.getItem('userRole') || 'student';
      const programsData = generateProgramsData(userRole);
      const allPrograms = programsData.allPrograms || programsData.availablePrograms || [];
      const program = allPrograms.find(p => p.id === programId);
      
      if (program) {
        return Promise.resolve({
          status: 200,
          data: {
            modules: program.modules,
            total: program.modules.length
          }
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Program not found' }
        });
      }
    }
    
    // Program resources endpoint
    if (url.match(/^\/api\/programs\/\d+\/resources$/)) {
      console.log('Mock API: Program resources request');
      const programId = parseInt(url.split('/')[3]);
      const resources = generateProgramResources(programId);
      
      return Promise.resolve({
        status: 200,
        data: resources
      });
    }
    
    // Program schedule endpoint
    if (url.match(/^\/api\/programs\/\d+\/schedule$/)) {
      console.log('Mock API: Program schedule request');
      const programId = parseInt(url.split('/')[3]);
      const schedule = generateProgramSchedule(programId);
      
      return Promise.resolve({
        status: 200,
        data: {
          schedule,
          total: schedule.length
        }
      });
    }
    
    // Program students endpoint
    if (url.match(/^\/api\/programs\/\d+\/students$/)) {
      console.log('Mock API: Program students request');
      
      const students = [
        { id: 1, name: "John Doe", progress: 75, lastActive: "2024-01-21" },
        { id: 2, name: "Jane Smith", progress: 82, lastActive: "2024-01-22" },
        { id: 3, name: "Mike Johnson", progress: 68, lastActive: "2024-01-20" },
        { id: 4, name: "Sarah Williams", progress: 90, lastActive: "2024-01-22" },
        { id: 5, name: "David Brown", progress: 45, lastActive: "2024-01-19" }
      ];
      
      return Promise.resolve({
        status: 200,
        data: {
          students,
          total: students.length
        }
      });
    }
    
    // Program categories endpoint
    if (url === '/api/programs/categories') {
      console.log('Mock API: Program categories request');
      
      const categories = [
        { id: 1, name: "Web Development", count: 12 },
        { id: 2, name: "Data Science", count: 8 },
        { id: 3, name: "Mobile Development", count: 6 },
        { id: 4, name: "UI/UX Design", count: 5 },
        { id: 5, name: "DevOps", count: 4 },
        { id: 6, name: "Cybersecurity", count: 3 },
        { id: 7, name: "Machine Learning", count: 7 },
        { id: 8, name: "Cloud Computing", count: 5 }
      ];
      
      return Promise.resolve({
        status: 200,
        data: {
          categories
        }
      });
    }
    
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  
  // Create program endpoint
  api.post = function(url, data, ...args) {
    if (url === '/api/programs') {
      console.log('Mock API: Create program', data);
      
      const newProgram = {
        id: Date.now(),
        ...data,
        status: 'draft',
        enrolled: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 201,
        data: newProgram
      });
    }
    
    // Enroll in program endpoint
    if (url.match(/^\/api\/programs\/\d+\/enroll$/)) {
      console.log('Mock API: Enroll in program');
      const programId = parseInt(url.split('/')[3]);
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          message: 'Successfully enrolled in program',
          programId,
          enrollmentDate: new Date().toISOString()
        }
      });
    }
    
    // Add program module
    if (url.match(/^\/api\/programs\/\d+\/modules$/)) {
      console.log('Mock API: Add program module', data);
      const programId = parseInt(url.split('/')[3]);
      
      const newModule = {
        id: Date.now(),
        ...data,
        programId,
        createdAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 201,
        data: newModule
      });
    }
    
    // Add program resource
    if (url.match(/^\/api\/programs\/\d+\/resources$/)) {
      console.log('Mock API: Add program resource', data);
      
      const newResource = {
        id: Date.now(),
        ...data,
        uploadedAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 201,
        data: newResource
      });
    }
    
    return originalFunctions.post.call(api, url, data, ...args);
  };
  
  // Update program endpoint
  api.put = function(url, data, ...args) {
    if (url.match(/^\/api\/programs\/\d+$/)) {
      console.log('Mock API: Update program', data);
      const programId = parseInt(url.split('/').pop());
      
      const updatedProgram = {
        ...data,
        id: programId,
        updatedAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 200,
        data: updatedProgram
      });
    }
    
    // Update program module
    if (url.match(/^\/api\/programs\/\d+\/modules\/\d+$/)) {
      console.log('Mock API: Update program module', data);
      const moduleId = parseInt(url.split('/').pop());
      
      const updatedModule = {
        ...data,
        id: moduleId,
        updatedAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 200,
        data: updatedModule
      });
    }
    
    // Update program status
    if (url.match(/^\/api\/programs\/\d+\/status$/)) {
      console.log('Mock API: Update program status', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          status: data.status,
          updatedAt: new Date().toISOString()
        }
      });
    }
    
    return originalFunctions.put.call(api, url, data, ...args);
  };
  
  // Delete program endpoint
  api.delete = function(url, ...args) {
    if (url.match(/^\/api\/programs\/\d+$/)) {
      console.log('Mock API: Delete program');
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          message: 'Program deleted successfully'
        }
      });
    }
    
    // Remove program module
    if (url.match(/^\/api\/programs\/\d+\/modules\/\d+$/)) {
      console.log('Mock API: Remove program module');
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          message: 'Module removed successfully'
        }
      });
    }
    
    // Remove program resource
    if (url.match(/^\/api\/programs\/\d+\/resources\/\d+$/)) {
      console.log('Mock API: Remove program resource');
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          message: 'Resource removed successfully'
        }
      });
    }
    
    // Unenroll from program
    if (url.match(/^\/api\/programs\/\d+\/unenroll$/)) {
      console.log('Mock API: Unenroll from program');
      
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          message: 'Successfully unenrolled from program'
        }
      });
    }
    
    return originalFunctions.delete.call(api, url, ...args);
  };
};