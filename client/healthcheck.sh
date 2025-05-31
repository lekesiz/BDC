#!/bin/sh
# Health check script for frontend container

# Check if nginx is running
if ! pgrep nginx > /dev/null; then
    echo "Nginx process not found"
    exit 1
fi

# Check if the application is responding
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "Frontend is healthy"
    exit 0
else
    echo "Frontend health check failed"
    exit 1
fi