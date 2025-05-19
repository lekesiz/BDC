export const setupBeneficiaryMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Get beneficiary evaluations
  api.get = function(url, ...args) {
    if (url.match(/^\/api\/beneficiaries\/\d+\/evaluations$/)) {
      return Promise.resolve({
        data: [
          {
            id: 1,
            title: 'JavaScript Fundamentals Test',
            description: 'Basic JavaScript concepts and syntax',
            evaluation_date: '2024-01-15',
            status: 'completed',
            score: 45,
            max_score: 50,
            percentage_score: 90,
            evaluator_name: 'John Trainer',
            time_taken: '45 minutes'
          },
          {
            id: 2,
            title: 'React Components Assessment',
            description: 'Understanding React component lifecycle',
            evaluation_date: '2024-01-20',
            status: 'in_progress',
            evaluator_name: 'Jane Smith'
          }
        ]
      });
    }
    
    // Get beneficiary sessions
    if (url.match(/^\/api\/beneficiaries\/\d+\/sessions$/)) {
      return Promise.resolve({
        data: [
          {
            id: 1,
            title: 'Introduction to Web Development',
            description: 'Basics of HTML, CSS, and JavaScript',
            scheduled_at: '2024-01-22T10:00:00',
            duration: 60,
            status: 'scheduled',
            trainer_name: 'John Trainer',
            location: 'Room 101'
          },
          {
            id: 2,
            title: 'React Fundamentals',
            description: 'Introduction to React and component-based architecture',
            scheduled_at: '2024-01-18T14:00:00',
            duration: 90,
            status: 'completed',
            trainer_name: 'Jane Smith',
            location: 'Online'
          }
        ]
      });
    }
    
    // Get beneficiary trainers
    if (url.match(/^\/api\/beneficiaries\/\d+\/trainers$/)) {
      return Promise.resolve({
        data: [
          {
            id: 1,
            first_name: 'John',
            last_name: 'Trainer',
            email: 'john.trainer@example.com',
            specialization: 'Web Development',
            assigned_date: '2024-01-01',
            is_primary: true,
            status: 'active'
          },
          {
            id: 2,
            first_name: 'Jane',
            last_name: 'Smith',
            email: 'jane.smith@example.com',
            specialization: 'React Development',
            assigned_date: '2024-01-10',
            is_primary: false,
            status: 'active'
          }
        ]
      });
    }
    
    // Get beneficiary progress
    if (url.match(/^\/api\/beneficiaries\/\d+\/progress$/)) {
      return Promise.resolve({
        data: {
          overall_progress: 75,
          completed_modules: 12,
          total_modules: 16,
          current_level: 'Intermediate',
          skills: [
            { name: 'JavaScript', level: 85, progress: 90 },
            { name: 'React', level: 70, progress: 80 },
            { name: 'CSS', level: 90, progress: 95 },
            { name: 'Node.js', level: 60, progress: 70 }
          ],
          recent_achievements: [
            {
              id: 1,
              title: 'JavaScript Master',
              description: 'Completed all JavaScript modules',
              earned_at: '2024-01-15',
              icon: 'trophy'
            },
            {
              id: 2,
              title: 'Quick Learner',
              description: 'Completed 5 modules in one week',
              earned_at: '2024-01-10',
              icon: 'lightning'
            }
          ],
          timeline: [
            {
              date: '2024-01-20',
              title: 'Completed React Basics',
              type: 'achievement'
            },
            {
              date: '2024-01-18',
              title: 'Started Node.js Module',
              type: 'milestone'
            },
            {
              date: '2024-01-15',
              title: 'Scored 90% on JavaScript Test',
              type: 'test'
            }
          ]
        }
      });
    }
    
    // Get beneficiary documents
    if (url.match(/^\/api\/beneficiaries\/\d+\/documents$/)) {
      return Promise.resolve({
        data: [
          {
            id: 1,
            name: 'Training Certificate - JavaScript',
            description: 'Certificate of completion for JavaScript fundamentals course',
            type: 'certificate',
            file_type: 'pdf',
            size: 1258291,
            size_formatted: '1.2 MB',
            created_at: '2024-01-15T10:00:00',
            uploaded_by_name: 'John Trainer',
            category: 'Certificates',
            download_url: '/api/documents/1/download'
          },
          {
            id: 2,
            name: 'Course Materials - React',
            description: 'Complete course materials for React development',
            type: 'study_material',
            file_type: 'pdf',
            size: 3669015,
            size_formatted: '3.5 MB',
            created_at: '2024-01-10T14:30:00',
            uploaded_by_name: 'Jane Smith',
            category: 'Study Materials',
            download_url: '/api/documents/2/download'
          },
          {
            id: 3,
            name: 'Progress Report - Q1 2024',
            description: 'Quarterly progress report for beneficiary performance',
            type: 'evaluation_report',
            file_type: 'pdf',
            size: 524288,
            size_formatted: '500 KB',
            created_at: '2024-01-05T09:00:00',
            uploaded_by_name: 'System',
            category: 'Reports',
            download_url: '/api/documents/3/download'
          }
        ]
      });
    }
    
    return originalGet.call(this, url, ...args);
  };
  
  // Keep other methods unchanged
  api.post = originalPost;
  api.put = originalPut;
  api.delete = originalDelete;
};