#!/bin/bash
# Start Celery worker

echo "Starting Celery worker..."

# Set environment to development if not set
export FLASK_ENV=${FLASK_ENV:-development}

# Start Celery worker
celery -A celery_app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --pool=prefork \
    -n worker@%h