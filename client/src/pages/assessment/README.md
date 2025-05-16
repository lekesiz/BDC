# Assessment Management System

This directory contains all the components for the comprehensive Assessment Management System in the BDC application.

## System Overview

The Assessment Management System provides a complete workflow for trainers to create, manage, assign, and grade assessments. It includes both trainer-facing management tools and student-facing assessment-taking functionality.

## Component Structure

### Core Pages

1. **TrainerAssessmentsPage** (`TrainerAssessmentsPage.jsx`)
   - Main dashboard for assessment management
   - Lists all templates and assigned assessments
   - Provides filtering and search functionality
   - Quick actions for creating new assessments

2. **TrainerAssessmentCreationPage** (`TrainerAssessmentCreationPage.jsx`)
   - Step-by-step wizard for creating assessments
   - Supports quiz and project types
   - Question builder with multiple question types
   - Requirements builder for projects
   - Comprehensive settings configuration

3. **TrainerAssessmentEditPage** (`TrainerAssessmentEditPage.jsx`)
   - Edit existing assessment templates
   - Modify questions, requirements, and settings
   - Track unsaved changes with warnings
   - Publish/unpublish functionality

4. **TrainerAssessmentTemplateDetailPage** (`TrainerAssessmentTemplateDetailPage.jsx`)
   - View detailed template information
   - Usage analytics and statistics
   - Assignment history
   - Actions: preview, edit, duplicate, assign, delete

5. **TrainerAssessmentPreviewPage** (`TrainerAssessmentPreviewPage.jsx`)
   - Preview assessments as students would see them
   - Test the assessment flow
   - Verify question ordering and timing
   - Check project submission interface

### Assignment Management

6. **TrainerAssignAssessmentPage** (`TrainerAssignAssessmentPage.jsx`)
   - Assign assessments to courses, groups, or individuals
   - Set due dates and availability periods
   - Configure assignment-specific settings
   - Add instructions for students

7. **TrainerAssignedAssessmentDetailPage** (`TrainerAssignedAssessmentDetailPage.jsx`)
   - Monitor assignment progress in real-time
   - View submission statistics
   - Send reminders to students
   - Extend due dates when needed
   - Manage assignment settings

8. **TrainerAssignedAssessmentEditPage** (`TrainerAssignedAssessmentEditPage.jsx`)
   - Edit existing assignment settings
   - Update due dates and instructions
   - Modify assignment configuration
   - Track changes with unsaved warnings

### Results & Grading

9. **TrainerAssessmentResultsPage** (`TrainerAssessmentResultsPage.jsx`)
   - Comprehensive analytics dashboard
   - Score distributions and performance metrics
   - Individual submission tracking
   - Export functionality for reports

10. **TrainerSubmissionDetailPage** (`TrainerSubmissionDetailPage.jsx`)
    - Detailed view of individual submissions
    - Side-by-side answer comparison for quizzes
    - Manual grading interface
    - Feedback system for students
    - Support for auto-graded and manually graded assessments

## Features

### Assessment Types
- **Quiz**: Multiple choice, true/false, short answer, matching questions
- **Project**: Requirements-based assessments with file upload support

### Question Types (Quiz)
- Multiple Choice (single answer)
- Multiple Answer (multiple correct answers)
- True/False
- Short Answer
- Matching (coming soon)

### Settings & Configuration
- Time limits for quizzes
- Attempts allowed
- Passing scores
- Late submission policies
- Automatic grading
- Notification preferences
- Result visibility options

### Analytics & Reporting
- Completion rates
- Score distributions
- Performance trends
- Student progress tracking
- Export functionality

### Assignment Features
- Bulk assignment to courses/groups
- Individual assignments
- Due date management
- Extension capabilities
- Reminder system
- Progress monitoring

## API Integration

All components integrate with the mock API system through:
- `setupAssessmentMockApi.js`: API endpoint handlers
- `mockData.js`: Mock data structures

## UI Components

The system uses the following UI components from the shared library:
- Button, Card, Badge, Table
- Tabs, Dialog, Form elements
- Loading states, Error boundaries
- Toast notifications

## State Management

Each component manages its own state using React hooks:
- `useState`: Local component state
- `useEffect`: Data fetching and side effects
- Custom hooks for common functionality

## Navigation Flow

1. Main dashboard → Create/Edit templates
2. Template details → Preview/Assign
3. Assignment → Monitor/Grade
4. Results → Individual submissions
5. Submissions → Grading/Feedback

## Best Practices

- Consistent error handling
- Loading states for async operations
- Form validation
- Unsaved changes warnings
- Responsive design
- Accessibility considerations

## Future Enhancements

- Question bank functionality
- Advanced analytics
- Bulk grading
- Rubric builder for projects
- Integration with external assessment tools
- AI-powered question generation
- Plagiarism detection for projects

## Development Guidelines

1. Follow existing component patterns
2. Use TypeScript for new components
3. Add proper JSDoc comments
4. Include error boundaries
5. Test with mock data
6. Ensure mobile responsiveness
7. Follow accessibility guidelines

## Testing

Each component should be tested with:
- Unit tests for logic
- Integration tests for API calls
- E2E tests for workflows
- Accessibility tests

## Documentation

- Keep this README updated
- Document component props
- Add usage examples
- Update API documentation