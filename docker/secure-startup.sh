#!/bin/sh
# Secure startup script with security checks and monitoring

set -euo pipefail

# Security: Check if running as root (should not be)
if [ "$(id -u)" -eq 0 ]; then
    echo "ERROR: Running as root is not allowed for security reasons"
    exit 1
fi

# Security: Validate environment variables
validate_env_vars() {
    local required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            echo "ERROR: Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Security: Check for default/weak values
    if [ "$SECRET_KEY" = "dev-secret-key-change-in-production" ]; then
        echo "ERROR: SECRET_KEY is still set to default development value"
        exit 1
    fi
    
    if [ "$JWT_SECRET_KEY" = "jwt-secret-key-change-in-production" ]; then
        echo "ERROR: JWT_SECRET_KEY is still set to default development value"
        exit 1
    fi
    
    echo "✓ Environment variables validated"
}

# Security: Check file permissions
check_file_permissions() {
    local app_dir="/app"
    local logs_dir="/app/logs"
    local uploads_dir="/app/uploads"
    
    # Check that sensitive directories are not world-readable
    if [ -d "$logs_dir" ] && [ "$(stat -c %a "$logs_dir")" -gt 750 ]; then
        echo "WARNING: Logs directory has overly permissive permissions"
        chmod 750 "$logs_dir"
    fi
    
    if [ -d "$uploads_dir" ] && [ "$(stat -c %a "$uploads_dir")" -gt 750 ]; then
        echo "WARNING: Uploads directory has overly permissive permissions"
        chmod 750 "$uploads_dir"
    fi
    
    # Check that configuration files are not world-readable
    for config_file in "$app_dir"/*.py "$app_dir"/*.conf; do
        if [ -f "$config_file" ] && [ "$(stat -c %a "$config_file")" -gt 644 ]; then
            echo "WARNING: $config_file has overly permissive permissions"
            chmod 644 "$config_file"
        fi
    done
    
    echo "✓ File permissions checked"
}

# Security: Validate database connection
check_database_connection() {
    echo "Checking database connection..."
    
    # Use Python to check database connection
    python3 -c "
import os
import sys
try:
    from sqlalchemy import create_engine
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✓ Database connection successful')
except Exception as e:
    print(f'ERROR: Database connection failed: {e}')
    sys.exit(1)
"
}

# Security: Check Redis connection
check_redis_connection() {
    echo "Checking Redis connection..."
    
    python3 -c "
import os
import sys
try:
    import redis
    r = redis.from_url(os.environ['REDIS_URL'])
    r.ping()
    print('✓ Redis connection successful')
except Exception as e:
    print(f'ERROR: Redis connection failed: {e}')
    sys.exit(1)
"
}

# Security: Run database migrations safely
run_migrations() {
    echo "Running database migrations..."
    
    # Set timeout for migrations
    timeout 300 python3 -c "
from app import create_app
from flask_migrate import upgrade

app = create_app()
with app.app_context():
    upgrade()
    print('✓ Database migrations completed')
" || {
    echo "ERROR: Database migrations failed or timed out"
    exit 1
}
}

# Security: Create required directories with proper permissions
setup_directories() {
    local dirs=(
        "/app/logs"
        "/app/uploads"
        "/app/temp"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            chmod 750 "$dir"
            echo "✓ Created directory: $dir"
        fi
    done
}

# Security: Setup log rotation
setup_log_rotation() {
    cat > /tmp/logrotate.conf << 'EOF'
/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 appuser appgroup
    postrotate
        /bin/kill -USR1 $(cat /var/run/gunicorn.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
EOF
    
    echo "✓ Log rotation configured"
}

# Security: Start monitoring processes
start_monitoring() {
    # Start log monitoring for security events
    (
        tail -f /app/logs/security.log 2>/dev/null | while read -r line; do
            if echo "$line" | grep -E "(ERROR|CRITICAL|SECURITY)" >/dev/null; then
                echo "SECURITY ALERT: $line" >&2
            fi
        done
    ) &
    
    # Monitor system resources
    (
        while true; do
            # Check memory usage
            mem_usage=$(free | awk '/^Mem:/{printf "%.2f", $3/$2 * 100.0}')
            if [ "$(echo "$mem_usage > 90" | bc -l)" -eq 1 ]; then
                echo "WARNING: High memory usage: ${mem_usage}%" >&2
            fi
            
            # Check disk usage
            disk_usage=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
            if [ "$disk_usage" -gt 90 ]; then
                echo "WARNING: High disk usage: ${disk_usage}%" >&2
            fi
            
            sleep 60
        done
    ) &
    
    echo "✓ Monitoring processes started"
}

# Security: Final security check
final_security_check() {
    # Check for any SUID/SGID files that shouldn't be there
    local suspicious_files
    suspicious_files=$(find /app -perm /6000 -type f 2>/dev/null || true)
    
    if [ -n "$suspicious_files" ]; then
        echo "WARNING: Found SUID/SGID files in application directory:"
        echo "$suspicious_files"
    fi
    
    # Check for world-writable files
    local writable_files
    writable_files=$(find /app -perm /002 -type f 2>/dev/null || true)
    
    if [ -n "$writable_files" ]; then
        echo "WARNING: Found world-writable files:"
        echo "$writable_files"
    fi
    
    echo "✓ Final security check completed"
}

# Main startup sequence
main() {
    echo "Starting BDC Application with Security Hardening..."
    echo "================================================"
    
    # Security checks
    validate_env_vars
    check_file_permissions
    setup_directories
    setup_log_rotation
    
    # Service checks
    check_database_connection
    check_redis_connection
    
    # Application setup
    run_migrations
    
    # Security monitoring
    start_monitoring
    final_security_check
    
    echo "✓ All security checks passed"
    echo "Starting application services..."
    
    # Start supervisord which will manage nginx and gunicorn
    exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
}

# Trap signals for graceful shutdown
trap 'echo "Received shutdown signal, cleaning up..."; exit 0' TERM INT

# Run main function
main "$@"