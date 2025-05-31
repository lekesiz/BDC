#!/bin/bash
# Health check script for backend container

# Check if gunicorn is running
if ! pgrep -f gunicorn > /dev/null; then
    echo "Gunicorn process not found"
    exit 1
fi

# Check if the application is responding
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Backend is healthy"
    exit 0
else
    echo "Backend health check failed"
    exit 1
fi