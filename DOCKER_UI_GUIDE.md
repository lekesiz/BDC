# Docker UI Guide

This document explains how to run the enhanced login and dashboard UI using Docker.

## System Requirements

- Docker Engine
- Docker Compose

## Overview

This Docker setup provides:

1. A Nginx web server serving the enhanced login and dashboard HTML pages
2. A test API server that provides authentication and mock data

## Running the Docker Container

### Quick Start

The simplest way to start the system is to use the included script:

```bash
./run_docker_ui.sh
```

This will build and start both containers.

### Manual Start

If you prefer to run the commands manually:

```bash
# Build and run in foreground
docker-compose -f docker-compose.html.yml up --build

# Or run in detached mode (background)
docker-compose -f docker-compose.html.yml up --build -d
```

### Stopping the Containers

If you ran the containers in detached mode, you can stop them with:

```bash
docker-compose -f docker-compose.html.yml down
```

## Accessing the UI

Once the containers are running, you can access:

- Enhanced Login: http://localhost:8090/
- Dashboard: http://localhost:8090/dashboard.html

## Test Accounts

You can use the following test accounts to log in:

| Role       | Email             | Password    |
|------------|-------------------|-------------|
| Admin      | admin@bdc.com     | Admin123!   |
| Tenant     | tenant@bdc.com    | Tenant123!  |
| Trainer    | trainer@bdc.com   | Trainer123! |
| Student    | student@bdc.com   | Student123! |

## Architecture

The Docker setup includes:

1. **html-server**: Nginx server that serves the HTML pages (port 8090)
2. **test-api**: Python Flask server that provides authentication and mock data (port 8888)

The servers are connected to a shared Docker network, allowing them to communicate.

## Troubleshooting

If you encounter any issues:

1. Check that ports 8090 and 8888 are not already in use on your system
2. Ensure Docker is running correctly
3. Check the container logs for error messages:

```bash
docker-compose -f docker-compose.html.yml logs html-server
docker-compose -f docker-compose.html.yml logs test-api
```