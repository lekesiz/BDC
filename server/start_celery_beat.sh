#!/bin/bash
# Start Celery beat scheduler

echo "Starting Celery beat scheduler..."

# Set environment to development if not set
export FLASK_ENV=${FLASK_ENV:-development}

# Start Celery beat
celery -A celery_app.celery_app beat \
    --loglevel=info \
    --pidfile=/tmp/celerybeat.pid \
    --schedule=/tmp/celerybeat-schedule