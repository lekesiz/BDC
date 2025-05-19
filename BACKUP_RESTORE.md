# BDC Backup and Restore Procedures

This guide provides comprehensive procedures for backing up and restoring the BDC application data.

## Table of Contents
- [Backup Strategy](#backup-strategy)
- [Database Backup](#database-backup)
- [File Storage Backup](#file-storage-backup)
- [Configuration Backup](#configuration-backup)
- [Automated Backups](#automated-backups)
- [Restore Procedures](#restore-procedures)
- [Disaster Recovery](#disaster-recovery)
- [Backup Verification](#backup-verification)

## Backup Strategy

### Backup Components
1. **PostgreSQL Database** - All application data
2. **File Storage** - Uploaded documents, images
3. **Configuration Files** - Environment variables, settings
4. **Application Code** - Source code and dependencies

### Backup Schedule
- **Full Backup**: Weekly (Sunday 2:00 AM)
- **Incremental Backup**: Daily (2:00 AM)
- **Transaction Logs**: Continuous

### Retention Policy
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months
- Yearly backups: 5 years

## Database Backup

### Manual Backup

```bash
# Full database backup
pg_dump -h localhost -U bdc_user -d bdc_db -f backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -h localhost -U bdc_user -d bdc_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Custom format (recommended)
pg_dump -h localhost -U bdc_user -d bdc_db -Fc -f backup_$(date +%Y%m%d_%H%M%S).dump

# Specific tables only
pg_dump -h localhost -U bdc_user -d bdc_db -t users -t beneficiaries -f users_backup.sql
```

### Automated Database Backup Script

```bash
#!/bin/bash
# backup_database.sh

# Configuration
DB_HOST="localhost"
DB_USER="bdc_user"
DB_NAME="bdc_db"
BACKUP_DIR="/backups/database"
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bdc_backup_$TIMESTAMP.dump"

# Perform backup
export PGPASSWORD=$DB_PASSWORD
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -Fc -f "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Remove old backups
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

# Upload to cloud storage (optional)
aws s3 cp "$BACKUP_FILE.gz" s3://bdc-backups/database/

echo "Backup completed: $BACKUP_FILE.gz"
```

### Point-in-Time Recovery Setup

```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'

# Create WAL archive directory
mkdir -p /backups/wal
chown postgres:postgres /backups/wal
```

## File Storage Backup

### Local File Backup

```bash
#!/bin/bash
# backup_files.sh

# Configuration
SOURCE_DIR="/app/uploads"
BACKUP_DIR="/backups/files"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup files with rsync
rsync -avz --delete "$SOURCE_DIR/" "$BACKUP_DIR/uploads_$TIMESTAMP/"

# Create tar archive
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" -C "$SOURCE_DIR" .

# Remove old backups
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +7 -delete
```

### Cloud Storage Backup

```bash
# AWS S3 backup
aws s3 sync /app/uploads s3://bdc-backups/uploads/ --delete

# Google Cloud Storage backup
gsutil -m rsync -r -d /app/uploads gs://bdc-backups/uploads/

# Azure Blob Storage backup
az storage blob upload-batch \
  --source /app/uploads \
  --destination bdc-backups \
  --destination-path uploads
```

## Configuration Backup

### Environment Files

```bash
#!/bin/bash
# backup_config.sh

# Configuration
CONFIG_DIR="/app/config"
BACKUP_DIR="/backups/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Files to backup
CONFIG_FILES=(
  ".env"
  ".env.production"
  "nginx.conf"
  "docker-compose.yml"
  "supervisord.conf"
)

# Create backup directory
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Copy configuration files
for file in "${CONFIG_FILES[@]}"; do
  if [ -f "$CONFIG_DIR/$file" ]; then
    cp "$CONFIG_DIR/$file" "$BACKUP_DIR/$TIMESTAMP/"
  fi
done

# Create archive
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR/$TIMESTAMP" .
rm -rf "$BACKUP_DIR/$TIMESTAMP"

# Encrypt sensitive configurations
gpg --encrypt --recipient backup@example.com "$BACKUP_DIR/config_$TIMESTAMP.tar.gz"
rm "$BACKUP_DIR/config_$TIMESTAMP.tar.gz"
```

## Automated Backups

### Cron Configuration

```bash
# Edit crontab
crontab -e

# Daily database backup at 2 AM
0 2 * * * /scripts/backup_database.sh >> /logs/backup.log 2>&1

# Daily file backup at 3 AM
0 3 * * * /scripts/backup_files.sh >> /logs/backup.log 2>&1

# Weekly full backup on Sunday at 4 AM
0 4 * * 0 /scripts/backup_full.sh >> /logs/backup.log 2>&1

# Configuration backup on changes
*/30 * * * * /scripts/backup_config_if_changed.sh >> /logs/backup.log 2>&1
```

### Docker-based Backup

```yaml
# docker-compose.backup.yml
version: '3.8'

services:
  backup:
    image: postgres:13
    environment:
      - PGPASSWORD=${DB_PASSWORD}
    volumes:
      - ./backups:/backups
      - ./scripts:/scripts
    command: >
      sh -c "
        while true; do
          /scripts/backup_database.sh
          sleep 86400
        done
      "
    
  file-backup:
    image: alpine:latest
    volumes:
      - ./uploads:/source
      - ./backups:/backups
      - ./scripts:/scripts
    command: >
      sh -c "
        apk add --no-cache rsync
        while true; do
          /scripts/backup_files.sh
          sleep 86400
        done
      "
```

## Restore Procedures

### Database Restore

```bash
# Restore from SQL dump
psql -h localhost -U bdc_user -d bdc_db < backup.sql

# Restore from compressed dump
gunzip -c backup.sql.gz | psql -h localhost -U bdc_user -d bdc_db

# Restore from custom format
pg_restore -h localhost -U bdc_user -d bdc_db backup.dump

# Restore specific tables
pg_restore -h localhost -U bdc_user -d bdc_db -t users -t beneficiaries backup.dump

# Create new database and restore
createdb -h localhost -U postgres -T template0 bdc_db_restored
pg_restore -h localhost -U postgres -d bdc_db_restored backup.dump
```

### Point-in-Time Recovery

```bash
# Stop PostgreSQL
systemctl stop postgresql

# Clear data directory
rm -rf /var/lib/postgresql/13/main/*

# Restore base backup
tar -xzf base_backup.tar.gz -C /var/lib/postgresql/13/main/

# Create recovery configuration
cat > /var/lib/postgresql/13/main/recovery.conf << EOF
restore_command = 'cp /backups/wal/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_timeline = 'latest'
EOF

# Start PostgreSQL
systemctl start postgresql
```

### File Storage Restore

```bash
# Restore from tar archive
tar -xzf uploads_backup.tar.gz -C /app/uploads/

# Restore from rsync backup
rsync -avz /backups/files/uploads_latest/ /app/uploads/

# Restore from S3
aws s3 sync s3://bdc-backups/uploads/ /app/uploads/

# Restore with permissions
tar -xzpf uploads_backup.tar.gz -C /app/uploads/
chown -R www-data:www-data /app/uploads/
```

### Configuration Restore

```bash
# Decrypt configuration backup
gpg --decrypt config_backup.tar.gz.gpg > config_backup.tar.gz

# Extract configuration
tar -xzf config_backup.tar.gz -C /app/config/

# Update permissions
chmod 600 /app/config/.env
chmod 644 /app/config/nginx.conf
```

## Disaster Recovery

### Full System Recovery

```bash
#!/bin/bash
# disaster_recovery.sh

# 1. Restore system configuration
tar -xzf system_config.tar.gz -C /

# 2. Restore application code
cd /app
git clone https://github.com/your-org/bdc.git .
git checkout v1.2.3  # Specific version

# 3. Install dependencies
cd client && npm install
cd ../server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Restore database
pg_restore -h localhost -U postgres -C -d postgres latest_backup.dump

# 5. Restore files
tar -xzf uploads_backup.tar.gz -C /app/uploads/

# 6. Restore configurations
gpg --decrypt config_backup.tar.gz.gpg | tar -xz -C /app/config/

# 7. Start services
docker-compose up -d
```

### Recovery Time Objectives

| Component | RTO | RPO |
|-----------|-----|-----|
| Database | 1 hour | 5 minutes |
| File Storage | 2 hours | 1 hour |
| Application | 30 minutes | N/A |
| Full System | 4 hours | 1 hour |

## Backup Verification

### Automated Verification

```python
#!/usr/bin/env python3
# verify_backups.py

import os
import subprocess
import psycopg2
from datetime import datetime, timedelta

def verify_database_backup(backup_file):
    """Verify database backup integrity"""
    try:
        # Test restore to temporary database
        temp_db = f"bdc_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create temporary database
        subprocess.run([
            'createdb', '-h', 'localhost', '-U', 'postgres', temp_db
        ], check=True)
        
        # Restore backup
        result = subprocess.run([
            'pg_restore', '-h', 'localhost', '-U', 'postgres',
            '-d', temp_db, backup_file
        ], capture_output=True)
        
        if result.returncode != 0:
            raise Exception(f"Restore failed: {result.stderr}")
        
        # Verify data
        conn = psycopg2.connect(
            host='localhost',
            database=temp_db,
            user='postgres'
        )
        cur = conn.cursor()
        
        # Check table counts
        tables = ['users', 'beneficiaries', 'programs']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table}: {count} records")
        
        conn.close()
        
        # Drop temporary database
        subprocess.run([
            'dropdb', '-h', 'localhost', '-U', 'postgres', temp_db
        ], check=True)
        
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def verify_file_backup(backup_file):
    """Verify file backup integrity"""
    try:
        # Test archive
        result = subprocess.run([
            'tar', '-tzf', backup_file
        ], capture_output=True)
        
        if result.returncode != 0:
            raise Exception(f"Archive test failed: {result.stderr}")
        
        # Check file count
        file_count = len(result.stdout.decode().split('\n'))
        print(f"Archive contains {file_count} files")
        
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

# Run verification
if __name__ == "__main__":
    # Find latest backups
    backup_dir = "/backups"
    
    # Verify database backup
    db_backups = sorted([
        f for f in os.listdir(f"{backup_dir}/database")
        if f.endswith('.dump')
    ])
    
    if db_backups:
        latest_db = f"{backup_dir}/database/{db_backups[-1]}"
        print(f"Verifying database backup: {latest_db}")
        verify_database_backup(latest_db)
    
    # Verify file backup
    file_backups = sorted([
        f for f in os.listdir(f"{backup_dir}/files")
        if f.endswith('.tar.gz')
    ])
    
    if file_backups:
        latest_files = f"{backup_dir}/files/{file_backups[-1]}"
        print(f"Verifying file backup: {latest_files}")
        verify_file_backup(latest_files)
```

### Manual Verification Checklist

- [ ] Database backup file exists and is not empty
- [ ] Database backup can be restored successfully
- [ ] All tables contain expected data
- [ ] File backup archive is not corrupted
- [ ] File permissions are preserved
- [ ] Configuration backups are encrypted
- [ ] Backup logs show no errors
- [ ] Cloud storage sync is working
- [ ] Retention policy is being applied
- [ ] Recovery procedures are documented

## Best Practices

1. **Test Restores Regularly**: Perform monthly restore tests
2. **Monitor Backup Jobs**: Set up alerts for failed backups
3. **Secure Backup Storage**: Encrypt sensitive backups
4. **Multiple Locations**: Store backups in multiple locations
5. **Document Procedures**: Keep restore procedures up to date
6. **Version Control**: Track backup script changes
7. **Access Control**: Limit backup access to authorized personnel
8. **Audit Trail**: Log all backup and restore operations
9. **Capacity Planning**: Monitor backup storage usage
10. **Compliance**: Ensure backups meet regulatory requirements