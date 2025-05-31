# Enhanced Login and Dashboard UI Setup Guide

This document provides an overview of the enhanced login and dashboard UI setup with both local and Docker options.

## Project Overview

The enhanced UI consists of:

1. A modern, responsive login page with animations and validations
2. A full-featured dashboard with mock data and interactive components
3. A mock API server for authentication and data retrieval

## Running Locally

For local development and testing, you can run the UI without Docker:

### Quick Start (Recommended)

1. **Start the API Server**:
   ```bash
   ./run_api_only.sh
   ```

2. **Start the HTML Server** (in a separate terminal):
   ```bash
   ./run_html_only.sh
   ```

3. **Access the UI**: Open http://localhost:8090/ in your browser

For more details, see the complete [Local UI Guide](LOCAL_UI_GUIDE.md).

## Running with Docker

For a more production-like environment, you can use Docker:

```bash
./run_docker_ui.sh
```

This will start containers for both the UI and API server, accessible at http://localhost:8090/

For more details, see the complete [Docker UI Guide](DOCKER_UI_GUIDE.md).

## Test Accounts

The following accounts are available for testing:

| Role       | Email             | Password    |
|------------|-------------------|-------------|
| Admin      | admin@bdc.com     | Admin123!   |
| Tenant     | tenant@bdc.com    | Tenant123!  |
| Trainer    | trainer@bdc.com   | Trainer123! |
| Student    | student@bdc.com   | Student123! |

## Features Overview

### Enhanced Login
- Modern, clean UI with animations
- Form validation for email and password
- Password visibility toggle
- Remember me functionality
- Success/Error notifications
- Mobile-responsive design

### Dashboard
- Clean and modern design
- Responsive sidebar navigation
- Stats dashboard with animated cards
- Recent evaluations and upcoming appointments
- Quick action buttons
- Mobile-responsive design

## Technical Implementation

- **HTML/CSS**: Uses modern HTML5 and Tailwind CSS for styling
- **JavaScript**: Vanilla JavaScript with fetch API for data retrieval
- **Mock API**: Python Flask server with test data
- **Containerization**: Docker and Docker Compose for easy deployment

## Files Structure

- `client/enhanced-login.html`: The enhanced login page
- `client/dashboard.html`: The dashboard page
- `client/index.html`: Landing page with links to both pages
- `server/complete_test_api.py`: Mock API server implementation
- `docker/`: Docker-related configuration files
- `*.sh` scripts: Helper scripts for running the UI locally and with Docker