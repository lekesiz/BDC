#!/bin/bash
# Backup script for BDC application

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_$DATE.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting backup process"

# Database backup
if [ ! -z "$DATABASE_URL" ]; then
    log "Creating database backup"
    
    # Extract database connection details
    DB_URL_NO_PROTOCOL=${DATABASE_URL#postgresql://}
    DB_AUTH_HOST=${DB_URL_NO_PROTOCOL%/*}
    DB_NAME=${DB_URL_NO_PROTOCOL##*/}
    DB_USER_PASS=${DB_AUTH_HOST%@*}
    DB_HOST_PORT=${DB_AUTH_HOST#*@}
    DB_USER=${DB_USER_PASS%:*}
    DB_PASS=${DB_USER_PASS#*:}
    DB_HOST=${DB_HOST_PORT%:*}
    DB_PORT=${DB_HOST_PORT#*:}
    
    # Set PostgreSQL password
    export PGPASSWORD="$DB_PASS"
    
    # Create database backup
    DB_BACKUP_FILE="$BACKUP_DIR/bdc_db_backup_$DATE.sql"
    
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-password -f "$DB_BACKUP_FILE"; then
        log "Database backup created: $DB_BACKUP_FILE"
        
        # Compress backup
        gzip "$DB_BACKUP_FILE"
        log "Database backup compressed: $DB_BACKUP_FILE.gz"
    else
        log "ERROR: Database backup failed"
        exit 1
    fi
    
    unset PGPASSWORD
else
    log "WARNING: DATABASE_URL not set, skipping database backup"
fi

# File backup (if uploads directory exists)
if [ -d "/app/uploads" ] && [ "$(ls -A /app/uploads)" ]; then
    log "Creating files backup"
    
    FILES_BACKUP_FILE="$BACKUP_DIR/bdc_files_backup_$DATE.tar.gz"
    
    if tar -czf "$FILES_BACKUP_FILE" -C /app uploads; then
        log "Files backup created: $FILES_BACKUP_FILE"
    else
        log "ERROR: Files backup failed"
        exit 1
    fi
else
    log "No files to backup in /app/uploads"
fi

# Upload to S3 if configured
if [ ! -z "$AWS_ACCESS_KEY_ID" ] && [ ! -z "$AWS_SECRET_ACCESS_KEY" ] && [ ! -z "$BACKUP_S3_BUCKET" ]; then
    log "Uploading backups to S3"
    
    # Install AWS CLI if not present
    if ! command -v aws &> /dev/null; then
        log "Installing AWS CLI"
        pip install awscli
    fi
    
    # Upload database backup
    if [ -f "$BACKUP_DIR/bdc_db_backup_$DATE.sql.gz" ]; then
        aws s3 cp "$BACKUP_DIR/bdc_db_backup_$DATE.sql.gz" "s3://$BACKUP_S3_BUCKET/database_backups/"
        log "Database backup uploaded to S3"
    fi
    
    # Upload files backup
    if [ -f "$FILES_BACKUP_FILE" ]; then
        aws s3 cp "$FILES_BACKUP_FILE" "s3://$BACKUP_S3_BUCKET/files_backups/"
        log "Files backup uploaded to S3"
    fi
else
    log "S3 upload not configured"
fi

# Cleanup old local backups (keep last 7 days)
log "Cleaning up old local backups"
find "$BACKUP_DIR" -name "bdc_*_backup_*.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "backup_*.log" -mtime +7 -delete

log "Backup process completed successfully"

# Send notification if configured
if [ ! -z "$BACKUP_NOTIFICATION_URL" ]; then
    curl -X POST "$BACKUP_NOTIFICATION_URL" \
         -H "Content-Type: application/json" \
         -d "{\"message\": \"BDC backup completed successfully at $DATE\"}"
fi