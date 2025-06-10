"""
Automated Backup and Recovery Service for BDC Platform
Provides scheduled backups, point-in-time recovery, and disaster recovery capabilities.
"""

import os
import shutil
import subprocess
import tarfile
import zipfile
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import schedule
import threading
import boto3
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Backup metadata information"""
    backup_id: str
    backup_type: str  # full, incremental, differential
    timestamp: datetime
    size_bytes: int
    duration_seconds: float
    status: str  # completed, failed, in_progress
    database_name: str
    app_version: str
    compression: str
    encryption: bool
    storage_location: str
    retention_days: int
    checksum: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    name: str
    backup_type: str
    frequency: str  # hourly, daily, weekly, monthly
    time: str  # HH:MM format
    retention_days: int
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

class BackupService:
    """Comprehensive backup and recovery service"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_schedules = []
        self.backup_history = []
        self.recovery_points = {}
        self._scheduler_thread = None
        self._running = False
        
        # Default configuration
        self.config = {
            'BACKUP_DIRECTORY': '/var/backups/bdc',
            'BACKUP_RETENTION_DAYS': 30,
            'BACKUP_COMPRESSION': 'gzip',  # gzip, bzip2, lzma
            'BACKUP_ENCRYPTION': True,
            'BACKUP_ENCRYPTION_KEY': None,
            'BACKUP_STORAGE': 'local',  # local, s3, azure, gcs
            'BACKUP_S3_BUCKET': None,
            'BACKUP_S3_PREFIX': 'bdc-backups',
            'BACKUP_MAX_SIZE_GB': 100,
            'BACKUP_PARALLEL_JOBS': 4,
            'BACKUP_VERIFY': True,
            'BACKUP_NOTIFICATION_EMAIL': None
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.backup_service = self
        
        # Update config from app
        self.config.update(app.config.get('BACKUP_CONFIG', {}))
        
        # Create backup directory
        Path(self.config['BACKUP_DIRECTORY']).mkdir(parents=True, exist_ok=True)
        
        # Initialize storage backend
        self._init_storage_backend()
        
        # Load backup schedules
        self._load_schedules()
        
        # Start scheduler
        self.start_scheduler()
    
    def _init_storage_backend(self):
        """Initialize storage backend"""
        storage_type = self.config['BACKUP_STORAGE']
        
        if storage_type == 's3':
            self.s3_client = boto3.client('s3')
            logger.info("S3 storage backend initialized")
        elif storage_type == 'azure':
            # Initialize Azure Blob Storage
            pass
        elif storage_type == 'gcs':
            # Initialize Google Cloud Storage
            pass
        else:
            logger.info("Using local storage backend")
    
    def _load_schedules(self):
        """Load backup schedules from configuration"""
        # Default schedules
        default_schedules = [
            BackupSchedule(
                name="daily_full_backup",
                backup_type="full",
                frequency="daily",
                time="02:00",
                retention_days=7
            ),
            BackupSchedule(
                name="hourly_incremental",
                backup_type="incremental",
                frequency="hourly",
                time="00",
                retention_days=1,
                enabled=False
            ),
            BackupSchedule(
                name="weekly_full_backup",
                backup_type="full",
                frequency="weekly",
                time="03:00",
                retention_days=30
            )
        ]
        
        # Load custom schedules from config or database
        custom_schedules = self._load_custom_schedules()
        
        self.backup_schedules = custom_schedules or default_schedules
        logger.info(f"Loaded {len(self.backup_schedules)} backup schedules")
    
    def _load_custom_schedules(self) -> Optional[List[BackupSchedule]]:
        """Load custom schedules from database"""
        try:
            # This would load from database
            return None
        except Exception as e:
            logger.error(f"Failed to load custom schedules: {str(e)}")
            return None
    
    def create_backup(
        self,
        backup_type: str = "full",
        description: str = None,
        include_files: bool = True,
        notify: bool = True
    ) -> BackupMetadata:
        """Create a backup"""
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.utcnow()
        
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            timestamp=start_time,
            size_bytes=0,
            duration_seconds=0,
            status="in_progress",
            database_name=self.app.config.get('DATABASE_NAME', 'bdc'),
            app_version=self._get_app_version(),
            compression=self.config['BACKUP_COMPRESSION'],
            encryption=self.config['BACKUP_ENCRYPTION'],
            storage_location="",
            retention_days=self.config['BACKUP_RETENTION_DAYS']
        )
        
        try:
            logger.info(f"Starting {backup_type} backup: {backup_id}")
            
            # Create backup directory
            backup_path = Path(self.config['BACKUP_DIRECTORY']) / backup_id
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup database
            db_backup_file = self._backup_database(backup_path, backup_type)
            
            # Backup files if requested
            if include_files:
                files_backup_file = self._backup_files(backup_path)
            
            # Create backup archive
            archive_file = self._create_archive(backup_path, backup_id)
            
            # Encrypt if enabled
            if self.config['BACKUP_ENCRYPTION']:
                archive_file = self._encrypt_backup(archive_file)
            
            # Calculate checksum
            metadata.checksum = self._calculate_checksum(archive_file)
            
            # Upload to storage
            storage_location = self._upload_backup(archive_file, backup_id)
            metadata.storage_location = storage_location
            
            # Verify backup if enabled
            if self.config['BACKUP_VERIFY']:
                self._verify_backup(archive_file, metadata)
            
            # Update metadata
            metadata.size_bytes = os.path.getsize(archive_file)
            metadata.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            metadata.status = "completed"
            
            # Clean up local files
            self._cleanup_local_files(backup_path, archive_file)
            
            # Record backup
            self.backup_history.append(metadata)
            self._save_backup_metadata(metadata)
            
            # Send notification
            if notify:
                self._send_backup_notification(metadata, success=True)
            
            logger.info(
                f"Backup completed: {backup_id} "
                f"({metadata.size_bytes / 1024 / 1024:.2f}MB in {metadata.duration_seconds:.1f}s)"
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            metadata.status = "failed"
            metadata.error_message = str(e)
            metadata.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            
            self.backup_history.append(metadata)
            
            if notify:
                self._send_backup_notification(metadata, success=False)
            
            raise
    
    def _backup_database(self, backup_path: Path, backup_type: str) -> Path:
        """Backup database"""
        db_config = self._get_db_config()
        backup_file = backup_path / f"database_{backup_type}.sql"
        
        if backup_type == "full":
            # Full database backup
            cmd = [
                'pg_dump',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-f', str(backup_file),
                '--verbose',
                '--clean',
                '--if-exists',
                '--no-owner',
                '--no-privileges'
            ]
            
            # Set password via environment
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Database backup failed: {result.stderr}")
                
        elif backup_type == "incremental":
            # Incremental backup using WAL archiving
            self._backup_wal_files(backup_path)
            
        return backup_file
    
    def _backup_files(self, backup_path: Path) -> Path:
        """Backup application files"""
        files_backup = backup_path / "files"
        files_backup.mkdir(exist_ok=True)
        
        # Backup uploaded files
        uploads_dir = Path(self.app.config.get('UPLOAD_FOLDER', 'uploads'))
        if uploads_dir.exists():
            shutil.copytree(
                uploads_dir,
                files_backup / 'uploads',
                ignore=shutil.ignore_patterns('*.tmp', '*.log')
            )
        
        # Backup configuration files
        config_files = ['config.py', '.env', 'requirements.txt']
        for config_file in config_files:
            if os.path.exists(config_file):
                shutil.copy2(config_file, files_backup)
        
        return files_backup
    
    def _create_archive(self, backup_path: Path, backup_id: str) -> Path:
        """Create compressed archive"""
        compression = self.config['BACKUP_COMPRESSION']
        
        if compression == 'gzip':
            archive_file = backup_path.parent / f"{backup_id}.tar.gz"
            with tarfile.open(archive_file, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_id)
                
        elif compression == 'bzip2':
            archive_file = backup_path.parent / f"{backup_id}.tar.bz2"
            with tarfile.open(archive_file, "w:bz2") as tar:
                tar.add(backup_path, arcname=backup_id)
                
        elif compression == 'lzma':
            archive_file = backup_path.parent / f"{backup_id}.tar.xz"
            with tarfile.open(archive_file, "w:xz") as tar:
                tar.add(backup_path, arcname=backup_id)
                
        else:  # zip
            archive_file = backup_path.parent / f"{backup_id}.zip"
            with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_path.parent)
                        zipf.write(file_path, arcname)
        
        return archive_file
    
    def _encrypt_backup(self, backup_file: Path) -> Path:
        """Encrypt backup file"""
        # This is a placeholder - implement actual encryption
        encrypted_file = backup_file.with_suffix(backup_file.suffix + '.enc')
        
        # Use GPG or another encryption method
        encryption_key = self.config['BACKUP_ENCRYPTION_KEY']
        if not encryption_key:
            logger.warning("Encryption key not configured, skipping encryption")
            return backup_file
        
        # Encrypt the file
        # subprocess.run(['gpg', '--encrypt', ...])
        
        return encrypted_file
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def _upload_backup(self, backup_file: Path, backup_id: str) -> str:
        """Upload backup to storage"""
        storage_type = self.config['BACKUP_STORAGE']
        
        if storage_type == 's3':
            bucket = self.config['BACKUP_S3_BUCKET']
            key = f"{self.config['BACKUP_S3_PREFIX']}/{backup_id}/{backup_file.name}"
            
            self.s3_client.upload_file(
                str(backup_file),
                bucket,
                key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'
                }
            )
            
            return f"s3://{bucket}/{key}"
            
        else:  # local storage
            storage_path = Path(self.config['BACKUP_DIRECTORY']) / 'storage' / backup_id
            storage_path.mkdir(parents=True, exist_ok=True)
            
            final_path = storage_path / backup_file.name
            shutil.move(str(backup_file), str(final_path))
            
            return str(final_path)
    
    def _verify_backup(self, backup_file: Path, metadata: BackupMetadata):
        """Verify backup integrity"""
        # Verify checksum
        calculated_checksum = self._calculate_checksum(backup_file)
        if calculated_checksum != metadata.checksum:
            raise Exception("Backup verification failed: checksum mismatch")
        
        # Test restore (optional)
        if self.config.get('BACKUP_TEST_RESTORE'):
            self._test_restore(backup_file)
    
    def restore_backup(
        self,
        backup_id: str,
        restore_point: Optional[datetime] = None,
        restore_database: bool = True,
        restore_files: bool = True,
        target_database: Optional[str] = None
    ) -> Dict[str, Any]:
        """Restore from backup"""
        logger.info(f"Starting restore from backup: {backup_id}")
        start_time = datetime.utcnow()
        
        try:
            # Find backup metadata
            metadata = self._find_backup_metadata(backup_id)
            if not metadata:
                raise Exception(f"Backup not found: {backup_id}")
            
            # Download backup if needed
            local_backup = self._download_backup(metadata)
            
            # Decrypt if needed
            if metadata.encryption:
                local_backup = self._decrypt_backup(local_backup)
            
            # Extract archive
            extract_path = self._extract_archive(local_backup)
            
            # Restore database
            if restore_database:
                self._restore_database(
                    extract_path / backup_id / f"database_{metadata.backup_type}.sql",
                    target_database
                )
            
            # Restore files
            if restore_files:
                self._restore_files(extract_path / backup_id / "files")
            
            # Apply point-in-time recovery if requested
            if restore_point and restore_point > metadata.timestamp:
                self._apply_point_in_time_recovery(restore_point)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                'success': True,
                'backup_id': backup_id,
                'restored_at': datetime.utcnow(),
                'duration_seconds': duration,
                'database_restored': restore_database,
                'files_restored': restore_files,
                'point_in_time': restore_point
            }
            
            logger.info(f"Restore completed in {duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
    
    def _restore_database(self, sql_file: Path, target_database: Optional[str] = None):
        """Restore database from SQL dump"""
        db_config = self._get_db_config()
        
        if target_database:
            db_config['database'] = target_database
        
        # Create database if it doesn't exist
        self._ensure_database_exists(db_config)
        
        # Restore from dump
        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', db_config['database'],
            '-f', str(sql_file)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Database restore failed: {result.stderr}")
    
    def _ensure_database_exists(self, db_config: Dict[str, Any]):
        """Ensure target database exists"""
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{db_config['database']}'"
        )
        
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_config['database']}")
            logger.info(f"Created database: {db_config['database']}")
        
        cursor.close()
        conn.close()
    
    def _restore_files(self, files_path: Path):
        """Restore application files"""
        if not files_path.exists():
            logger.warning("No files to restore")
            return
        
        # Restore uploads
        uploads_backup = files_path / 'uploads'
        if uploads_backup.exists():
            uploads_dir = Path(self.app.config.get('UPLOAD_FOLDER', 'uploads'))
            
            # Backup current uploads
            if uploads_dir.exists():
                backup_name = f"uploads_before_restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(str(uploads_dir), str(uploads_dir.parent / backup_name))
            
            # Restore uploads
            shutil.copytree(uploads_backup, uploads_dir)
            logger.info("Restored uploaded files")
    
    def schedule_backup(self, schedule: BackupSchedule):
        """Add a backup schedule"""
        self.backup_schedules.append(schedule)
        self._update_schedule_times()
        logger.info(f"Added backup schedule: {schedule.name}")
    
    def start_scheduler(self):
        """Start backup scheduler"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info("Backup scheduler started")
    
    def stop_scheduler(self):
        """Stop backup scheduler"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join()
        logger.info("Backup scheduler stopped")
    
    def _run_scheduler(self):
        """Run backup scheduler"""
        while self._running:
            try:
                # Check and run scheduled backups
                self._check_schedules()
                
                # Clean up old backups
                self._cleanup_old_backups()
                
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
            
            # Wait before next check
            time.sleep(60)  # Check every minute
    
    def _check_schedules(self):
        """Check and run scheduled backups"""
        now = datetime.utcnow()
        
        for schedule in self.backup_schedules:
            if not schedule.enabled:
                continue
            
            if schedule.next_run and now >= schedule.next_run:
                # Run backup
                try:
                    logger.info(f"Running scheduled backup: {schedule.name}")
                    self.create_backup(
                        backup_type=schedule.backup_type,
                        description=f"Scheduled backup: {schedule.name}"
                    )
                    
                    schedule.last_run = now
                    self._update_next_run(schedule)
                    
                except Exception as e:
                    logger.error(f"Scheduled backup failed: {schedule.name} - {str(e)}")
    
    def _update_next_run(self, schedule: BackupSchedule):
        """Update next run time for schedule"""
        if schedule.frequency == 'hourly':
            schedule.next_run = schedule.last_run + timedelta(hours=1)
        elif schedule.frequency == 'daily':
            schedule.next_run = schedule.last_run + timedelta(days=1)
        elif schedule.frequency == 'weekly':
            schedule.next_run = schedule.last_run + timedelta(weeks=1)
        elif schedule.frequency == 'monthly':
            # Add one month
            next_month = schedule.last_run.replace(day=1) + timedelta(days=32)
            schedule.next_run = next_month.replace(day=schedule.last_run.day)
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config['BACKUP_RETENTION_DAYS'])
        
        old_backups = [
            backup for backup in self.backup_history
            if backup.timestamp < cutoff_date and backup.status == 'completed'
        ]
        
        for backup in old_backups:
            try:
                self._delete_backup(backup)
                self.backup_history.remove(backup)
                logger.info(f"Deleted old backup: {backup.backup_id}")
            except Exception as e:
                logger.error(f"Failed to delete backup {backup.backup_id}: {str(e)}")
    
    def _delete_backup(self, metadata: BackupMetadata):
        """Delete a backup"""
        storage_type = self.config['BACKUP_STORAGE']
        
        if storage_type == 's3' and metadata.storage_location.startswith('s3://'):
            # Parse S3 location
            parts = metadata.storage_location.replace('s3://', '').split('/', 1)
            bucket = parts[0]
            key = parts[1]
            
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            
        else:  # local storage
            if os.path.exists(metadata.storage_location):
                os.remove(metadata.storage_location)
    
    def get_backup_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        backup_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[BackupMetadata]:
        """Get backup history with filters"""
        backups = self.backup_history
        
        if start_date:
            backups = [b for b in backups if b.timestamp >= start_date]
        
        if end_date:
            backups = [b for b in backups if b.timestamp <= end_date]
        
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        
        if status:
            backups = [b for b in backups if b.status == status]
        
        return sorted(backups, key=lambda x: x.timestamp, reverse=True)
    
    def get_recovery_points(self) -> List[Dict[str, Any]]:
        """Get available recovery points"""
        recovery_points = []
        
        for backup in self.backup_history:
            if backup.status == 'completed':
                recovery_points.append({
                    'backup_id': backup.backup_id,
                    'timestamp': backup.timestamp,
                    'type': backup.backup_type,
                    'size_mb': round(backup.size_bytes / 1024 / 1024, 2),
                    'can_restore_to': self._calculate_recovery_range(backup)
                })
        
        return recovery_points
    
    def _calculate_recovery_range(self, backup: BackupMetadata) -> Dict[str, datetime]:
        """Calculate point-in-time recovery range for a backup"""
        # Base recovery point is the backup timestamp
        start = backup.timestamp
        
        # End depends on next backup or current time
        next_backup = None
        for b in self.backup_history:
            if b.timestamp > backup.timestamp and b.status == 'completed':
                if not next_backup or b.timestamp < next_backup.timestamp:
                    next_backup = b
        
        end = next_backup.timestamp if next_backup else datetime.utcnow()
        
        return {'start': start, 'end': end}
    
    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        db_url = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Parse database URL
        if db_url.startswith('postgresql://'):
            import urllib.parse
            result = urllib.parse.urlparse(db_url)
            
            return {
                'host': result.hostname,
                'port': result.port or 5432,
                'user': result.username,
                'password': result.password,
                'database': result.path[1:]  # Remove leading /
            }
        
        return {}
    
    def _get_app_version(self) -> str:
        """Get application version"""
        try:
            with open('VERSION', 'r') as f:
                return f.read().strip()
        except:
            return '1.0.0'
    
    def _save_backup_metadata(self, metadata: BackupMetadata):
        """Save backup metadata to persistent storage"""
        # This would save to database or file
        pass
    
    def _find_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Find backup metadata by ID"""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def _send_backup_notification(self, metadata: BackupMetadata, success: bool):
        """Send backup notification"""
        if not self.config['BACKUP_NOTIFICATION_EMAIL']:
            return
        
        # Send email notification
        subject = f"Backup {'Completed' if success else 'Failed'}: {metadata.backup_id}"
        body = f"""
Backup {'completed successfully' if success else 'failed'}:

Backup ID: {metadata.backup_id}
Type: {metadata.backup_type}
Started: {metadata.timestamp}
Duration: {metadata.duration_seconds:.1f} seconds
Size: {metadata.size_bytes / 1024 / 1024:.2f} MB
Status: {metadata.status}
"""
        
        if not success and metadata.error_message:
            body += f"\nError: {metadata.error_message}"
        
        # Send email (implementation depends on email service)
        logger.info(f"Backup notification sent: {subject}")

# Global instance
backup_service = BackupService()