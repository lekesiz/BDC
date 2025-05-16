Project Overview
BDC (Beneficiary Development Center) is a modern web application designed for talent assessment (Bilan de Competence). The platform helps manage, track, and evaluate the development process of beneficiaries (students) using AI-assisted features.

Architecture

Backend

- Framework: Python/Flask with SQLAlchemy ORM
- Authentication: JWT-based authentication with refresh tokens
- Database: PostgreSQL for production, SQLite for development
- Caching: Redis for caching and session management
- AI Integration: OpenAI and LangChain for AI-assisted features
- API Structure: RESTful API with blueprints for different features

Frontend

- Framework: React with Vite for fast development
- Styling: Tailwind CSS
- Routing: React Router
- Form Handling: React Hook Form with Zod validation
- UI Components: Radix UI for accessible components
- State Management: Context API and custom hooks
- HTTP Client: Axios for API requests

Key Features

- User Role Management: Super Admin, Tenant Admin, Trainer, and Student roles
- Multi-tenancy: Support for multiple organizations with their branding
- Training and Assessment Management: Creating and assigning educational content
- Test Engine: Various question types, time management, and result analysis
- AI Assistant: Personalized feedback and recommendations
- Document Generator: PDF reports and analyses
- Dashboard and Analytics: Customized dashboards with performance metrics
- Notification System: Real-time notifications and reminders
- External Integrations: Wedof API, Google Workspace, Pennylane

Project Structure

Backend Structure

- app/api/: API endpoints organized by feature
- app/models/: Database models with SQLAlchemy
- app/schemas/: Marshmallow schemas for serialization
- app/services/: Business logic services
- app/middleware/: Request processing middleware
- app/utils/: Helper functions
- app/realtime/: Real-time communication with SocketIO

Frontend Structure

- src/components/: Reusable UI components
- src/pages/: Page components for different routes
- src/context/: Context providers for state management
- src/hooks/: Custom React hooks
- src/lib/: Utility libraries and API client
- src/assets/: Static assets like images and fonts
- src/store/: State management

Development Status

The project appears to be in active development, following a 15-week plan:
- Current stage: Based on the code examined, the project is likely in the early-to-mid stages of development (around weeks 4-7 of the plan)
- Completed: Basic infrastructure, authentication, user management
- In progress: Beneficiary management, test engine foundations
- Upcoming: Advanced features like AI integration, reporting, and external integrations

Technical Highlights

- Multi-tenancy: The architecture supports multiple organizations (tenants) with their own users
- Role-based Access Control: Comprehensive permission system
- Modern UI: Clean React components with Tailwind CSS
- API Security: JWT authentication with token refresh mechanism
- Test Engine: Flexible system for creating and managing assessments
- AI Integration: OpenAI and LangChain for personalized feedback and recommendations

Development Workflow

The project uses Docker for both development and production environments, with separate configurations for each. There appears to be a CI/CD pipeline in place (.github directory), following modern development practices.

Next Steps

According to the development plan, upcoming priorities include:
- Completing the test engine
- Implementing AI integration
- Building the reporting and dashboard features
- Adding external integrations
- Comprehensive testing and optimization

The project follows a well-structured approach with clear separation of concerns and modern best practices for both frontend and backend development.