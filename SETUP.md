# BDC Setup Guide

This guide will help you set up the BDC (Beneficiary Development Center) application for development.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Node.js 18+
- npm or yarn
- PostgreSQL (optional for development, required for production)
- Redis (optional for development, required for production)
- Docker and Docker Compose (optional, for containerized setup)

## Development Setup

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the server directory (use `.env.example` as a template):
   ```bash
   cp ../.env.example .env
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Seed the database with initial data (optional):
   ```bash
   python seed.py
   ```

7. Run the development server:
   ```bash
   flask run
   ```

The backend server will be available at `http://localhost:5000`.

### Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

3. Create a `.env` file in the client directory (use `.env.example` as a template):
   ```bash
   cp ../.env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

The frontend development server will be available at `http://localhost:3000`.

## Docker Setup

If you prefer to use Docker for development:

1. Create a `.env` file in the root directory (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Initialize the database:
   ```bash
   docker-compose exec server flask db upgrade
   ```

4. Seed the database with initial data (optional):
   ```bash
   docker-compose exec server python seed.py
   ```

The application will be available at:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`

## Default Credentials

After setting up the application, you can log in with the following default credentials:

- **Super Admin**:
  - Email: admin@bdc.com
  - Password: admin123

- **Demo Trainer**:
  - Email: trainer@bdc.com
  - Password: trainer123

- **Demo Student**:
  - Email: student@bdc.com
  - Password: student123

## Development Commands

### Backend Commands

- Run server in development mode:
  ```bash
  flask run
  ```

- Run tests:
  ```bash
  pytest
  ```

- Create database migrations:
  ```bash
  flask db migrate -m "Description of changes"
  ```

- Apply database migrations:
  ```bash
  flask db upgrade
  ```

### Frontend Commands

- Run development server:
  ```bash
  npm run dev
  # or
  yarn dev
  ```

- Build for production:
  ```bash
  npm run build
  # or
  yarn build
  ```

- Run linter:
  ```bash
  npm run lint
  # or
  yarn lint
  ```

## Troubleshooting

### Backend Issues

- **Database connection errors**:
  - Ensure PostgreSQL is running and the connection string in `.env` is correct.
  - For development, you can use SQLite by setting `DATABASE_URL=sqlite:///app.db`.

- **Redis connection errors**:
  - Ensure Redis is running and the connection string in `.env` is correct.
  - For development, you can disable Redis features by modifying the config.

### Frontend Issues

- **API connection errors**:
  - Ensure the backend server is running.
  - Check that `VITE_API_URL` in `.env` is set correctly.

- **Node module issues**:
  - Try deleting `node_modules` and `package-lock.json`, then run `npm install` again.

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)