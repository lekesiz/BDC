import { 
  generateAIData, 
  generateAIModelMetrics,
  generateAITrainingHistory,
  generateAIConfigOptions 
} from './mockAIData';
export const setupAIMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // AI endpoints
  api.get = function(url, ...args) {
    // AI recommendations endpoint
    if (url === '/api/ai/recommendations' || url.startsWith('/api/ai/recommendations?')) {
      const userRole = localStorage.getItem('userRole') || 'student';
      const aiData = generateAIData(userRole);
      // Parse query parameters
      const urlObj = new URL(url, 'http://localhost');
      const type = urlObj.searchParams.get('type');
      if (type) {
        return Promise.resolve({
          status: 200,
          data: aiData.recommendations[type] || []
        });
      }
      return Promise.resolve({
        status: 200,
        data: aiData.recommendations
      });
    }
    // AI insights endpoint
    if (url === '/api/ai/insights') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const aiData = generateAIData(userRole);
      return Promise.resolve({
        status: 200,
        data: aiData.insights
      });
    }
    // AI content generation endpoint
    if (url === '/api/ai/content-generation') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const aiData = generateAIData(userRole);
      return Promise.resolve({
        status: 200,
        data: aiData.contentGeneration
      });
    }
    // AI chatbot history endpoint
    if (url === '/api/ai/chatbot/history') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const aiData = generateAIData(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          conversations: aiData.chatbot.recentConversations,
          commonQuestions: aiData.chatbot.commonQuestions
        }
      });
    }
    // AI feedback endpoint
    if (url === '/api/ai/feedback') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const aiData = generateAIData(userRole);
      return Promise.resolve({
        status: 200,
        data: aiData.feedback
      });
    }
    // AI teaching assistant (trainer only)
    if (url === '/api/ai/teaching-assistant') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'trainer') {
        const aiData = generateAIData(userRole);
        return Promise.resolve({
          status: 200,
          data: aiData.teachingAssistant
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // AI performance predictions (admin only)
    if (url === '/api/ai/predictions') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'admin' || userRole === 'tenant_admin') {
        const aiData = generateAIData(userRole);
        return Promise.resolve({
          status: 200,
          data: aiData.performancePredictions
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // AI model metrics endpoint
    if (url === '/api/ai/models/metrics') {
      const metrics = generateAIModelMetrics();
      return Promise.resolve({
        status: 200,
        data: metrics
      });
    }
    // AI training history endpoint
    if (url === '/api/ai/training/history') {
      const history = generateAITrainingHistory();
      return Promise.resolve({
        status: 200,
        data: {
          history,
          total: history.length
        }
      });
    }
    // AI configuration endpoint
    if (url === '/api/ai/config') {
      const config = generateAIConfigOptions();
      return Promise.resolve({
        status: 200,
        data: config
      });
    }
    // AI learning path details
    if (url.match(/^\/api\/ai\/learning-paths\/\d+$/)) {
      const pathId = parseInt(url.split('/').pop());
      const pathDetails = {
        id: pathId,
        title: "Full Stack Developer Path",
        description: "Comprehensive path to become a full stack developer",
        totalDuration: "6 months",
        currentProgress: 35,
        modules: [
          { id: 1, title: "Frontend Fundamentals", status: "completed", duration: "4 weeks" },
          { id: 2, title: "Backend Development", status: "in_progress", duration: "6 weeks" },
          { id: 3, title: "Database Design", status: "upcoming", duration: "3 weeks" },
          { id: 4, title: "DevOps Basics", status: "upcoming", duration: "4 weeks" }
        ],
        milestones: [
          { id: 1, title: "Frontend Developer", achieved: true, date: "2024-01-15" },
          { id: 2, title: "Backend Developer", achieved: false, estimatedDate: "2024-03-01" },
          { id: 3, title: "Full Stack Developer", achieved: false, estimatedDate: "2024-06-15" }
        ]
      };
      return Promise.resolve({
        status: 200,
        data: pathDetails
      });
    }
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  // AI POST endpoints
  api.post = function(url, data, ...args) {
    // AI chatbot message endpoint
    if (url === '/api/ai/chatbot/message') {
      const response = {
        id: Date.now(),
        message: "I understand you're asking about " + data.message + ". Here's what I can help you with...",
        timestamp: new Date().toISOString(),
        suggestions: [
          "View related documentation",
          "Watch video tutorial",
          "Try example code"
        ],
        resources: [
          { type: "doc", title: "Official Documentation", url: "/docs/topic" },
          { type: "video", title: "Tutorial Video", url: "/videos/123" }
        ]
      };
      return Promise.resolve({
        status: 200,
        data: response
      });
    }
    // Generate AI content endpoint
    if (url === '/api/ai/content/generate') {
      let generatedContent;
      if (data.type === 'quiz') {
        generatedContent = {
          id: Date.now(),
          type: 'quiz',
          title: `Quiz: ${data.topic}`,
          questions: [
            {
              id: 1,
              question: `What is the main purpose of ${data.topic}?`,
              options: ["Option A", "Option B", "Option C", "Option D"],
              correctAnswer: 0
            },
            {
              id: 2,
              question: `Which of the following is true about ${data.topic}?`,
              options: ["Option A", "Option B", "Option C", "Option D"],
              correctAnswer: 2
            }
          ]
        };
      } else if (data.type === 'summary') {
        generatedContent = {
          id: Date.now(),
          type: 'summary',
          title: `Summary: ${data.topic}`,
          content: `This is an AI-generated summary of ${data.topic}. Key points include...`,
          keyPoints: [
            "Important concept 1",
            "Important concept 2",
            "Important concept 3"
          ]
        };
      } else if (data.type === 'study_plan') {
        generatedContent = {
          id: Date.now(),
          type: 'study_plan',
          title: `Study Plan: ${data.topic}`,
          duration: "4 weeks",
          schedule: [
            { week: 1, topics: ["Introduction", "Basic Concepts"], hours: 10 },
            { week: 2, topics: ["Advanced Topics", "Practice"], hours: 12 },
            { week: 3, topics: ["Projects", "Real-world Applications"], hours: 15 },
            { week: 4, topics: ["Review", "Assessment"], hours: 8 }
          ]
        };
      }
      return Promise.resolve({
        status: 201,
        data: generatedContent
      });
    }
    // Request AI feedback endpoint
    if (url === '/api/ai/feedback/request') {
      const feedback = {
        id: Date.now(),
        submissionId: data.submissionId,
        score: 85,
        feedback: "Great work overall! Your code structure is clean and well-organized.",
        strengths: [
          "Excellent use of design patterns",
          "Clear variable naming",
          "Good error handling"
        ],
        improvements: [
          "Consider adding more comments",
          "Optimize loop performance",
          "Add unit tests"
        ],
        timestamp: new Date().toISOString()
      };
      return Promise.resolve({
        status: 200,
        data: feedback
      });
    }
    // Train AI model endpoint (admin only)
    if (url === '/api/ai/models/train') {
      return Promise.resolve({
        status: 202,
        data: {
          trainingId: Date.now(),
          model: data.model,
          status: 'queued',
          estimatedTime: '2 hours',
          message: 'Training job queued successfully'
        }
      });
    }
    // Generate AI report endpoint
    if (url === '/api/ai/reports/generate') {
      return Promise.resolve({
        status: 202,
        data: {
          reportId: Date.now(),
          type: data.type,
          status: 'processing',
          estimatedTime: '5 minutes',
          message: 'Report generation started'
        }
      });
    }
    return originalFunctions.post.call(api, url, data, ...args);
  };
  // AI PUT endpoints
  api.put = function(url, data, ...args) {
    // Update AI configuration
    if (url === '/api/ai/config') {
      return Promise.resolve({
        status: 200,
        data: {
          ...data,
          updatedAt: new Date().toISOString(),
          message: 'AI configuration updated successfully'
        }
      });
    }
    // Update AI model
    if (url.match(/^\/api\/ai\/models\/\d+$/)) {
      const modelId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: modelId,
          ...data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    // Update learning path progress
    if (url.match(/^\/api\/ai\/learning-paths\/\d+\/progress$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          progress: data.progress,
          updatedAt: new Date().toISOString(),
          nextMilestone: "Backend Developer"
        }
      });
    }
    return originalFunctions.put.call(api, url, data, ...args);
  };
  // AI DELETE endpoints
  api.delete = function(url, ...args) {
    // Delete AI conversation
    if (url.match(/^\/api\/ai\/chatbot\/conversations\/\d+$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Conversation deleted successfully'
        }
      });
    }
    // Remove AI training data
    if (url.match(/^\/api\/ai\/training\/data\/\d+$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Training data removed successfully'
        }
      });
    }
    // Cancel AI job
    if (url.match(/^\/api\/ai\/jobs\/\d+$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'AI job cancelled successfully'
        }
      });
    }
    return originalFunctions.delete.call(api, url, ...args);
  };
};