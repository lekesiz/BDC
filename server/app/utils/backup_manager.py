"""Backup and recovery management for production deployment."""

import os
import gzip
import shutil
import boto3
from app.utils.secure_subprocess import SecureSubprocess, DatabaseBackupSecure
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import current_app
from cryptography.fernet import Fernet
import schedule
import time


class BackupManager:
    """Comprehensive backup and recovery system."""
    
    def __init__(self, app=None):
        self.app = app
        self.s3_client = None
        self.encryption_key = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize backup manager with Flask app."""
        self.app = app
        
        # Initialize S3 client if configured
        aws_access_key = app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = app.config.get('AWS_SECRET_ACCESS_KEY')
        
        if aws_access_key and aws_secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=app.config.get('AWS_S3_REGION', 'us-east-1')
            )
        
        # Initialize encryption
        encryption_key = app.config.get('BACKUP_ENCRYPTION_KEY')
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            # Generate a key if none provided (store this securely!)
            self.encryption_key = Fernet.generate_key()
            app.logger.warning(
                f"Generated backup encryption key: {self.encryption_key.decode()}"
                " - Store this securely!"
            )
    
    def create_database_backup(self):
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"bdc_db_backup_{timestamp}.sql"
            backup_path = os.path.join('/tmp', backup_filename)
            
            database_url = current_app.config.get('DATABASE_URL')
            
            if database_url.startswith('postgresql://'):
                # PostgreSQL backup
                self._create_postgres_backup(database_url, backup_path)
            elif database_url.startswith('sqlite://'):
                # SQLite backup
                self._create_sqlite_backup(database_url, backup_path)
            else:
                raise ValueError(f"Unsupported database type: {database_url}")
            
            # Compress the backup
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            os.remove(backup_path)
            
            # Encrypt the backup
            encrypted_path = self._encrypt_file(compressed_path)
            os.remove(compressed_path)
            
            # Upload to S3 if configured
            if self.s3_client:
                s3_key = f"database_backups/{os.path.basename(encrypted_path)}"
                self._upload_to_s3(encrypted_path, s3_key)
            
            # Clean up local file if uploaded to S3
            if self.s3_client:
                os.remove(encrypted_path)
                backup_location = f"s3://{current_app.config.get('BACKUP_S3_BUCKET')}/{s3_key}"
            else:
                backup_location = encrypted_path
            
            current_app.logger.info(f"Database backup created: {backup_location}")
            
            return {
                'success': True,
                'location': backup_location,
                'timestamp': timestamp,
                'size': self._get_file_size(encrypted_path) if not self.s3_client else None
            }
            
        except Exception as e:
            current_app.logger.error(f"Database backup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def create_files_backup(self):
        """Create a backup of uploaded files."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            
            if not os.path.exists(upload_folder):
                return {
                    'success': True,
                    'message': 'No files to backup',
                    'timestamp': timestamp
                }
            
            backup_filename = f"bdc_files_backup_{timestamp}.tar.gz"
            backup_path = os.path.join('/tmp', backup_filename)
            
            # Create tar.gz archive securely
            SecureSubprocess.run_secure([
                'tar', '-czf', backup_path, '-C', os.path.dirname(upload_folder),
                os.path.basename(upload_folder)
            ], timeout=1800, check=True)
            
            # Encrypt the backup
            encrypted_path = self._encrypt_file(backup_path)
            os.remove(backup_path)
            
            # Upload to S3 if configured
            if self.s3_client:
                s3_key = f"files_backups/{os.path.basename(encrypted_path)}"
                self._upload_to_s3(encrypted_path, s3_key)
                os.remove(encrypted_path)
                backup_location = f"s3://{current_app.config.get('BACKUP_S3_BUCKET')}/{s3_key}"
            else:
                backup_location = encrypted_path
            
            current_app.logger.info(f"Files backup created: {backup_location}")
            
            return {
                'success': True,
                'location': backup_location,
                'timestamp': timestamp
            }
            
        except Exception as e:
            current_app.logger.error(f"Files backup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def create_full_backup(self):
        """Create a full system backup."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'database': self.create_database_backup(),
            'files': self.create_files_backup()
        }
        
        # Create backup manifest
        manifest = {
            'backup_type': 'full',
            'created_at': results['timestamp'],
            'components': results,
            'version': current_app.config.get('VERSION', '1.0.0')
        }
        
        # Save manifest
        manifest_path = self._save_backup_manifest(manifest)
        
        success = all(
            result.get('success', False) 
            for result in [results['database'], results['files']]
        )
        
        if success:
            current_app.logger.info("Full backup completed successfully")
        else:
            current_app.logger.error("Full backup completed with errors")
        
        return {
            'success': success,
            'manifest': manifest,
            'manifest_path': manifest_path
        }
    
    def restore_database_backup(self, backup_location, timestamp=None):
        """Restore database from backup."""
        try:
            # Download and decrypt backup if needed
            local_path = self._prepare_backup_for_restore(backup_location)
            
            # Decompress
            decompressed_path = local_path.replace('.encrypted', '').replace('.gz', '')
            with gzip.open(local_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            database_url = current_app.config.get('DATABASE_URL')
            
            if database_url.startswith('postgresql://'):
                self._restore_postgres_backup(database_url, decompressed_path)
            elif database_url.startswith('sqlite://'):
                self._restore_sqlite_backup(database_url, decompressed_path)
            else:
                raise ValueError(f"Unsupported database type: {database_url}")
            
            # Clean up temporary files
            os.remove(local_path)
            os.remove(decompressed_path)
            
            current_app.logger.info(f"Database restored from: {backup_location}")
            
            return {'success': True, 'message': 'Database restored successfully'}
            
        except Exception as e:
            current_app.logger.error(f"Database restore failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_backups(self):
        """List available backups."""
        backups = []
        
        if self.s3_client:
            # List S3 backups
            bucket = current_app.config.get('BACKUP_S3_BUCKET')
            try:
                response = self.s3_client.list_objects_v2(Bucket=bucket)
                for obj in response.get('Contents', []):
                    backups.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'location': f"s3://{bucket}/{obj['Key']}"
                    })
            except Exception as e:
                current_app.logger.error(f"Failed to list S3 backups: {e}")
        
        # Sort by last modified
        backups.sort(key=lambda x: x['last_modified'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, retention_days=30):
        """Clean up backups older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if self.s3_client:
            bucket = current_app.config.get('BACKUP_S3_BUCKET')
            try:
                response = self.s3_client.list_objects_v2(Bucket=bucket)
                deleted_count = 0
                
                for obj in response.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
                        deleted_count += 1
                
                current_app.logger.info(f"Cleaned up {deleted_count} old backups")
                return {'success': True, 'deleted_count': deleted_count}
                
            except Exception as e:
                current_app.logger.error(f"Backup cleanup failed: {e}")
                return {'success': False, 'error': str(e)}
    
    def _create_postgres_backup(self, database_url, backup_path):
        """Create PostgreSQL backup using secure method."""
        success = DatabaseBackupSecure.create_postgres_backup(database_url, backup_path)
        if not success:
            raise Exception("PostgreSQL backup failed")
    
    def _create_sqlite_backup(self, database_url, backup_path):
        """Create SQLite backup."""
        db_path = database_url.replace('sqlite:///', '')
        shutil.copy2(db_path, backup_path)
    
    def _restore_postgres_backup(self, database_url, backup_path):
        """Restore PostgreSQL backup using secure method."""
        success = DatabaseBackupSecure.restore_postgres_backup(database_url, backup_path)
        if not success:
            raise Exception("PostgreSQL restore failed")
    
    def _restore_sqlite_backup(self, database_url, backup_path):
        """Restore SQLite backup."""
        db_path = database_url.replace('sqlite:///', '')
        shutil.copy2(backup_path, db_path)
    
    def _encrypt_file(self, file_path):
        """Encrypt a file."""
        if not self.encryption_key:
            return file_path
        
        fernet = Fernet(self.encryption_key)
        encrypted_path = f"{file_path}.encrypted"
        
        with open(file_path, 'rb') as f_in:
            with open(encrypted_path, 'wb') as f_out:
                f_out.write(fernet.encrypt(f_in.read()))
        
        return encrypted_path
    
    def _decrypt_file(self, encrypted_path):
        """Decrypt a file."""
        if not self.encryption_key:
            return encrypted_path
        
        fernet = Fernet(self.encryption_key)
        decrypted_path = encrypted_path.replace('.encrypted', '')
        
        with open(encrypted_path, 'rb') as f_in:
            with open(decrypted_path, 'wb') as f_out:
                f_out.write(fernet.decrypt(f_in.read()))
        
        return decrypted_path
    
    def _upload_to_s3(self, file_path, s3_key):
        """Upload file to S3."""
        bucket = current_app.config.get('BACKUP_S3_BUCKET')
        self.s3_client.upload_file(file_path, bucket, s3_key)
    
    def _download_from_s3(self, s3_key, local_path):
        """Download file from S3."""
        bucket = current_app.config.get('BACKUP_S3_BUCKET')
        self.s3_client.download_file(bucket, s3_key, local_path)
    
    def _prepare_backup_for_restore(self, backup_location):
        """Prepare backup file for restoration."""
        if backup_location.startswith('s3://'):
            # Download from S3
            s3_key = backup_location.replace(f"s3://{current_app.config.get('BACKUP_S3_BUCKET')}/", "")
            local_path = f"/tmp/{os.path.basename(s3_key)}"
            self._download_from_s3(s3_key, local_path)
        else:
            local_path = backup_location
        
        # Decrypt if needed
        if local_path.endswith('.encrypted'):
            decrypted_path = self._decrypt_file(local_path)
            if local_path != backup_location:  # Downloaded file
                os.remove(local_path)
            return decrypted_path
        
        return local_path
    
    def _save_backup_manifest(self, manifest):
        """Save backup manifest."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        manifest_filename = f"backup_manifest_{timestamp}.json"
        manifest_path = os.path.join('/tmp', manifest_filename)
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        # Upload manifest to S3 if configured
        if self.s3_client:
            s3_key = f"manifests/{manifest_filename}"
            self._upload_to_s3(manifest_path, s3_key)
        
        return manifest_path
    
    def _get_file_size(self, file_path):
        """Get file size in human readable format."""
        if not os.path.exists(file_path):
            return None
        
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def setup_backup_scheduler(app, backup_manager):
    """Setup automated backup scheduling."""
    
    backup_schedule = app.config.get('BACKUP_SCHEDULE', '0 2 * * *')  # Default: 2 AM daily
    
    def scheduled_backup():
        with app.app_context():
            backup_manager.create_full_backup()
            backup_manager.cleanup_old_backups()
    
    # Parse cron expression and schedule accordingly
    # For simplicity, using daily schedule - implement full cron parsing if needed
    schedule.every().day.at("02:00").do(scheduled_backup)
    
    app.logger.info(f"Backup scheduler configured: {backup_schedule}")