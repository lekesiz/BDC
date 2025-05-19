#!/bin/bash
# Database backup script for BDC application

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-"/opt/bdc/backup"}
RETENTION_DAYS=${RETENTION_DAYS:-30}
DB_CONTAINER="bdc-postgres-${ENVIRONMENT:-prod}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# S3 backup configuration (optional)
S3_BUCKET=${S3_BACKUP_BUCKET:-""}
S3_PREFIX="backups/${ENVIRONMENT:-prod}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)"

# Backup database
echo "Backing up database..."
docker exec -t "$DB_CONTAINER" pg_dumpall -c -U postgres > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Backup uploaded files
echo "Backing up uploaded files..."
tar czf "$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz" -C /opt/bdc uploads/

# Backup environment configuration
echo "Backing up configuration..."
cp /opt/bdc/.env "$BACKUP_DIR/env_backup_$TIMESTAMP"
cp /opt/bdc/docker-compose.yml "$BACKUP_DIR/compose_backup_$TIMESTAMP.yml"

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ]; then
    echo "Uploading backup to S3..."
    aws s3 cp "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz" \
        "s3://$S3_BUCKET/$S3_PREFIX/db_backup_$TIMESTAMP.sql.gz"
    aws s3 cp "$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz" \
        "s3://$S3_BUCKET/$S3_PREFIX/files_backup_$TIMESTAMP.tar.gz"
fi

# Clean up old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "env_backup_*" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "compose_backup_*" -mtime +$RETENTION_DAYS -delete

# Clean up S3 if configured
if [ -n "$S3_BUCKET" ]; then
    cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
    aws s3api list-objects --bucket "$S3_BUCKET" --prefix "$S3_PREFIX/" \
        --query "Contents[?LastModified<'$cutoff_date'].Key" \
        --output text | tr '\t' '\n' | \
        xargs -I {} aws s3 rm "s3://$S3_BUCKET/{}"
fi

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo "Backup completed at $(date)"
echo "Backup size: $BACKUP_SIZE"
echo "Backup location: $BACKUP_DIR"

# Verify backup
echo "Verifying backup..."
if gzip -t "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"; then
    echo "Database backup verified successfully"
else
    echo "ERROR: Database backup verification failed!"
    exit 1
fi

# Send notification (optional)
if [ -n "$BACKUP_NOTIFICATION_EMAIL" ]; then
    echo "Backup completed successfully for $ENVIRONMENT environment" | \
        mail -s "BDC Backup Success - $TIMESTAMP" "$BACKUP_NOTIFICATION_EMAIL"
fi

exit 0