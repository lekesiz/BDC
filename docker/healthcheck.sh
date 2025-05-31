#!/bin/bash

# Health check script for BDC application
set -e

# Check if Nginx is running
if ! curl -f http://localhost:80/health > /dev/null 2>&1; then
    echo "ERROR: Nginx health check failed"
    exit 1
fi

# Check if Flask app is responding
if ! curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "ERROR: Flask app health check failed"
    exit 1
fi

# Check Redis connection
if ! redis-cli ping > /dev/null 2>&1; then
    echo "ERROR: Redis health check failed"
    exit 1
fi

# Check database connection
python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'bdc_db'),
        user=os.getenv('DB_USER', 'bdc_user'),
        password=os.getenv('DB_PASSWORD')
    )
    conn.close()
    print('Database connection: OK')
except Exception as e:
    print(f'ERROR: Database health check failed: {e}')
    exit(1)
"

echo "All health checks passed"
exit 0