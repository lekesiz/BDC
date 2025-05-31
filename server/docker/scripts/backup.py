#!/usr/bin/env python3
"""Automated backup service for BDC application."""

import os
import sys
import time
import logging
import schedule
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupService:
    """Automated backup service for production deployment."""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.backup_dir = Path('/backups')
        self.retention_days = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_database_backup(self):
        """Create database backup."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"bdc_db_backup_{timestamp}.sql"
            
            logger.info(f"Starting database backup to {backup_file}")
            
            # Extract database connection details
            if self.database_url.startswith('postgresql://'):
                self._backup_postgres(backup_file)
            else:
                logger.error(f"Unsupported database type: {self.database_url}")
                return False
            
            # Compress backup
            compressed_file = f"{backup_file}.gz"
            subprocess.run(['gzip', str(backup_file)], check=True)
            
            logger.info(f"Database backup completed: {compressed_file}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def _backup_postgres(self, backup_file):
        """Backup PostgreSQL database."""
        # Parse database URL
        url = self.database_url.replace('postgresql://', '')
        auth, host_db = url.split('@')
        username, password = auth.split(':')
        host_port, database = host_db.split('/')
        host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
        
        # Set environment for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Run pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', database,
            '--no-password',
            '-f', str(backup_file)
        ]
        
        subprocess.run(cmd, env=env, check=True)
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob('bdc_db_backup_*.sql.gz'):
                # Extract timestamp from filename
                try:
                    timestamp_str = backup_file.stem.replace('bdc_db_backup_', '').replace('.sql', '')
                    file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    if file_date < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup_file}")
                        
                except ValueError:
                    # Skip files with unexpected naming
                    continue
            
            logger.info(f"Cleanup completed: {deleted_count} old backups removed")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def upload_to_s3(self):
        """Upload backups to S3 if configured."""
        try:
            import boto3
            
            s3_bucket = os.environ.get('BACKUP_S3_BUCKET')
            if not s3_bucket:
                logger.info("S3 backup not configured")
                return
            
            s3_client = boto3.client('s3')
            
            # Upload recent backups
            for backup_file in self.backup_dir.glob('bdc_db_backup_*.sql.gz'):
                s3_key = f"database_backups/{backup_file.name}"
                
                try:
                    # Check if already uploaded
                    s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
                    logger.info(f"Backup already in S3: {s3_key}")
                except s3_client.exceptions.NoSuchKey:
                    # Upload the file
                    s3_client.upload_file(str(backup_file), s3_bucket, s3_key)
                    logger.info(f"Uploaded backup to S3: {s3_key}")
            
        except ImportError:
            logger.warning("boto3 not available for S3 upload")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
    
    def run_backup_cycle(self):
        """Run complete backup cycle."""
        logger.info("Starting backup cycle")
        
        # Create database backup
        if self.create_database_backup():
            # Upload to S3 if configured
            self.upload_to_s3()
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            logger.info("Backup cycle completed successfully")
        else:
            logger.error("Backup cycle failed")
    
    def start_scheduler(self):
        """Start the backup scheduler."""
        # Schedule daily backup at 2 AM
        schedule.every().day.at("02:00").do(self.run_backup_cycle)
        
        # Schedule weekly cleanup
        schedule.every().sunday.at("03:00").do(self.cleanup_old_backups)
        
        logger.info("Backup scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point."""
    backup_service = BackupService()
    
    # Check if we should run a one-time backup or start the scheduler
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        backup_service.run_backup_cycle()
    else:
        backup_service.start_scheduler()


if __name__ == '__main__':
    main()